import cv2
from PIL import Image
import numpy as np

# Read the image
# image_path = '/liujinxin/code/models/PSALM/datasets/coco_normal/panoptic_semseg_train2017/pill/defective/3.png'  # Replace with the actual path to your image
image_path = '/liujinxin/code/models/PSALM/datasets/coco_normal/panoptic_train2017/pill/defective/3.png'  # Replace with the actual path to your image
image = Image.open(image_path)
image_np = np.array(image)

# Check if the image was successfully loaded
if image is not None:
    # Get the shape of the image
    print(f"Image.mode: {image.mode}")
    print(f"Image.size: {image_np.shape}")
else:
    print("Failed to load the image.")
