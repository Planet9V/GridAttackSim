import json
import shutil
import os
import sys
import subprocess
import time
from datetime import datetime, timedelta

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

# --- NS-3 Configuration ---

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
        if normal_value is None: continue

        if 'cluster' in key:
            attribute_name = "DataRate" if "data_rate" in key else "Delay"
            attack_body += f'for(auto const& channel : g_csmaChannels) {{ channel->SetAttribute("{attribute_name}", {"DataRateValue" if "data_rate" in key else "TimeValue"}({value if "data_rate" in key else f"MilliSeconds({value})"})); }}\n'
            normal_body += f'for(auto const& channel : g_csmaChannels) {{ channel->SetAttribute("{attribute_name}", {"DataRateValue" if "data_rate" in key else "TimeValue"}({normal_value if "data_rate" in key else f"MilliSeconds({normal_value})"})); }}\n'
        elif 'peer_to_peer' in key:
            attribute_name = "DataRate" if "data_rate" in key else "Delay"
            attack_body += f'for(auto const& dev : g_p2pDevices) {{ dev->SetAttribute("{attribute_name}", {"DataRateValue" if "data_rate" in key else "TimeValue"}({value if "data_rate" in key else f"MilliSeconds({value})"})); }}\n'
            normal_body += f'for(auto const& dev : g_p2pDevices) {{ dev->SetAttribute("{attribute_name}", {"DataRateValue" if "data_rate" in key else "TimeValue"}({normal_value if "data_rate" in key else f"MilliSeconds({normal_value})"})); }}\n'

    # 2. Inject C++ code into the file content
    header_injection = """
#include <vector>
#include "ns3/csma-channel.h"
#include "ns3/point-to-point-net-device.h"
std::vector<Ptr<CsmaChannel>> g_csmaChannels;
std::vector<Ptr<PointToPointNetDevice>> g_p2pDevices;
"""
    functions_injection = f"void SetAttackParameters() {{ NS_LOG_UNCOND(\"ATTACK STARTING\");\n{attack_body} }}\nvoid SetNormalParameters() {{ NS_LOG_UNCOND(\"ATTACK ENDING\");\n{normal_body} }}\n"
    schedule_injection = f"Simulator::Schedule(Seconds({start_seconds}.0), &SetAttackParameters);\nSimulator::Schedule(Seconds({end_seconds}.0), &SetNormalParameters);"
    csma_capture_injection = "csmaDevices[i] = chelper.Install(model->csma[i]);\ng_csmaChannels.push_back(DynamicCast<CsmaChannel>(csmaDevices[i].Get(0)->GetChannel()));"
    p2p_capture_injection = "NetDeviceContainer csma1dbell1=phelper3.Install(model->market.Get(0), model->csma[i].Get(0));\ng_p2pDevices.push_back(DynamicCast<PointToPointNetDevice>(csma1dbell1.Get(0)));\ng_p2pDevices.push_back(DynamicCast<PointToPointNetDevice>(csma1dbell1.Get(1)));"

    filedata = filedata.replace('using namespace std;', f'using namespace std;\n{header_injection}\n{functions_injection}')
    filedata = filedata.replace('csmaDevices[i] = chelper.Install(model->csma[i]);', csma_capture_injection)
    filedata = filedata.replace('NetDeviceContainer csma1dbell1=phelper3.Install(\n                    model->market.Get(0), model->csma[i].Get(0));', p2p_capture_injection)
    filedata = filedata.replace('Simulator::Run ();', f'{schedule_injection}\n    Simulator::Run ();')
    filedata = filedata.replace('//Flag', '')

    with open(filepath, 'w') as f: f.write(filedata)

# --- GridLab-D Configuration ---

def find_all_property_paths_and_values(glm_content, property_names):
    """
    Parses GLM content to find all full object paths and original values for given property names.
    """
    found_targets = {prop: [] for prop in property_names}
    object_stack = []
    lines = glm_content.splitlines()

    for line in lines:
        stripped = line.strip().split('//')[0].strip() # Ignore comments
        if not stripped: continue

        if stripped.startswith("object"):
            parts = stripped.split()
            class_name = parts[1]
            object_stack.append({'class': class_name, 'name': None, 'path_part': class_name})
        elif stripped.startswith("name ") and object_stack:
            name = stripped.split()[1].replace(';', '')
            object_stack[-1]['name'] = name
            object_stack[-1]['path_part'] = name
        elif '}' in stripped and object_stack:
            object_stack.pop()
        else:
            for prop in property_names:
                if stripped.startswith(prop):
                    try:
                        value = stripped.split()[1].replace(';', '')
                        path_parts = [item['path_part'] for item in object_stack]
                        path_parts.append(prop)
                        full_path = ".".join(path_parts)
                        found_targets[prop].append({'path': full_path, 'value': value})
                        break
                    except IndexError:
                        continue # Not a valid property line
    return found_targets

