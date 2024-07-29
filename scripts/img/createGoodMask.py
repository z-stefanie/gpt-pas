import os
from PIL import Image
import numpy as np
import argparse

def create_black_images(source_folder, target_folder):
    # Check if the source folder exists
    if not os.path.exists(source_folder):
        print(f"Source folder '{source_folder}' does not exist.")
        return

    # Create the target folder if it does not exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Iterate over each file in the source folder
    for filename in os.listdir(source_folder):
        source_path = os.path.join(source_folder, filename)
        
        # Check if it is a file and an image
        if os.path.isfile(source_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Open the image
            img = Image.open(source_path)
            # Create a black image with the same size
            black_image = Image.fromarray(np.zeros((img.height, img.width, 3), dtype=np.uint8))
            if black_image.mode != 'RGB':
                black_image = black_image.convert('RGB')
            # Save the black image to the target folder
            target_path = os.path.join(target_folder, filename)
            black_image.save(target_path)
            print(f"Created black image: {target_path}")

if __name__=='__main__':
# Define source and target folders
    parser = argparse.ArgumentParser(description="Retrieve category and MVTec path from command line")
    parser.add_argument("--category", required=True, help="The category value")
    parser.add_argument("--mvtec-path", required=True, help="The path to the MVTec dataset")
    args = parser.parse_args()

    prefix_folder = os.path.join(args.mvtec_path,args.category)
    source_folder = os.path.join(prefix_folder,'train',args.category,'good')
    target_folder = os.path.join(prefix_folder,'panoptic_train2017',args.category,'good')

    # Create black images
    create_black_images(source_folder, target_folder)

    source_folder = os.path.join(prefix_folder,'test',args.category,'good')
    target_folder = os.path.join(prefix_folder,'ground_truth',args.category,'good')

    # Create black images
    create_black_images(source_folder, target_folder)