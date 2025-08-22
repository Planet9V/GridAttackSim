from tkinter import *
from tkinter.ttk import *
from tkinter import ttk
import tkinter.font as tkfont
import json
import shutil
import os
import sys
import fileinput
import subprocess
from tkinter import messagebox
from tkinter import Menu
import time
import glob
import datetime
from graphviz import Source  
window = Tk()

window.title("Smart Grid Simulation")
window.option_add( "*font", "Times 14" )

window.geometry()
window.config(bg="#D6E2F3")

database_path = "Database/"


menu = Menu(window)

menu_file = Menu(menu)
menu_file.add_command(label='New', font=("Times", 11))

menu_file.add_separator()

menu_file.add_command(label='Open', font=("Times", 11))

menu_file.add_separator()

menu_file.add_command(label='Exit', font=("Times", 11))

menu.add_cascade(label='File', menu=menu_file, font=("Times", 11))

menu_documents = Menu(menu)
menu_documents.add_command(label='Document', font=("Times", 11))
menu.add_cascade(label='Document', menu=menu_documents, font=("Times", 11))


menu_help = Menu(menu)
menu_help.add_command(label='Contact Us', font=("Times", 11))
menu.add_cascade(label='Help', menu=menu_help, font=("Times", 11))

menu.config(bg='#49A')

window.config(menu=menu)






lbl = Label(window, text="Smart Grid Attack Simulation System ", font=("Times", 18), background="#D6E2F3", foreground="#000280")

lbl.grid(column=0, row=0, columnspan=2)


lbl_smartgrid_model = Label(window, text="   Smart Grid Model\n", background="#D6E2F3", foreground="#000280")
# sticky="W" left align
lbl_smartgrid_model.grid(sticky="W", column=0, row=2)
lbl_smartgrid_model.config(width=18)
combo_smartgrid_model = Combobox(window, width=35)

combo_smartgrid_model['values']= ("1 Node 255 Houses", 
	"4 Nodes 1 House", 
	"4 Nodes 492 Houses", 
	"13 Nodes 15 Houses", 
	"13 Nodes 73 Houses")

combo_smartgrid_model.current(4) #set the selected item

combo_smartgrid_model.grid(column=1, row=2)



def show_model():
    model_dir_name = combo_smartgrid_model.get().replace(" ", "_")
    model_path = os.path.join(database_path, model_dir_name)
    path_1 = os.path.join(model_path, 'GridLab-D.glm')
    path_2 = os.path.join(model_path, 'GridLab-D.dot')
    subprocess.run(['python3', 'glmMap.py', path_1, path_2])
    s = Source.from_file(path_2)
    s.view()




btn_show_model = Button(window, text=" Show Model", command=show_model)
btn_show_model.grid(column=2, row=2)





lbl_application = Label( window, justify=LEFT, anchor="w", text="   Application\n", background="#D6E2F3", foreground="#000280")
lbl_application.grid(sticky="W", column=0, row=4)
combo_application = Combobox(window, width=35)

combo_application ['values']= ("Demand/Response (DR)", "Dynamic Pricing (DP)", "Both DR and DP")

combo_application.current(0) #set the selected item

combo_application.grid(column=1, row=4)






def on_attack_category_change(index, value, op):
    if combo_attack_category.get() == "Nefarious Activity":
        combo_attack_type['values']= ("1 - Channel Jamming - Cluster", 
        	"2 - Channel Jamming - Peer-to-Peer", 
        	"3 - DNS attacks - Cluster", 
        	"4 - DNS attacks - Peer-to-Peer", 
        	"5 - Injection Attacks - Control Systems", 
        	"6 - Injection Attacks - End-point Systems", 
        	"7 - Malicious Code - End-point Systems")
        combo_attack_type.current(0) #set the selected item
    elif combo_attack_category.get() == "Eavesdropping, Interception and Hijacking":
        combo_attack_type['values']= ("8 - Replay of Messages - Cluster", 
        	"9 - Replay of Messages - Peer-to-Peer")
        combo_attack_type.current(0) #set the selected item
    elif combo_attack_category.get() == "None":
        combo_attack_type['values']= ("None")
        combo_attack_type.current(0) #set the selected item






