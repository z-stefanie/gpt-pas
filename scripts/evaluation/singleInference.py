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

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        fcntl.flock(file, fcntl.LOCK_SH)
        data = json.load(file)
        fcntl.flock(file, fcntl.LOCK_UN)
    return data

def write_json_file(file_path, data):
    with open(file_path, 'w') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        json.dump(data, file, indent=4)
        fcntl.flock(file, fcntl.LOCK_UN)

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
    folder_path = os.path.join('/liujinxin/code/models/PSALM/outputImg',args.category)
    # 获取顶级文件夹下所有子文件夹中的图片文件路径
    image_classes = list_image_paths(folder_path)

    # 获取scores
    scores = scores_map(image_classes)
    # scores = s_map(image_classes)

    # test_imgs, scores, gt_mask_list = specify_resolution(test_imgs, scores, gt_mask_list, resolution=(resolution, resolution))；在eval_utils.py中
    # scores, gt_mask_list = specify_resolution(scores, gt_mask_list, resolution=(kwargs['resolution'], kwargs['resolution']))
    result_dict = metric_cal(np.array(scores), gt_list, gt_mask_list, cal_pro=kwargs['cal_pro'])

    # 打印结果
    print('result_dict:', result_dict)
    
    # 创建.txt，存储结果
    json_path = '/liujinxin/code/models/PSALM/outputJson/result.json'
    
    # Check if the file exists
    if not os.path.exists(json_path):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

    data = read_json_file(json_path)
    data[args.category] = result_dict 
    
    # 将结果字符串写入文本文件
    write_json_file(json_path,data)
    # 返回结果字典
    return result_dict

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")
    
def get_args():
    parser = argparse.ArgumentParser(description='Anomaly detection')
    parser.add_argument('--dataset', type=str, default='mvtec', choices=['mvtec', 'visa'])
    parser.add_argument("--category", required=True, help="The category value")

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