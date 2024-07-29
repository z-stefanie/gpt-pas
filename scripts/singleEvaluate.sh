#!/bin/bash

# coco_path="/liujinxin/code/models/PSALM/datasets/coco_all
coco_path=$1
category=$2
model_path=$3
epoch=$4
lr=$5

source /root/miniforge3/etc/profile.d/conda.sh
# Activate the mamba environment
# mamba init
conda activate psalm

# Switch to PSALM to satisfy the relative path
cd /liujinxin/code/models/PSALM/

python psalm/eval/panoptic_segmentation.py --image_folder ${coco_path}/${category}/val2017 --model_path ${model_path}/${category}_epoch${epoch} --json_path ${coco_path}/${category} --output_folder ${category}_epoch${epoch}

# category="pill"
# coco_path="/liujinxin/code/models/PSALM/datasets/coco_all"
# python psalm/eval/panoptic_segmentation.py --image_folder ${coco_path}/${category}/val2017 --model_path /liujinxin/code/models/PSALM/checkpoint/PSALM_normal_vision_background --json_path ${coco_path}/${category}