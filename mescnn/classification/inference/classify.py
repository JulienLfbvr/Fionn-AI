import os
import numpy as np
import torch
from PIL import Image
import pandas as pd
import datetime as dt
import shutil

from mescnn.classification.gutils.utils import get_proper_device, str2bool
from mescnn.classification.inference.oxford import binarize, oxfordify
from mescnn.classification.inference.download import download_classifier
from mescnn.classification.inference.encoding import mesc_def
from mescnn.classification.inference.threshold import opt_thr
from mescnn.classification.inference.config import (GlomeruliTestConfig, GlomeruliTestConfig3,
                                                  GlomeruliTestConfigViT, GlomeruliTestConfigViT3)
from mescnn.classification.inference.paths import get_logs_path
from mescnn.definitions import ROOT_DIR


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Classifiers Inference for Glomeruli Task')
    parser.add_argument('-r', '--root-path', type=str, help='Root path', default=ROOT_DIR)
    parser.add_argument('-e', '--export-dir', type=str, help='Directory to export report', required=True)
    parser.add_argument('--netM', type=str, help='Network architecture for M lesion', required=True)
    parser.add_argument('--netE', type=str, help='Network architecture for E lesion', required=True)
    parser.add_argument('--netS', type=str, help='Network architecture for S lesion', required=True)
    parser.add_argument('--netC', type=str, help='Network architecture for C lesion', required=True)
    parser.add_argument('--vitM', type=str2bool, help='Use ViT for M lesion', default=False)
    parser.add_argument('--vitE', type=str2bool, help='Use ViT for E lesion', default=False)
    parser.add_argument('--vitS', type=str2bool, help='Use ViT for S lesion', default=False)
    parser.add_argument('--vitC', type=str2bool, help='Use ViT for C lesion', default=False)
    parser.add_argument('--tverM', type=str, help='Training version for M lesion', default="V3")
    parser.add_argument('--tverE', type=str, help='Training version for M lesion', default="V3")
    parser.add_argument('--tverS', type=str, help='Training version for M lesion', default="V3")
    parser.add_argument('--tverC', type=str, help='Training version for M lesion', default="V3")
    parser.add_argument('--path_wsi', type=str, help='Path to WSI', default=None)
    parser.add_argument('--img', type=str2bool, help='Use image', default=False)
    parser.add_argument('--filterM', type=str2bool, help='Use our model ', default=False)
    parser.add_argument('--filterE', type=str2bool, help='Use our model ', default=False)
    parser.add_argument('--filterS', type=str2bool, help='Use our model ', default=False)
    parser.add_argument('--filterC', type=str2bool, help='Use our model ', default=False)
    args = parser.parse_args()


    use_vit_dict = {
        "M": args.vitM,
        "E": args.vitE,
        "S": args.vitS,
        "C": args.vitC,
    }

    net_name_dict = {
        "M": args.netM,
        "E": args.netE,
        "S": args.netS,
        "C": args.netC,
    }

    tver_dict = {
        "M": args.tverM,
        "E": args.tverE,
        "S": args.tverS,
        "C": args.tverC,
    }
    
    use_our_models = {
        "M" : args.filterM,
        "E" : args.filterE,
        "S" : args.filterS,
        "C" : args.filterC,
    }
    
    print(use_our_models)

    criterion_pr = "min"
    root_path = args.root_path
    export_dir = args.export_dir

    mesc_log_dir = get_logs_path(root_path)
    report_dir = os.path.join(export_dir, "Report")
    # report_dir = os.path.join(export_dir, "Report", f"M-{args.netM}_E-{args.netE}_S-{args.netS}_C-{args.netC}")
    os.makedirs(report_dir, exist_ok=True)
    
    if args.img:
        crop_dir = ROOT_DIR
        wsi_ids = ["current-files"]
        name_img_ext = args.path_wsi.split('/')[2]
        name_img = name_img_ext.split('.')[0]
        
    else :
        crop_dir = os.path.join(export_dir, "Temp", "json2exp-output", "Crop-256")
        wsi_ids = os.listdir(crop_dir)

    logs_path = get_logs_path(ROOT_DIR)
    subdir = "test-res"

    wsi_dict = {
        'WSI-ID': [],
        'M-score': [],
        'E-score': [],
        'S-score': [],
        'C-score': [],
        'M-ratio': [],
        'E-ratio': [],
        'S-ratio': [],
        'C-ratio': [],
        'Date': [],
        'Size': [],
        'GGS-count': 0,
        'GGS-filename': []
    }

    output_file_score_csv = os.path.join(report_dir, "Oxford.csv")
    file_exists = os.path.exists(output_file_score_csv)
    

    for wsi_id in wsi_ids:
        if args.img:
            output_file_csv = os.path.join(export_dir, "Temp", f"{name_img}.csv")
        else : 
            output_file_csv = os.path.join(export_dir, "Temp", f"{wsi_id}.csv")
        prediction_dir = os.path.join(crop_dir, wsi_id)

        GGS_count = 0
        GGS_filename = []
        mesc_dict = {
            'filename': [],
            'M': [],
            'E': [],
            'S': [],
            'C': [],

            'M-bin': [],
            'E-bin': [],
            'S-bin': [],
            'C-bin': [],

            'M-prob': [],
            'E-prob': [],
            'S-prob': [],
            'C-prob': [],
        }

        # make a copy of the prediction_dir directory
        images_dir = os.path.join(crop_dir, "copy", wsi_id)
        shutil.copytree(prediction_dir, images_dir)
            
        for target in "SMEC":
            target_prob = f"{target}-prob"
            target_bin = f"{target}-bin"

            if use_vit_dict[target]:
                config = GlomeruliTestConfigViT() if target in ['E', 'C'] else GlomeruliTestConfigViT3()
                net_type = "vit"
            else:
                config = GlomeruliTestConfig() if target in ['E', 'C'] else GlomeruliTestConfig3()
                net_type = "cnn"

            net_fold = os.path.join(mesc_log_dir, net_type)
            net_name = net_name_dict[target]
            train_version = tver_dict[target]

            if use_our_models[target] : 
                net_path = os.path.join(net_fold, 'holdout', f'{net_name}_{target}_{train_version}_fine_tuned.pth')
            else : 
                net_path = os.path.join(net_fold, 'holdout', f'{net_name}_{target}_{train_version}.pth')
                
            if not os.path.exists(net_path):
                print(f"Path: {net_path} not found!")
                model_path = download_classifier(net_name, target, train_version, net_type, use_our_models[target])
                print(f"Downloaded: {model_path}")
            else:
                print(f"Path: {net_path} found!")
            net = torch.load(net_path)
            device = get_proper_device()

            net.eval()
            net = net.to(device)
              
            images_list = os.listdir(images_dir)
            images_list = [os.path.join(images_dir, f) for f in images_list if f.endswith(".jpeg")]

            if target in ['E', 'C']:
                threshold = opt_thr[net_type][target][train_version][net_name]
            else:
                threshold = None

            with torch.no_grad():
                for image_path in images_list:
                    image = Image.open(image_path)
                    image = config.transform(image)
                    image = torch.unsqueeze(image, 0)
                    image = image.to(device)
                    outputs = net(image)

                    if target in ['E', 'C']:
                        predictions = outputs[:, 1] > threshold
                    else:
                        _, predictions = torch.max(outputs, 1)

                    outputs = outputs.cpu().numpy()
                    prob_out = outputs[:, -1]
                    prob_out = 1 / (1 + np.exp(-prob_out))
                    int_pred = predictions.cpu().numpy().item()
                    label_pred = mesc_def[target][int_pred]
                    if label_pred in ['yesC', 'yesE', 'SGS']:
                        print(f"[lesion] label pred: {label_pred}")

                    # if label_pred == 'GGS' add to GGS count, add the filename to GGS_filename, remove the image from the prediction_dir and continue
                    if label_pred == 'GGS':
                        GGS_count += 1
                        # remove the copy from the image_path
                        GGS_filename.append(image_path.replace('/copy/', '/'))
                        os.remove(image_path)
                        continue
                    
                    if target == 'S':
                        mesc_dict['filename'].append(image_path)
                        
                    bin_int_pred = binarize(int_pred, target)
                    print(f"Image Path: {image_path}, threshold: {threshold}, "
                          f"output-pred: {int_pred:d}, binarized-output-pred: {bin_int_pred:d}, "
                          f"output-label: {label_pred}, "
                          f"prob_out: {prob_out.item():.5f}")

                    mesc_dict[target_bin].append(bin_int_pred)
                    mesc_dict[target].append(label_pred)
                    mesc_dict[target_prob].append(f"{prob_out.item():.5f}")
        # remove the copy directory
        copy_dir = os.path.join(crop_dir, "copy")
        shutil.rmtree(copy_dir)
        
        mesc_df = pd.DataFrame(data=mesc_dict)

        if args.img == False : 
            for target in "MESC":
                target_bin = f"{target}-bin"
                target_score = f"{target}-score"
                target_ratio = f"{target}-ratio"

                target_mean = np.mean(mesc_dict[target_bin])
                target_sum = np.sum(mesc_dict[target_bin])
                target_len = len(mesc_dict[target_bin])
                target_oxford = oxfordify(target_mean, target)

                if target == 'M':
                    wsi_dict['WSI-ID'].append(wsi_id)
                wsi_dict[target_score].append(target_oxford)
                wsi_dict[target_ratio].append(f"{target_sum} | {target_len}")
                if target == 'S':
                    wsi_dict['GGS-count'] = GGS_count
                    wsi_dict['GGS-filename'].append(GGS_filename)
                if target == 'C':
                    wsi_dict['Date'].append(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    wsi_dict["Size"].append(os.path.getsize(os.path.join(ROOT_DIR, args.path_wsi)))

        mesc_df.to_csv(output_file_csv, sep=';', index=False)

    if args.img == False :
        wsi_df = pd.DataFrame(data=wsi_dict)
        
        if file_exists:
            wsi_df.to_csv(output_file_score_csv, sep=';', index=False, mode='a', header=False)
        else:
            wsi_df.to_csv(output_file_score_csv, sep=';', index=False)