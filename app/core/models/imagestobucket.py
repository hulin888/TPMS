from minio import Minio
# from minio.error import ResponseError
import os
from datetime import timedelta

eos_client = Minio('objectstore.e2enetworks.net',
                   access_key='HZ550Y3QVC4TRWXMRA3W',
                   secret_key='FBABAEN0DMW6I2AMDCQ524D7GD4W8AR08ZSPRYYR',
                   secure=True)

def get_imageurl_fromS3(bucket_name, imagepath):
    presigned_get_object_url = eos_client.presigned_get_object(bucket_name, imagepath, expires=timedelta(minutes=15))
    return presigned_get_object_url

def get_file_froms3(bucket_name, filepath):

    try:
        data = eos_client.get_object(bucket_name, filepath)
        # with open('test-file', 'wb') as file_data:
        #     for d in data.stream(32*1024):
        #         file_data.write(d)
    except:
        print('Not Successfull')

def upload_image_toS3(bucket_name, imagepath):
    try:
        with open(imagepath, 'rb') as file_data:
            file_stat = os.stat(imagepath)
            eos_client.put_object(bucket_name, imagepath,
                                file_data, file_stat.st_size,
                                content_type='image/jpeg')

    except:
        print('not successfull')

def upload_video_toS3(bucket_name, videopath):
    try:
        with open(videopath, 'rb') as file_data:
            file_stat = os.stat(videopath)
            eos_client.put_object(bucket_name, videopath,
                                file_data, file_stat.st_size,
                                content_type='video/mp4')

    except:
        print('not successful')


# upload_video_toS3(bucket_name, '/root/TNMS_Live/data/videoclips/59faeaab-413e-4a47-8419-02a7aaaa9760/28/clip.mp4')

