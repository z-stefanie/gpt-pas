#!/bin/bash

# Set the parent directory containing the subfolders
original_mvtec_path="PATH_TO_MVTEC"
mvtec_path="PATH_TO_SAVE_FOLDER"
ratio=0.8

# Check if the folder exists
if [ -d "$mvtec_path" ]; then
    # Remove the folder and its contents
    rm -rf "$mvtec_path"
fi

# Create the folder again
mkdir -p "$mvtec_path"

echo "Folder $mvtec_path has been deleted and recreated."

cp -r "$original_mvtec_path"/* "$mvtec_path"

echo "Folder $mvtec_path has been copied"


# Initialize Mamba
source /root/miniforge3/etc/profile.d/conda.sh # Modify to your conda file 

# Activate the mamba environment
# mamba init
conda activate psalm

coco_path="xxxxx/datasets/coco_all"
datasets_path="xxxx/datasets"

# Check if the folder exists
if [ -d "$coco_path" ]; then
    # Remove the folder and its contents
    rm -rf "$coco_path"
fi

# Create the folder again
mkdir -p "$coco_path"

echo "Folder $coco_path has been deleted and recreated."

# Iterate over each folder in the parent directory
for dir in "$mvtec_path"/*; do
    if [ -d "$dir" ]; then
        # Get the folder name and assign it to the variable 'category'
        category=$(basename "$dir")

        cd PATH_TO_SCRIPTS_FOLDER
        
        # Execute the python scripts with the category argument
        python img/moveImg.py --mvtec-path "$mvtec_path" --category "$category"
        python json/splitData.py --mvtec-path "$mvtec_path" --category "$category" --ratio $ratio 
        # python json/splitData.py --mvtec-path "$mvtec_path" --category "$category"
        
        # Navigate up one level
        cd PATH_TO_PSALM_FOLDER 
        
        # Remove and recreate the 'datum' directory
        rm -rf datum
        mkdir datum
        cd datum
        
        # Execute the datum commands with the category argument
        datum project create
        datum project import --format mvtec_segmentation "$mvtec_path"/"$category"
        datum project export -f coco -o output
        
        # Navigate to the scripts directory and execute the remaining python scripts
        cd /liujinxin/code/models/scripts
        python img/moveImgFolder.py --mvtec-path "$mvtec_path" --category "$category"
        python json/modifyBothJson.py --category "$category" 
        python img/createGoodMask.py --mvtec-path "$mvtec_path" --category "$category"
        python img/moveAllToCoco.py --mvtec-path "$mvtec_path" --category "$category" 

        # Convert all the images to RGB mode
        python img/turnLtoRGB.py --category "$category"

        python img/copySemanticMask.py --category "$category"
        # python prepare_coco_semantic_annos_from_panoptic_annos.py --category "$category" 
    fi
done
