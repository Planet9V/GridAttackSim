import os
import shutil
import datetime

database_path = "Database/"

def rename_output_files(model_path, run_name):
    """
    Renames the standard output files from a simulation run to prevent them
    from being overwritten. The new filenames are based on the provided
    run_name and a timestamp.
    """
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Sanitize the run_name for use in a filename
    sanitized_run_name = run_name.replace(" ", "_").replace("-", "")

    # Rename price file
    old_price_file = os.path.join(model_path, 'baseprice_clearedprice_clearedquantity.csv')
    if os.path.exists(old_price_file):
        new_price_file = os.path.join(model_path, f'price_{sanitized_run_name}_{current_time}.csv')
        shutil.move(old_price_file, new_price_file)
        print(f"Renamed price file to: {os.path.basename(new_price_file)}")

    # Rename total load file
    old_load_file = os.path.join(model_path, 'totalload.csv')
    if os.path.exists(old_load_file):
        new_load_file = os.path.join(model_path, f'totalload_{sanitized_run_name}_{current_time}.csv')
        shutil.move(old_load_file, new_load_file)
        print(f"Renamed total load file to: {os.path.basename(new_load_file)}")
