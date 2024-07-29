#!/bin/bash

output_img_path="xxxxx/outputImg"
output_json_path="xxxx/outputJson/result.json"
error_path="xxxx/outputJson/error.json"
# Initialize Mamba
source /root/miniforge3/etc/profile.d/conda.sh # Modify to your conda file 

# Activate the mamba environment
conda activate psalm

# Switch to PSALM to satisfy the relative path
cd xxxx/scripts

# categories=("capsule" "grid" "leather" "screw" "zipper" "transistor" "toothbrush")
# categories=("transistor" "leather" "screw" "zipper" "transistor" "toothbrush")
# categories=("capsule")

for dir in "$output_img_path"/*; do
    if [ -d "$dir" ]; then
        category=$(basename "$dir")
        # python inference.py --category ${category} &
        categories+=("$category")  # Append the category to the array
        # bash singleInference.sh "$category" "$threshold" & 
    fi
done

epochs=()

# Loop from 5 to 20 and add each number to the array
for ((i=11; i<=30; i=i+3)); do
    epochs+=("$i")
done

lrs=("6e-5")

thresholds=('128')

for category in "${categories[@]}"; do
    for epoch in "${epochs[@]}"; do
        for lr in "${lrs[@]}"; do 
            for threshold in "${thresholds[@]}"; do 
                bash singleInference.sh "$output_json_path" "$error_path" "$category" "$epoch" "$lr" "$threshold" & 
            done
        done
    done
done

# Wait for all background processes to finish
wait

echo "All processes completed."

