import json
import shutil
import os
import subprocess
import time

def get_attack_details(attack_id):
    with open('attack_library.json', 'r') as f:
        distros_dict = json.load(f)
    for x in range(len(distros_dict['object'])):
        if distros_dict['object'][x]["attack_id"] == str(attack_id):
            return distros_dict['object'][x]
    return None

def apply_attack_config(attack_id, model_path):
    attack = get_attack_details(attack_id)
    if not attack:
        print(f"No attack found for ID: {attack_id}")
        return

    print("\n \n------------------------------------------")
    print("You selected Attack ID: " + str(attack["attack_id"]))
    print('- Category Name:  ' + str(attack["category_name"]))
    print('- Attack Type: ' + str(attack["name"]))
    print('- Description:  ' + str(attack["attack_type"][0]["description"]))
    print('- Attack Component:  ' + str(attack["attack_component"][0]["component_name"]))
    print('- Start Time:  ' + str(attack["attack_schedule"][0]["start_time"]))
    print('- End Time: ' + str(attack["attack_schedule"][0]["end_time"]))

    filepath = str(attack["attack_component"][0]["file"])
    file_out = str("run_" + filepath)
    affected_value = attack["attack_type"][0]["affected_value"][0]
    print('- Affected Value: ')
    for key, value in affected_value.items():
        print('\t- ' + str(key) + " = " + str(value))
        _config(filepath, file_out, key, value, model_path)


def _config(filepath, file_out, key, value, model_path):
    full_file_out_path = os.path.join(model_path, file_out)
    with open(full_file_out_path, 'r') as f:
        filedata = f.read()

    if filepath == "ns-3.cc":
        newdata = filedata.replace("//Flag", "//Flag"+ "\n \t" + key + " = " + str(value) + ";//")
    else:
        newdata = filedata.replace(key,key + " " + str(value) + ";//")

    with open(full_file_out_path, 'w') as f:
        f.write(newdata)


def run_simulation(model_path, attack_id, start_time, end_time):
    if attack_id != "0":
        print(f"Attack scheduled from {start_time} to {end_time}.")
        print("Note: Attack scheduling is a UI feature and is not yet implemented in the simulation core.")

    # Clean up previous run files and create new ones
    run_ns3_cc = os.path.join(model_path, "run_ns-3.cc")
    run_gridlabd_glm = os.path.join(model_path, "run_GridLab-D.glm")
    if os.path.exists(run_ns3_cc):
        os.remove(run_ns3_cc)
    if os.path.exists(run_gridlabd_glm):
        os.remove(run_gridlabd_glm)

    time.sleep(1)

    shutil.copyfile(os.path.join(model_path, "ns-3.cc"), run_ns3_cc)
    shutil.copyfile(os.path.join(model_path, "GridLab-D.glm"), run_gridlabd_glm)

    # Apply attack configuration
    apply_attack_config(attack_id, model_path)

    # Compile simulation
    print("Compiling ns-3 model...")
    # The CWD is the model path, so the script path is relative to that.
    compile_script_path = '../../scripts/compile-ns3.sh'
    compile_proc = subprocess.run([compile_script_path, 'run_ns-3.cc'],
                                  capture_output=True, text=True,
                                  cwd=model_path)
    if compile_proc.returncode != 0:
        print("Compilation failed!")
        print(compile_proc.stdout)
        print(compile_proc.stderr)
        return {"status": "error", "message": "Compilation failed"}

    print("Compilation successful.")
    print("Starting simulation... This may take a while.")

    # Run the simulation. This will block until run.sh completes.
    run_script_path = '../../scripts/run.sh'
    sim_proc = subprocess.run([run_script_path],
                              capture_output=True, text=True,
                              cwd=model_path)

    # The simulation logs are now in ns3.log, gridlabd.log, and fncs.log
    # in the model directory. We can print the output of run.sh itself.
    print(sim_proc.stdout)
    if sim_proc.returncode != 0:
        print("Simulation script finished with errors.")
        print(sim_proc.stderr)
        return {"status": "error", "message": "Simulation failed"}

    print("Finished!")
    return {"status": "success", "message": "Simulation finished successfully"}
