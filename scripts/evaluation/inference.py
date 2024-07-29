import argparse
from imgdatasets import *
# from imgdatasets import dataset_classes
# from utils.csv_utils import *
from utils.metrics import *
# from utils.training_utils import *
# from WinCLIP import *
from utils.eval_utils import *
from skimage.segmentation import slic
from utils.abc import list_image_paths,scores_map
# from scripts.evaluation.utils.abc import list_image_paths,scores_map
# from abc import list
import json
import fcntl
from datetime import datetime

def read_json_file(file_path):

    if not os.path.exists(file_path):
        # Create the file if it doesn't exist
        with open(file_path, 'w') as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            json.dump({}, file)
            fcntl.flock(file, fcntl.LOCK_UN)

    # Read the file's content
    with open(file_path, 'r') as file:
        fcntl.flock(file, fcntl.LOCK_SH)
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = []
        fcntl.flock(file, fcntl.LOCK_UN)

    return data

def write_json_file(file_path, data):
    with open(file_path, 'w') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        json.dump(data, file, indent=4)
        fcntl.flock(file, fcntl.LOCK_UN)

def convert_to_serializable(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    else:
        return obj


def main(args):
    kwargs = vars(args)
    
    if kwargs['use_cpu'] == 0:
        device = f"cuda:0"
        # device = f"cpu"
    else:
        device = f"cpu"
        # device = f"cuda:0"
    kwargs['device'] = device

    scores = []
    test_imgs = []
    gt_list = []
    gt_mask_list = []
    names = []

    # get the test dataloader
    test_dataloader, test_dataset_inst = get_dataloader_from_args(phase='test', perturbed=False, **kwargs)
    
    for (data, mask, label, name, img_type) in test_dataloader:

        # data = [model.transform(Image.fromarray(f.numpy())) for f in data]
        # print('data.shape_1:', data.shape)
        # data = torch.stack(data, dim=0)
        # print('data.shape_2:', data.shape)
        
        for d, n, l, m in zip(data, name, label, mask):
            
            # test_imgs += [denormalization(d.cpu().numpy())]
            
            l = l.numpy()
            m = m.numpy()
            m[m > 0] = 1
            
            names += [n]
            gt_list += [l]
            gt_mask_list += [m]

        # data = data.to(device)
        # score = model(data) # score是列表[]
        # scores += score
    # 实现
    
    # 指定要遍历的顶级文件夹路径
    folder_path = os.path.join('/liujinxin/code/models/PSALM/outputImg',f'{args.category}_epoch{args.epoch}')
    # 获取顶级文件夹下所有子文件夹中的图片文件路径
    image_classes = list_image_paths(folder_path)

    # 获取scores
    scores = scores_map(image_classes,args.threshold)
    # scores = s_map(image_classes)

    # test_imgs, scores, gt_mask_list = specify_resolution(test_imgs, scores, gt_mask_list, resolution=(resolution, resolution))；在eval_utils.py中
    # scores, gt_mask_list = specify_resolution(scores, gt_mask_list, resolution=(kwargs['resolution'], kwargs['resolution']))


     # Check if the file exists
    if not os.path.exists(args.output_json_path):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(args.error_log_path), exist_ok=True)

     # Check if the file exists
    if not os.path.exists(args.output_json_path):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(args.output_json_path), exist_ok=True)

    try:
        result_dict = metric_cal(np.array(scores), gt_list, gt_mask_list, cal_pro=kwargs['cal_pro'])
    except Exception as e:
        print(f"An error occurred: {e}")
        # Get the current date and time
        now = datetime.now()
        readable_time = now.strftime("%Y-%m-%d %H:%M:%S")
        log_data = {
            "category": args.category,
            "error": str(e),
            'time': readable_time
        }
        log_entries = read_json_file(args.error_log_path)
        # Append the new log entry
        attribute_name = f'{args.category}_epoch{args.epoch}'
        log_entries[attribute_name] = log_data 

        # Write the updated log entries back to the file
        # with open(args.error_log_path, 'w') as log_file:
        #     json.dump(log_entries, log_file, indent=4)
        # return
        write_json_file(args.error_log_path,log_entries)

    # 打印结果
    result_dict = convert_to_serializable(result_dict)
    print('result_dict:', result_dict)
    
    data = read_json_file(args.output_json_path)
    attribute_name = f'{args.category}_epoch{args.epoch}'
    data[attribute_name] = result_dict 
    
    # 将结果字符串写入文本文件
    write_json_file(args.output_json_path,data)
    # 返回结果字典
    return result_dict

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")
    
def get_args():
    parser = argparse.ArgumentParser(description='Anomaly detection')
    parser.add_argument('--dataset', type=str, default='mvtec', choices=['mvtec', 'visa'])
    parser.add_argument("--category", required=True, help="The category value")
    parser.add_argument("--threshold", required=False,default=128,type=int,help="The threshold")
    parser.add_argument("--epoch", required=False,default=10,type=int,help="The epoch")
    parser.add_argument("--output_json_path", required=True,type=str,help="The file of the result")
    parser.add_argument("--error_log_path", required=True,type=str,help="The file of the error log")

    # parser.add_argument('--img-resize', type=int, default=240)
    # parser.add_argument('--img-cropsize', type=int, default=240)
    # parser.add_argument('--resolution', type=int, default=400)

    parser.add_argument('--batch-size', type=int, default=128)
    # parser.add_argument('--vis', type=str2bool, choices=[True, False], default=True)
    # parser.add_argument("--root-dir", type=str, default="./result_winclip")
    # parser.add_argument("--load-memory", type=str2bool, default=True)
    parser.add_argument("--cal-pro", type=str2bool, default=True)
    parser.add_argument("--experiment_indx", type=int, default=0)
    parser.add_argument("--gpu-id", type=int, default=0)

    # pure test
    parser.add_argument("--pure-test", type=str2bool, default=False)

    # method related parameters
    parser.add_argument('--k-shot', type=int, default=0)
    parser.add_argument('--scales', nargs='+', type=int, default=(2, 3, ))
    parser.add_argument("--backbone", type=str, default="ViT-B-16-plus-240",
                        choices=['ViT-B-16-plus-240'])
    parser.add_argument("--pretrained_dataset", type=str, default="laion400m_e32")

    parser.add_argument("--use-cpu", type=int, default=0)
    

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    import os

    args = get_args()
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['CUDA_VISIBLE_DEVICES'] = f"{args.gpu_id}"
    main(args)