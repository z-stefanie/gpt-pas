#!/bin/bash

# Set the parent directory containing the subfolders
original_mvtec_path="/liujinxin/code/models/PSALM/mvtec"
mvtec_path="/liujinxin/code/models/PSALM/mvtec3"
ratio=0.8

# Create the folder again
mkdir -p "$mvtec_path"

echo "Folder $mvtec_path has been created."

# Initialize Mamba
source /root/miniforge3/etc/profile.d/conda.sh

# Activate the mamba environment
# mamba init
conda activate psalm

coco_path="/liujinxin/code/models/PSALM/datasets/coco_all"
datasets_path="/liujinxin/code/models/PSALM/datasets"

category='toothbrush'

original_category_path="${original_mvtec_path}/${category}"
category_path="${mvtec_path}/${category}"
coco_category_path="${coco_path}/${category}"

# Check if the folder exists
if [ -d "$category_path" ]; then
    # Remove the folder and its contents
    rm -rf "$category_path"
fi

# Check if the folder exists
if [ -d "$coco_category_path" ]; then
    # Remove the folder and its contents
    rm -rf "$coco_category_path"
fi

cp -r  "$original_category_path" "$category_path"

echo "Folder $cateogry_path has been copied"

cd /liujinxin/code/models/PSALM/scripts

# # Execute the python scripts with the category argument
python img/moveImg.py --mvtec-path "$mvtec_path" --category "$category"
python json/splitData.py --mvtec-path "$mvtec_path" --category "$category" --ratio $ratio 

# Navigate up one level
cd /liujinxin/code/models/PSALM 

# Remove and recreate the 'datum' directory
rm -rf datum
mkdir datum
cd datum

# Execute the datum commands with the category argument
datum project create
datum project import --format mvtec_segmentation "$mvtec_path"/"$category"
datum project export -f coco -o output

# Navigate to the scripts directory and execute the remaining python scripts
cd /liujinxin/code/models/PSALM/scripts
python img/moveImgFolder.py --mvtec-path "$mvtec_path" --category "$category"
python json/modifyBothJson.py --category "$category" 
python img/createGoodMask.py --mvtec-path "$mvtec_path" --category "$category"
python img/moveAllToCoco.py --mvtec-path "$mvtec_path" --category "$category" 

# Convert all the images to RGB mode
python img/turnLtoRGB.py --category "$category"

python img/copySemanticMask.py --category "$category"
# python prepare_coco_semantic_annos_from_panoptic_annos.py --category "$category" 