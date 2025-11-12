import json
import shutil
import os
import sys
import subprocess
import time

# --- Helper Functions ---

def time_to_seconds(time_str):
    """Converts a HH:MM:SS string to seconds."""
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

def get_attack_details(attack_id):
    """Retrieves attack details from the JSON library."""
    with open('attack_library.json', 'r') as f:
        distros_dict = json.load(f)
    for attack in distros_dict['object']:
        if attack["attack_id"] == str(attack_id):
            return attack
    return None

def config_ns3(model_path, affected_values, start_seconds, end_seconds):
    """
    Modifies the run_ns-3.cc file to include scheduled attack parameters.
    """
    filepath = os.path.join(model_path, "run_ns-3.cc")
    with open(filepath, 'r') as f:
        filedata = f.read()

    # 1. Prepare C++ code for injection
    normal_values = {
        "data_rate_cluster": 10000000, "delay_cluster": 3,
        "data_rate_peer_to_peer": 40000000, "delay_peer_to_peer": 3
    }

    attack_body = ""
    normal_body = ""

    for key, value in affected_values.items():
        normal_value = normal_values.get(key)
        if normal_value is None:
            continue

        if 'cluster' in key:
            channel_vector = 'g_csmaChannels'
            attribute_name = "DataRate" if "data_rate" in key else "Delay"
            attribute_type = "DataRateValue" if "data_rate" in key else "TimeValue"
            attack_val_str = str(value) if "data_rate" in key else f"MilliSeconds({value})"
            normal_val_str = str(normal_value) if "data_rate" in key else f"MilliSeconds({normal_value})"
            
            attack_body += f'for(auto const& channel : {channel_vector}) {{ channel->SetAttribute("{attribute_name}", {attribute_type}({attack_val_str})); }}\n'
            normal_body += f'for(auto const& channel : {channel_vector}) {{ channel->SetAttribute("{attribute_name}", {attribute_type}({normal_val_str})); }}\n'

        elif 'peer_to_peer' in key:
            channel_vector = 'g_p2pDevices'
            attribute_name = "DataRate" if "data_rate" in key else "Delay"
            attribute_type = "DataRateValue" if "data_rate" in key else "TimeValue"
            attack_val_str = str(value) if "data_rate" in key else f"MilliSeconds({value})"
            normal_val_str = str(normal_value) if "data_rate" in key else f"MilliSeconds({normal_value})"

            attack_body += f'for(auto const& dev : g_p2pDevices) {{ dev->SetAttribute("{attribute_name}", {attribute_type}({attack_val_str})); }}\n'
            normal_body += f'for(auto const& dev : g_p2pDevices) {{ dev->SetAttribute("{attribute_name}", {attribute_type}({normal_val_str})); }}\n'


    # 2. Inject C++ code into the file content
    header_injection = """
#include <vector>
#include "ns3/csma-channel.h"
#include "ns3/point-to-point-channel.h"
std::vector<Ptr<CsmaChannel>> g_csmaChannels;
std::vector<Ptr<PointToPointNetDevice>> g_p2pDevices;
"""
    functions_injection = f"""
void SetAttackParameters() {{
    NS_LOG_UNCOND("ATTACK STARTING");
    {attack_body}
}}
void SetNormalParameters() {{
    NS_LOG_UNCOND("ATTACK ENDING");
    {normal_body}
}}
"""
    schedule_injection = f"""
    Simulator::Schedule(Seconds({start_seconds}.0), &SetAttackParameters);
    Simulator::Schedule(Seconds({end_seconds}.0), &SetNormalParameters);
"""
    csma_capture_injection = """
    csmaDevices[i] = chelper.Install(model->csma[i]);
    Ptr<Channel> channel = csmaDevices[i].Get(0)->GetChannel();
    g_csmaChannels.push_back(DynamicCast<CsmaChannel>(channel));
"""
    p2p_capture_injection = """
            NetDeviceContainer csma1dbell1=phelper3.Install(
                    model->market.Get(0), model->csma[i].Get(0));
            g_p2pDevices.push_back(DynamicCast<PointToPointNetDevice>(csma1dbell1.Get(0)));
            g_p2pDevices.push_back(DynamicCast<PointToPointNetDevice>(csma1dbell1.Get(1)));
"""

    filedata = filedata.replace('using namespace std;', 'using namespace std;\n' + header_injection + functions_injection)
    filedata = filedata.replace('csmaDevices[i] = chelper.Install(model->csma[i]);', csma_capture_injection)
    filedata = filedata.replace('NetDeviceContainer csma1dbell1=phelper3.Install(\n'
                                '                    model->market.Get(0), model->csma[i].Get(0));', p2p_capture_injection)
    filedata = filedata.replace('Simulator::Run ();', schedule_injection + '\n    Simulator::Run ();')
    # Remove old placeholder
    filedata = filedata.replace('//Flag', '')

    with open(filepath, 'w') as f:
        f.write(filedata)

