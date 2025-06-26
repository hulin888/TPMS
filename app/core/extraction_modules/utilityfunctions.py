import pytesseract  # this is tesseract module
import matplotlib.pyplot as plt
import cv2  # this is opencv module
import glob
import os
from skimage.segmentation import clear_border
import re
from app.imports import *
import io
import torch
import torchvision
import time
import numpy as np
import ffmpeg
from datetime import datetime, timedelta
import pytz
import shutil
from google.cloud import vision
from google.cloud.vision_v1 import types
from google.cloud.vision_v1 import AnnotateImageResponse
# from google.cloud.vision import types
import pandas as pd
import requests
import traceback
from fuzzywuzzy import fuzz

from app.core.extraction_modules import global_loader

ocrmodel = global_loader.ocrmodel
# from icecream import ic

apikey = './config/visionapikey.json'

rtocodedf = pd.read_csv('config/rto_codes.csv')
statecode = rtocodedf['statecode'].unique()
statedistrictcode = rtocodedf['code'].unique()
def validate_license_plate(text):
    license_plate_data = re.search(r'[A-Z]{2}[0-9]{1,2}([A-Z])(?:[A-Z]*)?[0-9]{4}', text)
    if license_plate_data:
        license_plate =  text[license_plate_data.start():license_plate_data.end()]
        if license_plate[:2].upper() not in statecode:
            license_plate = np.nan
    else:
        license_plate = np.nan
    return license_plate

def get_valid_text(plate_text):
    if plate_text[:2].upper() not in statecode:
        return np.nan
    else:
        return plate_text

# def get_matching_statecode(platetext):


def clean_plate_text(plate_text):
    text = re.sub(r'[^A-Za-z0-9]+', '', plate_text.upper())
    # text = text.replace('IND', '').replace('INO','')
    return text.upper()

def get_text_length(text):
    return len(text)


def read_licence_paddleocr(imagearray_list):
    df = pd.DataFrame()
    for imagearray in imagearray_list:
        hir1 = cv2.pyrUp(imagearray)

        result = ocrmodel.ocr(hir1, cls=True)
        text = []
        for line in result:
            text.append(line[1])
        tempdf = pd.DataFrame(text, columns=['text', 'score'])
        tempdf['ratio'] = tempdf['text'].apply(lambda x: fuzz.ratio(x, 'IND'))
        tempdf = tempdf.loc[~(tempdf["ratio"]>60)]
        tempdf['ratio'] = tempdf['text'].apply(lambda x: fuzz.ratio(x, 'NO'))
        tempdf = tempdf.loc[~(tempdf["ratio"]>60)]
        tempdf. drop('ratio', axis=1, inplace=True)
        tempdf['text'] = tempdf['text'].str.cat(sep='')
        tempdf['score'] = tempdf['score'].max()
        tempdf.drop_duplicates(inplace=True)
        df = df.append(tempdf)
    df.reset_index(drop=True, inplace=True)
    df['text'] = df['text'].apply(clean_plate_text)
    df['valid_text'] = df['text'].apply(validate_license_plate)
    print(df)
    if df['valid_text'].isnull().all():
        df['clean_text'] = df['text'].apply(get_valid_text)
        if df['clean_text'].isnull().all():
            df["length"]= df["text"].str.len()
            if 10 in df["length"].tolist():
                df = df[df['length']==10]
            platedf = df[df['score']==df['score'].max()]
            platedf.drop_duplicates(inplace=True)
            license_plate = platedf['text'].str.cat(sep='')
        else:
            df.dropna(subset=['clean_text'], inplace=True)
            df["length"]= df["clean_text"].str.len()
            if 10 in df["length"].tolist():
                df = df[df['length']==10]
            platedf = df[df['score']==df['score'].max()]
            platedf.drop_duplicates(inplace=True)
            license_plate = platedf['clean_text'].str.cat(sep='')
    else:
        df.dropna(subset=['valid_text'], inplace=True)
        df["length"]= df["valid_text"].str.len()
        if 10 in df["length"].tolist():
            df = df[df['length']==10]
        platedf = df[df['score']==df['score'].max()]
        platedf.drop_duplicates(inplace=True)
        license_plate = platedf['valid_text'].str.cat(sep='')
    # license_plate = re.sub(r'[^A-Za-z0-9]+', '', plate_text)
    #     
    # else:
    #     license_plate = ''
    if license_plate[:2].upper() not in statecode:
        wrong_det = ['NH', 'WH', 'HH']
        try:
            index = wrong_det.index(license_plate[:2])
        except:
            index = None
        if index:
            license_plate = license_plate.replace(wrong_det[index], 'MH')
    if license_plate=='':
        license_plate = 'unprocessed'
    return license_plate


