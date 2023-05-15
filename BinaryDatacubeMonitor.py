import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import h5py
import os
import argparse
import time

import pickle

parser = argparse.ArgumentParser()
parser.add_argument("--file", help="Path to the selected folder")
parser.add_argument("--selectedOption", help="SelectedOption")
parser.add_argument("--inputValue", help="Input Value")
parser.add_argument("--limitingOption", help="Limiting option")
parser.add_argument("--minValueLimit", help="Min value for limit")
parser.add_argument("--maxValueLimit", help="Max value for limit")
args = parser.parse_args()

# Retrieve the folder path from the command-line argument
print(args.selectedOption)
print(args.inputValue)
print(args.limitingOption)
# print(args.minValueLimit)
# print(args.maxValueLimit)
file = args.file
selectedOption = args.selectedOption
limitingOption = args.limitingOption
minValue = float(args.minValueLimit)
maxValue = float(args.maxValueLimit)
nthPoint = int(args.inputValue)
folderName = os.path.basename(file)

tempVelocity = []
tempDates = []
tempAmplitude = []

velocity = []
dates = []
amplitude = []

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

def convertToListData(file):
    global tempVelocity, tempDates, tempAmplitude
    with open(file, 'rb') as f:
        tempVelocity, tempDates, tempAmplitude = pickle.load(f)


# Add data to velocity, dates and amplitude arrays from the binary code using every nth point
def everyNthPoint(nthPoint):
    
    velocity.extend(tempVelocity[::nthPoint])
    dates.extend(tempDates[::nthPoint])
    amplitude.extend(tempAmplitude[::nthPoint])
    print(len(velocity))


# Add data to velocity, dates and amplitude arrays from the file_paths using the average of n points
def averageOfNPoints(nthPoint):
    global tempVelocity, tempDates, tempAmplitude
    num_complete_groups = len(tempVelocity) // nthPoint
    tempVelocity = tempVelocity[:num_complete_groups * nthPoint]
    tempDates = tempDates[:num_complete_groups * nthPoint]
    tempAmplitude = tempAmplitude[:num_complete_groups * nthPoint]

    reshaped_velocity = np.reshape(tempVelocity, (-1, nthPoint))
    reshaped_amplitude = np.reshape(tempAmplitude, (-1, nthPoint))
    reshaped_dates = np.reshape(tempDates, (-1, nthPoint))

    averageVelocity = np.mean(reshaped_velocity, 1)
    averageAmplitude = np.mean(reshaped_amplitude, 1)
    averageDates = np.mean(reshaped_dates, 1)

    dates[:len(averageDates)] = averageDates
    velocity[:len(averageVelocity)] = averageVelocity
    amplitude[:len(averageAmplitude)] = averageAmplitude
    print(len(velocity))    


def interpolateDataInNPoints(nthPoint):

    drop_indices = []

    # Iterate through the list and check for drops
    for i in range(1, len(tempVelocity)):
        if tempVelocity[i] < tempVelocity[i-1]:
            drop_indices.append(i)

    # Add the start and end indices to the drop_indices list
    drop_indices = [0] + drop_indices + [len(tempVelocity)]

    # Use the drop_indices list to split the original list into smaller arrays
    velocitySplit = [tempVelocity[start:end] for start, end in zip(drop_indices, drop_indices[1:])]
    datesSplit = [tempDates[start:end] for start, end in zip(drop_indices, drop_indices[1:])]
    amplitudeSplit = [tempAmplitude[start:end] for start, end in zip(drop_indices, drop_indices[1:])]
    


    for i in range(len(velocitySplit)):
        print(len(velocitySplit[i]))
        # print(datesSplit)
        newVelocity = np.linspace(np.min(velocitySplit[i]), np.max(velocitySplit[i]), nthPoint)
        newAmplitude = np.interp(newVelocity, velocitySplit[i], amplitudeSplit[i])
        newDates = np.interp(newVelocity, velocitySplit[i], datesSplit[i])

        velocity.extend(newVelocity)
        dates.extend(newDates)
        amplitude.extend(newAmplitude)

        
        
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
        convertToListData(file)
        limitingVelocities(minValue, maxValue)
        plotTheData(velocity, dates, amplitude)
    elif limitingOption == "MJD":
        convertToListData(file)
        limitingDates(minValue, maxValue)
        plotTheData(velocity, dates, amplitude)
    elif limitingOption == "None":
        if selectedOption == "Every nth point":
            convertToListData(file)
            everyNthPoint(nthPoint)
            plotTheData(velocity, dates, amplitude)
        
        elif selectedOption == "Average of n-points":
            convertToListData(file)
            averageOfNPoints(nthPoint)
            plotTheData(velocity, dates, amplitude)

        elif selectedOption == "Interpolate":
            convertToListData(file)
            interpolateDataInNPoints(nthPoint)
            plotTheData(velocity, dates, amplitude)

    end_time = time.time()

    time_taken = end_time - start_time
    print("Time taken by function: ", time_taken, " seconds")
    plt.show()

if __name__ == '__main__':
    main()
