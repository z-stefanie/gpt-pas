import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

def convert_to_png(jpeg_path, png_path):
    try:
        with Image.open(jpeg_path) as img:
            img.save(png_path, 'PNG')
        print(f"Converted {jpeg_path} to {png_path}")
    except Exception as e:
        print(f"Failed to convert {jpeg_path}: {e}")

def convert_images_in_folder(folder_path):
    with ThreadPoolExecutor() as executor:
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                jpeg_path = os.path.join(folder_path, filename)
                png_filename = os.path.splitext(filename)[0] + '.png'
                png_path = os.path.join(folder_path, png_filename)
                executor.submit(convert_to_png, jpeg_path, png_path)

if __name__ == "__main__":
    folder_path = "/liujinxin/code/models/PSALM/datasets/coco/val2017"  # Replace with the path to your folder
    convert_images_in_folder(folder_path)