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
args = parser.parse_args()


print("Resolution change option:",args.selectedOption)
print("N points:",args.inputValue)
print("Limiting Option:",args.limitingOption)
print("Limiting range:", args.minValueLimit, "-", args.maxValueLimit)
print("ViewAngle:", args.viewAngle)
path_to_dir = args.folder
selectedOption = args.selectedOption
limitingOption = args.limitingOption
min_value = float(args.minValueLimit)
max_value = float(args.maxValueLimit)
nth_point = int(args.inputValue)
folderName = os.path.basename(args.folder)
viewAngle = int(args.viewAngle) -1


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

def read_data_from_files(file_paths):
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
def add_files_for_plotting(path_to_dir):
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
    temp_velocity, temp_dates, temp_amplitude = [],[],[]
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



    ax.set_xlabel('Ātrums (km/s^-1)')
    ax.set_ylabel('Modificētā Juliāna diena')
    ax.set_zlabel('Amplitūda (Jy)')
    ax.set_title(f"{folderName} Waterfall Plot")

    fig.colorbar(scat)
    

def visualize_3d_data(velocity, dates, amplitude):
    hover_text = [f'Velocity: {v}<br>Date: {d}<br>Amplitude: {a}' for v, d, a in zip(velocity, dates, amplitude)]

    fig = go.Figure(data=[go.Scatter3d(x=velocity, y=dates, z=amplitude, mode='markers', hovertemplate='%{text}', text=hover_text,
                                       marker=dict(color=amplitude, colorscale='jet', cmin=np.min(amplitude),
                                                   cmax=np.max(amplitude), colorbar=dict(title='Amplitude intensity')))
    ])
    
    fig.update_layout(scene=dict(xaxis_title='Ātrums (km/s^-1)', yaxis_title='Modificētā Juliāna diena', zaxis_title='Amplitūda (Jy)'),
                      title='Datacube monitoring',)

    fig.show()



def main():

    start_time = time.time()
    if limitingOption == "Velocity":
        add_files_for_plotting(path_to_dir)
        read_data_from_files(file_paths)
        limiting_velocities(min_value, max_value)
        plot_the_data(velocity, dates, amplitude)
        # visualize_3d_data(velocity, dates, amplitude)
    elif limitingOption == "MJD":
        add_files_for_plotting(path_to_dir)
        read_data_from_files(file_paths)
        limiting_dates(min_value, max_value)
        # plot_the_data(velocity, dates, amplitude)
        visualize_3d_data(velocity, dates, amplitude)
    elif limitingOption == "None":
        if selectedOption == "Every nth point":
            add_files_for_plotting(path_to_dir)
            every_nth_point(nth_point)
            # plot_the_data(velocity, dates, amplitude)
            visualize_3d_data(velocity, dates, amplitude)
        elif selectedOption == "Average of n-points":
            add_files_for_plotting(path_to_dir)
            average_of_n_points(nth_point)
            # plot_the_data(velocity, dates, amplitude)
            visualize_3d_data(velocity, dates, amplitude)

        elif selectedOption == "Interpolate":
            add_files_for_plotting(path_to_dir)
            interpolate_data_to_n_points(nth_point)
            # plot_the_data(velocity, dates, amplitude)
            visualize_3d_data(velocity, dates, amplitude)

    end_time = time.time()

    time_taken = end_time - start_time
            
    print("Data points:",len(velocity))
    print("Time taken by function: ", time_taken, " seconds")
    plt.show()
    

if __name__ == '__main__':
    main()
