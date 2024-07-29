#!/bin/bash

coco_path="xxxxx/datasets/coco_all"
model_path="xxxxx/checkpoint_coco"

# Initialize Mamba
source /root/miniforge3/etc/profile.d/conda.sh # Modify to your conda file 

# Activate the mamba environment
conda activate psalm

# Switch to PSALM to satisfy the relative path
cd xxxxx/scripts

# for dir in "$coco_path"/*; do
#     if [ -d "$dir" ]; then
#         category=$(basename "$dir")
#         # python eval/panoptic_segmentation.py --image_folder ${coco_path}/${category}/val2017 --model_path /liujinxin/code/models/checkpoint_all/${category}_epoch10 --json_path ${coco_path}/${category}
#         bash singleEvaluate.sh "$category" "$coco_path"
#     fi
# done

# categories=("capsule" "grid" "leather" "screw" "zipper" "transistor" "toothbrush")

# Iterate over the directories in the specified path
for dir in "$coco_path"/*; do
    if [ -d "$dir" ]; then
        category=$(basename "$dir")
        categories+=("$category")  # Append the category to the array
    fi
done

epochs=()

# Loop from 5 to 20 and add each number to the array
for ((i=11; i<=30; i=i+3)); do
    epochs+=("$i")
done

lrs=("6e-5")

for category in "${categories[@]}"; do
    for epoch in "${epochs[@]}"; do
        for lr in "${lrs[@]}"; do 
            bash singleEvaluate.sh "$coco_path" "$category" "$model_path" "$epoch" "$lr"
        done 
    done
done