def config_glm(model_path, affected_values):
    """
    Modifies the run_GridLab-D.glm file with all specified attack values.
    """
    filepath = os.path.join(model_path, "run_GridLab-D.glm")
    with open(filepath, 'r') as f:
        filedata = f.read()

    for key, value in affected_values.items():
        filedata = filedata.replace(key, f"{key} {value};")

    with open(filepath, 'w') as f:
        f.write(filedata)

def apply_attack_config(attack_id, model_path, start_time_str, end_time_str):
    """
    Reads attack details and modifies the appropriate simulation files.
    """
    attack = get_attack_details(attack_id)
    if not attack:
        print(f"No attack found for ID: {attack_id}")
        return

    print("\n\n------------------------------------------")
    print(f"Selected Attack ID: {attack['attack_id']}")
    print(f"- Category Name:  {attack['category_name']}")
    print(f"- Attack Type: {attack['name']}")
    print(f"- Start Time:  {start_time_str}")
    print(f"- End Time: {end_time_str}")

    filepath = attack["attack_component"][0]["file"]
    affected_values = attack["attack_type"][0]["affected_value"][0]

    print("- Affected Values:")
    for key, value in affected_values.items():
        print(f"\t- {key} = {value}")

    if filepath == "ns-3.cc":
        start_seconds = time_to_seconds(start_time_str)
        end_seconds = time_to_seconds(end_time_str)
        config_ns3(model_path, affected_values, start_seconds, end_seconds)
    elif filepath == "GridLab-D.glm":
        config_glm(model_path, affected_values)
    else:
        print(f"Warning: Configuration for file type '{filepath}' is not implemented.")

# --- Main Execution ---

def main():
    if len(sys.argv) != 5:
        print("Usage: python attack_broker.py <path_to_model> <attack_id> <start_time> <end_time>")
        sys.exit(1)

    model_path, attack_id, start_time, end_time = sys.argv[1:5]

    # Clean up previous run files and create new ones by copying originals
    run_ns3_cc = os.path.join(model_path, "run_ns-3.cc")
    if os.path.exists(run_ns3_cc):
        os.remove(run_ns3_cc)

    run_gridlabd_glm = os.path.join(model_path, "run_GridLab-D.glm")
    if os.path.exists(run_gridlabd_glm):
        os.remove(run_gridlabd_glm)

    time.sleep(1)
    shutil.copyfile(os.path.join(model_path, "ns-3.cc"), run_ns3_cc)
    shutil.copyfile(os.path.join(model_path, "GridLab-D.glm"), run_gridlabd_glm)

    # If an attack is selected, apply the configuration
    if attack_id != "0":
        apply_attack_config(attack_id, model_path, start_time, end_time)

    # Compile simulation
    print("Compiling ns-3 model...")
    compile_script_path = '../../scripts/compile-ns3.sh'
    compile_proc = subprocess.run([compile_script_path, 'run_ns-3.cc'],
                                  capture_output=True, text=True, cwd=model_path)
    if compile_proc.returncode != 0:
        print("Compilation failed!")
        print(compile_proc.stdout)
        print(compile_proc.stderr)
        return

    print("Compilation successful.")
    print("Starting simulation... This may take a while.")

    # Run the simulation
    run_script_path = '../../scripts/run.sh'
    sim_proc = subprocess.run([run_script_path],
                              capture_output=True, text=True, cwd=model_path)

    print(sim_proc.stdout)
    if sim_proc.returncode != 0:
        print("Simulation script finished with errors.")
        print(sim_proc.stderr)

    print("Finished!")


if __name__ == '__main__':
    main()
