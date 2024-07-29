import json

# Function to remove bbox fields
def remove_bbox(data):
    if 'annotations' in data:
        for annotation in data['annotations']:
            if 'segments_info' in annotation:
                for segment in annotation['segments_info']:
                    if 'bbox' in segment:
                        del segment['bbox']
    return data

# Load JSON file
input_file = '/liujinxin/code/models/PSALM/datasets/coco/annotations/panoptic_train2017.json'
output_file = '/liujinxin/code/models/PSALM/scripts/panoptic_train2017.json'

with open(input_file, 'r') as f:
    data = json.load(f)

# Remove bbox fields
modified_data = remove_bbox(data)

# Save the modified JSON
with open(output_file, 'w') as f:
    json.dump(modified_data, f, indent=4)

print(f"The 'bbox' fields have been removed and saved to {output_file}.")