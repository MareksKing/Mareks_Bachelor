import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import h5py
import os
from astropy.time import Time
import datetime as date
from mpl_toolkits.mplot3d import Axes3D
import argparse
import time
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--folder", help="Path to the selected folder")
parser.add_argument("--selectedOption", help="SelectedOption")
parser.add_argument("--inputValue", help="Input Value")
parser.add_argument("--limitingOption", help="Limiting option")
parser.add_argument("--minValueLimit", help="Min value for limit")
parser.add_argument("--maxValueLimit", help="Max value for limit")
args = parser.parse_args()

# Retrieve the folder path from the command-line argument
print(args.folder)
print(args.selectedOption)
print(args.inputValue)
print(args.limitingOption)
path_to_dir = args.folder
selectedOption = args.selectedOption
limitingOption = args.limitingOption
minValue = float(args.minValueLimit)
maxValue = float(args.maxValueLimit)
nthPoint = int(args.inputValue)
folderName = os.path.basename(args.folder)

velocity = []
dates = []
amplitude = []

tempVelocity = []
tempDates = []
tempAmplitude = []


def limitingVelocities(minValue, maxValue):
    for i, velocity_value in enumerate(tempVelocity):
        if minValue <= velocity_value <= maxValue:
            velocity.append(velocity_value)
            dates.append(tempDates[i])
            amplitude.append(tempAmplitude[i])
    print(len(velocity))
    

def limitingDates(minValue, maxValue):
    for i, date in enumerate(tempDates):
        if minValue <= date <= maxValue:
            dates.append(date)
            velocity.append(tempVelocity[i])
            amplitude.append(tempAmplitude[i])
    
    print(len(velocity))
   

file_paths = []

def readDataFromFiles(file_paths):
    for i, file_path in enumerate(file_paths):
        with h5py.File(file_path, 'r') as f:
            
            if 'amplitude_corrected' in f:
                data = f['amplitude_corrected'][:]
                
            elif 'amplitude' in f:
                continue
            else:
                print(f"No 'amplitude_corrected' or 'amplitude' dataset found in {file_path}")
                continue

            tempVelocity.extend(data[:, 0])
            file_name = os.path.basename(file_path)
            
            mjd = int(file_name.split('_')[1].split('.')[0])
            tempDates.extend(np.full(data.shape[0], mjd))
            tempAmplitude.extend(data[:, 3])

# Loop through the files in the directory and append their paths to the file_paths array
def addFilesForPlotting(path_to_dir):
    for filename in os.listdir(path_to_dir):
        full_path = os.path.join(path_to_dir, filename)
        if os.path.isfile(full_path) and full_path.endswith('.h5'):
            file_paths.append(full_path)

 

# Add data to velocity, dates and amplitude arrays from the file_paths using every nth point
def everyNthPoint(nthPoint):
    """
    This function extracts data from HDF5 files and appends specific columns to lists based on a given
    interval.
    
    :param nthPoint: nthPoint is an integer that specifies the interval at which data points are
    selected from the 'amplitude_corrected' dataset in each file. For example, if nthPoint is 2, every
    other data point will be selected
    """
    for i, file_path in enumerate(file_paths):
        with h5py.File(file_path, 'r') as f:
            
            if 'amplitude_corrected' in f:
                data = f['amplitude_corrected'][::nthPoint, :]
                
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
    
    print(len(velocity))


