import os
import shutil
import argparse

def move_and_rename_defective_images(source_folder,category):
    # Create the defective folder if it doesn't exist
    # defective_folder = os.path.join(source_folder,category,'defective')
    defective_folder = os.path.join(source_folder,'defective')
    os.makedirs(defective_folder, exist_ok=True)

    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    image_counter = 1

    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(source_folder):
        dirs.sort()
        files.sort()

        # Note: toothbrush only have defective and good categories!!
        if (root == defective_folder and category != 'toothbrush')or 'good' in root : continue
        for file in files:
            if os.path.splitext(file)[1].lower() in image_extensions:
                src_path = os.path.join(root, file)
                dest_path = os.path.join(defective_folder, f"{image_counter}.png")
                shutil.move(src_path, dest_path)
                print(f"Moved {file} to {dest_path}")
                image_counter += 1

def move_and_rename_good_images(source_folder):
    # Check if source folder exists

    original_good_folder = os.path.join(source_folder,'good')
    new_good_folder = os.path.join(source_folder,args.category,'good')

    os.makedirs(new_good_folder, exist_ok=True)
    
    if not os.path.exists(original_good_folder):
        print(f"Original folder {original_good_folder} does not exist.")
        return
    
    # Get list of all files in source folder
    files = os.listdir(original_good_folder)
    
    # Move each file to the destination folder
    for file in files:
        file_path = os.path.join(original_good_folder, file)
        new_file_path = os.path.join(new_good_folder, file) 
        if os.path.isfile(file_path):  # Check if it is a file
            shutil.move(file_path, new_file_path)
            print(f"Moved: {file_path} -> {new_good_folder}")

def delete_contents(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)

        elif os.path.isdir(item_path):
            if item not in ['good','defective']:
                delete_contents(item_path)
                os.rmdir(item_path)

# Example usage
# The path to the class of mvtec you wanna manipulate
# /liujinxin/code/models/PSALM/mvtec/cable
if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Retrieve category and MVTec path from command line")
    parser.add_argument("--category", required=True, help="The category value")
    parser.add_argument("--mvtec-path", required=True, help="The path to the MVTec dataset")
    args = parser.parse_args()

    source_folder = os.path.join(args.mvtec_path,args.category,'ground_truth')
    move_and_rename_defective_images(source_folder,args.category)
    # move_and_rename_good_images(source_folder)
    delete_contents(source_folder)

    source_folder = os.path.join(args.mvtec_path,args.category,'test')
    move_and_rename_defective_images(source_folder,args.category)
    # move_and_rename_good_images(source_folder)
    delete_contents(source_folder)




