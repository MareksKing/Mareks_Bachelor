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
        folderName = folder_path.split("/")[-1]
        lbl_selected_folder.config(text=folderName)

    

def plot_files_in_folder():
        
    if minValue.get():
        minLimit = int(minValue.get())
    else:
        minLimit = 1

    if maxValue.get():
        maxLimit = int(maxValue.get())
    else:
        maxLimit = 1


    if minLimit > maxLimit :
            minLimit, maxLimit = maxLimit, minLimit
            print("Switching limits")
    else:
            minLimit = minValue.get()
            maxLimit = maxValue.get()

    if limiterOption.get() != "None":
        limitingOption = str(limiterOption.get())
    else:
            limitingOption = "None"
            minLimit = 1
            maxLimit = 1

    if selectedOption.get() != "Options":
        option = str(selectedOption.get())
    else:
            option = "Every nth point"


    if nthPoint.get():
        input_value = int(nthPoint.get())
    else:
        input_value = 1
    plotter_file = "DatacubeMonitor.py"

    subprocess.run(["python", plotter_file,"--folder",selectedFolder, "--selectedOption", option, "--inputValue", str(input_value), "--limitingOption", limitingOption, "--minValueLimit", str(minLimit),"--maxValueLimit", str(maxLimit)])

def createBinaryCodeFromFolder():
      plotter_file = "FolderToBinaryCodeConverter.py"

      subprocess.run(["python", plotter_file,"--folder",selectedFolder])

def selectBinFile():
    global selectedFile
    filePath = filedialog.askopenfilename(filetypes=[('Binary files', '*.bin')])
    if filePath:
        selectedFile = filePath
        fileName = filePath.split("/")[-1]
        lbl_selected_folder.config(text=fileName)

def plotBinaryData():
    

    if minValue.get():
        minLimit = int(minValue.get())
    else:
        minLimit = 1
    
    if maxValue.get():
        maxLimit = int(maxValue.get())
    else:
        maxLimit = 1


    if minLimit > maxLimit :
         minLimit, maxLimit = maxLimit, minLimit
         print("Switching limits")
    else:
         minLimit = minValue.get()
         maxLimit = maxValue.get()

    if limiterOption.get() != "None":
        limitingOption = str(limiterOption.get())
    else:
         limitingOption = "None"
         minLimit = 1
         maxLimit = 1

    if selectedOption.get() != "Options":
        option = str(selectedOption.get())
    else:
         option = "Every nth point"


    if nthPoint.get():
        input_value = int(nthPoint.get())
    else:
        input_value = 1
    plotter_file = "BinaryDatacubeMonitor.py"

    subprocess.run(["python", plotter_file,"--file",selectedFile, "--selectedOption", option, "--inputValue", str(input_value), "--limitingOption", limitingOption, "--minValueLimit", str(minLimit),"--maxValueLimit", str(maxLimit)])

# Create the GUI root
root = tk.Tk()
root.title("Datacube monitoring")
root.geometry("800x600")

lbl_selected_folder = tk.Label(root, text="")
lbl_selected_folder.pack(side="top")

# Button to select a folder
btn_select_folder = tk.Button(root, text="Select Folder", command=select_folder)
btn_select_folder.place(x=100, y=50)

btn_start_plotting = tk.Button(root, text="Start Plotting", command=plot_files_in_folder)
btn_start_plotting.place(x=200, y=50)

btn_select_file = tk.Button(root, text="Select .bin file", command=selectBinFile)
btn_select_file.place(x=100, y=100)

btn_select_file = tk.Button(root, text="Start Binary Plotting", command=plotBinaryData)
btn_select_file.place(x=200, y=100)

# Button to start the plotting process

btn_start_plotting = tk.Button(root, text="Convert To Binary code", command=createBinaryCodeFromFolder)
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
minValue = tk.Entry(root)
maxValue = tk.Entry(root)
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
minValue.place(x=300, y=250)
maxValue.place(x=490, y=250)


# Start the GUI event loop
root.mainloop()