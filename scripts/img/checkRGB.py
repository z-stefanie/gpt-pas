import os
import imghdr
from PIL import Image

def is_image(file_path):
    return imghdr.what(file_path) is not None

def check_images_rgb(folder_path):
    all_rgb = True
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if is_image(file_path):
                try:
                    with Image.open(file_path) as img:
                        if img.mode != 'RGB':
                            # print(f"{file_path} is in {img.mode} mode, not RGB.")
                            all_rgb = False
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    return all_rgb

if __name__ == "__main__":
    folder_path="/liujinxin/code/models/PSALM/mvtec"
    all_rgb = check_images_rgb(folder_path)
    if all_rgb:
        print("All image files are in RGB mode.")
    else:
        print("Not all image files are in RGB mode.")
