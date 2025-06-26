# from extractor import EXTRACTOR
from celery import Celery
from app.core.extraction_modules.extractor import EXTRACTOR
from app.core.models.datatoserver import DATABASESERV
import time
from celery_singleton import Singleton

# REDIS_URL = 'redis://redis:6379/0'
REDIS_URL = 'redis://redis:6379/0'
BROKER_URL = 'redis://redis:6379/0'

# BROKER_URL = 'amqp://guest:guest@rabbit//'
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
cloud_url = 'mongodb://global_tnms:fkJmzaD0JINWr@tolltax.xyz:27000/?'
local_url = "mongodb://global_tnms:fkJmzaD0JINWr@mongo:27017/?authSource=admin&readPreference=primary&appname=mongodb-vscode%200.6.10&ssl=false"
db_name = 'TNMS_Live'

CELERY = Celery('tasks',
                backend=REDIS_URL,
                broker=BROKER_URL)

# CELERY.conf.accept_content = ['json', 'msgpack']
# CELERY.conf.result_serializer = 'msgpack'

@CELERY.task()

def docextractor(company, location, tollid, laneno, inout, cctvlink):
    # return 'celery task'
    object_name =  f"obj_{laneno}"
    object_name = EXTRACTOR(company, location, tollid, laneno, inout, cctvlink)
    object_name.video_process()

@CELERY.task(base=Singleton)

def datatoserver():
    dobj = DATABASESERV(cloud_url, local_url, db_name)
    while True:
        dobj.update_vehicle_details()
        time.sleep(10)