def get_index_nparray(array, noofvalues):
    
    indices = (-array).argsort()[:noofvalues]
    return indices

def read_licence_plate(imagearray):
    # license_plate = cv2.imread(image_path)
    # gray = cv2.cvtColor(imagearray, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(imagearray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255,
                           cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))

    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    # license_plate = clear_border(license_plate)

    invert = 255 - opening

    alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    options = "-c tessedit_char_whitelist={}".format(alphanumeric)
# set the PSM mode
    psm = 6
    options += " --psm {}".format(psm)
    predicted_licenceplate = pytesseract.image_to_string(
        blur, config=options)  # '--oem 3 -l eng --psm 11')  # -c tessedit_char_whitelist = ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    license_plate = "".join(predicted_licenceplate.split()).replace(
        ":", "").replace("-", "")
    license_plate = re.sub(r'[^A-Za-z0-9 ]+', '', license_plate)
    return license_plate

def recognise_pate(imagearray):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = apikey
    client = vision.ImageAnnotatorClient()
    # imagePath = '/home/sanjay/Desktop/GlobalSuntec/TNMS_OCR_training/platesdata/images/14_2021-08-25_123417-converted253.jpg'
    # with io.open(imagePath, 'rb') as image_file:
    #     content = image_file.read()
    content=cv2.imencode('.jpg', imagearray)[1].tostring()
    image = types.Image(content=content)

    # Performs text detection on image

    response = client.text_detection(image)

    serialized_proto_plus = AnnotateImageResponse.serialize(response)
    response = AnnotateImageResponse.deserialize(serialized_proto_plus)
    license_plate = response.full_text_annotation.text
    license_plate = re.sub(r'[^A-Za-z0-9]+', '', license_plate)
    print(license_plate)
    return license_plate

def ratioCheck(area, width, height):
    ratio = float(width) / float(height)
    if ratio < 1:
        ratio = 1 / ratio
    if (area < 1063.62 or area > 73862.5) or (ratio < 3 or ratio > 6):
        return False
    return True
    
def clean2_plate(plate):
    gray_img = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray_img, 110, 255, cv2.THRESH_BINARY)
    if cv2.waitKey(0) & 0xff == ord('q'):
        pass
    num_contours,hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if num_contours:
        contour_area = [cv2.contourArea(c) for c in num_contours]
        max_cntr_index = np.argmax(contour_area)

        max_cnt = num_contours[max_cntr_index]
        max_cntArea = contour_area[max_cntr_index]
        x,y,w,h = cv2.boundingRect(max_cnt)

        if not ratioCheck(max_cntArea,w,h):
            return plate,None

        final_img = thresh[y:y+h, x:x+w]
        return final_img,[x,y,w,h]

    else:
        return plate,None

def extract_frames(vidpath):
    savimgpath = os.path.join(image_dir, os.path.splitext(os.path.basename(vidpath))[0])
    if os.path.isdir(savimgpath):
        shutil.rmtree(savimgpath)
    os.makedirs(savimgpath)
    command = 'ffmpeg  -i '+vidpath+' -r 1 '+savimgpath+'/image-%04d.jpg'
    os.system(command)
    return savimgpath

def extract_videoclip(job_id, imagename, vidpath):
    img_time = os.path.splitext(imagename)[0]
    img_time = int(img_time.split('-')[-1]) -1
    img_timefrom = timedelta(seconds=img_time-5)
    img_timeto = timedelta(seconds=img_time+5)
    savclippath = os.path.join(videoclip_dir, job_id, str(img_time))
    if os.path.isdir(savclippath):
        shutil.rmtree(savclippath)
    os.makedirs(savclippath)

    # ffmpeg -i movie.mp4 -ss 00:00:03 -t 00:00:08 -async 1 cut.mp4

    command = 'ffmpeg  -i '+vidpath+' -ss '+str(img_timefrom)+' -t '+'00:00:10'+ ' -async 1 '+savclippath+'/clip.mp4'
    os.system(command)
    return savclippath

def extract_time(vidpath):
    metadata = ffmpeg.probe(vidpath)
    date = metadata['streams'][0]['tags']['creation_time']
    converted = pytz.timezone('Asia/Kolkata')
    dateTimeObj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
    thirty_minute = timedelta(seconds=1860)
    dateTimeObj = dateTimeObj.astimezone(converted) - thirty_minute
    return dateTimeObj

