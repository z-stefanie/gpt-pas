import shutil
import os
import argparse

def copyFolder(src,dst):
    # Check if the destination directory exists, if not create it
    if not os.path.exists(dst):
        os.makedirs(dst)

    # Copy the directory tree
    shutil.copytree(src, dst, dirs_exist_ok=True)  # Set dirs_exist_ok=True to allow existing directories

    print(f"Copied {src} to {dst}")

if __name__=='__main__':

    parser = argparse.ArgumentParser(description="Retrieve category and MVTec path from command line")
    parser.add_argument("--category", required=True, help="The category value")
    args = parser.parse_args()

    cocoPath = '/liujinxin/code/models/PSALM/datasets/coco_all'
    
    src = os.path.join(cocoPath,args.category,'panoptic_train2017')
    dst = os.path.join(cocoPath,args.category,'panoptic_semseg_train2017')
    copyFolder(src,dst)

    src = os.path.join(cocoPath,args.category,'panoptic_val2017')
    dst = os.path.join(cocoPath,args.category,'panoptic_semseg_val2017')
    copyFolder(src,dst) 

