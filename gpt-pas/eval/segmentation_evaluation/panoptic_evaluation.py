from pycocotools.cocoeval import COCOeval
from pycocotools import mask
from tabulate import tabulate
import os
import logging
import io
import numpy as np
import detectron2.utils.comm as comm
from detectron2.config import CfgNode
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.data.datasets.coco import convert_to_coco_json
from detectron2.evaluation.coco_evaluation import COCOEvaluator, _evaluate_predictions_on_coco
from detectron2.evaluation import COCOPanopticEvaluator,SemSegEvaluator
from detectron2.evaluation.fast_eval_api import COCOeval_opt
from detectron2.structures import Boxes, BoxMode, pairwise_iou, PolygonMasks, RotatedBoxes
from detectron2.utils.file_io import PathManager
from typing import Optional
from detectron2.utils.logger import create_small_table
from iopath.common.file_io import file_lock
import shutil
from tqdm import tqdm
from PIL import Image
logger = logging.getLogger(__name__)
import torch
from typing import Optional, Union
import cv2
_CV2_IMPORTED = True
def load_image_into_numpy_array(
    filename: str,
    copy: bool = False,
    dtype: Optional[Union[np.dtype, str]] = None,
) -> np.ndarray:
    with PathManager.open(filename, "rb") as f:
        array = np.array(Image.open(f), copy=copy, dtype=dtype)
    return array
class my_SemSegEvaluator(SemSegEvaluator):
    """
    Evaluate semantic segmentation metrics.
    """

    def __init__(
        self,
        dataset_name,
        distributed=True,
        output_dir=None,
        *,
        sem_seg_loading_fn=load_image_into_numpy_array,
        num_classes=None,
        ignore_label=None,
        dataset_id_to_cont_id=None,
        class_name=None
    ):
        """
        Args:
            dataset_name (str): name of the dataset to be evaluated.
            distributed (bool): if True, will collect results from all ranks for evaluation.
                Otherwise, will evaluate the results in the current process.
            output_dir (str): an output directory to dump results.
            sem_seg_loading_fn: function to read sem seg file and load into numpy array.
                Default provided, but projects can customize.
            num_classes, ignore_label: deprecated argument
        """
        self._logger = logging.getLogger(__name__)
        if num_classes is not None:
            self._logger.warn(
                "SemSegEvaluator(num_classes) is deprecated! It should be obtained from metadata."
            )
        if ignore_label is not None:
            self._logger.warn(
                "SemSegEvaluator(ignore_label) is deprecated! It should be obtained from metadata."
            )
        self._dataset_name = dataset_name
        self._distributed = distributed
        self._output_dir = output_dir

        self._cpu_device = torch.device("cpu")


        # self.input_file_to_gt_file = {
        #     dataset_record["file_name"]: dataset_record["sem_seg_file_name"]
        #     for dataset_record in DatasetCatalog.get(dataset_name)
        # }

        # meta = MetadataCatalog.get(dataset_name)
        # Dict that maps contiguous training ids to COCO category ids
        try:
            c2d = dataset_id_to_cont_id
            self._contiguous_id_to_dataset_id = {v: k for k, v in c2d.items()}
        except AttributeError:
            self._contiguous_id_to_dataset_id = None
        self._class_names = class_name
        self.sem_seg_loading_fn = sem_seg_loading_fn
        self._num_classes = len(class_name)
        if num_classes is not None:
            assert self._num_classes == num_classes, f"{self._num_classes} != {num_classes}"
        self._ignore_label = ignore_label

        # This is because cv2.erode did not work for int datatype. Only works for uint8.
        self._compute_boundary_iou = True
        if not _CV2_IMPORTED:
            self._compute_boundary_iou = False
            self._logger.warn(
                """Boundary IoU calculation requires OpenCV. B-IoU metrics are
                not going to be computed because OpenCV is not available to import."""
            )
        if self._num_classes >= np.iinfo(np.uint8).max:
            self._compute_boundary_iou = False
            self._logger.warn(
                f"""SemSegEvaluator(num_classes) is more than supported value for Boundary IoU calculation!
                B-IoU metrics are not going to be computed. Max allowed value (exclusive)
                for num_classes for calculating Boundary IoU is {np.iinfo(np.uint8).max}.
                The number of classes of dataset {self._dataset_name} is {self._num_classes}"""
            )
    def process(self, inputs, outputs):
        """
        Args:
            inputs: the inputs to a model.
                It is a list of dicts. Each dict corresponds to an image and
                contains keys like "height", "width", "file_name".
            outputs: the outputs of a model. It is either list of semantic segmentation predictions
                (Tensor [H, W]) or list of dicts with key "sem_seg" that contains semantic
                segmentation prediction in the same format.
        """
        for input, output in zip(inputs, outputs):
            output = output["sem_seg"].argmax(dim=0).to(self._cpu_device)
            pred = np.array(output, dtype=int)
            gt_filename = input["sem_seg_file_name"]
            gt = self.sem_seg_loading_fn(gt_filename, dtype=int)

            gt[gt == self._ignore_label] = self._num_classes

            self._conf_matrix += np.bincount(
                (self._num_classes + 1) * pred.reshape(-1) + gt.reshape(-1),
                minlength=self._conf_matrix.size,
            ).reshape(self._conf_matrix.shape)

            if self._compute_boundary_iou:
                b_gt = self._mask_to_boundary(gt.astype(np.uint8))
                b_pred = self._mask_to_boundary(pred.astype(np.uint8))

                self._b_conf_matrix += np.bincount(
                    (self._num_classes + 1) * b_pred.reshape(-1) + b_gt.reshape(-1),
                    minlength=self._conf_matrix.size,
                ).reshape(self._conf_matrix.shape)

            self._predictions.extend(self.encode_json_sem_seg(pred, input["file_name"]))
