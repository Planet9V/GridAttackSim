import os
import shutil
import subprocess
import datetime
import glob
from tkinter import messagebox, END
from graphviz import Source
from openai import OpenAI

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
            model="llama-3-sonar-large-32k-online",
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred while searching with Perplexity AI: {e}"

def show_model(smartgrid_model_name):
    """
    Generates and displays a .dot model of the selected smart grid.
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
    """
    Runs the attack simulation and renames the output files.
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

    # Rename the output files
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    attack_name_sanitized = attack_type.replace(" ", "_").replace("-", "")

    # Rename price file
    old_price_file = os.path.join(model_path, 'baseprice_clearedprice_clearedquantity.csv')
    new_price_file = os.path.join(model_path, f'price_{attack_name_sanitized}_{current_time}.csv')
    if os.path.exists(old_price_file):
        shutil.move(old_price_file, new_price_file)

    # Rename total load file
    old_load_file = os.path.join(model_path, 'totalload.csv')
    new_load_file = os.path.join(model_path, f'totalload_{attack_name_sanitized}_{current_time}.csv')
    if os.path.exists(old_load_file):
        shutil.move(old_load_file, new_load_file)


def load_results(lb_files_widget, smartgrid_model_name, application_type):
    """
    Loads the simulation result files into the listbox.
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
    """
    Calls the plot_result.py script to show charts for selected files.
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
