import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import subprocess
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar
from matplotlib.figure import Figure


selected_folder = ""
selected_file = ""


def select_folder():
    
    global selected_folder
    folder_path = filedialog.askdirectory(title="Select Folder")
    if folder_path:
        selected_folder = folder_path
        folder_name = folder_path.split("/")[-1]
        lbl_selected_folder.config(text=folder_name)
        print("Folder selected")
    else:
        print("No folder selected")
    # return folder_name

    

def plot_files_in_folder_with_resolution_change():
        
    plotter_file = "DatacubeMonitor.py"
    plot_viewing_angle = int(view_angle_option.get())
    plot_visualization_option = visualization_option.get()
    
    if limiterOption.get() != "None":
        plot_files_in_folder_with_limitations()
    else:
    # Resolution minimization
        if selectedOption.get() == options[0]:
            option = str(selectedOption.get())
            subprocess.run(["python", plotter_file,"--folder",selected_folder,"--selectedOption", option, "--visualizationOption", plot_visualization_option, "--viewAngle", str(plot_viewing_angle)])
        elif selectedOption.get() == options[-1]:
            velocity_list = ', '.join(str(x) for x in selected_option_input.get().split(','))
            option = str(selectedOption.get())
            subprocess.run(["python", plotter_file,"--folder",selected_folder,"--selectedOption", option, "--velocity_list", velocity_list,"--visualizationOption", plot_visualization_option,"--viewAngle", str(plot_viewing_angle)])
        else:
            if selected_option_input.get():
                input_value = int(selected_option_input.get())
            else:
                input_value = 1
            option = str(selectedOption.get())
            subprocess.run(["python", plotter_file,"--folder",selected_folder,"--selectedOption", option,"--inputValue", str(input_value),"--visualizationOption", plot_visualization_option, "--viewAngle", str(plot_viewing_angle)])


    


def plot_files_in_folder_with_limitations():

    plotter_file = "DatacubeMonitor.py"
    plot_viewing_angle = int(view_angle_option.get())
    plot_visualization_option = visualization_option.get()
    #Plot limitation 
    if min_value.get():
        min_limit = float(min_value.get())
    else:
        min_limit = 1

    if max_value.get():
        max_limit = float(max_value.get())
    else:
        max_limit = 1


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
    
    subprocess.run(["python", plotter_file,"--folder",selected_folder, "--limitingOption", limiting_option, 
                    "--minValueLimit", str(min_limit),"--maxValueLimit", str(max_limit), 
                    "--visualizationOption", plot_visualization_option, "--viewAngle", str(plot_viewing_angle)])
    

def update_label(folder_path):
    folder_name = folder_path.split("/")[-1]
    lbl_selected_folder.config(text=folder_name)

def create_binary_code_from_folder():
      
      plotter_file = "FolderToBinaryCodeConverter.py"

      subprocess.run(["python", plotter_file,"--folder",selected_folder])

def select_bin_or_h5_file():
    global selected_file
    file_path = filedialog.askopenfilename(filetypes=[('Files', ['.bin', '.h5'])])
    if file_path:
        selected_file = file_path
        file_name = file_path.split("/")[-1]
        lbl_selected_folder.config(text=file_name)
        print("File selected")
    else:
        print("No file selected")

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


    if selected_option_input.get():
        input_value = int(selected_option_input.get())
    else:
        input_value = 1
    plotter_file = "BinaryDatacubeMonitor.py"

    subprocess.run(["python", plotter_file,"--file",selected_file, "--selectedOption", option, "--inputValue", str(input_value), "--limitingOption", limiting_option, "--minValueLimit", str(min_limit),"--maxValueLimit", str(max_limit), "--viewAngle", str(plot_viewing_angle)])

# Create the GUI root

root = tk.Tk()
root.title("Datu kuba Vizualizācija")
root.geometry("800x400")

lbl_selected_folder = tk.Label(root, text="")
lbl_selected_folder.pack(side="top")

# Button to select a folder
btn_select_folder= tk.Button(root, text="Izvēlēties mapi", command=select_folder)
btn_select_folder.place(x=100, y=50)

btn_start_plotting = tk.Button(root, text="Sākt vizualizāciju", command=plot_files_in_folder_with_resolution_change)
btn_start_plotting.place(x=475, y=300)

btn_select_file = tk.Button(root, text="Izvēlēties .bin failu", command=select_bin_or_h5_file)
btn_select_file.place(x=100, y=100)

# btn_select_file = tk.Button(root, text="Sākt bināro vizualizāciju", command=plot_binary_data)
# btn_select_file.place(x=450, y=300)

btn_start_conversion_to_binary = tk.Button(root, text="Pārvērst binārā kodā", command=create_binary_code_from_folder)
btn_start_conversion_to_binary.place(x=600, y=300)

# Dropdown menu for visualization options
label = tk.Label(root, text="Izvēlēties vizualizācijas opciju")
label.place(x=100, y=100)

options = ["Nav", "Every nth point", "Average of n-points", "Interpolate", "Velocity list"]
selectedOption = tk.StringVar(root, value=options[0])
dropdown_menu = tk.OptionMenu(root, selectedOption, *options)
dropdown_menu.place(x=100, y=200)

selectedOption.trace("w", lambda *args: update_selected_option_label())
def update_selected_option_label():
    if selectedOption.get() == options[-1]:
        label.config(text=f"Selected option: {selectedOption.get()}, write all values in sequence, seperate with ','")
    else:
        label.config(text=f"Selected option: {selectedOption.get()}")
    

# Field where user inputs nth point
selected_option_input = tk.Entry(root)
min_value = tk.Entry(root)
max_value = tk.Entry(root)
label.place(x=100, y=150)
selected_option_input.place(x=100, y=250)

limiterOption = tk.StringVar(value="None")
radio_button_none = tk.Radiobutton(root, text="Nav", variable=limiterOption, value="None")
radio_button_velocity = tk.Radiobutton(root, text="Ātruma ierobežots", variable=limiterOption, value="Velocity")
radio_button_time = tk.Radiobutton(root, text="MJD ierobežots", variable=limiterOption, value="MJD")


minLabel = tk.Label(root, text="Min vērtība")
maxLabel = tk.Label(root, text="Max vērtība")
dashSymbol = tk.Label(root, text = "-")

radio_button_none.place(x=250, y=200)
radio_button_velocity.place(x=350, y=200)
radio_button_time.place(x=500, y=200)
minLabel.place(x=300, y=230)
maxLabel.place(x=490, y=230)
dashSymbol.place(x=450, y=250)
min_value.place(x=300, y=250)
max_value.place(x=490, y=250)

viewAngle = tk.Label(root, text= "Izvēlēties skata punktu")
viewAngle.place(x=230, y=30)
view_angle_option = tk.StringVar(value="5")

# Create radiobuttons in the grid using the place manager
for i in range(3):
    for j in range(3):
        rb = tk.Radiobutton(root, variable=view_angle_option, value=f"{i*3+j+1}")
        rb.place(x=230+j*30, y=50+i*30)

visualization_option = tk.StringVar(value="Matplotlib")
radio_button_matplotlib = tk.Radiobutton(root, text="Matplotlib", variable=visualization_option, value="Matplotlib")
radio_button_plotly = tk.Radiobutton(root, text="Plotly", variable=visualization_option, value="Plotly")

radio_button_matplotlib.place(x=340, y=50)
radio_button_plotly.place(x=340, y=80)
# Start the GUI event loop
root.mainloop()