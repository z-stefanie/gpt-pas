import json

def process_images(json_file_path, output_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    count = 1
    annotations = []

    for item in data.get('images', []):
        file_name = item.get('file_name', '')
        image_id = item.get('id', None)

        if 'good' in file_name:
            annotation = {
                "id": count,
                "image_id": image_id,
                "file_name": file_name,
                "segments_info": [
                    {
                        "id": 0,
                        "category_id": 2,
                        "iscrowd": 0,
                        "area": 1
                    }
                ]
            }
            annotations.append(annotation)
            count += 1
        elif 'defective' in file_name:
            annotation = {
                "id": count,
                "image_id": image_id,
                "file_name": file_name,
                "segments_info": [
                    {
                        "id": 0,
                        "category_id": 2,
                        "iscrowd": 0,
                        "area": 1
                    },
                    {
                        "id": 16777215,
                        "category_id": 1,
                        "iscrowd": 0,
                        "area": 1
                    }
                ]
            }
            annotations.append(annotation)
            count += 1
    
    data['annotations'] = annotations

    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Example usage
process_images('/liujinxin/code/models/PSALM/datasets/coco_all/toothbrush/annotations/panoptic_train2017.json', '/liujinxin/code/models/PSALM/datasets/coco_all/toothbrush/annotations/panoptic_train2017.json')
