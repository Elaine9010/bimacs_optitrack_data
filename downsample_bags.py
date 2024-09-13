# This scripte downsample the bag files to 30fps
# Usage
# python downsample_bags.py -subject_name subject0 -output_folder downsampled_60

import rosbag
from rospy import Time
import os
import argparse


def downsample_bags(args):
    #read filenames from subdirectory subject_name
    subject_files = os.listdir(f"./{args.subject_name}")

    for file in subject_files:
        # Input and output bag files
        input_bag_file = f"./{args.subject_name}/{file}" 
        output_bag_file = f"./{args.output_folder}/downsampled_{args.subject_name}/{file}"
        # Create file path if it does not exist
        os.makedirs(f"./{args.output_folder}/downsampled_{args.subject_name}", exist_ok=True)

        # Initialize last message time
        last_message_time = None
        count = 0

        # Open the input bag file for reading and create a new output bag file for writing
        with rosbag.Bag(output_bag_file, 'w') as outbag:
            with rosbag.Bag(input_bag_file, 'r') as bag:
                for topic, msg, t in bag.read_messages(topics=['/natnet_node/natnet_frame']):
                    # If this is the first message or enough time has passed since the last one
                    if last_message_time is None or (t - last_message_time).to_sec() >= 0.016: # 0.03 for 30fps, 0.016 for 60fps
                        # Write the message to the output bag
                        outbag.write(topic, msg, t)
                        count+=1
                        # Update the last message time
                        last_message_time = t
                        
        print(f"{count} messages written to file {output_bag_file}")

        print(f"Downsampled bag file saved to {output_bag_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downsample a ROS bag file')
    parser.add_argument('-subject_name',type=str, required=True, help='input file path')
    parser.add_argument('-output_folder',type=str, required=True, help='output file path')
    args = parser.parse_args()
    downsample_bags(args)