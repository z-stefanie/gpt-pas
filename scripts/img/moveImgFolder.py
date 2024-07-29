import os
import shutil
import argparse

def move_folders(src_folder, dest_folder,category):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder,exist_ok=True)
    
    for folder_name in os.listdir(src_folder):
        if folder_name ==category:
            continue
        
        folder_path = os.path.join(src_folder, folder_name)
        if os.path.isdir(folder_path):
            dest_path = os.path.join(dest_folder, folder_name)
            shutil.move(folder_path, dest_path)
            print(f"Moved {folder_path} to {dest_path}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Retrieve category and MVTec path from command line")
    parser.add_argument("--category", required=True, help="The category value")
    parser.add_argument("--mvtec-path", required=True, help="The path to the MVTec dataset")
    args = parser.parse_args()

    source_folder = os.path.join(args.mvtec_path,args.category)

    folders = ['train','test','ground_truth','panoptic_train2017']
    for folder in folders:

        original_folder = os.path.join(source_folder, folder)  # Update this to your specific test folder
        new_folder =  os.path.join(source_folder, folder,args.category)

        move_folders(original_folder, new_folder,args.category)