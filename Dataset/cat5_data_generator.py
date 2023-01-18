from captcha.image import ImageCaptcha
import random
import os
import json
import argparse
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor


def parse_args():
    parser = argparse.ArgumentParser(description="Create a dataset and save with COCO format")
    parser.add_argument('--save-dir', help="Path to folder to save the dataset", default='data/coco')
    parser.add_argument('--train-samples', help="Number of train samples", type=int, default=10000)
    parser.add_argument('--val-samples', help="Number of val samples", type=int, default=1000)
    parser.add_argument('--min-char', help="Minimum number of characters", type=int, default=5)
    parser.add_argument('--max-char', help="Maximum number of characters", type=int, default=9)
    parser.add_argument('--img-width', help='Width of images', type=int, default=400)
    parser.add_argument('--img-height', help='Height of images', type=int, default=150)
    args = parser.parse_args()
    return args

def gen_image(generator, img_id, split, args):
    char_count = random.randint(args.min_char, args.max_char)
    dictionary = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    chars_idx = random.choices(list(range(len(dictionary))), k=char_count)
    chars = [dictionary[i] for i in chars_idx]
    image, bboxes = generator.generate_image(chars, return_bbox=True)
    
    filename = f'{img_id}.png'
    image_meta = {
        'id': img_id,
        'width': args.img_width,
        'height': args.img_height,
        'file_name': filename
    }
    annotations = []
    for i in range(char_count):
        bbox = bboxes[i]
        ann = {
            'image_id': img_id,
            'category_id': chars_idx[i],
            'segmentation': [],
            'area': bbox[2] * bbox[3],
            'bbox': bbox,
            'iscrowd': 0
        }
        annotations.append(ann)
        
    path = os.path.join(args.save_dir, 'images', split, filename)
    image.save(path)
    return {'image': image_meta, 'annotations': annotations}

def gen_dataset(args, split, num_samples):
    os.makedirs(os.path.join(args.save_dir, 'images', split), exist_ok=True)

    font_files = os.listdir('fonts')
    font_files = ['fonts/' + f for f in font_files]
    generator = ImageCaptcha(width=args.img_width, height=args.img_height,
                            fonts=font_files, font_sizes=[70])
    
    print(f"Generating {split} images")
    pool = ProcessPoolExecutor(max_workers=16)

    futures = []
    print("Submitting jobs")
    for i in tqdm(range(num_samples)):
        futures.append(pool.submit(gen_image, generator=generator, img_id=i, split=split, args=args))

    print('Running jobs')
    results = []
    for future in tqdm(futures):
        results.append(future.result())

    print("Creating annotations")
    imgs = []
    anns = []
    ann_id = 0
    for result in tqdm(results):
        imgs.append(result['image'])
        for ann in result['annotations']:
            ann['id'] = ann_id
            ann_id += 1
            anns.append(ann)
            
    dictionary = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    cats = []
    for i, char in enumerate(dictionary):
        cat = {
            'id': i,
            'name': char,
            'supercategory': ''
        }
        cats.append(cat)
    coco = {
        'images': imgs,
        'annotations': anns,
        'categories': cats
    }
    with open(os.path.join(args.save_dir, 'annotations', f'{split}.json'), 'w') as f:
        json.dump(coco, f)


if __name__ == '__main__':
    args = parse_args()
    os.makedirs(args.save_dir, exist_ok=True)
    os.makedirs(args.save_dir + '/images', exist_ok=True)
    os.makedirs(args.save_dir + '/annotations', exist_ok=True)
    gen_dataset(args, 'train', args.train_samples)
    gen_dataset(args, 'val', args.val_samples)
