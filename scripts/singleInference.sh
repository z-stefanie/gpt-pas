#!/bin/bash

output_path="/liujinxin/code/models/PSALM/outputImg"

# Initialize Mamba
source /root/miniforge3/etc/profile.d/conda.sh

# Activate the mamba environment
conda activate psalm

# Switch to PSALM to satisfy the relative path
cd /liujinxin/code/models/PSALM/scripts/evaluation

output_json_path=$1
error_log_path=$2
category=$3
epoch=$4
lr=$5
threshold=$6



python inference.py --output_json_path ${output_json_path} --error_log_path ${error_log_path} --category ${category} --epoch ${epoch} --threshold ${threshold} &

# Wait for all background processes to finish
wait

echo "$category processes completed."