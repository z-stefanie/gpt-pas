import os
from PIL import Image

# Define the root directory
root_dir = "/liujinxin/code/models/PSALM/datasets/coco_white_black/panoptic_train2017/pill"

# Iterate through all folders in the root directory
for folder_name in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder_name)
    if os.path.isdir(folder_path):
        # Create a duplicate folder
        duplicate_folder_path = os.path.join(root_dir, f"{folder_name}_duplicate")
        os.makedirs(duplicate_folder_path, exist_ok=True)
        
        # Iterate through all files in the original folder
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                # Open the original image
                with Image.open(file_path) as img:
                    # Create a white image with the same size
                    white_img = Image.new('RGB', img.size, (32,32,32))
                    width, height = img.size

                    # Create a dark grey and white half split
                    for x in range(width):
                        for y in range(height):
                            if x < width // 2:
                                white_img.putpixel((x, y), (32, 32, 32))  # Left half with dark grey
                            else:
                                white_img.putpixel((x, y), (255, 255, 255))  # Right half with white

                    # Save the white image in the duplicate folder with the same name
                    white_img.save(os.path.join(duplicate_folder_path, file_name))

print("Folders duplicated and white images created successfully.")