import json

# Load the JSON file
with open('/liujinxin/code/models/PSALM/datasets/coco_black_category3/annotations/panoptic_val2017.json') as json_file:
    data = json.load(json_file)

# Remove "supercategory" attribute from each category
for category in data['categories']:
    category.pop('supercategory', None)

# Save the modified data to a new JSON file
with open('/liujinxin/code/models/PSALM/datasets/coco_black_category3/annotations/panoptic_val2017.json', 'w') as json_file:
    json.dump(data, json_file,indent=4)