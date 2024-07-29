import os
from PIL import Image

def change_black_pixels(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        pixels = img.load()
        
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                if pixels[i, j] == (128,128,128):
                    pixels[i, j] = (32,32,32)
        
        img.save(image_path)

def process_images_in_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff')):
                image_path = os.path.join(root, file)
                change_black_pixels(image_path)

if __name__ == "__main__":
    folder_path = "/liujinxin/code/models/PSALM/datasets/coco8/panoptic_val2017/pill"
    process_images_in_folder(folder_path)