string_attack_category = StringVar()
string_attack_category.trace('w',on_attack_category_change)
lbl_attack_category = Label(window, text="   Attack Category\n", background="#D6E2F3", foreground="#000280")
lbl_attack_category.grid(sticky="W", column=0, row=6)
combo_attack_category = Combobox(window, textvar=string_attack_category, width=35)

combo_attack_category['values']= ("None","Nefarious Activity", "Eavesdropping, Interception and Hijacking")




combo_attack_category.grid(column=1, row=6)







lbl_attack_type = Label(window, text="   Attack Type\n", background="#D6E2F3", foreground="#000280")
lbl_attack_type.grid(sticky="W", column=0, row=8)
combo_attack_type = Combobox(window, width=35)


combo_attack_type.grid(column=1, row=8)






def run():
    messagebox.showinfo("Message", "The simulation is running")

    model_dir_name = combo_smartgrid_model.get().replace(" ", "_")
    model_path = os.path.join(database_path, model_dir_name)
    attack_id = combo_attack_type.get().split(' ')[0]

    # Run the simulation using python3 to be explicit
    subprocess.run(['python3', 'attack_broker.py', model_path, attack_id])

    messagebox.showinfo("Message", "The simulation has been finished")

    # Rename the output files
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    attack_name_sanitized = combo_attack_type.get().replace(" ", "_").replace("-", "")

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





def result():
    Lb_files.delete(0, END)
    model_dir_name = combo_smartgrid_model.get().replace(" ", "_")
    path = os.path.join(database_path, model_dir_name)
    extension = 'csv'

    # Use full path for glob and get basenames for logic
    file_list = glob.glob(os.path.join(path, f'*.{extension}'))
    filenames = [os.path.basename(f) for f in file_list]

    j = 0
    app_type = combo_application.get()

    for f in filenames:
        is_dr = app_type == "Demand/Response (DR)" and f.startswith("totalload")
        is_dp = app_type == "Dynamic Pricing (DP)" and f.startswith("price")
        is_both = app_type == "Both DR and DP" and (f.startswith("totalload") or f.startswith("price"))

        if is_dr or is_dp or is_both:
            Lb_files.insert(j, f)
            j += 1



btn_run = Button(window, text="Run Simulation", command=run)
btn_run.grid(column=0, row=10)


btn_result= Button(window, text="Load Results", command=result)
btn_result.grid(column=1, row=10)


lbl_result = Label(window, text="\nSimulation Results", font=("Times", 18), background="#D6E2F3", foreground="#000280")

lbl_result.grid(column=0, row=11, columnspan=2)
lbl_files = Label(window, text="Output Files", background="#D6E2F3", foreground="#000280")
lbl_files.grid(column=0, row=12)




Lb_files = Listbox(window, width=35, selectmode=MULTIPLE, height = 10)
Lb_files.grid(row=12, column=1)



def show():
    plot_price = ["null"]
    plot_totalload = ["null"]
    selection = Lb_files.curselection()
    for i in selection:
        filename = Lb_files.get(i)
        if filename.startswith('totalload'):
            plot_totalload.append(filename)
        elif filename.startswith('price'):
            plot_price.append(filename)

    model_dir_name = combo_smartgrid_model.get().replace(" ", "_")
    model_path = os.path.join(database_path, model_dir_name)

    # Join the filenames with a colon for the plot script argument
    price_arg = ":".join(plot_price)
    totalload_arg = ":".join(plot_totalload)

    subprocess.run(['python3', 'plot_result.py', model_path, price_arg, totalload_arg])


btn_show = Button(window, text="Show Charts", command=show)
btn_show.grid(column=1, row=13)





window.mainloop()
