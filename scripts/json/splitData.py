import os
import shutil
import random
import argparse

def delete_all_contents(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)

        elif os.path.isdir(item_path):
                delete_all_contents(item_path)
                os.rmdir(item_path)

def move_files(src_folder, dest_folder, file_list):
    for file_name in file_list:
        src_file = os.path.join(src_folder, file_name)
        dest_file = os.path.join(dest_folder, file_name)
        if os.path.exists(src_file):
            shutil.move(src_file, dest_file)
            print(f"Moved {src_file} to {dest_file}")

def process_folders(root_dir,ratio):
    test_dir = os.path.join(root_dir, 'test')
    train_dir = os.path.join(root_dir, 'train')
    ground_truth_defective_dir = os.path.join(root_dir, 'ground_truth')
    panoptic_defective_dir = os.path.join(root_dir, 'panoptic_train2017')

    for folder_name in os.listdir(test_dir):
        test_folder = os.path.join(test_dir, folder_name)
        train_folder = os.path.join(train_dir, folder_name)
        ground_truth_folder = os.path.join(ground_truth_defective_dir, folder_name)
        panoptic_folder = os.path.join(panoptic_defective_dir, folder_name)

        if not os.path.exists(train_folder):
            os.makedirs(train_folder)

        if not os.path.exists(panoptic_folder):
            os.makedirs(panoptic_folder)

        images = [f for f in os.listdir(test_folder) if os.path.isfile(os.path.join(test_folder, f))]
        random.shuffle(images)
        num_files_to_move = int(len(images) * ratio)
        files_to_move = images[:num_files_to_move]

        # Move 80% of images from test to train
        move_files(test_folder, train_folder, files_to_move)

        # Move corresponding defective images
        for file_name in files_to_move:
            ground_truth_file = os.path.join(ground_truth_folder, file_name)
            panoptic_file = os.path.join(panoptic_folder, file_name)
            if os.path.exists(ground_truth_file):
                shutil.move(ground_truth_file, panoptic_file)
                print(f"Moved {ground_truth_file} to {panoptic_file}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Retrieve category and MVTec path from command line")
    parser.add_argument("--category", required=True, help="The category value")
    parser.add_argument("--mvtec-path", required=True, help="The path to the MVTec dataset")
    parser.add_argument("--ratio", required=True,type=float,default=0.8,help="The ratio of the data to be split to the training dataset")
    args = parser.parse_args()

    # Delete the original train category
    source_folder = os.path.join(args.mvtec_path,args.category,'train')
    delete_all_contents(source_folder)

    # Split the dataset from test to train
    source_folder = os.path.join(args.mvtec_path,args.category)
    process_folders(source_folder,args.ratio)
