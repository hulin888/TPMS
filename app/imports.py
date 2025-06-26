import os

base_dir = os.getcwd()
data_dir = os.path.join(base_dir, 'data')
os.makedirs(data_dir, exist_ok=True)
# vid_dir = os.path.join(data_dir, 'videos')
# os.makedirs(vid_dir, exist_ok=True)
# image_dir = os.path.join(data_dir, 'images')
# os.makedirs(image_dir, exist_ok=True)
# videoclip_dir = os.path.join(data_dir, 'videoclips')
# os.makedirs(videoclip_dir, exist_ok=True)