class my_coco_panoptic_evaluator(COCOPanopticEvaluator):
    """
    Evaluate Panoptic Quality metrics on COCO using PanopticAPI.
    It saves panoptic segmentation prediction in `output_dir`

    It contains a synchronize call and has to be called from all workers.
    """

    def __init__(self, dataset_name, output_dir = None, dataset_id_to_cont_id = None, is_thing_list = None):
        """
        Args:
            dataset_name: name of the dataset
            output_dir: output directory to save results for evaluation.
        """
        assert dataset_id_to_cont_id is not None, 'need to give dataset_id_to_cont_id'
        assert is_thing_list is not None, 'need to give is_thing_list'
        self._metadata = MetadataCatalog.get(dataset_name)
        self.is_thing_list = is_thing_list
        self._contiguous_id_to_dataset_id = {
            v: k for k, v in dataset_id_to_cont_id.items()
        }
        self._output_dir = output_dir
        if self._output_dir is not None:
            PathManager.mkdirs(self._output_dir)

    def _convert_category_id(self, segment_info):
        isthing = segment_info.pop("isthing", None)
        segment_info["category_id"] = self._contiguous_id_to_dataset_id[
            segment_info["category_id"]
        ]
        return segment_info
    def process(self, inputs, outputs,output_folder):
        from panopticapi.utils import id2rgb

        for input, output in zip(inputs, outputs):
            panoptic_img, segments_info = output["panoptic_seg"]
            panoptic_img = panoptic_img.cpu().numpy()
            if segments_info is None:
                # If "segments_info" is None, we assume "panoptic_img" is a
                # H*W int32 image storing the panoptic_id in the format of
                # category_id * label_divisor + instance_id. We reserve -1 for
                # VOID label, and add 1 to panoptic_img since the official
                # evaluation script uses 0 for VOID label.
                label_divisor = 1000
                segments_info = []
                for panoptic_label in np.unique(panoptic_img):
                    if panoptic_label == -1:
                        # VOID region.
                        continue
                    pred_class = panoptic_label // label_divisor
                    isthing = self.is_thing_list[pred_class]
                    segments_info.append(
                        {
                            "id": int(panoptic_label) + 1,
                            "category_id": int(pred_class),
                            "isthing": bool(isthing),
                        }
                    )
                # Official evaluation script uses 0 for VOID label.
                panoptic_img += 1

            file_name = os.path.basename(input["file_name"])
            file_name_png = os.path.splitext(file_name)[0] + ".png"


            def extract_last_parts(path):
                parts = path.split('/')
                last_two_parts = '/'.join(parts[-2:])
                last_folder_paths = '/'.join(parts[-2:-1])
                return last_folder_paths,last_two_parts
            output_dir = '/liujinxin/code/models/PSALM/outputImg'
            output_quality_folder_path,output_file_name = extract_last_parts(input["file_name"])
            
            os.makedirs(os.path.join(output_dir,output_folder,output_quality_folder_path), exist_ok=True)

            def id2color(id_map, segments_info):
                # Define the colors
                red = np.array([255, 0, 0], dtype=np.uint8)
                white = np.array([255, 255, 255], dtype=np.uint8)
                black = np.array([0, 0, 0], dtype=np.uint8)
                
                # Create a dictionary mapping id to category_id
                id_to_category = {segment['id']: segment['category_id'] for segment in segments_info}

                # Create the output RGB map initialized to red (for category 0)
                rgb_map = np.full((*id_map.shape, 3), red, dtype=np.uint8)

                # Create a mask for pixels that have ids in id_to_category
                id_mask = np.isin(id_map, list(id_to_category.keys()))

                # Set the corresponding pixels in the RGB map
                for id_value, category in id_to_category.items():
                    category_mask = (id_map == id_value)
                    if category == 0:
                        rgb_map[category_mask] = white
                    elif category == 1:
                        rgb_map[category_mask] = black

                return rgb_map

            # print("output: ",output)
            # print("input: ",input)
            # if isinstance(panoptic_img, np.ndarray):
                # print("yessssss!")
            print("panoptic_img",panoptic_img)
            print("segments_info: ",segments_info)

            with io.BytesIO() as out:
                Image.fromarray(id2rgb(panoptic_img)).save(out, format="PNG")
                # Convert the panoptic image to RGB and save it directly to the specified folder
                output_path = os.path.join(output_dir,output_folder,output_file_name)
                Image.fromarray(id2color(panoptic_img,segments_info)).save(output_path, format="PNG")

                segments_info = [self._convert_category_id(x) for x in segments_info]
                self._predictions.append(
                    {
                        "image_id": input["image_id"],
                        "file_name": file_name_png,
                        "png_string": out.getvalue(),
                        "segments_info": segments_info,
                    }
                )

