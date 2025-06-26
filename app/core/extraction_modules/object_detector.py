
# from os import name
# from pytesseract.pytesseract import main
# from yolov5 import YOLOv5
from track_object import YOLO

veh_detect = YOLO("./trained_models/yolov5n.pt")
licence_detect = YOLO("./trained_models/licenceplate_detection_nanomodel.pt")
axle_detect = YOLO("./trained_models/axle_detection.pt")

def detect_vehicles(model = veh_detect, imagespath=None):
    results = model.predict(imagespath, size=640, augment=True)
    detection_df = results.pandas().xyxy[0]
    detection_df = detection_df[detection_df['class'].isin([2,5,7])]
    detection_df = detection_df[detection_df['confidence']==detection_df['confidence'].max()]
    if not detection_df.empty:
        detection_df = detection_df.to_dict('records')[0]
        # results.save('./results')
        return detection_df
    else:
        return {}

def detect_licenceplate(model = licence_detect, imagespath=None):
    results = model.predict(imagespath, size=640, augment=True)
    detection_df = results.pandas().xyxy[0]
    detection_df = detection_df[detection_df['confidence']>0.9]
    # print(detection_df)
    detection_df = detection_df[detection_df['confidence']==detection_df['confidence'].max()]
    # results.save('./results')
    return detection_df

def detect_axle(model= axle_detect, imagespath=None):
    results = model.predict(imagespath, size=640, augment=True)
    detection_df = results.pandas().xyxy[0]
    detection_df = detection_df[detection_df['confidence']==detection_df['confidence'].max()]
    return detection_df

if __name__ == "__main__":
    imagespath = "/home/sanjay/Desktop/TNMS/data/images/12_2021-08-25_122849"
    ##print(detect_vehicles(veh_detect, imagespath))
    import os, re
    imagelist = os.listdir(imagespath) 
    imagelist.sort(key=lambda f: int(re.sub('\D', '', f)))
    for image in imagelist:
        imagepath = os.path.join(imagespath,image)
        detect_licenceplate(imagespath=imagepath)