import tkinter as tk
from tkinter.ttk import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys
import pandas as pd
import matplotlib.ticker as plticker

model_path = sys.argv[1]
price_files_arg = sys.argv[2]
totalload_files_arg = sys.argv[3]

root_name = os.path.basename(model_path).replace("_", " ") + " Simulation Result"

root = tk.Tk()
root.title(root_name)

lbl = Label(root, text=root_name, font=("Times", 18), foreground="#000280")
lbl.pack()


def plot_price(file_list_str):
    file_list = file_list_str.split(':')
    if len(file_list) <= 1:
        return

    # Create one figure with two subplots, side-by-side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    legend_list = []
    y_1 = [] # To store x-axis labels

    # Loop over all files passed, skipping the first "null" item
    for filename in file_list[1:]:
        full_path = os.path.join(model_path, filename)
        data_loading = pd.read_csv(full_path, delimiter=',', skiprows=9,
                                   names=["timestamp", "capacity_reference_bid_price",
                                          "current_market.clearing_price", "current_market.clearing_quantity"])

        # Generate x-axis labels only from the first file
        if not y_1:
            my_xticks = data_loading["timestamp"]
            # This is inefficient, but we'll keep the logic for now
            with open(full_path) as f:
                row_count = sum(1 for line in f) - 9
                for k in range(0, row_count):
                    y_1.append(my_xticks.values[k][11:19])

        ax1.plot(y_1, 'current_market.clearing_price', data=data_loading, linewidth=4)
        ax2.plot(y_1, 'current_market.clearing_quantity', data=data_loading, linewidth=4)
        legend_list.append(filename.replace('.csv', ''))

    ax1.set_title('Clearing Price')
    ax1.tick_params(axis='x', rotation=45)
    ax1.xaxis.set_major_locator(plticker.MultipleLocator(base=100))
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Price $')
    ax1.legend(legend_list)
    ax1.grid(True)

    ax2.set_title('Clearing Quantity')
    ax2.tick_params(axis='x', rotation=45)
    ax2.xaxis.set_major_locator(plticker.MultipleLocator(base=100))
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Quantity') # Corrected label
    ax2.legend(legend_list)
    ax2.grid(True)

    fig.tight_layout()
    canvas.draw()


def plot_total_load(file_list_str):
    file_list = file_list_str.split(':')
    if len(file_list) <= 1:
        return

    fig, ax = plt.subplots(figsize=(6, 5))
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    legend_list = []
    y_1 = [] # To store x-axis labels

    # Loop over all files passed, skipping the first "null" item
    for filename in file_list[1:]:
        full_path = os.path.join(model_path, filename)
        data_loading = pd.read_csv(full_path, delimiter=',', skiprows=9,
                                   names=["timestamp", "power_out_real"])

        if not y_1:
            my_xticks = data_loading["timestamp"]
            with open(full_path) as f:
                row_count = sum(1 for line in f) - 9
                for k in range(0, row_count):
                    y_1.append(my_xticks.values[k][11:19])

        ax.plot(y_1, 'power_out_real', data=data_loading, linewidth=4)
        legend_list.append(filename.replace('.csv', ''))

    ax.set_title('Total Load')
    ax.tick_params(axis='x', rotation=45)
    ax.xaxis.set_major_locator(plticker.MultipleLocator(base=100))
    ax.set_xlabel('Time')
    ax.set_ylabel('kWh')
    ax.legend(legend_list)
    ax.grid(True)

    fig.tight_layout()
    canvas.draw()


# Main execution
if len(price_files_arg.split(':')) > 1:
    plot_price(price_files_arg)
if len(totalload_files_arg.split(':')) > 1:
    plot_total_load(totalload_files_arg)

root.mainloop()