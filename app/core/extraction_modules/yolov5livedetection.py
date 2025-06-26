import torch

def load_model(modelpath="", conf_thres=0.25, iou_tresh=0.45):
    # Model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
    # model = torch.hub.load('config/yolov5', 'custom', path=modelpath, source='local')  # local repo

    model.conf = conf_thres  # confidence threshold (0-1)
    model.iou = iou_tresh  # NMS IoU threshold (0-1)
    return model


model = load_model()
results = model(imgs, size=640)  # includes NMS

# Results
results.print()  
results.save()  # or .show()