def get_time(imagename, vidtime):
    img_time = os.path.splitext(imagename)[0]
    img_time = int(img_time.split('-')[-1]) -1
    time_sec = timedelta(seconds=img_time)
    time = vidtime + time_sec
    return time

def get_laneno(imagearray):
    laneimg = imagearray[int(620):int(670), int(760):int(1020)]
    lanenotext = read_licence_plate(laneimg)
    lanenotext = re.sub(r'[^0-9 ]+', '', lanenotext)
    return lanenotext


def get_laneno_df(df):
    # laneimg = imagearray[int(620):int(670), int(760):int(1020)]
    lanenodf = df[(df['x0']>760)&(df['x1']<1020) & (df['y0']>620) & (df['y2']<670)]
    # lanenodf = lanenodf.reset_index()
    # #print(lanenodf)
    lanenodf.sort_values(['x0'], inplace = True)
    lanenotextlist = lanenodf['Token'].values.tolist()
    lanenotext = " ".join(lanenotextlist)
    # lanenotext = read_licence_plate(laneimg)
    lanenotext = re.sub(r'[^0-9 ]+', '', lanenotext)
    return lanenotext

def get_time_df(df):
    # laneimg = imagearray[int(620):int(670), int(760):int(1020)]
    timedf = df[(df['x0']>37)&(df['x1']<610) & (df['y0']>45) & (df['y2']<90)]
    timedf = timedf.reset_index()
    timedf.sort_values(['x0'], inplace = True)
    timetextlist = timedf['Token'].values.tolist()
    timetext = " ".join(timetextlist)
    # lanenotext = read_licence_plate(laneimg)
    # lanenotext = re.sub(r'[^0-9 ]+', '', lanenotext)
    # timetext = re.sub(r'[^A-Za-z0-9 ]+', '', timetext)
    return timetext

def get_licenceplate_df(df, cords):
    # laneimg = imagearray[int(620):int(670), int(760):int(1020)]
    license_platedf = df[(df['x_centre']>int(cords['xmin']))&(df['x_centre']<int(cords['xmax'])) & (df['y_centre']>int(cords['ymin'])) & (df['y_centre']<int(cords['ymax']))]
    license_platedf = license_platedf.reset_index()
    # license_platedf.sort_values(['y0', 'x0'], inplace = True)
    license_platetextlist = license_platedf['Token'].values.tolist()
    license_platetext = "".join(license_platetextlist)
    # lanenotext = read_licence_plate(laneimg)
    # lanenotext = re.sub(r'[^0-9 ]+', '', lanenotext)
    license_platetext = re.sub(r'[^A-Za-z0-9]+', '', license_platetext)
    return license_platetext

def get_vehicle_info(vehicleno):
    try:
        vehicle_class = ''
        url = f"https://api.apiclub.in/api/v1/vehicle_info/{vehicleno}"

        # payload = "vehicleId=AP15BK6666"
        headers = {
        'Referer': 'http://tolltax.xyz/index.php',
        'API-KEY': '8a85caaace9fdd2d4d2a0a1dd51931c0'
        }

        response = requests.request("POST", url, headers=headers)

        # string = response.read().decode('utf-8')
        response = response.json()
        print(response)
        if response.get('status') == 'success':
            vehicle_class = response.get("response").get('class')
            vehicle_class = vehicle_class[vehicle_class.find("(")+1:vehicle_class.find(")")]
    except:
        print(traceback.print_exc())
        vehicle_class = ''
    return vehicle_class


def visionocr(imagePath):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = apikey
    client = vision.ImageAnnotatorClient()

    with io.open(imagePath, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs text detection on image

    response = client.text_detection(image)

    texts = response.text_annotations
    imvertices = []
    resp = ''
    for text in texts[1:]:
        vertices = (['{}\t{}'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
        vertices = ' '.join(vertices)
        vertices = vertices.split()
        vertices = [int(x) for x in vertices]
        vertices.insert(0, text.description)
        imvertices.append(vertices)
    df = pd.DataFrame(imvertices, columns=['Token', 'x0', 'y0', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3'])
    return df

# df = visionocr('/home/sanjay/Desktop/TNMS/data/images/13_2021-08-25_123133/image-0103.jpg')

# #print(df)
# df = pd.read_csv('test.csv')
# add_lineno(df)
