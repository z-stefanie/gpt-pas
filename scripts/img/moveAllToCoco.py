import shutil
import os
import argparse

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Retrieve category and MVTec path from command line")
    parser.add_argument("--category", required=True, help="The category value")
    parser.add_argument("--mvtec-path", required=True, help="The path to the MVTec dataset")
    args = parser.parse_args()

    datumPath = '/liujinxin/code/models/PSALM/datum/output/annotations'
    cocoPath = os.path.join('/liujinxin/code/models/PSALM/datasets/coco_all',args.category)
    annotationPath = os.path.join(cocoPath,'annotations')
    mvtecPath = os.path.join(args.mvtec_path,args.category)

    # Create the folder
    os.makedirs(cocoPath, exist_ok=True)
    os.makedirs(annotationPath, exist_ok=True)

    #Move the json
    shutil.move(os.path.join(datumPath,'labels_train.json'),os.path.join(annotationPath,'panoptic_train2017.json'))
    shutil.move(os.path.join(datumPath,'labels_test.json'),os.path.join(annotationPath,'panoptic_val2017.json'))

    # Move the input image
    
    shutil.move(os.path.join(mvtecPath,'train'),os.path.join(cocoPath,'train2017'))
    shutil.move(os.path.join(mvtecPath,'test'),os.path.join(cocoPath,'val2017'))
    
    # Move the ground_truth mask
    shutil.move(os.path.join(mvtecPath,'ground_truth'),os.path.join(cocoPath,'panoptic_val2017'))
    shutil.move(os.path.join(mvtecPath,'panoptic_train2017'),os.path.join(cocoPath,'panoptic_train2017'))

    