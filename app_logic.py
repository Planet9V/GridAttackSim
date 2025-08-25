import os
import shutil
import subprocess
import datetime
import glob
import pandas as pd
from tkinter import messagebox, END
from graphviz import Source
from openai import OpenAI
from scripts import shared_utils

# --- Constants ---
# NOTE: In a production application, this should be an environment variable.
PERPLEXITY_API_KEY = "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"
database_path = "Database/"

# --- Perplexity AI Client ---
# Note: This will raise an error if the API key is invalid.
try:
    perplexity_client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
except Exception as e:
    perplexity_client = None
    print(f"Could not initialize Perplexity AI client: {e}")

def perform_perplexity_search(query):
    """
    Performs a search using the Perplexity AI API and returns the result.
    """
    if not perplexity_client:
        return "Perplexity AI client is not available. Please check the API key."

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an artificial intelligence assistant and you need to "
                    "find information about power grid components, substations, and transmission lines."
                ),
            },
            {
                "role": "user",
                "content": query,
            },
        ]
        response = perplexity_client.chat.completions.create(
            model="sonar-deep-research",
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred while searching with Perplexity AI: {e}"

def show_model(smartgrid_model_name):
    """Generates and displays a .dot model of the selected smart grid.

    This function calls the legacy `glmMap.py` script to convert a
    GridLab-D model file (.glm) into a graphviz .dot file, and then
    uses the graphviz library to render and display it.

    Args:
        smartgrid_model_name (str): The name of the smart grid model,
            as selected in the GUI (e.g., "13 Nodes 73 Houses").
    """
    model_dir_name = smartgrid_model_name.replace(" ", "_")
    model_path = os.path.join(database_path, model_dir_name)
    path_1 = os.path.join(model_path, 'GridLab-D.glm')
    path_2 = os.path.join(model_path, 'GridLab-D.dot')

    # Ensure the script is called with the correct python executable if needed
    subprocess.run(['python3', 'glmMap.py', path_1, path_2])

    if os.path.exists(path_2):
        s = Source.from_file(path_2)
        s.view()
    else:
        messagebox.showerror("Error", f"Could not find the model file to display: {path_2}")


def run_simulation(smartgrid_model_name, attack_type, start_time, end_time):
    """Initiates a simulation run via the attack_broker.py script.

    This function gathers the simulation parameters from the GUI, calls
    the `attack_broker.py` script to run the co-simulation, and displays
    the results (success or failure) to the user in a message box.
    If the simulation is successful, it renames the output files to
    prevent them from being overwritten on subsequent runs.

    Args:
        smartgrid_model_name (str): The name of the grid model.
        attack_type (str): The string describing the selected attack.
        start_time (str): The simulation start time for the attack.
        end_time (str): The simulation end time for the attack.
    """
    messagebox.showinfo("Message", "The simulation is running")

    model_dir_name = smartgrid_model_name.replace(" ", "_")
    model_path = os.path.join(database_path, model_dir_name)

    if not attack_type or attack_type == "None":
        attack_id = "0" # Assuming "0" means no attack
    else:
        attack_id = attack_type.split(' ')[0]

    # Run the simulation using python3 to be explicit
    proc = subprocess.run(
        ['python3', 'attack_broker.py', model_path, attack_id, start_time, end_time],
        capture_output=True, text=True
    )

    if proc.returncode == 0:
        messagebox.showinfo("Success", "The simulation has finished successfully.")
    else:
        # Try to read log files for more details
        error_message = f"Simulation failed with return code {proc.returncode}.\n\n"
        error_message += "STDOUT:\n" + proc.stdout + "\n\n"
        error_message += "STDERR:\n" + proc.stderr + "\n\n"

        log_files = ['ns3.log', 'gridlabd.log', 'fncs.log']
        for log_file in log_files:
            try:
                log_path = os.path.join(model_path, log_file)
                if os.path.exists(log_path):
                    with open(log_path, 'r') as f:
                        # Get the last 10 lines of the log
                        log_content = "".join(f.readlines()[-10:])
                    error_message += f"--- Tail of {log_file} ---\n{log_content}\n\n"
            except Exception as e:
                error_message += f"Could not read log file {log_file}: {e}\n"

        messagebox.showerror("Simulation Failed", error_message)

    # Rename the output files if the simulation was successful
    if proc.returncode == 0:
        run_name = f"{smartgrid_model_name}_{attack_type}"
        shared_utils.rename_output_files(model_path, run_name)


def load_results(lb_files_widget, smartgrid_model_name, application_type):
    """Loads simulation result files into the GUI listbox.

    This function scans the specified model's directory for CSV files,
    filters them based on the selected application type (DR, DP, or Both),
    and populates the listbox widget with the relevant filenames.

    Args:
        lb_files_widget (tkinter.Listbox): The listbox widget to populate.
        smartgrid_model_name (str): The name of the grid model.
        application_type (str): The application type ("Demand/Response (DR)",
            "Dynamic Pricing (DP)", or "Both DR and DP").
    """
    lb_files_widget.delete(0, END)
    model_dir_name = smartgrid_model_name.replace(" ", "_")
    path = os.path.join(database_path, model_dir_name)
    extension = 'csv'

    # Use full path for glob and get basenames for logic
    file_list = glob.glob(os.path.join(path, f'*.{extension}'))
    filenames = [os.path.basename(f) for f in file_list]

    j = 0
    for f in filenames:
        is_dr = application_type == "Demand/Response (DR)" and f.startswith("totalload")
        is_dp = application_type == "Dynamic Pricing (DP)" and f.startswith("price")
        is_both = application_type == "Both DR and DP" and (f.startswith("totalload") or f.startswith("price"))

        if is_dr or is_dp or is_both:
            lb_files_widget.insert(j, f)
            j += 1


def show_charts(lb_files_widget, smartgrid_model_name):
    """Calls the plot_result.py script to display charts for selected files.

    This function retrieves the selected filenames from the listbox,
    separates them into price and total load files, and then calls the
    `plot_result.py` script with the appropriate arguments to generate
    and display the plots.

    Args:
        lb_files_widget (tkinter.Listbox): The listbox widget containing
            the result filenames.
        smartgrid_model_name (str): The name of the grid model.
    """
    plot_price = ["null"]
    plot_totalload = ["null"]
    selection = lb_files_widget.curselection()

    for i in selection:
        filename = lb_files_widget.get(i)
        if filename.startswith('totalload'):
            plot_totalload.append(filename)
        elif filename.startswith('price'):
            plot_price.append(filename)

    model_dir_name = smartgrid_model_name.replace(" ", "_")
    model_path = os.path.join(database_path, model_dir_name)

    # Join the filenames with a colon for the plot script argument
    price_arg = ":".join(plot_price)
    totalload_arg = ":".join(plot_totalload)

    subprocess.run(['python3', 'plot_result.py', model_path, price_arg, totalload_arg])


def compare_results(filenames, model_name):
    """Generates a statistical comparison of selected result files.

    This function reads two or more result CSV files, uses the pandas
    library to calculate descriptive statistics for each, and also
    calculates the statistical difference between each file and the first
    file (as a baseline).

    Args:
        filenames (list): A list of result CSV filenames to compare.
        model_name (str): The name of the grid model.

    Returns:
        str: A formatted string containing the full statistical comparison.
    """
    model_dir_name = model_name.replace(" ", "_")
    model_path = os.path.join(database_path, model_dir_name)

    results_text = "--- Results Comparison ---\n\n"

    dataframes = {}
    for filename in filenames:
        try:
            full_path = os.path.join(model_path, filename)
            # Adjust skiprows based on file type
            if filename.startswith('price'):
                df = pd.read_csv(full_path, delimiter=',', skiprows=9, names=["timestamp","capacity_reference_bid_price","current_market.clearing_price","current_market.clearing_quantity"])
            elif filename.startswith('totalload'):
                df = pd.read_csv(full_path, delimiter=',', skiprows=9, names=["timestamp","power_out_real"])
            else:
                continue # Skip unknown files
            dataframes[filename] = df
        except Exception as e:
            results_text += f"Could not read or process {filename}: {e}\n\n"
            continue

    if not dataframes:
        return "No valid result files to compare."

    # Generate stats for each file
    for filename, df in dataframes.items():
        results_text += f"--- Statistics for {filename} ---\n"
        if "current_market.clearing_price" in df.columns:
            results_text += "Clearing Price Stats:\n"
            results_text += df["current_market.clearing_price"].describe().to_string() + "\n\n"
        if "power_out_real" in df.columns:
            results_text += "Total Load (kW) Stats:\n"
            results_text += (df["power_out_real"] / 1000).describe().to_string() + "\n\n"

    # Compare files against the first file as a baseline
    if len(dataframes) > 1:
        baseline_name = list(dataframes.keys())[0]
        baseline_df = dataframes[baseline_name]
        results_text += f"--- Comparison against baseline: {baseline_name} ---\n"

        for i in range(1, len(dataframes)):
            compare_name = list(dataframes.keys())[i]
            compare_df = dataframes[compare_name]
            results_text += f"Comparing with: {compare_name}\n"

            # Compare price if both have it
            if "current_market.clearing_price" in baseline_df.columns and "current_market.clearing_price" in compare_df.columns:
                price_diff = (compare_df['current_market.clearing_price'] - baseline_df['current_market.clearing_price']).describe()
                results_text += "Difference in Clearing Price:\n"
                results_text += price_diff.to_string() + "\n\n"

            # Compare load if both have it
            if "power_out_real" in baseline_df.columns and "power_out_real" in compare_df.columns:
                load_diff = ((compare_df['power_out_real'] - baseline_df['power_out_real']) / 1000).describe()
                results_text += "Difference in Total Load (kW):\n"
                results_text += load_diff.to_string() + "\n\n"

    return results_text
