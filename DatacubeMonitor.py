import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import h5py
import os
from astropy.time import Time
import datetime as date
from mpl_toolkits.mplot3d import Axes3D
import argparse
import time
import sys
import plotly.graph_objects as go


parser = argparse.ArgumentParser()
parser.add_argument("--folder", help="Path to the selected folder")
parser.add_argument("--selectedOption", help="SelectedOption")
parser.add_argument("--inputValue", help="Input Value")
parser.add_argument("--limitingOption", help="Limiting option")
parser.add_argument("--minValueLimit", help="Min value for limit")
parser.add_argument("--maxValueLimit", help="Max value for limit")
parser.add_argument("--viewAngle", help="Viewing angle for the plot")
parser.add_argument("--velocity_list", help="List of velocities to search")
parser.add_argument("--visualizationOption", help="Which plot to generate")
args = parser.parse_args()

path_to_dir = args.folder
if args.viewAngle:
    viewAngle = int(args.viewAngle) -1
else:
    viewAngle = 4


selectedOption = args.selectedOption
limitingOption = args.limitingOption
plotting_option = args.visualizationOption

if limitingOption != None:
    min_value, max_value = float(args.minValueLimit), float(args.maxValueLimit)
else:
    if selectedOption:
        if selectedOption == "Nav":
            viewAngle = int(args.viewAngle) -1

        elif selectedOption == "Velocity list":
            if args.velocity_list :
                converted_velocities = [float(x) for x in str(args.velocity_list).split(',')]
                print(converted_velocities)
            else:
                print("No velocities given")
                sys.exit()
            viewAngle = int(args.viewAngle) -1
        else:
            nth_point = int(args.inputValue)
            viewAngle = int(args.viewAngle) -1





print("Resolution change option:",args.selectedOption)
print("N points:",args.inputValue)


velocity = []
dates = []
amplitude = []
listOfViewAngles =[[45, 135], [45, 90], [45, 45], [45, 180], [90, -90], [45, 0], [45,-135], [45,-90], [45,-45]]
elevation = listOfViewAngles[viewAngle][0]
azimuth = listOfViewAngles[viewAngle][1]


temp_velocity = []
temp_dates = []
temp_amplitude = []


def limiting_velocities(min_value, max_value):
    for i, velocity_value in enumerate(temp_velocity):
        if min_value <= velocity_value <= max_value:
            velocity.append(velocity_value)
            dates.append(temp_dates[i])
            amplitude.append(temp_amplitude[i])
    

def limiting_dates(min_value, max_value):
    for i, date in enumerate(temp_dates):
        if min_value <= date <= max_value:
            dates.append(date)
            velocity.append(temp_velocity[i])
            amplitude.append(temp_amplitude[i])


file_paths = []

def read_data_from_files(file_paths, temp_velocity, temp_dates, temp_amplitude):
    for i, file_path in enumerate(file_paths):
        with h5py.File(file_path, 'r') as f:
            
            if 'amplitude_corrected' in f:
                data = f['amplitude_corrected'][:]
                
            elif 'amplitude' in f:
                continue
            else:
                print(f"No 'amplitude_corrected' or 'amplitude' dataset found in {file_path}")
                continue

            temp_velocity.extend(data[:, 0])
            file_name = os.path.basename(file_path)
            
            mjd = int(file_name.split('_')[1].split('.')[0])
            temp_dates.extend(np.full(data.shape[0], mjd))
            temp_amplitude.extend(data[:, 3])

# Loop through the files in the directory and append their paths to the file_paths array
def add_files_for_plotting(path_to_dir, file_paths):
    for filename in os.listdir(path_to_dir):
        full_path = os.path.join(path_to_dir, filename)
        if os.path.isfile(full_path) and full_path.endswith('.h5'):
            file_paths.append(full_path)

 

# Add data to velocity, dates and amplitude arrays from the file_paths using every nth point
def every_nth_point(nth_point):
    """
    This function extracts data from HDF5 files and appends specific columns to lists based on a given
    interval.
    
    :param nth_point: nth_point is an integer that specifies the interval at which data points are
    selected from the 'amplitude_corrected' dataset in each file. For example, if nth_point is 2, every
    other data point will be selected
    """
    for i, file_path in enumerate(file_paths):
        with h5py.File(file_path, 'r') as f:
            
            if 'amplitude_corrected' in f:
                data = f['amplitude_corrected'][::nth_point, :]
                
            elif 'amplitude' in f:
                continue
            else:
                print(f"No 'amplitude_corrected' or 'amplitude' dataset found in {file_path}")
                continue

            velocity.extend(data[:, 0])
            file_name = os.path.basename(file_path)
            
            mjd = int(file_name.split('_')[1].split('.')[0])
            dates.extend(np.full(data.shape[0], mjd))
            amplitude.extend(data[:, 3])


