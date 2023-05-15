import dask
import dask.array as da
import dask.dataframe as dd
import h5py
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def print_attrs(name, obj):
    print(name)
    for key, val in obj.attrs.items():
        print("    %s: %s" % (key, val))
        
dates =[]
file_paths=[]
numbers= []
data=pd.DataFrame()

def read_h5_file(file_paths):
    global data, numbers
    for i, file_path in enumerate(file_paths):
        with h5py.File(file_path, 'r') as f:
            if 'amplitude_corrected' in f:
                readData = pd.DataFrame(f['amplitude_corrected'])
                data=pd.concat([data, readData]) 
            elif 'amplitude' in f:
                print(file_path)
                continue
            else:
                print(f"No 'amplitude_corrected' or 'amplitude' dataset found in {file_path}")
                continue

        file_name = os.path.basename(file_path)
        mjd = int(file_name.split('_')[1].split('.')[0])
        numbers.extend(np.full(data.shape[0], mjd))  
    
    print(data.shape)
    num_entries = data.shape[0]
    num_complete_groups = num_entries // 4

    # Discard the remaining incomplete entries
    data = data[:num_complete_groups * 4]

    # Extract velocity, left polarization, right polarization, and mean amplitude
    velocity = data[0]
    left_polarization = data[1]
    right_polarization = data[2]
    mean_amplitude = data[3] 
          
    
    # Reshape the data arrays to calculate the average of every four entries
    reshaped_velocity = velocity.values.reshape(-1, 4)
    reshaped_left_polarization = left_polarization.values.reshape(-1, 4)
    reshaped_right_polarization = right_polarization.values.reshape(-1, 4)
    reshaped_mean_amplitude = mean_amplitude.values.reshape(-1, 4)

    # Calculate the average of each group
    velocity_avg = da.mean(reshaped_velocity, axis=1)
    left_polarization_avg = da.mean(reshaped_left_polarization, axis=1)
    right_polarization_avg = da.mean(reshaped_right_polarization, axis=1)
    mean_amplitude_avg = da.mean(reshaped_mean_amplitude, axis=1)


   
    # Combine the averages into a single Dask dataframe
    df = dd.from_dask_array(
        da.stack([velocity_avg, left_polarization_avg, right_polarization_avg, mean_amplitude_avg, numbers], axis=1),
        columns=['velocity', 'left_polarization', 'right_polarization', 'mean_amplitude', 'date']
    )


    # numbers = np.array(mjd_list)
    # numbers = np.repeat(numbers, 4)
    return df


fig = plt.figure()
path_to_dir = r'Spektru dati\6668\afgl6366'

ax = fig.add_subplot(projection='3d') 
for filename in os.listdir(path_to_dir):
    full_path = os.path.join(path_to_dir, filename)
    if os.path.isfile(full_path) and full_path.endswith('.h5'):
        file_paths.append(full_path)
    
df= read_h5_file(file_paths)
print("Printing DATAFRAME_________________________")

pandas_df = df.compute()

velocity = pandas_df['velocity']
amplitude = pandas_df['mean_amplitude']
dates = pandas_df['date']

velocity_repeated = np.repeat(velocity, 4)
amplitude_repeated = np.repeat(amplitude, 4)

# velocity = velocity[:len(dates)]

# amplitude = amplitude[:len(dates)]

print(len(velocity))
print(len(amplitude))
print(len(dates))

# dates = dates[:len(velocity)]
# print(len(dates))
# plt.plot(df['velocity'], df['mean_amplitude'])
# Read multiple HDF files into a single Dask dataframe
# df = dd.read_hdf(pattern=file_paths, key="amplitude_corrected", mode = 'r')

# Concatenate all the dataframes into a single Dask dataframe

# print(df)

# # Convert the Dask dataframe to a Pandas dataframe
# dfes = merged_df.to_dask_dataframe()
# print(merged_df.compute())

# # Visualize the dataframe
# pandas_df.plot(kind='scatter', x='velocity', y=dates, z='mean_amplitude')
# ax.scatter(amplitude, dates, amplitude, c=amplitude)
cmap = plt.get_cmap('jet')

# Create a scatter plot with a colormap
scat = ax.scatter(velocity, dates, amplitude, c=amplitude, cmap=cmap)
ax.view_init(elev=90, azim=-90)

# # Set the axis labels and title
ax.set_xlabel('Ātrums')
ax.set_ylabel('Modificētā Juliāna diena')
ax.set_zlabel('Amplitūda')

# Add a colorbar
fig.colorbar(scat)
# plt.xlabel('Velocity')
# plt.ylabel('Mean Amplitude')
# plt.title('Velocity vs Mean Amplitude')
plt.show()