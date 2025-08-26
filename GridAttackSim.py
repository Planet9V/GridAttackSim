"""
GridAttackSim: Smart Grid Attack Simulation Framework

This script launches the main graphical user interface (GUI) for the
GridAttackSim application. The GUI allows users to configure, run, and
analyze smart grid co-simulations.

The application logic (e.g., running simulations, processing data) is
separated into the `app_logic.py` module. This script is responsible
for building and managing the tkinter UI components.
"""
from tkinter import *
from tkinter import ttk
import app_logic # Import the new application logic module

__version__ = "2.0.0"

def open_research_window():
    """Creates and displays the 'AI Research Assistant' window.

    This window provides a simple interface to query the Perplexity AI API
    for information related to smart grids, cybersecurity, and other relevant
    topics.
    """
    research_window = Toplevel(window)
    research_window.title("AI Research Assistant")
    research_window.geometry("700x500")
    research_window.config(bg="#D6E2F3")

    # Search frame
    search_frame = Frame(research_window, padding=10)
    search_frame.pack(fill=X, padx=5, pady=5)

    lbl_search = Label(search_frame, text="Search Query:")
    lbl_search.pack(side=LEFT, padx=(0, 5))

    entry_query = Entry(search_frame, width=60)
    entry_query.pack(side=LEFT, expand=True, fill=X)

    # Results frame
    results_frame_research = Frame(research_window, padding=10)
    results_frame_research.pack(expand=True, fill=BOTH, padx=5, pady=5)

    txt_results = Text(results_frame_research, wrap=WORD, height=20, width=80)
    scrollbar = Scrollbar(results_frame_research, command=txt_results.yview)
    txt_results.config(yscrollcommand=scrollbar.set)

    txt_results.pack(side=LEFT, expand=True, fill=BOTH)
    scrollbar.pack(side=RIGHT, fill=Y)

    def perform_search():
        """Nested function to handle the search button click event."""
        query = entry_query.get()
        if not query:
            return
        txt_results.delete(1.0, END)
        txt_results.insert(END, "Searching...")
        window.update_idletasks() # Update GUI to show "Searching..." message

        result = app_logic.perform_perplexity_search(query)

        txt_results.delete(1.0, END)
        txt_results.insert(END, result)

    btn_search = Button(search_frame, text="Search", command=perform_search)
    btn_search.pack(side=LEFT, padx=(5, 0))


# --- Main Window Setup ---
window = Tk()
window.title("Smart Grid Simulation")
window.option_add("*font", "Times 14")
window.geometry()
window.config(bg="#D6E2F3")

# --- Menu Bar ---
menu = Menu(window)
menu_file = Menu(menu)
menu_file.add_command(label='New', font=("Times", 11))
menu_file.add_separator()
menu_file.add_command(label='Open', font=("Times", 11))
menu_file.add_separator()
menu_file.add_command(label='Exit', command=window.quit, font=("Times", 11))
menu.add_cascade(label='File', menu=menu_file, font=("Times", 11))
window.config(menu=menu)

# --- Main Title ---
lbl = Label(window, text="Smart Grid Attack Simulation System", font=("Times", 18), background="#D6E2F3", foreground="#000280")
lbl.grid(column=0, row=0, columnspan=3, pady=10)

# --- Simulation Configuration Frame ---
config_frame = LabelFrame(window, text="Configuration", background="#D6E2F3", padding=10)
config_frame.grid(column=0, row=1, columnspan=3, padx=10, pady=5, sticky="ew")

# Smart Grid Model
lbl_smartgrid_model = Label(config_frame, text="Smart Grid Model:", background="#D6E2F3", foreground="#000280")
lbl_smartgrid_model.grid(sticky="W", column=0, row=0, padx=5, pady=5)
combo_smartgrid_model = Combobox(config_frame, width=35)
combo_smartgrid_model['values']= ("1 Node 255 Houses", "4 Nodes 1 House", "4 Nodes 492 Houses", "13 Nodes 15 Houses", "13 Nodes 73 Houses")
combo_smartgrid_model.current(4)
combo_smartgrid_model.grid(column=1, row=0, padx=5)
btn_show_model = Button(config_frame, text="Show Model", command=lambda: app_logic.show_model(combo_smartgrid_model.get()))
btn_show_model.grid(column=2, row=0, padx=5)

# Application
lbl_application = Label(config_frame, text="Application:", background="#D6E2F3", foreground="#000280")
lbl_application.grid(sticky="W", column=0, row=1, padx=5, pady=5)
combo_application = Combobox(config_frame, width=35)
combo_application['values']= ("Demand/Response (DR)", "Dynamic Pricing (DP)", "Both DR and DP")
combo_application.current(0)
combo_application.grid(column=1, row=1, padx=5)

# Attack Category
def on_attack_category_change():
    """Updates the 'Attack Type' dropdown based on the selected category.

    This function is registered as a callback for when the 'Attack Category'
    combobox changes. It dynamically populates the 'Attack Type' combobox
    with the appropriate attacks from the library.
    """
    category = combo_attack_category.get()
    if category == "Nefarious Activity":
        combo_attack_type['values']= ("1 - Channel Jamming - Cluster", "2 - Channel Jamming - Peer-to-Peer", "3 - DNS attacks - Cluster", "4 - DNS attacks - Peer-to-Peer", "5 - Injection Attacks - Control Systems", "6 - Injection Attacks - End-point Systems", "7 - Malicious Code - End-point Systems")
    elif category == "Eavesdropping, Interception and Hijacking":
        combo_attack_type['values']= ("8 - Replay of Messages - Cluster", "9 - Replay of Messages - Peer-to-Peer")
    else: # "None"
        combo_attack_type['values']= ["None"]
    combo_attack_type.current(0)

