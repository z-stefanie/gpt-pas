import json
import os

def add_isthing_attribute(json_file):
    # Read the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Add the "isthing":1 attribute to each item in the "images" list
    if "images" in data:
        for item in data["categories"]:
            item["isthing"] = 1
    
    # Write the modified data back to the JSON file
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)
    
    print(f'Added "isthing":1 to each item in "images" in {json_file}')

def convert_path(path):
    new_path = os.path.join(category,path)
    return new_path

def add_file_name_to_annotations(json_file_path, output_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    image_id_to_filename = {image['id']: image['file_name'] for image in data['images']}
    
    for annotation in data['annotations']:
        image_id = annotation['image_id']
        if image_id in image_id_to_filename:
            annotation['file_name'] = image_id_to_filename[image_id]
        else:
            annotation['file_name'] = None  # Or some default value or error handling
    
    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def modify_image_file_name(json_file_path, output_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for image in data['images']:
        original_path = image['file_name']
        image['file_name'] = convert_path(original_path)
    
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def add_segment_info_to_annotations(json_file_path, output_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    for annotation in data['annotations']:
        segment_info = [{
            "id": 0,
            "category_id": annotation.get("category_id", None),
            "iscrowd": 0,
            "area": 1
        }]
        annotation['segments_info'] = segment_info
    
    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def delete_category_id_from_annotations(json_file_path, output_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    for annotation in data['annotations']:
        if 'category_id' in annotation:
            del annotation['category_id']
    
    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Example usage
category = 'pill'

json_file_path = '/liujinxin/code/models/PSALM/datum/output/annotations/labels_train.json'
add_isthing_attribute(json_file_path)
modify_image_file_name(json_file_path,json_file_path)
add_file_name_to_annotations(json_file_path,json_file_path)
add_segment_info_to_annotations(json_file_path, json_file_path)
delete_category_id_from_annotations(json_file_path, json_file_path)
