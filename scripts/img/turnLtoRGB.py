import os
import imghdr
from PIL import Image
import argparse

def is_image(file_path):
    return imghdr.what(file_path) is not None

def convert_images_to_rgb(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if is_image(file_path):
                try:
                    with Image.open(file_path) as img:
                        if img.mode == 'L':
                            rgb_image = img.convert('RGB')
                            rgb_image.save(file_path)
                            print(f"Converted {file_path} to RGB mode.")
                        else:
                            print(f"Skipped {file_path}, already in {img.mode} mode.")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
            else:
                print(f"Skipped {file_path}, not an image file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve category and MVTec path from command line")
    parser.add_argument("--category", required=True, help="The category value")
    args = parser.parse_args()

    cocoPath = '/liujinxin/code/models/PSALM/datasets/coco_all'
    categoryPath = os.path.join(cocoPath,args.category)

    convert_images_to_rgb(categoryPath)
    # print(f'Convert all the images to RGB mode')