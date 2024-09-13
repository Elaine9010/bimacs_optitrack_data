# This script reads the ROS bag files and saves the 3D object data to json files
# Usage
# python read_bags.py -input_folder downsampled_subject0 -output_folder our_derived_data/subject0/task_1_k_cooking

import rosbag
import json
import os
import argparse


# Define object mapping  new_name: [class_name, instance_name, class_index]
mapped_objs = {"Whisk":["whisk","whisk_2",5],"HandRight":["RightHand","RightHand_4",0],"HandLeft":["LeftHand","LeftHand_5",0],"Bottle":["bottle","bottle_1",7],"Bowl":["bowl","bowl_3",1]}

# Define object sizes (you may need to adjust these values)
object_sizes = {
    "Whisk": {"x": 0.05, "y": 0.2, "z": 0.05},
    "HandRight": {"x": 0.1, "y": 0.2, "z": 0.05},
    "HandLeft": {"x": 0.1, "y": 0.2, "z": 0.05},
    "Bottle": {"x": 0.1, "y": 0.3, "z": 0.1},
    "Bowl": {"x": 0.2, "y": 0.1, "z": 0.2}
}

# Define color mapping (you may want to adjust these)
color_mapping = {
    "Whisk": [255, 143, 0],
    "HandRight": [199, 7, 247],
    "HandLeft": [199, 7, 247],
    "Bottle": [207, 255, 0],
    "Bowl": [255, 0, 175]
}

def create_bounding_box(position, size):
    half_x, half_y, half_z = size["x"]/2, size["y"]/2, size["z"]/2
    bbox= {
        "x0": position.x - half_x,
        "x1": position.x + half_x,
        "y0": position.y - half_y,
        "y1": position.y + half_y,
        "z0": position.z - half_z,
        "z1": position.z + half_z
    }
    
    bbox = {k: v*1000 for k, v in bbox.items()}
    return bbox
    
def process_bag(bag_file, output_path):
    past_positions = {}
    frame_num = 0
    with rosbag.Bag(bag_file, 'r') as bag:
        for topic, msg, t in bag.read_messages(topics=['/natnet_node/natnet_frame']):
            #check whether the msg.rigid_bodies is empty
            if msg.rigid_bodies == []:
                continue
            frame_data = []
            for body in msg.rigid_bodies:
                class_name, instance_name, class_index = mapped_objs[body.name]
                size = object_sizes[body.name]
                try:
                    current_box = create_bounding_box(body.pose.position, size)
                except:
                    print(body)
                obj_id = body.id
                if obj_id in past_positions:
                        past_box = create_bounding_box(past_positions[obj_id], size)
                else:
                        past_box = current_box  # Use current box for the first occurrence
                obj_data = {
                    "bounding_box": current_box,
                    "certainty": 1 - body.error,  # Convert error to certainty
                    "class_index": class_index,
                    "class_name": class_name,
                    "colour": color_mapping[body.name],
                    "instance_name": instance_name,
                    "past_bounding_box":past_box,
                }
                
                #save current bounding box for next frame
                past_bbox = obj_data["bounding_box"]
                frame_data.append(obj_data)

                # Update past position for next frame
                past_positions[obj_id] = body.pose.position

            # Write the processed data to a JSON file for current frame, create the path if it doesn't exist
            output_file = os.path.join(output_path, f'frame_{frame_num}.json')
            os.makedirs(output_path, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(frame_data, f, indent=2)
            frame_num += 1
    print(f"{frame_num} frames saved to {output_path}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read from ROS bag files and save to json files')
    parser.add_argument('-input_folder',type=str, required=True, help='input file path')
    parser.add_argument('-output_folder',type=str, required=True, help='output file path')
    args = parser.parse_args()
    bag_file_path = args.input_folder
    print("Reading bag files from: ", bag_file_path)
    bag_file_names = os.listdir(bag_file_path)
    sorted_bag_file_names = sorted(bag_file_names)
    take_num = 0
    for bag_file_name in sorted_bag_file_names:
        bag_file = os.path.join(bag_file_path, bag_file_name)
        output_path = os.path.join(args.output_folder, f"take_{take_num}/3d_objects")
        os.makedirs(output_path, exist_ok=True)
        process_bag(bag_file, output_path)
        take_num += 1
    print("All 3d obj data saved to: ", args.output_folder)
        