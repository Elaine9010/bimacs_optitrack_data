#!/bin/bash

### this is a bash file used for optitrack dataset generation
### it will convert the optitrack data to the format of bimanual dataset
### the optitrack data is in the format of .bag file

# first downsample the optitrack data to 60fps
python downsample_bags.py -subject_name subject0 -output_folder downsampled_60
python downsample_bags.py -subject_name subject1 -output_folder downsampled_60

# then read the ROS bag files and saves the 3D object data to json files
python read_bags.py -input_folder downsampled_60/downsampled_subject0 -output_folder optitrack_derived_data/subject0/task_1_k_cooking
python read_bags.py -input_folder downsampled_60/downsampled_subject1 -output_folder optitrack_derived_data/subject1/task_1_k_cooking

# read data from 3d_obj , generates spatial relations between objects and saves them to json files
python generate_relations.py -input_folder optitrack_derived_data/subject0/task_1_k_cooking -output_folder optitrack_derived_data/subject0/task_1_k_cooking
python generate_relations.py -input_folder optitrack_derived_data/subject1/task_1_k_cooking -output_folder optitrack_derived_data/subject1/task_1_k_cooking