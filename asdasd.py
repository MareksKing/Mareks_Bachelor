import h5py
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
import time
import os
import numpy as np


path_to_dir = r'Spektru dati\6668\cepa'

def calculate_time_diff(start_times, end_times):
    """
    Calculate the time difference between the start and end times for each element in the arrays.

    Parameters:
    start_times (list): A list of start times.
    end_times (list): A list of end times.

    Returns:
    None.
    """
    if len(start_times) != len(end_times):
        raise ValueError("The number of start and end times should be the same.")
        
    for i in range(len(start_times)):
        diff = end_times[i] - start_times[i]
        print(f"Time difference {i}: {diff} seconds")

velocity = []
amplitude = []
dates = []
# file_paths=[]
file_paths = [

r'Spektru dati\6668\cepa\cepa_58279.35146990741_IRBENE16_18.h5',
r'Spektru dati\6668\cepa\cepa_58283.30556712963_IRBENE16_20.h5',
r'Spektru dati\6668\cepa\cepa_58285.450266203705_IRBENE16_22.h5',
# r'Spektru dati\6668\cepa\cepa_58305.45402777778_IRBENE16_23.h5',
# r'Spektru dati\6668\cepa\cepa_58305.68471064815_IRBENE16_24.h5',
# r'Spektru dati\6668\cepa\cepa_58306.35255787037_IRBENE16_25.h5',
# r'Spektru dati\6668\cepa\cepa_58307.356458333335_IRBENE16_26.h5',
# r'Spektru dati\6668\cepa\cepa_58308.31613425926_IRBENE16_27.h5',
# r'Spektru dati\6668\cepa\cepa_58312.75827546296_IRBENE16_28.h5',
# r'Spektru dati\6668\cepa\cepa_58315.20685185185_IRBENE16_29.h5',
# r'Spektru dati\6668\cepa\cepa_58315.221087962964_IRBENE16_30.h5',
# r'Spektru dati\6668\cepa\cepa_58318.21053240741_IRBENE16_36.h5',
# r'Spektru dati\6668\cepa\cepa_58318.88019675926_IRBENE16_37.h5',
# r'Spektru dati\6668\cepa\cepa_58319.23674768519_IRBENE16_38.h5',
# r'Spektru dati\6668\cepa\cepa_58319.89346064815_IRBENE16_39.h5',
# r'Spektru dati\6668\cepa\cepa_58320.90153935185_IRBENE16_41.h5',
# r'Spektru dati\6668\cepa\cepa_58320.208136574074_IRBENE16_40.h5',
# r'Spektru dati\6668\cepa\cepa_58321.209131944444_IRBENE16_42.h5',
# r'Spektru dati\6668\cepa\cepa_58321.901550925926_IRBENE16_43.h5',
# r'Spektru dati\6668\cepa\cepa_58322.28244212963_IRBENE16_44.h5',
# r'Spektru dati\6668\cepa\cepa_58322.93377314815_IRBENE16_46.h5',
# r'Spektru dati\6668\cepa\cepa_58323.30033564815_IRBENE16_47.h5',
# r'Spektru dati\6668\cepa\cepa_58323.55619212963_IRBENE16_48.h5',
# r'Spektru dati\6668\cepa\cepa_58323.89336805556_IRBENE16_49.h5',
# r'Spektru dati\6668\cepa\cepa_58324.30674768519_IRBENE16_50.h5',
# r'Spektru dati\6668\cepa\cepa_58324.90792824074_IRBENE16_51.h5',
# r'Spektru dati\6668\cepa\cepa_58325.34554398148_IRBENE16_53.h5',
# r'Spektru dati\6668\cepa\cepa_58325.91925925926_IRBENE16_54.h5'
]
# for filename in os.listdir(path_to_dir):
#     full_path = os.path.join(path_to_dir, filename)
#     if os.path.isfile(full_path) and full_path.endswith('.h5'):
#         file_paths.append(full_path)

start_time = time.time()
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
    
for i, file_path in enumerate(file_paths):
    with h5py.File(file_path, 'r') as f:
        # Read the data from the h5 file and append it to the arrays
        if 'amplitude_corrected' in f:
            data = f['amplitude_corrected'][:]
                    
        elif 'amplitude' in f:
            continue
        else:
            print(f"No 'amplitude_corrected' or 'amplitude' dataset found in {file_path}")
            continue

        velocity.extend(data[:, 0])
        print(velocity)
        file_name = os.path.basename(file_path)
        
        mjd = int(file_name.split('_')[1].split('.')[0])
        dates.extend(np.full(data.shape[0], mjd))
        amplitude.extend(data[:, 3])
    
velocity = velocity[:len(dates)]
amplitude = amplitude[:len(dates)]
ax.scatter(velocity, dates, amplitude)
ax.set_xlabel('Ātrums (km s^-1)')
ax.set_ylabel('Modificētā Juliāna diena')
ax.set_zlabel('Amplitūda (Jy)')
# ax.view_init(elev=90, azim=-90)

    

    
end_time = time.time()
print(end_time-start_time)

plt.show()

