import argparse

import numpy as np
import torch
from typing import Union, List, Optional
from norfair import Detection

class YOLO:
    def __init__(self, model_path: str, device: Optional[str] = None):
        if device is not None and "cuda" in device and not torch.cuda.is_available():
            raise Exception(
                "Selected device='cuda', but cuda is not available to Pytorch."
            )
        # automatically set device if its None
        elif device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        # load model
        # self.model = yolov5.load(model_path, device=device)
        self.model = torch.hub.load('yolov5', 'custom', path=model_path, source='local')
        # self.model = torch.hub.load('/home/sanjay/Desktop/GlobalSuntec/yolov5-master', 'yolov5s',source='local')

    def __call__(
        self,
        img: Union[str, np.ndarray],
        conf_threshold: float = 0.8,
        iou_threshold: float = 0.45,
        image_size: int = 640,
        classes: Optional[List[int]] = None
    ) -> torch.tensor:

        self.model.conf = conf_threshold
        self.model.iou = iou_threshold
        if classes is not None:
            self.model.classes = classes
        # self.model.classes = [2]
        
        detections = self.model(img, size=image_size)
        return detections


def euclidean_distance(detection, tracked_object):
    return np.linalg.norm(detection.points - tracked_object.estimate)


def yolo_detections_to_norfair_detections(
    yolo_detections: torch.tensor,
    track_points: str = 'centroid'  # bbox or centroid
) -> List[Detection]:
    """convert detections_as_xywh to norfair detections
    """
    norfair_detections: List[Detection] = []

    if track_points == 'centroid':
        detections_as_xywh = yolo_detections.xywh[0]
        for detection_as_xywh in detections_as_xywh:
            centroid = np.array(
                [
                    detection_as_xywh[0].item(),
                    detection_as_xywh[1].item()
                ]
            )
            scores = np.array([detection_as_xywh[4].item()])
            norfair_detections.append(
                Detection(points=centroid, scores=scores)
            )
    elif track_points == 'bbox':
        detections_as_xyxy = yolo_detections.xyxy[0]
        for detection_as_xyxy in detections_as_xyxy:
            bbox = np.array(
                [
                    [detection_as_xyxy[0].item(), detection_as_xyxy[1].item()],
                    [detection_as_xyxy[2].item(), detection_as_xyxy[3].item()]
                ]
            )
            scores = np.array([detection_as_xyxy[4].item(), detection_as_xyxy[4].item()])
            norfair_detections.append(
                Detection(points=bbox, scores=scores)
            )

    return norfair_detections


# parser = argparse.ArgumentParser(description="Track objects in a video.")
# parser.add_argument("files", type=str, nargs="+", help="Video files to process")
# parser.add_argument("--detector_path", type=str, default="yolov5m6.pt", help="YOLOv5 model path")
# parser.add_argument("--img_size", type=int, default="720", help="YOLOv5 inference size (pixels)")
# parser.add_argument("--conf_thres", type=float, default="0.25", help="YOLOv5 object confidence threshold")
# parser.add_argument("--iou_thresh", type=float, default="0.45", help="YOLOv5 IOU threshold for NMS")
# parser.add_argument('--classes', nargs='+', type=int, help='Filter by class: --classes 0, or --classes 0 2 3')
# parser.add_argument("--device", type=str, default=None, help="Inference device: 'cpu' or 'cuda'")
# parser.add_argument("--track_points", type=str, default="centroid", help="Track points: 'centroid' or 'bbox'")
# args = parser.parse_args()

# model = YOLO(args.detector_path, device=args.device)

# for input_path in args.files:
#     video = Video(input_path=input_path)
#     tracker = Tracker(
#         distance_function=euclidean_distance,
#         distance_threshold=max_distance_between_points,
#     )
#     objectcountlist = []
#     nodetect = 0
#     for frame in video:
#         yolo_detections = model(
#             frame,
#             conf_threshold=0.2,
#             iou_threshold=0.25,
#             image_size=640,
#             classes=[0]
#         )

#         height, width, channels = frame.shape
#         half = height/0.5
#         xywh = yolo_detections.xywh[0].tolist()
#         xywh = [i[1] for i in xywh if i[1]>half]

#         if xywh:
#             detections = yolo_detections_to_norfair_detections(yolo_detections, track_points=args.track_points)
#             tracked_objects = tracker.update(detections=detections)
#             if args.track_points == 'centroid':
#                 norfair.draw_points(frame, detections)
#             elif args.track_points == 'bbox':
#                 norfair.draw_boxes(frame, detections)
#             norfair.draw_tracked_objects(frame, tracked_objects)
            
#             if tracked_objects:
#                 for obj in tracked_objects:
#                     count = obj.id
#                     # if count not in objectcountlist:
#                     objectcountlist.append(count)

#             nodetect = 0
#         else:
#             if nodetect>100:
#                 if objectcountlist:
#                     # print(objectcountlist)
#                     noofaxles = len(set(objectcountlist))
#                     print('=================>',noofaxles)
#                 tracker = Tracker(
#                 distance_function=euclidean_distance,
#                 distance_threshold=max_distance_between_points,
#                 )
#                 objectcountlist = []

#             nodetect+=1
            
#         cv2.imshow('image', frame)
#         cv2.waitKey(1)
#         video.write(frame)

# python yolov5demo.py /home/sanjay/Desktop/for_axle_mp4/80_2021-08-25_153458-converted.mp4 --detector_path ./axle_detection.pt --device cuda --track_points bbox
# 'ffmpeg  -i '+vidpath+' -r 1 '+savimgpath+'/image-%04d.jpg'