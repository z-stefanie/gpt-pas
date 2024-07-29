import json

def update_annotations(input_file, output_file):
    # Read the JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Iterate over each item in the annotations
    for item in data['annotations']:
        item['segments_info'] = [
                {
                    "id": 2105376,
                    "category_id": 2,
                    "iscrowd": 0,
                    "area": 1
                },
                {
                    "id": 16777215,
                    "category_id": 1,
                    "iscrowd": 0,
                    "area": 1
                },
            ]
        # if 'good' in item['file_name']:
        #     item['segments_info'] = [
        #         {
        #             "id": 0,
        #             "category_id": 2,
        #             "iscrowd": 0,
        #             "area": 1
        #         }
        #     ]
        # else:
        #     item['segments_info'] = [
        #         {
        #             "id": 0,
        #             "category_id": 2,
        #             "iscrowd": 0,
        #             "area": 1
        #         },
        #         {
        #             "id": 16777215,
        #             "category_id": 1,
        #             "iscrowd": 0,
        #             "area": 1
        #         }
        #     ]

    # Write the updated data back to a JSON file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

# Example usage
input_file = '/liujinxin/code/models/PSALM/datasets/coco_white_black/annotations/panoptic_train2017.json'
output_file = '/liujinxin/code/models/PSALM/datasets/coco_white_black/annotations/panoptic_train2017.json'
update_annotations(input_file, output_file)