# Add data to velocity, dates and amplitude arrays from the file_paths using the average of n points
def averageOfNPoints(nthPoint):
    """
    This function calculates the average velocity and amplitude of a set of data points, given a
    specific number of points to group together.
    
    :param nthPoint: nthPoint is an integer that represents the number of data points to be averaged
    together. The function takes in data from multiple files and groups them into sets of nthPoint data
    points, then calculates the average velocity and amplitude for each set
    """
    tempVelocity, tempDates, tempAmplitude = [],[],[]
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
            num_complete_groups = num_entries // nthPoint

            data = data[:num_complete_groups * nthPoint]

            tempVelocity.extend(data[:, 0])
            file_name = os.path.basename(file_path)
            
            mjd = int(file_name.split('_')[1].split('.')[0])
            dates.extend(np.full(data.shape[0] // nthPoint, mjd))
            tempAmplitude.extend(data[:, 3])
            reshaped_velocity = np.reshape(tempVelocity, (-1, nthPoint))
            reshaped_amplitude = np.reshape(tempAmplitude, (-1, nthPoint))

            averageVelocity = np.mean(reshaped_velocity, 1)
            averageAmplitude = np.mean(reshaped_amplitude, 1)

            velocity[:len(averageVelocity)] = averageVelocity
            amplitude[:len(averageAmplitude)] = averageAmplitude
    print(len(velocity))    


def interpolateDataInNPoints(nthPoint):
    """
    This function interpolates data in n points using velocity, amplitude, and date information from
    multiple files.
    
    :param nthPoint: nthPoint is an integer that represents the number of points to interpolate the data
    into. It is used to create a new set of evenly spaced velocity values, and then interpolate the
    corresponding amplitude and date values based on the original data
    """
    tempDates, tempVelocity, tempAmplitude = [], [], []
    for i, file_path in enumerate(file_paths):
        with h5py.File(file_path, 'r') as f:
            if 'amplitude_corrected' in f:
                data = f['amplitude_corrected'][:]
                
            elif 'amplitude' in f:
                continue
            else:
                print(f"No 'amplitude_corrected' or 'amplitude' dataset found in {file_path}")
                continue

            tempVelocity.extend(data[:, 0])
            file_name = os.path.basename(file_path)
            
            mjd = int(file_name.split('_')[1].split('.')[0])
            tempDates.extend(np.full(data.shape[0], mjd))
            tempAmplitude.extend(data[:, 3])
            
            newVelocity = np.linspace(min(tempVelocity), max(tempVelocity), nthPoint)
            newAmplitude = np.interp(newVelocity, tempVelocity, tempAmplitude)
            newDates = np.interp(newVelocity, tempVelocity, tempDates)

            velocity.extend(newVelocity)
            dates.extend(newDates)
            amplitude.extend(newAmplitude)

            tempVelocity.clear()
            tempDates.clear()
            tempAmplitude.clear()
        
    print(len(velocity))

# Create a 3D plot using the waterfall method
def plotTheData(velocity, dates, amplitude):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
 
    cmap = plt.get_cmap('jet')

    scat = ax.scatter(velocity, dates, amplitude, c=amplitude, cmap=cmap)
    ax.view_init(elev=90, azim=-90)

    ax.set_xlabel('Ātrums (km ^-1/s)')
    ax.set_ylabel('Modificētā Juliāna diena')
    ax.set_zlabel('Amplitūda (Jy)')
    ax.set_title(f"{folderName} Waterfall Plot")

    fig.colorbar(scat)
    

def main():

    start_time = time.time()
    if limitingOption == "Velocity":
        addFilesForPlotting(path_to_dir)
        readDataFromFiles(file_paths)
        limitingVelocities(minValue, maxValue)
        plotTheData(velocity, dates, amplitude)
    elif limitingOption == "MJD":
        addFilesForPlotting(path_to_dir)
        readDataFromFiles(file_paths)
        limitingDates(minValue, maxValue)
        plotTheData(velocity, dates, amplitude)
    elif limitingOption == "None":
        if selectedOption == "Every nth point":
            addFilesForPlotting(path_to_dir)
            everyNthPoint(nthPoint)
            plotTheData(velocity, dates, amplitude)
        
        elif selectedOption == "Average of n-points":
            addFilesForPlotting(path_to_dir)
            averageOfNPoints(nthPoint)
            plotTheData(velocity, dates, amplitude)

        elif selectedOption == "Interpolate":
            addFilesForPlotting(path_to_dir)
            interpolateDataInNPoints(nthPoint)
            plotTheData(velocity, dates, amplitude)

    end_time = time.time()

    time_taken = end_time - start_time
    print("Time taken by function: ", time_taken, " seconds")
    plt.show()

if __name__ == '__main__':
    main()