# Add data to velocity, dates and amplitude arrays from the file_paths using the average of n points
def average_of_n_points(nth_point):
    """
    This function calculates the average velocity and amplitude of a set of data points, given a
    specific number of points to group together.
    
    :param nth_point: nth_point is an integer that represents the number of data points to be averaged
    together. The function takes in data from multiple files and groups them into sets of nth_point data
    points, then calculates the average velocity and amplitude for each set
    """
    temp_velocity, temp_amplitude = [],[]
    for i, file_path in enumerate(file_paths):
        with h5py.File(file_path, 'r') as f:

            if 'amplitude_corrected' in f:
                data = f['amplitude_corrected'][:]
                
            elif 'amplitude' in f:
                continue
            else:
                print(f"No 'amplitude_corrected' or 'amplitude' dataset found in {file_path}")
                continue

            num_entries = data.shape[0]
            num_complete_groups = num_entries // nth_point

            data = data[:num_complete_groups * nth_point]

            temp_velocity.extend(data[:, 0])
            file_name = os.path.basename(file_path)
            
            mjd = int(file_name.split('_')[1].split('.')[0])
            dates.extend(np.full(data.shape[0] // nth_point, mjd))
            temp_amplitude.extend(data[:, 3])
    reshaped_velocity = np.reshape(temp_velocity, (-1, nth_point))
    reshaped_amplitude = np.reshape(temp_amplitude, (-1, nth_point))

    average_velocity = np.mean(reshaped_velocity, 1)
    average_amplitude = np.mean(reshaped_amplitude, 1)

    velocity[:len(average_velocity)] = average_velocity
    amplitude[:len(average_amplitude)] = average_amplitude    


def interpolate_data_to_n_points(nth_point):
    """
    This function interpolates data in n points using velocity, amplitude, and date information from
    multiple files.
    
    :param nth_point: nth_point is an integer that represents the number of points to interpolate the data
    into. It is used to create a new set of evenly spaced velocity values, and then interpolate the
    corresponding amplitude and date values based on the original data
    """
    temp_dates, temp_velocity, temp_amplitude = [], [], []
    for i, file_path in enumerate(file_paths):
        with h5py.File(file_path, 'r') as f:
            if 'amplitude_corrected' in f:
                data = f['amplitude_corrected'][:]
                
            elif 'amplitude' in f:
                continue
            else:
                print(f"No 'amplitude_corrected' or 'amplitude' dataset found in {file_path}")
                continue

            temp_velocity.extend(data[:, 0])
            file_name = os.path.basename(file_path)
            
            mjd = int(file_name.split('_')[1].split('.')[0])
            temp_dates.extend(np.full(data.shape[0], mjd))
            temp_amplitude.extend(data[:, 3])
            
            new_velocity = np.linspace(min(temp_velocity), max(temp_velocity), nth_point)
            new_amplitude = np.interp(new_velocity, temp_velocity, temp_amplitude)
            new_dates = np.interp(new_velocity, temp_velocity, temp_dates)

            velocity.extend(new_velocity)
            dates.extend(new_dates)
            amplitude.extend(new_amplitude)

            temp_velocity.clear()
            temp_dates.clear()
            temp_amplitude.clear()


# Create a 3D plot using the waterfall method
def plot_the_data(velocity, dates, amplitude):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
 
    cmap = plt.get_cmap('jet')

    
    scat = ax.scatter(velocity, dates, amplitude, c=amplitude, cmap=cmap)
    ax.view_init(elev=elevation, azim=azimuth)



    ax.set_xlabel('Ātrums (km s$^{-1}$)')
    ax.set_ylabel('Modificētā Juliāna diena')
    ax.set_zlabel('Amplitūda (Jy)')
    ax.set_title(f"{os.path.basename(args.folder)} Waterfall Plot")

    fig.colorbar(scat)
    

def visualize_3d_data(velocity, dates, amplitude):
    hover_text = [f'Velocity: {v}<br>Date: {d}<br>Amplitude: {a}' for v, d, a in zip(velocity, dates, amplitude)]

    fig = go.Figure(data=[go.Scatter3d(x=velocity, y=dates, z=amplitude, mode='markers', hovertemplate='%{text}', text=hover_text,
                                       marker=dict(color=amplitude, colorscale='jet', cmin=np.min(amplitude),
                                                   cmax=np.max(amplitude), colorbar=dict(title='Amplitude intensity')))
    ])
    
    fig.update_layout(scene=dict(xaxis_title=r'Ātrums (km s⁻¹)', yaxis_title='Modificētā Juliāna diena', zaxis_title='Amplitūda (Jy)'),
                      title='Datacube monitoring',)

    fig.show()

def velocity_selection(converted_velocities, all_velocities, all_dates, all_amplitudes):
    number_of_subplots = len(converted_velocities)
    num_of_rows = int(number_of_subplots ** 0.5) + 1
    num_of_cols = int(number_of_subplots ** 0.5)
    fig = plt.figure(figsize=(8, 5))
    subplots = []

    for i, conv_velocity in enumerate(converted_velocities):
        ax = fig.add_subplot(num_of_rows, num_of_cols, i + 1, projection='3d')
        ax.view_init(elev=elevation, azim=azimuth)
        subplots.append(ax)
        min_velocity_value = conv_velocity-0.5
        max_velocity_value = conv_velocity+0.5

        for i, temp_velocity_value in enumerate(all_velocities):
            if min_velocity_value <= temp_velocity_value <= max_velocity_value:
                velocity.append(temp_velocity_value)
                dates.append(all_dates[i])
                amplitude.append(all_amplitudes[i])

        cmap = plt.get_cmap('jet')
        scat = ax.scatter(velocity, dates, amplitude, c=amplitude, cmap=cmap)
        
        ax.set_title(f"{conv_velocity} Velocity")
        velocity.clear()
        amplitude.clear()
        dates.clear()

        fig.colorbar(scat)  
    # Adjust spacing between subplots
    plt.tight_layout()

    # Show the figure
    plt.show()

def plot_choice(plotting_option, velocity, dates, amplitude):
    if plotting_option == "Matplotlib":
        plot_the_data(velocity, dates, amplitude)
    elif plotting_option == "Plotly":
        visualize_3d_data(velocity, dates, amplitude)
    else:
        print("Not valid plotting option")

    print("Data points:",len(velocity))

if limitingOption == "Velocity":
    add_files_for_plotting(path_to_dir, file_paths)
    read_data_from_files(file_paths, temp_velocity, temp_dates, temp_amplitude)
    limiting_velocities(min_value, max_value)
    plot_choice(plotting_option, velocity, dates, amplitude)
elif limitingOption == "MJD":
    add_files_for_plotting(path_to_dir, file_paths)
    read_data_from_files(file_paths, temp_velocity, temp_dates, temp_amplitude)
    limiting_dates(min_value, max_value)
    plot_choice(plotting_option, velocity, dates, amplitude)

# elif limitingOption == "None":
if selectedOption == "Every nth point":
    add_files_for_plotting(path_to_dir, file_paths)
    every_nth_point(nth_point)
    plot_choice(plotting_option, velocity, dates, amplitude)
elif selectedOption == "Average of n-points":
    add_files_for_plotting(path_to_dir, file_paths)
    average_of_n_points(nth_point)
    plot_choice(plotting_option, velocity, dates, amplitude)

elif selectedOption == "Interpolate":
    add_files_for_plotting(path_to_dir, file_paths)
    interpolate_data_to_n_points(nth_point)
    plot_choice(plotting_option, velocity, dates, amplitude)
elif selectedOption == "Velocity list":
    add_files_for_plotting(path_to_dir, file_paths)
    read_data_from_files(file_paths, temp_velocity, temp_dates, temp_amplitude)
    velocity_selection(converted_velocities, temp_velocity, temp_dates, temp_amplitude)
elif selectedOption == "Nav":
    add_files_for_plotting(path_to_dir, file_paths)
    read_data_from_files(file_paths, temp_velocity, temp_dates, temp_amplitude)
    plot_choice(plotting_option, temp_velocity, temp_dates, temp_amplitude)


        
print("Data points:",len(velocity))
# print("Time taken by function: ", time_taken, " seconds")
plt.show()
    