def config_glm(model_path, affected_values, start_time_str, end_time_str):
    """
    Modifies the run_GridLab-D.glm file to schedule attacks using a generalized player file.
    """
    glm_filepath = os.path.join(model_path, "run_GridLab-D.glm")
    player_filepath = os.path.join(model_path, "attack_schedule.player")

    with open(glm_filepath, 'r') as f: glm_content = f.read()

    # 1. Find all target properties and their original values
    all_targets = find_all_property_paths_and_values(glm_content, list(affected_values.keys()))

    flat_target_list = []
    for prop, targets in all_targets.items():
        for target in targets:
            flat_target_list.append({'path': target['path'], 'original': target['value'], 'attack': affected_values[prop]})

    if not flat_target_list:
        print("Warning: No target properties for the attack were found in the GLM file.")
        return

    # 2. Create the player file
    base_date_str = "2009-07-21" # Dummy date from GLM clock
    start_dt = datetime.strptime(f"{base_date_str} {start_time_str}", "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(f"{base_date_str} {end_time_str}", "%Y-%m-%d %H:%M:%S")

    with open(player_filepath, 'w') as f:
        f.write(f"# {','.join([t['path'] for t in flat_target_list])}\n")
        # Line just before attack
        f.write(f"{(start_dt - timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S %Z')},{','.join([str(t['original']) for t in flat_target_list])}\n")
        # Attack starts
        f.write(f"{start_dt.strftime('%Y-%m-%d %H:%M:%S %Z')},{','.join([str(t['attack']) for t in flat_target_list])}\n")
        # Attack ends
        f.write(f"{end_dt.strftime('%Y-%m-%d %H:%M:%S %Z')},{','.join([str(t['original']) for t in flat_target_list])}\n")

    # 3. Create and inject the player object into the GLM file
    properties_str = ",".join([f'"{t["path"]}"' for t in flat_target_list])
    player_object = f"""
object player {{
    name attack_player;
    file "attack_schedule.player";
    property {properties_str};
}};
"""
    # Inject the player object at the top of the file, after the clock.
    glm_content = glm_content.replace('};', f'}}; \n{player_object}', 1)
    with open(glm_filepath, 'w') as f: f.write(glm_content)


# --- Main Orchestration ---

def apply_attack_config(attack_id, model_path, start_time_str, end_time_str):
    """
    Reads attack details and modifies the appropriate simulation files.
    """
    attack = get_attack_details(attack_id)
    if not attack:
        print(f"No attack found for ID: {attack_id}")
        return

    print("\n\n------------------------------------------")
    print(f"Selected Attack ID: {attack['attack_id']}\n- Category Name:  {attack['category_name']}\n- Attack Type: {attack['name']}\n- Start Time:  {start_time_str}\n- End Time: {end_time_str}")

    filepath = attack["attack_component"][0]["file"]
    affected_values = attack["attack_type"][0]["affected_value"][0]

    print("- Affected Values:")
    for key, value in affected_values.items(): print(f"\t- {key} = {value}")

    if filepath == "ns-3.cc":
        config_ns3(model_path, affected_values, time_to_seconds(start_time_str), time_to_seconds(end_time_str))
    elif filepath == "GridLab-D.glm":
        config_glm(model_path, affected_values, start_time_str, end_time_str)
    else:
        print(f"Warning: Configuration for file type '{filepath}' is not implemented.")

def main():
    if len(sys.argv) != 5:
        print("Usage: python attack_broker.py <path_to_model> <attack_id> <start_time> <end_time>")
        sys.exit(1)

    model_path, attack_id, start_time, end_time = sys.argv[1:5]

    for file_to_copy in ["ns-3.cc", "GridLab-D.glm"]:
        run_file = os.path.join(model_path, f"run_{file_to_copy}")
        if os.path.exists(run_file): os.remove(run_file)
        time.sleep(0.1) # Small delay to ensure file is gone
        shutil.copyfile(os.path.join(model_path, file_to_copy), run_file)

    if attack_id != "0":
        apply_attack_config(attack_id, model_path, start_time, end_time)

    print("Compiling ns-3 model...")
    compile_proc = subprocess.run(['../../scripts/compile-ns3.sh', 'run_ns-3.cc'], capture_output=True, text=True, cwd=model_path)
    if compile_proc.returncode != 0:
        print(f"Compilation failed!\n{compile_proc.stdout}\n{compile_proc.stderr}")
        return

    print("Compilation successful.\nStarting simulation... This may take a while.")
    sim_proc = subprocess.run(['../../scripts/run.sh'], capture_output=True, text=True, cwd=model_path)

    print(sim_proc.stdout)
    if sim_proc.returncode != 0: print(f"Simulation script finished with errors.\n{sim_proc.stderr}")
    print("Finished!")

if __name__ == '__main__':
    main()
