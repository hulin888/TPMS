import traceback
import cv2
from app.imports import *
from app.core.extraction_modules.track_object import YOLO, yolo_detections_to_norfair_detections, euclidean_distance
from norfair import Tracker
import norfair
from datetime import datetime
from app.core.models.database import DATABASE
from app.core.models.database_setup import DATABASE_SETUP

from app.core.extraction_modules.utilityfunctions import recognise_pate, read_licence_paddleocr, get_index_nparray
import numpy as np
import gc
database = DATABASE()
dbsetup = DATABASE_SETUP()
max_distance_between_points: int = 50

platemodelpath = 'trained_models/licenceplate_detection_nanomodel.pt'
axlemodelpath = 'trained_models/axle_detection_11Nov2022.pt'
vehiclemodelpath = 'trained_models/licence_and_vehicle_type_detection_with_other_10Nov2022.pt'

platemodel = YOLO(platemodelpath)
axlemodel = YOLO(axlemodelpath)
vehiclemodel = YOLO(vehiclemodelpath)

    
class EXTRACTOR:
    def __init__(self, company, location, tollid, laneno, inout, cctvlink):
        self.company = company
        self.location = location
        self.tollid = tollid
        self.laneno = laneno
        self.inout = inout
        self.cctvlink = cctvlink

    def video_process(self):
        try:
            self.plate_tracker = Tracker(distance_function=euclidean_distance,
            distance_threshold=max_distance_between_points,
                )
            self.axle_tracker = Tracker(distance_function=euclidean_distance,
                    distance_threshold=max_distance_between_points,
                )
            self.job_id = self.laneno
            self.job_path = os.path.join(data_dir, self.company, self.location, self.tollid, self.job_id)
            if not os.path.exists(self.job_path):
                os.makedirs(self.job_path)
            # imagepath = os.path.join(job_path, f'{datetime.now()}.jpg')
            # videopath = os.path.join(job_path, f'{datetime.now()}.mp4')
            # video = Video(input_path = self.cctvlink) # video path
            self.cap = cv2.VideoCapture(self.cctvlink)
            self.platecountlist = []
            self.axlecountlist = []
            self.nodetect = 0
            self.framestosave = []
            self.timetosave = []
            self.platesdetected = []
            self.detection = 'plate_detection'
            # for frame in video:
            self.vehicletype = ''
            self.noofaxles = None
            self.vehiclesubtype = ''
            while True:
                flag, frame = self.cap.read()
                self.frametime = datetime.utcnow()
                # ret, frame = cap.read()
                if (frame is None):
                    print("[INFO] End of Video")
                    dbsetup.update_setup(self.company, self.location, self.tollid, self.laneno, False)
                    break
                # else:
                #     database.update_setup(self.company, self.location, self.tollid, self.laneno, True)

                if self.detection=='plate_detection':
                    self.plate_detections = platemodel(
                    frame,
                    conf_threshold=0.2,
                    iou_threshold=0.45,
                    image_size=640,
                    classes=None
                    )
                    self.height, self.width, self.channels = frame.shape
                    self.xyxy = self.plate_detections.xyxy[0].tolist()
                    # xyxy = [i for i in xyxy if i[1]>min]
                    self.track_points = 'bbox'
                    # print(self.xyxy)
                    if self.xyxy:
                        # print(xyxy[0][1], height/1.8)
                        if self.xyxy[0][1]>self.height/1.8:
                            self.detection = 'axle_detection'
                        self.xmin, self.ymin, self.xmax, self.ymax, _, _ = [int(i) for i in self.xyxy[0]]
                        self.plate_img = frame[self.ymin:self.ymax, self.xmin:self.xmax]
                        self.p_detections = yolo_detections_to_norfair_detections(self.plate_detections, track_points=self.track_points)
                        self.plate_tracked_objects = self.plate_tracker.update(detections=self.p_detections)
                        # if args.track_points == 'centroid':
                        #     norfair.draw_points(frame, detections)
                        # elif args.track_points == 'bbox':
                        # norfair.draw_boxes(frame, detections)
                        # norfair.draw_tracked_objects(frame, tracked_objects)
                        
                        if self.plate_tracked_objects:
                            for obj in self.plate_tracked_objects:
                                self.count = obj.id
                                # if count not in objectcountlist:
                                self.platecountlist.append(self.count)

                        self.nodetect = 0
                        if len(self.platesdetected)<150:
                            self.resizedframe = cv2.resize(frame, (1280, 720), interpolation = cv2.INTER_AREA)
                            self.framestosave.append(self.resizedframe)
                            self.timetosave.append(self.frametime)
                            self.platesdetected.append(self.plate_img)

                        # print(framestosave)
                        # print(timetosave)
                    else:
                        if self.nodetect>100:
                            if self.platecountlist:
                                # print(objectcountlist)
                                self.noofplates = len(set(self.platecountlist))
                                # print('=================>',noofaxles)
                            self.plate_tracker = Tracker(
                            distance_function=euclidean_distance,
                            distance_threshold=max_distance_between_points,
                            )
                            self.platecountlist = []
                            # if timetosave and framestosave:
                            #     imagepath = os.path.join(job_path,f'{timetosave[0]}.jpg')
                            #     videopath = os.path.join(job_path, f'{timetosave[0]}.mp4')
                            #     cv2.imwrite(imagepath, framestosave[0])
                            #     height, width, _ = framestosave[0].shape
                            #     out = cv2.VideoWriter(videopath, cv2.VideoWriter_fourcc(*'mp4v'), 30, (width, height))
                            #     [out.write(f) for f in framestosave]
                            #     out.release()
                            #     vehicldetections = vehiclemodel(
                            #     frame,
                            #     conf_threshold=0.2,
                            #     iou_threshold=0.25,
                            #     image_size=640,
                            #     classes=[2,5,7]
                            #     )
                            #     detection_df = vehicldetections.pandas().xyxy[0]
                            #     detection_df = detection_df[detection_df['confidence']==detection_df['confidence'].max()]
                            #     if not detection_df.empty:
                            #         detection_df = detection_df.to_dict('records')[0]
                            #         vehicletype = detection_df['name']
                            #     else:
                            #         vehicletype = 'other'
                            #     plateimage = platesdetected[int(len(platesdetected)/3)]
                            #     # cv2.imshow('plate image', plateimage)
                            #     # cv2.waitKey(1)
                            #     time = timetosave[0]
                            #     vehicleno = recognise_pate(plateimage)
                            #     # vehicleno = 'MH23RT2356'
                            #     print(detection_df)
                            #     print('------>>>', vehicletype, vehicleno)
                            #     platesdetected = []
                            #     framestosave = []
                            #     timetosave = []

                        self.nodetect+=1
                else:
                    # print('In axle detection')
                    self.axle_detections = axlemodel(
                        frame,
                        conf_threshold=0.35,
                        iou_threshold=0.45,
                        image_size=640,
                        classes=None
                    )
                    
                    self.height, self.width, self.channels = frame.shape
                    # half = height/1.5
                    self.xywh = self.axle_detections.xywh[0].tolist()
                    # xywh = [i[1] for i in xywh if i[1]>half]
                    self.track_points = 'bbox'
                    # print('in axle_tracker')
                    # print(self.xywh)
                    if self.xywh:
                        self.ax_detections = yolo_detections_to_norfair_detections(self.axle_detections, track_points=self.track_points)
                        self.axle_tracked_objects = self.axle_tracker.update(detections=self.ax_detections)
                        # if args.track_points == 'centroid':
                        #     norfair.draw_points(frame, detections)
                        # elif args.track_points == 'bbox':
                        # norfair.draw_boxes(frame, ax_detections)
                        # norfair.draw_tracked_objects(frame, axle_tracked_objects)
                        
                        if self.axle_tracked_objects:
                            for obj in self.axle_tracked_objects:
                                self.count = obj.id
                                # if count not in objectcountlist:
                                self.axlecountlist.append(self.count)

                        self.nodetect = 0
                    else:
                        if self.nodetect>100:
                            if self.axlecountlist:
                                self.noofaxles = len(set(self.axlecountlist))
                                print('No. of axles = ', self.noofaxles)
                            self.axle_tracker = Tracker(
                            distance_function=euclidean_distance,
                            distance_threshold=max_distance_between_points,
                            )
                            self.axlecountlist = []
                            self.detection='plate_detection'
                            if self.timetosave and self.framestosave:
                                self.plateimage_sizes = [image.shape[1::-1] for image in self.platesdetected]
                                self.plateimage_sizes = [im[0]*im[1] for im in self.plateimage_sizes]
                                self.plateimage_sizes = np.array(self.plateimage_sizes)
                                # plateimage = platesdetected[platimage_sizes.argmax()]
                                self.indices = get_index_nparray(self.plateimage_sizes, 5)

                                self.plateimages = [self.platesdetected[i] for i in self.indices]
                                self.framestosave = [self.framestosave[i] for i in self.indices]
                                self.timetosave = [self.timetosave[i] for i in self.indices]
                                
                                self.imagepath = os.path.join(self.job_path,f'{self.timetosave[0]}.jpg')
                                self.videopath = os.path.join(self.job_path, f'{self.timetosave[0]}.mp4')
                                self.dim = (1280, 720)
                                try:
                                    cv2.imwrite(self.imagepath, self.framestosave[-5])
                                except:
                                    
                                    cv2.imwrite(self.imagepath, self.framestosave[-1])

                                self.height, self.width, _ = self.framestosave[-1].shape
                                self.out = cv2.VideoWriter(self.videopath, cv2.VideoWriter_fourcc(*'mp4v'), 30, self.dim)
                                [self.out.write(f) for f in self.framestosave]
                                self.out.release()
                                self.vehicldetections = vehiclemodel(
                                self.imagepath,
                                conf_threshold=0.4,
                                iou_threshold=0.45,
                                image_size=640,
                                classes= [0,1,2,3,6]
                                )
                                self.detection_df = self.vehicldetections.pandas().xyxy[0]
                                print(self.detection_df)
                                self.detection_df = self.detection_df[self.detection_df['confidence']==self.detection_df['confidence'].max()]
                                if not self.detection_df.empty:
                                    self.detection_df = self.detection_df.to_dict('records')[0]
                                    self.vehicletype = self.detection_df['name']
                                else:
                                    self.vehicletype = 'other'

                                self.vehicleno = read_licence_paddleocr(self.plateimages)
                                
                                '''
                                vehiclenos = []
                                for plateimage in plateimages:
                                    vehicleno = read_licence_paddleocr(plateimage)
                                    if vehicleno:
                                        vehiclenos.append(vehicleno)
                                    # print('------>>>', vehicletype, vehicleno)
                                    # vehicleno = 'MH23RT2356'
                                    # print(detection_df)
                                    
                                    # cv2.imwrite(f"{plateimagepath}/{self.videoname}_image-{counter}.jpg", plateimage)
                                    # cv2.imshow('plate image', plateimage)
                                    # cv2.waitKey(0)
                                print('------>>>', vehiclenos)
                                try:
                                    vehicleno = vehiclenos[0]
                                except:
                                    vehicleno = ''
                                '''
                                # plateimage = platesdetected[int(len(platesdetected)/3)]
                                # cv2.imshow('plate image', plateimage)
                                # cv2.waitKey(1)
                                try:
                                    self.time = self.timetosave[-5]
                                except:
                                    self.time = self.timetosave[-1]
                                print('Final number plates',self.vehicleno)
                                # del self.platesdetected
                                # del self.framestosave
                                # del self.timetosave
                                # gc.collect()
                                # vehicleno = read_licence_paddleocr(plateimage)
                                # vehicleno = 'MH23RT2356'
                                # print(detection_df)
                                print('------>>>', self.vehicletype, self.vehicleno)
                                self.platesdetected = []
                                self.framestosave = []
                                self.timetosave = []
                            try:
                                subtype = {1:"Truck", 2:"Truck", 3:"Upto 3 Axle Vehicle",
                                4:"4 to 6 Axle", 5:"4 to 6 Axle", 6:"4 to 6 Axle",
                                7:"7 or more Axle"}
                                if self.vehicletype == 'truck':
                                    if self.noofaxles:
                                        if self.noofaxles>7:
                                            self.noofaxles = 7
                                        self.vehiclesubtype = subtype.get(self.noofaxles)
                                        if self.vehiclesubtype:
                                            self.vehiclesubtype = self.vehiclesubtype
                                    else:
                                        self.vehiclesubtype = 'Truck'
                                    self.vehicletype = self.vehicletype.capitalize()
                                    
                                elif self.vehicletype=='car' or self.vehicletype=='bus'  or  self.vehicletype=='other':
                                    self.vehiclesubtype=self.vehicletype.capitalize()
                                    self.vehicletype = self.vehicletype.capitalize()
                                elif self.vehicletype=='lcv':
                                    self.vehicletype = 'LCV'
                                    self.vehiclesubtype = 'LCV'
                                
                                database.insert_data(self.company, self.location, self.tollid, self.laneno, self.inout, self.vehicletype, self.vehiclesubtype, self.vehicleno.upper(), self.imagepath, self.videopath, self.time)
                            except:
                                print(traceback.print_exc())
                        self.nodetect+=1
                # cv2.imshow('video', frame)
                # cv2.waitKey(1)
                    # cv2.destroyAllWindows()
        except:
            traceback.print_exc()
