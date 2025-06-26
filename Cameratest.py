import cv2

# http://192.168.1.22/doc/page/preview.asp
address = 'rtsp://admin:biso@123@192.168.1.24:554'
# address = f'rtsp://admin:admin@123@192.168.1.147:554'
cap = cv2.VideoCapture(address)

while(True):
      
    # reading from frame
    ret,frame = cap.read()
  
    if ret:
        # if video is still left continue creating images
        frame = cv2.resize(frame, (780, 540),
               interpolation = cv2.INTER_NEAREST)
        cv2.imshow('lane 2', frame)
        cv2.waitKey(1)
        # increasing counter so that it will
        # show how many frames are created
    else:
        break