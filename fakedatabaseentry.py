import random
from pymongo import MongoClient
from turtle import done
import uuid
from datetime import datetime
from string import digits, ascii_uppercase
import time
# from icecream import ic
import glob
# database = DATABASE()
imagedir = "data/**/*.jpg"
videodir = "./data/**/*.mp4"
statecodes = ['AN','AP','AR','AS','BH','BR','CH','CG','DD','DL','GA','GJ','HR','HP','JK','JH','KA','KL','LA','LD','MP','MH','MN','ML','MZ','NL','OD','PY','PB','RJ','SK','TN','TS','TR','UP','UK','WB']
database_data = {}
tollfee = {'car': 110, 'bus': 260, 'truck': 375}
inout = {0: 'in', 1:'out'}
monthlypass = {0: 'Y', 1: 'N'}
cvrwithindtp = {0: 'Y', 1: 'N'}
veh_detected = {0: "car", 1: "bus", 2: "truck"}
images =glob.glob(imagedir)
print(images)
videoclips = glob.glob(videodir)
count = 0
mongodb_url = MongoClient("mongodb://global_tnms:fkJmzaD0JINWr@localhost:27017/?authSource=admin&readPreference=primary&appname=mongodb-vscode%200.6.10&ssl=false")
mongo_db_client = mongodb_url

while True:
    db = mongo_db_client['TNMS_Live']
    collection = db['vehicle_detail']
    img_path = images[random.randint(0, len(images)-1)]
    saveclippath = videoclips[random.randint(0, len(videoclips)-1)]
    # job_id = str(uuid.uuid4())
    code_2 = f"{random.choice(digits)}{random.choice(digits)}"
    alpha = f"{random.choice(ascii_uppercase)}{random.choice(ascii_uppercase)}"
    code_4 = f"{random.choice(digits)}{random.choice(digits)}{random.choice(digits)}{random.choice(digits)}"
    plateno = f"{statecodes[random.randint(0,36)]}{code_2}{alpha}{code_4}"
    vehicletype =  veh_detected[random.randint(0,2)]
    # database_data['jobid'] = job_id
    database_data['company'] = 'ABC Toll Plaza'
    database_data['location'] = 'Nagpur'
    database_data['tollid'] = '11'
    database_data['laneno'] = "1"#str(random.randint(1,10))
    database_data['vehicletype'] = vehicletype
    # database_data['vehicle_subtype'] = get_vehicle_info(plateno)
    database_data['vehiclesubtype'] = ' '
    database_data['image'] = img_path.split('TNMS_Live')[-1]
    database_data['vehicleno'] = plateno
    database_data['time'] = datetime.utcnow()
    # savclippath = extract_videoclip(job_id, image, vid_path)
    database_data['videoclip'] = saveclippath.split('TNMS_Live')[-1]
    database_data['fee'] = tollfee[vehicletype]
    database_data['inout'] = inout[random.randint(0,1)]
    database_data['exemptionflag'] = 'N'
    database_data['monthlypass'] = monthlypass[random.randint(0,1)]
    database_data['cvrwithindtp'] = cvrwithindtp[random.randint(0,1)]
    # ic(database_data)
    database_data['archived'] = False
    # database.insert_data(database_data)
    collection.replace_one({"vehicleno":""},database_data, upsert=True)
    time.sleep(1)
    print('done', database_data['laneno'])
    if count == 10:
        break
    count+=1
    mongo_db_client.close()