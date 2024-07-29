#!/bin/bash

source /root/miniforge3/etc/profile.d/conda.sh
# Activate the mamba environment
# mamba init
conda activate psalm

# Switch to PSALM to satisfy the relative path
cd /liujinxin/code/models/PSALM/

category=$1
epoch=$2
lr=$3
export DISABLE_ADDMM_CUDA_LT=1
    deepspeed psalm/train/finetune.py \
        --deepspeed ./scripts/zero2.json \
        --model_name_or_path "/liujinxin/code/models/PSALM/models/PSALM" \
        --version "llava_phi" \
        --panoptic_json_path "/liujinxin/code/models/PSALM/datasets/coco_all/${category}" \
        --image_folder "/liujinxin/code/models/PSALM/datasets/coco_all/${category}/train2017" \
        --mm_vision_select_layer -2 \
        --mm_use_im_start_end False \
        --mm_use_im_patch_token False \
        --fp16 True \
        --output_dir ./checkpoint_coco/${category}_epoch${epoch} \
        --num_train_epochs ${epoch} \
        --per_device_train_batch_size 4 \
        --per_device_eval_batch_size 2 \
        --gradient_accumulation_steps 1 \
        --evaluation_strategy "no" \
        --save_strategy "steps" \
        --save_steps 15000 \
        --save_total_limit 1 \
        --learning_rate ${lr} \
        --weight_decay 0. \
        --warmup_ratio 0.03 \
        --lr_scheduler_type "cosine" \
        --logging_steps 1 \
        --tf32 False \
        --model_max_length 2048 \
        --gradient_checkpointing True \
        --dataloader_num_workers 4 \
        --lazy_preprocess True \
        --report_to none \
        --seg_task 'panoptic'