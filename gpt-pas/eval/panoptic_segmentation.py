import argparse
import torch
import os
import json
from tqdm import tqdm
import shortuuid
from pycocotools import mask
import time
import numpy as np
import cv2
from psalm.constants import IGNORE_INDEX, IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, \
    DEFAULT_IM_END_TOKEN, DEFAULT_SEG_TOKEN, SEG_TOKEN_INDEX, CLS_TOKEN_INDEX
from psalm.conversation import conv_templates, SeparatorStyle
from psalm.model.builder import load_pretrained_model
from psalm.utils import disable_torch_init
from psalm.mm_utils import tokenizer_image_token, get_model_name_from_path, KeywordsStoppingCriteria
from psalm.eval.segmentation_evaluation.instance_evaluation import InstanceSegEvaluator, my_coco_evaluator
from psalm.eval.segmentation_evaluation.panoptic_evaluation import my_coco_panoptic_evaluator, my_SemSegEvaluator
from transformers import StoppingCriteria, StoppingCriteriaList

from torch.utils.data import Dataset, DataLoader

from psalm import conversation as conversation_lib
from psalm.model.datasets_mapper.coco_instance_mapper import COCOInstanceNewBaselineDatasetMapperForEval

from PIL import Image
import math
import copy
from detectron2.structures import BoxMode
from detectron2.evaluation import inference_on_dataset, COCOEvaluator
from detectron2.data import MetadataCatalog, DatasetCatalog

from typing import Dict, Optional, Sequence, List
from dataclasses import dataclass, field
from psalm.train.train_datasets import DataCollatorForCOCODatasetV2, COCO_panoptic_dataset

import transformers

@dataclass
class DataArguments:
    data_path: str = field(default=None,
                           metadata={"help": "Path to the training data."})
    lazy_preprocess: bool = False
    is_multimodal: bool = False
    image_folder: Optional[str] = field(default='/path/to/val2017')
    model_path: Optional[str] = field(default="/path/to/model")
    mask_config: Optional[str] = field(default="./psalm/mask_config/maskformer2_swin_base_384_bs16_50ep.yaml")
    image_aspect_ratio: str = 'square'
    image_grid_pinpoints: Optional[str] = field(default=None)
    json_path: str = '/path/to/coco'
    output_folder: str = "the folder of the results"
    model_map_name: str = 'psalm'
    version: str = 'llava_phi'
    output_dir: str = './output/panoptic_segmentation'
    segmentation: bool = True
    eval_batch_size: int = 1
    dataloader_num_workers: int = 4
    seg_task: Optional[str] = field(default="panoptic")

class StoppingCriteriaSub(StoppingCriteria):
    def __init__(self, stops=[], encounters=1):
        super().__init__()
        self.stops = stops

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor):
        last_token = input_ids[0][-1]
        for stop in self.stops:
            if stop == last_token:
                return True
        return False


def split_list(lst, n):
    """Split a list into n (roughly) equal-sized chunks"""
    chunk_size = math.ceil(len(lst) / n)  # integer division
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def get_chunk(lst, n, k):
    chunks = split_list(lst, n)
    return chunks[k]


def evaluation():
    parser = transformers.HfArgumentParser(DataArguments)
    data_args = parser.parse_args_into_dataclasses()[0]
    disable_torch_init()
    model_path = os.path.expanduser(data_args.model_path)
    model_name = get_model_name_from_path(model_path)
    tokenizer, model, image_processor, context_len = load_pretrained_model(model_path, None, model_name,mask_config=data_args.mask_config,model_args=data_args)
    data_args.image_processor = image_processor
    data_args.is_multimodal = True

    conversation_lib.default_conversation = conversation_lib.conv_templates[data_args.version]
    eval_dataset = COCO_panoptic_dataset(json_path=data_args.json_path, tokenizer=tokenizer,
                                                                    data_args=data_args, is_train=False)

    data_collator = DataCollatorForCOCODatasetV2(tokenizer=tokenizer)
    dataloader_params = {
        "batch_size": data_args.eval_batch_size,
        "num_workers": data_args.dataloader_num_workers,
    }
    eval_dataloader = DataLoader(eval_dataset, batch_size=dataloader_params['batch_size'], collate_fn=data_collator,
                                 num_workers=dataloader_params['num_workers'])

    def load_instruction_dataset():
        return eval_dataset

    DatasetCatalog.register('instruction_dataset', load_instruction_dataset)
    MetadataCatalog.get('instruction_dataset').set(panoptic_json=eval_dataset.panoptic_json_path,
                                                   panoptic_root=eval_dataset.panoptic_gt_path)

    evaluator = my_coco_panoptic_evaluator('instruction_dataset',
                                  output_dir=data_args.output_dir, dataset_id_to_cont_id=eval_dataset.coco_id_to_cont_id, is_thing_list=eval_dataset.coco_is_thing)
    # sem_evaluator = my_SemSegEvaluator('instruction_dataset',
                                #   output_dir=data_args.output_dir, dataset_id_to_cont_id=eval_dataset.coco_id_to_cont_id, class_name=eval_dataset.coco_class_name[:-1],ignore_label=255)
    evaluator.reset()
    # sem_evaluator.reset()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # print(model)
    # Freeze mm_projector parameters
    for param in model.get_model().mm_projector.parameters():
        param.requires_grad = False

    # Freeze vision_tower parameters
    for param in model.get_model().vision_tower.parameters():
        param.requires_grad = False     
    model.to(dtype=torch.float32, device=device).eval()
    
    with torch.no_grad():
        for idx, inputs in tqdm(enumerate(eval_dataloader), total=len(eval_dataloader)):
            inputs = {k: v.to(device) if torch.is_tensor(v) else v for k, v in inputs.items()}
            outputs = model.eval_seg(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                images=inputs['images'].float(),
                seg_info=inputs['seg_info'],
                class_name_embedding_indices=inputs['class_name_embedding_indices'],
                class_name_ids=inputs['class_name_ids'],
                cls_indices=inputs['cls_indices'],
                labels=inputs['labels'],
                is_thing_list=eval_dataset.coco_is_thing
            )
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            # print(outputs)
            # time.sleep(10) 
            evaluator.process(inputs['seg_info'], outputs,data_args.output_folder)
            # sem_evaluator.process(inputs['seg_info'], outputs)

    results = evaluator.evaluate()
    # sem_results = sem_evaluator.evaluate()
    print(results)
    # print(sem_results)

    if results is None:
        results = {}
    return results


def intersectionAndUnionGPU(output, target, K, ignore_index=255):
    # 'K' classes, output and target sizes are N or N * L or N * H * W, each value in range 0 to K - 1.
    assert output.dim() in [1, 2, 3]
    assert output.shape == target.shape
    output = output.view(-1)
    target = target.view(-1)
    output[target == ignore_index] = ignore_index
    intersection = output[output == target]
    area_intersection = torch.histc(intersection, bins=K, min=0, max=K - 1)
    area_output = torch.histc(output, bins=K, min=0, max=K - 1)
    area_target = torch.histc(target, bins=K, min=0, max=K - 1)
    area_union = area_output + area_target - area_intersection
    return area_intersection, area_union, area_target

if __name__ == "__main__":
    evaluation()