string_attack_category = StringVar()
string_attack_category.trace('w', on_attack_category_change)
lbl_attack_category = Label(config_frame, text="Attack Category:", background="#D6E2F3", foreground="#000280")
lbl_attack_category.grid(sticky="W", column=0, row=2, padx=5, pady=5)
combo_attack_category = Combobox(config_frame, textvariable=string_attack_category, width=35)
combo_attack_category['values']= ("None", "Nefarious Activity", "Eavesdropping, Interception and Hijacking")
combo_attack_category.grid(column=1, row=2, padx=5)

# Attack Type
lbl_attack_type = Label(config_frame, text="Attack Type:", background="#D6E2F3", foreground="#000280")
lbl_attack_type.grid(sticky="W", column=0, row=3, padx=5, pady=5)
combo_attack_type = Combobox(config_frame, width=35)
combo_attack_type.grid(column=1, row=3, padx=5)
on_attack_category_change() # Initialize the attack types

# Attack Schedule
lbl_start_time = Label(config_frame, text="Attack Start Time:", background="#D6E2F3", foreground="#000280")
lbl_start_time.grid(sticky="W", column=0, row=4, padx=5, pady=5)
entry_start_time = Entry(config_frame, width=38)
entry_start_time.grid(column=1, row=4, padx=5)
entry_start_time.insert(0, "12:00:00") # Default value

lbl_end_time = Label(config_frame, text="Attack End Time:", background="#D6E2F3", foreground="#000280")
lbl_end_time.grid(sticky="W", column=0, row=5, padx=5, pady=5)
entry_end_time = Entry(config_frame, width=38)
entry_end_time.grid(column=1, row=5, padx=5)
entry_end_time.insert(0, "18:00:00") # Default value

# --- Simulation Control Frame ---
control_frame = LabelFrame(window, text="Controls", background="#D6E2F3", padding=10)
control_frame.grid(column=0, row=2, padx=10, pady=10, sticky="ew")

btn_run = Button(control_frame, text="Run Simulation", command=lambda: app_logic.run_simulation(combo_smartgrid_model.get(), combo_attack_type.get(), entry_start_time.get(), entry_end_time.get()))
btn_run.pack(side=LEFT, padx=10)

btn_load_results= Button(control_frame, text="Load Results", command=lambda: app_logic.load_results(Lb_files, combo_smartgrid_model.get(), combo_application.get()))
btn_load_results.pack(side=LEFT, padx=10)

btn_research = Button(control_frame, text="AI Research", command=open_research_window)
btn_research.pack(side=LEFT, padx=10)

# --- Results Frame ---
results_frame = LabelFrame(window, text="Results", background="#D6E2F3", padding=10)
results_frame.grid(column=0, row=3, columnspan=3, padx=10, pady=5, sticky="ew")

lbl_files = Label(results_frame, text="Output Files:", background="#D6E2F3", foreground="#000280")
lbl_files.grid(column=0, row=0, sticky="W", pady=5)

Lb_files = Listbox(results_frame, width=60, selectmode=MULTIPLE, height=8)
Lb_files.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5)

def open_comparison_window():
    """Creates and displays the 'Results Comparison' window.

    This window shows a side-by-side statistical comparison of two or more
    selected result files, generated by the `app_logic.compare_results`
    function.
    """
    selected_indices = Lb_files.curselection()
    if len(selected_indices) < 2:
        return

    selected_filenames = [Lb_files.get(i) for i in selected_indices]
    model_name = combo_smartgrid_model.get()

    comparison_text = app_logic.compare_results(selected_filenames, model_name)

    # Create new window
    comp_window = Toplevel(window)
    comp_window.title("Results Comparison")
    comp_window.geometry("700x500")
    comp_window.config(bg="#D6E2F3")

    # Add text widget with scrollbar
    text_frame = Frame(comp_window, padding=10)
    text_frame.pack(expand=True, fill=BOTH)

    results_widget = Text(text_frame, wrap=WORD, font=("Courier", 10))
    scrollbar = Scrollbar(text_frame, command=results_widget.yview)
    results_widget.config(yscrollcommand=scrollbar.set)

    results_widget.pack(side=LEFT, expand=True, fill=BOTH)
    scrollbar.pack(side=RIGHT, fill=Y)

    results_widget.insert(END, comparison_text)
    results_widget.config(state=DISABLED) # Make it read-only

btn_show = Button(results_frame, text="Show Charts", command=lambda: app_logic.show_charts(Lb_files, combo_smartgrid_model.get()))
btn_show.grid(column=0, row=2, pady=10)

btn_compare = Button(results_frame, text="Compare Selected Results", state=DISABLED, command=open_comparison_window)
btn_compare.grid(column=1, row=2, pady=10)

def on_listbox_select():
    """Enables or disables the 'Compare' button based on selection.

    This callback function is triggered when the selection in the results
    listbox changes. It enables the 'Compare Selected Results' button only
    if two or more items are selected.
    """
    if len(Lb_files.curselection()) >= 2:
        btn_compare.config(state=NORMAL)
    else:
        btn_compare.config(state=DISABLED)

Lb_files.bind('<<ListboxSelect>>', on_listbox_select)

# Start the GUI event loop
window.mainloop()
