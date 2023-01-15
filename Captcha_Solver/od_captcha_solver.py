import mmcv
from mmdet.apis import init_detector, inference_detector
from DL_cracker.predict import decode

class ODCracker():
    def __init__(self, config_path='src/DL_cracker/mmdetection/custom/yolox_captcha_config.py', 
                       checkpoint_path='src/DL_cracker/mmdetection/work_dirs/yolox_captcha_config/yolox_captcha_v1.pth',
                       device='cpu',
                       score_thres=0.1):
        super().__init__()
        self.model = init_detector(config_path, checkpoint_path, device=device)
        self.score_thres = score_thres

    def crack(self, file_path):
        # Load image
        img = mmcv.imread(file_path, channel_order='rgb')

        # Run model
        detection_result = inference_detector(self.model, img)
        _, res = decode(detection_result, self.score_thres)
        return res
    

if __name__ == "__main__":
    cracker = ODCracker()
    res = cracker.crack('Dataset/cat5/9CmNn.jpeg')
    print(res)