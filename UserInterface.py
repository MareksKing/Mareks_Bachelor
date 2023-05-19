import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import subprocess
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar
from matplotlib.figure import Figure


selectedFolder = ""
selectedFile = ""

def select_folder():
    
    global selectedFolder
    folder_path = filedialog.askdirectory(title="Select Folder")
    if folder_path:
        selectedFolder = folder_path
        folder_name = folder_path.split("/")[-1]
        lbl_selected_folder.config(text=folder_name)

    

def plot_files_in_folder():
        
    if min_value.get():
        min_limit = int(min_value.get())
    else:
        min_limit = 1

    if max_value.get():
        max_limit = int(max_value.get())
    else:
        max_limit = 1

    if view_angle_option.get():
        plot_viewing_angle = int(view_angle_option.get())
    else:
        plot_viewing_angle = 5

    if min_limit > max_limit :
            min_limit, max_limit = max_limit, min_limit
            print("Switching limits")
    else:
            min_limit = min_value.get()
            max_limit = max_value.get()

    if limiterOption.get() != "None":
        limiting_option = str(limiterOption.get())
    else:
            limiting_option = "None"
            min_limit = 1
            max_limit = 1

    if selectedOption.get() != "Options":
        option = str(selectedOption.get())
    else:
        option = options[0]


    if nthPoint.get():
        input_value = int(nthPoint.get())
    else:
        input_value = 1
    plotter_file = "DatacubeMonitor.py"

    subprocess.run(["python", plotter_file,"--folder",selectedFolder, "--selectedOption", option, "--inputValue", str(input_value), "--limitingOption", limiting_option, "--minValueLimit", str(min_limit),"--maxValueLimit", str(max_limit), "--viewAngle", str(plot_viewing_angle)])

def create_binary_code_from_folder():
      plotter_file = "FolderToBinaryCodeConverter.py"

      subprocess.run(["python", plotter_file,"--folder",selectedFolder])

def select_bin_file():
    global selectedFile
    file_path = filedialog.askopenfilename(filetypes=[('Binary files', '*.bin')])
    if file_path:
        selectedFile = file_path
        file_name = file_path.split("/")[-1]
        lbl_selected_folder.config(text=file_name)

def plot_binary_data():
    

    if min_value.get():
        min_limit = int(min_value.get())
    else:
        min_limit = 1
    
    if max_value.get():
        max_limit = int(max_value.get())
    else:
        max_limit = 1

    if view_angle_option.get():
        plot_viewing_angle = int(view_angle_option.get())
    else:
        plot_viewing_angle = 5


    if min_limit > max_limit :
         min_limit, max_limit = max_limit, min_limit
         print("Switching limits")
    else:
         min_limit = min_value.get()
         max_limit = max_value.get()

    if limiterOption.get() != "None":
        limiting_option = str(limiterOption.get())
    else:
         limiting_option = "None"
         min_limit = 1
         max_limit = 1

    if selectedOption.get() != "Options":
        option = str(selectedOption.get())
    else:
        option = options[0]


    if nthPoint.get():
        input_value = int(nthPoint.get())
    else:
        input_value = 1
    plotter_file = "BinaryDatacubeMonitor.py"

    subprocess.run(["python", plotter_file,"--file",selectedFile, "--selectedOption", option, "--inputValue", str(input_value), "--limitingOption", limiting_option, "--minValueLimit", str(min_limit),"--maxValueLimit", str(max_limit), "--viewAngle", str(plot_viewing_angle)])

# Create the GUI root
root = tk.Tk()
root.title("Datacube monitoring")
root.geometry("800x600")

lbl_selected_folder = tk.Label(root, text="")
lbl_selected_folder.pack(side="top")

# Button to select a folder
btn_select_folder= tk.Button(root, text="Select Folder", command=select_folder)
btn_select_folder.place(x=100, y=50)

btn_start_plotting = tk.Button(root, text="Start Plotting", command=plot_files_in_folder)
btn_start_plotting.place(x=200, y=50)

btn_select_file = tk.Button(root, text="Select .bin file", command=select_bin_file)
btn_select_file.place(x=100, y=100)

btn_select_file = tk.Button(root, text="Start Binary Plotting", command=plot_binary_data)
btn_select_file.place(x=200, y=100)

# Button to start the plotting process

btn_start_plotting = tk.Button(root, text="Convert To Binary code", command=create_binary_code_from_folder)
btn_start_plotting.place(x=300, y=50)

# Dropdown menu for visualization options
label = tk.Label(root, text="Choose visualization option")
label.place(x=100, y=100)

options = ["Every nth point", "Average of n-points", "Interpolate"]
selectedOption = tk.StringVar(root)
selectedOption.set("Options")
dropdown_menu = tk.OptionMenu(root, selectedOption, *options)
dropdown_menu.place(x=100, y=200)

selectedOption.trace("w", lambda *args: update_label())
def update_label():
    label.config(text=f"Selected option: {selectedOption.get()}")

# Field where user inputs nth point
nthPoint = tk.Entry(root)
min_value = tk.Entry(root)
max_value = tk.Entry(root)
label.place(x=100, y=150)
nthPoint.place(x=100, y=250)

limiterOption = tk.StringVar(value="None")
radio_button_none = tk.Radiobutton(root, text="None", variable=limiterOption, value="None")
radio_button_velocity = tk.Radiobutton(root, text="Velocity limiting", variable=limiterOption, value="Velocity")
radio_button_time = tk.Radiobutton(root, text="MJD limiting", variable=limiterOption, value="MJD")


minLabel = tk.Label(root, text="Min value")
maxLabel = tk.Label(root, text="Max value")
dashSymbol = tk.Label(root, text = "-")

radio_button_none.place(x=250, y=200)
radio_button_velocity.place(x=350, y=200)
radio_button_time.place(x=500, y=200)
minLabel.place(x=300, y=230)
maxLabel.place(x=490, y=230)
dashSymbol.place(x=450, y=250)
min_value.place(x=300, y=250)
max_value.place(x=490, y=250)

viewAngle = tk.Label(root, text= "Select viewing angle")
viewAngle.place(x=490, y=30)
view_angle_option = tk.StringVar(value="5")

# Create radiobuttons in the grid using the place manager
for i in range(3):
    for j in range(3):
        rb = tk.Radiobutton(root, variable=view_angle_option, value=f"{i*3+j+1}")
        rb.place(x=490+j*30, y=50+i*30)


# Start the GUI event loop
root.mainloop()