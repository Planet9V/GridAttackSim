"""
GridAttackSim Batch Simulation Runner

This script allows for running a series of simulations automatically based on
a JSON configuration file. This is useful for running large-scale experiments
for research purposes.
"""

import json
import os
import sys
import subprocess
from shared_utils import rename_output_files

# The root of the database directory, relative to the project root.
DATABASE_PATH = "Database"

def run_batch(config_path):
    """
    Parses a config file and runs the defined simulations.
    """
    print(f"Starting batch run with config: {config_path}")

    try:
        with open(config_path, 'r') as f:
            batch_config = json.load(f)
    except Exception as e:
        print(f"Error reading or parsing config file: {e}")
        sys.exit(1)

    for i, run_params in enumerate(batch_config):
        run_name = run_params.get("run_name", f"run_{i+1}")
        model = run_params.get("model")
        attack_id = run_params.get("attack_id")
        start_time = run_params.get("start_time", "00:00:00")
        end_time = run_params.get("end_time", "00:00:00")

        if not model or not attack_id:
            print(f"Skipping run '{run_name}' due to missing 'model' or 'attack_id'.")
            continue

        print(f"\n--- Starting Run {i+1}/{len(batch_config)}: {run_name} ---")

        model_path = os.path.join(DATABASE_PATH, model)
        if not os.path.isdir(model_path):
            print(f"Error: Model directory not found at '{model_path}'. Skipping run.")
            continue

        try:
            # The attack_broker.py script is in the parent directory of this script's location
            broker_script_path = os.path.join(os.path.dirname(__file__), '..', 'attack_broker.py')

            proc = subprocess.run(
                ['python3', broker_script_path, model_path, attack_id, start_time, end_time],
                capture_output=True, text=True, check=True # check=True will raise an exception on non-zero exit codes
            )

            print(f"Run '{run_name}' completed successfully.")
            print("Broker script output:\n", proc.stdout)

            # Rename the output files to save them
            rename_output_files(model_path, run_name)

        except subprocess.CalledProcessError as e:
            print(f"Run '{run_name}' FAILED with return code {e.returncode}.")
            print("STDOUT:\n", e.stdout)
            print("STDERR:\n", e.stderr)
        except Exception as e:
            print(f"An unexpected error occurred during run '{run_name}': {e}")

        print(f"--- Finished Run: {run_name} ---")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/batch_runner.py <path_to_config_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    if not os.path.exists(config_file):
        print(f"Error: Config file not found at {config_file}")
        sys.exit(1)

    run_batch(config_file)
    print("\nBatch run fully completed.")
