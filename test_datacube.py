import os
import unittest
import h5py
import DatacubeMonitor
import subprocess
from unittest import mock
file_paths = []

temp_velocity = []
temp_dates = []
temp_amplitude = []

velocity = []
dates = []
amplitude = []
class H5FilesTestCase(unittest.TestCase):
    def setUp(self):
        self.folder_path = r'Simulation data'
        self.selected_option = "None"
        self.visualization_option = "Matplotlib"
        self.view_angle = 5
        self.file_paths = [os.path.join(self.folder_path, f) for f in os.listdir(self.folder_path) if f.endswith(".h5")]
        self.datacube_monitor = DatacubeMonitor # create DatacubeMonitor object with necessary arguments
        self.temp_velocity = []
        self.temp_dates = []
        self.temp_amplitude = []

    # def tearDown(self):
    #     ... # clean up resources if necessary

    # def test_add_files_for_plotting(self):
    #     print("Testing folder reading")
    #     self.datacube_monitor.add_files_for_plotting(self.folder_path, self.file_paths)
    #     self.assertEqual(len(self.file_paths), 100)

    def test_add_files_for_plotting_has_correct_file_paths(self):
        """
        Test that the function adds the correct files
        """
        self.datacube_monitor.add_files_for_plotting(self.folder_path, self.file_paths)
        file_names=[]
        for file in self.file_paths:
            file_names.append(os.path.basename(file))
        
        expected_file_paths = [os.path.join(self.folder_path, file_names[i]) for i in range(len(file_names))]
        for file_path in expected_file_paths:
            self.assertIn(file_path, self.file_paths)
    
    def test_read_data_from_files(self):
        print("Testing data reading")
        self.datacube_monitor.read_data_from_files(self.file_paths, self.temp_velocity, self.temp_dates, self.temp_amplitude)
        self.assertEqual(len(self.temp_velocity), 20000)

    def test_every_nth_point(self):
        print("Testing every nth point method")
        self.datacube_monitor.read_data_from_files(self.file_paths, self.temp_velocity, self.temp_dates, self.temp_amplitude)
        self.datacube_monitor.every_nth_point(2)
        self.assertEqual(len(self.temp_velocity), 20000)


    
        

class TestProgram(unittest.TestCase):
    def test_program_runs(self):
        # Call the subprocess without any arguments
        plotter_file = "DatacubeMonitor.py"
        folder_path = r'Simulation data'
        plot_viewing_angle = 5
        process = subprocess.run(["python", plotter_file, "--folder",folder_path,"--selectedOption", "None", "--visualizationOption", "Matplotlib", "--viewAngle", str(plot_viewing_angle)])

        # Assert that the process exited successfully
        self.assertEqual(process.returncode, 0)

if __name__ == '__main__':
    unittest.main()