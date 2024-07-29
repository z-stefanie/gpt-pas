import requests
from io import BytesIO
import numpy as np
import cv2
import os
import re
from skimage.segmentation import slic
from PIL import Image
import numpy as np


# 待修改
def list_image_paths(folder_path):
    image_paths_by_folder = {}
    # 遍历指定文件夹中的所有子文件夹
    subfolders = sorted(os.listdir(folder_path)) 
    for subfolder in subfolders:
        # Note: The AUROC is not the case where there is only one category
        # if subfolder == 'good': continue

        print("score_folder: ",subfolder) #To make sure the order is same

        subfolder_path = os.path.join(folder_path, subfolder)
        # 检查是否为文件夹
        if os.path.isdir(subfolder_path):
            # 在子文件夹中遍历所有文件
            subfolder_images = []
            for root, dirs, files in os.walk(subfolder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    subfolder_images.append(file_path)
            subfolder_images.sort()
            image_paths_by_folder[subfolder] = subfolder_images
            
    return image_paths_by_folder


def convert(image_path,threshold):
    # 读取图像
    # image_path = 'path_to_your_image.png'  # 替换为实际图像路径
    image = Image.open(image_path).convert('L')  # 将图像转换为灰度图
    
    # 将图像转换为NumPy数组
    image_array = np.array(image)
    
    # 将灰度值转换为二值化值（0 和 1）
    # Note: the grayscale value of red color is (255+0+0) / 3 = 85 < 128 -> 0 -> black -> good 
    # score_map = np.where(image_array > threshold, 1, 0)  # 阈值128可以调整
    score_map = np.where(image_array > 6, 1, 0)  # 阈值128可以调整
    
    # 确认转换结果
    # print(score_map)
    # print(score_map.shape)  # 应为 (800, 800)

    return score_map


# 读取每张图片并进行描述
def scores_map(image_classes,threshold):
    scores_map = []
    for subfolder, image_paths in image_classes.items():
        print(f"Subfolder: {subfolder}")
        for image_path in image_paths:
            # 从图片文件名中提取编号
            # match = re.match(r'(\d+)_superpixel_img_edge_number.png', os.path.basename(image_path))
            # if match:
                # image_id = match.group(1)
                
                # 获取图片所在的目录路径
            # output_directory = os.path.dirname(image_path)  
            # output_file_path = os.path.join(output_directory, f"{image_id}_superpixel_out.txt")
    
                # 进行像素映射
            score_map = convert(image_path,threshold)
            # print('score_map.shape:', score_map.shape)
                
            scores_map.append(score_map)
            # print('scores_map.length:', len(scores_map))

                # else:
                #     # 文件不为空，跳过这个循环，处理下一张图片
                #     print(f"文件 {output_file_path} 不为空，跳过当前图片。")
                #     continue
          
    # print('scores_map.length:', len(scores_map))
    return scores_map


if __name__ == '__main__':
    # 指定要遍历的顶级文件夹路径
    folder_path = '/root/autodl-tmp/mvtec-re/cable/test'
    # 获取顶级文件夹下所有子文件夹中的图片文件路径
    image_classes = list_image_paths(folder_path)
    
    scores_map(image_classes)

