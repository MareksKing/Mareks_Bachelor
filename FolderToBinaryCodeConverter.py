import argparse
import os
import h5py
import pickle
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--folder", help="Path to the selected folder")
args = parser.parse_args()

path_to_dir = args.folder
folderName = os.path.basename(args.folder)

pathForConversionFiles = r'Converted To Binary Code'


velocity = []
dates = []
amplitude = []


file_paths = []

# Loop through the files in the directory and append their paths to the file_paths array
def add_files_for_conversion(path_to_dir):
    for filename in os.listdir(path_to_dir):
        full_path = os.path.join(path_to_dir, filename)
        if os.path.isfile(full_path) and full_path.endswith('.h5'):
            file_paths.append(full_path)

def add_data_from_files_to_list():
    for i, file_path in enumerate(file_paths):
        with h5py.File(file_path, 'r') as f:
            
            if 'amplitude_corrected' in f:
                data = f['amplitude_corrected'][:]
                
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


def convert_to_binary_code(path_to_file, velocity, dates, amplitude):
    with open(path_to_file, 'wb') as f:
        pickle.dump((velocity, dates, amplitude), f)


velocity2 = []
dates2 = []
amplitude2 = []
file = r'data.bin'


if __name__ == '__main__':
    add_files_for_conversion(path_to_dir)
    add_data_from_files_to_list()
    fileCount = len(file_paths)
    first_date = dates[0]
    last_date = dates[-1]
    fileName = '{}_{}-{}_{}.bin'.format(folderName, first_date, last_date, fileCount)
    path_to_file = os.path.join(pathForConversionFiles, fileName)
    convert_to_binary_code(path_to_file, velocity, dates, amplitude)
    


