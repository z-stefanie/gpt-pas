import json

def update_annotations(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    for annotation in data.get('annotations', []):
        file_name = annotation.get('file_name', '')
        if 'good' in file_name:
            annotation['segments_info'] = []
        elif 'defective' in file_name:
            annotation['segments_info'] = [{
                "id": 16777215,
                "category_id": 1,
                "iscrowd": 0,
                "area": 1
            }]
    
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

# Example usage
update_annotations('/liujinxin/code/models/PSALM/datasets/coco_normal_category1/annotations/panoptic_val2017.json')