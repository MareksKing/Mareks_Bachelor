import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import h5py
import os
import argparse
import time
import plotly.graph_objects as go
import pickle


parser = argparse.ArgumentParser()
parser.add_argument("--file", help="Path to the selected folder")
parser.add_argument("--selectedOption", help="SelectedOption")
parser.add_argument("--inputValue", help="Input Value")
parser.add_argument("--limitingOption", help="Limiting option")
parser.add_argument("--minValueLimit", help="Min value for limit")
parser.add_argument("--maxValueLimit", help="Max value for limit")
parser.add_argument("--viewAngle", help="Viewing angle for the plot")
args = parser.parse_args()


# Retrieve the folder path from the command-line argument
print("Resolution change option:",args.selectedOption)
print("N points:",args.inputValue)
print("Limiting Option:",args.limitingOption)
print("Limiting range:", args.minValueLimit, "-", args.maxValueLimit)
print("ViewAngle:", args.viewAngle)
file = args.file
selectedOption = args.selectedOption
limitingOption = args.limitingOption
min_value = float(args.minValueLimit)
max_value = float(args.maxValueLimit)
nth_point = int(args.inputValue)
folderName = os.path.basename(file)
viewAngle = int(args.viewAngle) -1

tempVelocity = []
tempDates = []
tempAmplitude = []

velocity = []
dates = []
amplitude = []
listOfViewAngles =[[45, 135], [45, 90], [45, 45], [45, 180], [90, -90], [45, 0], [45,-135], [45,-90], [45,-45]]
elevation = listOfViewAngles[viewAngle][0]
azimuth = listOfViewAngles[viewAngle][1]


def limiting_velocities(min_value, max_value):
    for i, velocity_value in enumerate(tempVelocity):
        if min_value <= velocity_value <= max_value:
            velocity.append(velocity_value)
            dates.append(tempDates[i])
            amplitude.append(tempAmplitude[i])

    

def limiting_dates(min_value, max_value):
    for i, date in enumerate(tempDates):
        if min_value <= date <= max_value:
            dates.append(date)
            velocity.append(tempVelocity[i])
            amplitude.append(tempAmplitude[i])
    


def convert_to_list_data(file):
    global tempVelocity, tempDates, tempAmplitude
    with open(file, 'rb') as f:
        tempVelocity, tempDates, tempAmplitude = pickle.load(f)

# Add data to velocity, dates and amplitude arrays from the binary code using every nth point
def every_nth_point(nth_point):
    
    velocity.extend(tempVelocity[::nth_point])
    dates.extend(tempDates[::nth_point])
    amplitude.extend(tempAmplitude[::nth_point])


# Add data to velocity, dates and amplitude arrays from the file_paths using the average of n points
def average_of_n_points(nth_point):
    global tempVelocity, tempDates, tempAmplitude
    num_complete_groups = len(tempVelocity) // nth_point
    tempVelocity = tempVelocity[:num_complete_groups * nth_point]
    tempDates = tempDates[:num_complete_groups * nth_point]
    tempAmplitude = tempAmplitude[:num_complete_groups * nth_point]

    reshaped_velocity = np.reshape(tempVelocity, (-1, nth_point))
    reshaped_amplitude = np.reshape(tempAmplitude, (-1, nth_point))
    reshaped_dates = np.reshape(tempDates, (-1, nth_point))

    average_velocity = np.mean(reshaped_velocity, 1)
    average_amplitude = np.mean(reshaped_amplitude, 1)
    average_dates = np.mean(reshaped_dates, 1)

    dates[:len(average_dates)] = average_dates
    velocity[:len(average_velocity)] = average_velocity
    amplitude[:len(average_amplitude)] = average_amplitude
  


def interpolate_data_to_n_points(nth_point):

    drop_indices = []

    # Iterate through the list and check for drops
    for i in range(1, len(tempVelocity)):
        if tempVelocity[i] < tempVelocity[i-1]:
            drop_indices.append(i)

    # Add the start and end indices to the drop_indices list
    drop_indices = [0] + drop_indices + [len(tempVelocity)]

    # Use the drop_indices list to split the original list into smaller arrays
    velocity_split = [tempVelocity[start:end] for start, end in zip(drop_indices, drop_indices[1:])]
    dates_split = [tempDates[start:end] for start, end in zip(drop_indices, drop_indices[1:])]
    amplitude_split = [tempAmplitude[start:end] for start, end in zip(drop_indices, drop_indices[1:])]
    


    for i in range(len(velocity_split)):
        new_velocity = np.linspace(np.min(velocity_split[i]), np.max(velocity_split[i]), nth_point)
        new_amplitude = np.interp(new_velocity, velocity_split[i], amplitude_split[i])
        new_dates = np.interp(new_velocity, velocity_split[i], dates_split[i])

        velocity.extend(new_velocity)
        dates.extend(new_dates)
        amplitude.extend(new_amplitude)


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
    fig = go.Figure(data=[go.Scatter3d(x=velocity , y=dates, z=amplitude, mode='markers',
                     marker=dict(color=amplitude, colorscale='jet', cmin=np.min(amplitude),
                                 cmax=np.max(amplitude), colorbar=dict(title='Amplitude intensity')))
    ])
    fig.update_layout(scene=dict(xaxis_title='Velocity', yaxis_title='Dates', zaxis_title='Amplitude'),
                      title='Datacube monitoring')

    fig.show()



def main():
    start_time = time.time()
    if limitingOption == "Velocity":
        convert_to_list_data(file)
        limiting_velocities(min_value, max_value)
        plot_the_data(velocity, dates, amplitude)
        # visualize_3d_data(velocity, dates, amplitude)
    elif limitingOption == "MJD":
        convert_to_list_data(file)
        limiting_dates(min_value, max_value)
        plot_the_data(velocity, dates, amplitude)
        # visualize_3d_data(velocity, dates, amplitude)
    elif limitingOption == "None":
        if selectedOption == "Every nth point":
            convert_to_list_data(file)
            every_nth_point(nth_point)
            plot_the_data(velocity, dates, amplitude)
            # visualize_3d_data(velocity, dates, amplitude)
        
        elif selectedOption == "Average of n-points":
            convert_to_list_data(file)
            average_of_n_points(nth_point)
            plot_the_data(velocity, dates, amplitude)
            # visualize_3d_data(velocity, dates, amplitude)

        elif selectedOption == "Interpolate":
            convert_to_list_data(file)
            interpolate_data_to_n_points(nth_point)
            plot_the_data(velocity, dates, amplitude)
            # visualize_3d_data(velocity, dates, amplitude)

    end_time = time.time()
            
    time_taken = end_time - start_time
    print("Data points:",len(velocity))
    print("Time taken by function: ", time_taken, " seconds")
    plt.show()

if __name__ == '__main__':
    main()
