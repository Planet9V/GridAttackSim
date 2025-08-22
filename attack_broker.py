import json
import shutil
import os
import sys
import fileinput
import subprocess
import time

with open('attack_library.json', 'r') as f:
    distros_dict = json.load(f)

def readfile(index, model_path):
    for x in range(len(distros_dict['object'])):
        if distros_dict['object'][x]["attack_id"]==str(index):
            print("\n \n------------------------------------------")
            print("You selected Attack ID: " + str(distros_dict['object'][x]["attack_id"]))
            print('- Category Name:  ' + str(distros_dict['object'][x]["category_name"]))
            print('- Attack Type: ' + str(distros_dict['object'][x]["name"]))
            print('- Description:  ' + str(distros_dict['object'][x]["attack_type"][0]["description"]))
            print('- Attack Component:  ' + str(distros_dict['object'][x]["attack_component"][0]["component_name"]))
            print('- Start Time:  ' + str(distros_dict['object'][x]["attack_schedule"][0]["start_time"]))
            print('- End Time: ' + str(distros_dict['object'][x]["attack_schedule"][0]["end_time"]))
            
            filepath = str(distros_dict['object'][x]["attack_component"][0]["file"])
            file_out = str("run_" + filepath)
            affected_value = distros_dict['object'][x]["attack_type"][0]["affected_value"][0]
            print('- Affected Value: ')
            for key, value in affected_value.items():
                print('\t- ' + str(key) + " = " + str(value))
                config(filepath, file_out, key, value, model_path)


def config(filepath, file_out, key, value, model_path):
    full_file_out_path = os.path.join(model_path, file_out)
    with open(full_file_out_path, 'r') as f:
        filedata = f.read()

    if filepath == "ns-3.cc":
        newdata = filedata.replace("//Flag", "//Flag"+ "\n \t" + key + " = " + str(value) + ";//")
    else:
        newdata = filedata.replace(key,key + " " + str(value) + ";//")

    with open(full_file_out_path, 'w') as f:
        f.write(newdata)

def main():
    if len(sys.argv) != 3:
        print("Usage: python attack_broker.py <path_to_model> <attack_id>")
        sys.exit(1)

    model_path = sys.argv[1]
    attack_id = sys.argv[2]

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
    readfile(attack_id, model_path)

    # Compile simulation
    print("Compiling ns-3 model...")
    compile_proc = subprocess.run(['./compile-ns3.sh', 'run_ns-3.cc'],
                                  capture_output=True, text=True,
                                  cwd=model_path)
    if compile_proc.returncode != 0:
        print("Compilation failed!")
        print(compile_proc.stdout)
        print(compile_proc.stderr)
        return # Exit if compilation fails

    print("Compilation successful.")
    print("Starting simulation... This may take a while.")

    # Run the simulation. This will block until run.sh completes.
    sim_proc = subprocess.run(['./run.sh'],
                              capture_output=True, text=True,
                              cwd=model_path)

    # The simulation logs are now in ns3.log, gridlabd.log, and fncs.log
    # in the model directory. We can print the output of run.sh itself.
    print(sim_proc.stdout)
    if sim_proc.returncode != 0:
        print("Simulation script finished with errors.")
        print(sim_proc.stderr)

    print("Finished!")


if __name__ == '__main__':
    main()
