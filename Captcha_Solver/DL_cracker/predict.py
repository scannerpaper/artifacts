from argparse import ArgumentParser
import os
import numpy as np
import mmcv
from mmdet.apis import init_detector, inference_detector
from tqdm import tqdm

def parse_args():
    parser = ArgumentParser(description="Predict all captcha images in a folder")
    parser.add_argument('--images-dir', help="Path to folder containing the images", required=True)
    parser.add_argument('--config', help="Path to config file", required=True)
    parser.add_argument('--checkpoint', help="Path to checkpoint file", required=True)
    parser.add_argument('--device', help="Device to run the model", default='cuda')
    parser.add_argument('--score_thres', help="Minimum score threshold", type=float, default=0.1)
    parser.add_argument('--out_file', help="Output file containing filename and prediction in each line", default='results.txt')
    args = parser.parse_args()
    return args

def decode(result, score_thres):
    cls = []
    for i, res in enumerate(result):
        cls.extend([i] * res.shape[0])

    result_arr = np.concatenate(result)

    boxes, indices = mmcv.ops.nms(result_arr[:,:4], result_arr[:, -1], 0.5)
    centers = (boxes[:, 0] + boxes[:, 2]) / 2
    permute = np.argsort(centers)
    boxes = boxes[permute]
    indices = indices[permute]

    highscore = boxes[:, -1] > score_thres
    boxes = boxes[highscore]
    indices = indices[highscore]

    dictionary = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    texts = ''.join(dictionary[cls[i]] for i in indices)
    return boxes, texts

def get_predictions(model, images_dir, score_thres):
    img_files = os.listdir(images_dir)
    results = []
    for filename in tqdm(img_files):
        img = mmcv.imread(os.path.join(images_dir, filename), channel_order='rgb')
        detection_result = inference_detector(model, img)
        boxes, text = decode(detection_result, score_thres)
        results.append((filename.split('.')[0], text))
    return results


if __name__ == '__main__':
    args = parse_args()
    model = init_detector(args.config, args.checkpoint, device=args.device)
    print("Running the model")
    results = get_predictions(model, args.images_dir, args.score_thres)
    
    correct = sum(result[0] == result[1] for result in results)
    print(f"Accuracy: {correct / len(results):.2%}")
    print(f"Exporting results to {args.out_file}")
    with open(args.out_file, 'w') as f:
        for imgfile, pred in results:
            f.write(f"{imgfile} {pred}\n")
            