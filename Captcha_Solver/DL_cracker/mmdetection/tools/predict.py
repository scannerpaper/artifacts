import os
from random import shuffle

import mmcv
from mmcv.cnn import fuse_conv_bn
from mmcv.runner import load_checkpoint
from mmdet.apis.test import single_gpu_test
from mmdet.models import build_detector
from mmdet.datasets import build_dataset, build_dataloader, replace_ImageToTensor
from mmdet.utils import build_dp, compat_cfg, replace_cfg_vals, update_data_root, setup_multi_processes

from tqdm import tqdm


def create_dataset(img_path_src, test_json):
    os.makedirs('.tmp/data', exist_ok=True)
    img_path_tgt = '.tmp/data/images'
    if os.path.exists(img_path_tgt):
        os.remove(img_path_tgt)
    os.symlink(os.path.abspath(img_path_src), img_path_tgt)
    
    images = []
    print('Creating COCO-formatted dataset')
    for i, filename in enumerate(tqdm(os.listdir(img_path_tgt))):
        img = mmcv.imread(os.path.join(img_path_tgt, filename))
        img_info = {
            'id': i,
            'width': img.shape[1],
            'height': img.shape[0],
            'file_name': filename
        }
        images.append(img_info)

    coco_test = mmcv.load(test_json)
    coco = {
        'images': images,
        'annotations': [],
        'categories': coco_test['categories']
    }
    mmcv.dump(coco, '.tmp/data/test.json')


if __name__ == '__main__':
    test_json = 'data/coco/annotations/val.json'
    img_path = 'data/coco/images/val'
    create_dataset(img_path, test_json)

    config_file = 'custom/yolox_captcha_config.py'
    cfg = mmcv.Config.fromfile(config_file)
    cfg = replace_cfg_vals(cfg)
    update_data_root(cfg)
    cfg = compat_cfg(cfg)
    setup_multi_processes(cfg)

    ckpt = 'checkpoints/yolox_captcha.pth'
    device = 'cuda'
    cfg.model.train_cfg = None
    model = build_detector(cfg.model)
    checkpoint = load_checkpoint(model, ckpt, 'cpu')
    # model = fuse_conv_bn(model)
    model.CLASSES = checkpoint['meta']['CLASSES']
    model = build_dp(model, device)

    cfg.data.test['ann_file'] = '.tmp/data/test.json'
    cfg.data.test['img_prefix'] = '.tmp/data/images/'
    cfg.data.test.test_mode = True
    cfg.data.test.pipeline = replace_ImageToTensor(cfg.data.test.pipeline)
    dataset = build_dataset(cfg.data.test)
    import ipdb; ipdb.set_trace()
    data_loader = build_dataloader(
        dataset=dataset,
        samples_per_gpu=32,
        workers_per_gpu=16,
        dist=False,
        shuffle=False
    )

    outputs = single_gpu_test(model, data_loader)