import json

def extract_categories(input_file, output_file):
    with open(input_file, 'r') as input_json:
        data = json.load(input_json)

    categories = data.get('categories', [])  # Get the 'categories' attribute, defaulting to an empty list if not found

    with open(output_file, 'r+') as output_json:
        output_data = json.load(output_json)
        output_data['categories'] = categories
        output_json.seek(0)
        json.dump(output_data, output_json, indent=4)
        output_json.truncate()

# Example usage
input_file = '/liujinxin/code/models/PSALM/datasets/coco/annotations/panoptic_val2017.json'
output_file = '/liujinxin/code/models/PSALM/datasets/coco_white_gray_all/annotations/panoptic_val2017.json'

extract_categories(input_file, output_file)