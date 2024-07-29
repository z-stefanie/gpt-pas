#!/bin/bash

coco_path="xxxxxx/datasets/coco_all"
export DISABLE_ADDMM_CUDA_LT=1

# Initialize Mamba
source /root/miniforge3/etc/profile.d/conda.sh # Modify to your conda file 

# Activate the mamba environment
# mamba init
conda activate psalm

# Switch to PSALM to satisfy the relative path
cd xxxx/scripts

# Parameter1
# categories=("capsule" "grid" "leather" "screw" "zipper" "transistor" "toothbrush")

# Iterate over the directories in the specified path
for dir in "$coco_path"/*; do
    if [ -d "$dir" ]; then
        category=$(basename "$dir")
        categories+=("$category")  # Append the category to the array
    fi
done

# Parameter2
epochs=()

# Loop from 5 to 20 and add each number to the array
for ((i=11; i<=30; i=i+3)); do
    epochs+=("$i")
done

# Parameter3
lrs=("6e-5")

for category in "${categories[@]}"; do
    for epoch in "${epochs[@]}"; do
        for lr in "${lrs[@]}"; do 
            bash singleFinetune.sh "$category" "$epoch" "$lr"
        done 
    done
done
