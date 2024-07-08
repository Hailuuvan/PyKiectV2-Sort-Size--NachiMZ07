import image_recognition_singlecam
import XYZ_realworld
import socket
import time
import math
import cv2 as cv
import numpy as np
import cv2
import os

imgdir = "D:\DATN\FinalProject\Calib\Captures/"
imgprefix1 = "CapDectect"
img_counter = 0
cam = cv.VideoCapture(r'D:\DATN\FinalProject\VideoTest\angle4.mp4')
back = cv.VideoCapture(r'D:\DATN\FinalProject\VideoTest\background1.mp4')

video_output_path = 'D:\DATN\FinalProject\VideoTest\output_video7.mp4'
os.makedirs(os.path.dirname(video_output_path), exist_ok=True)

# Đọc và lấy frame đầu tiên
ret, frame_init = cam.read()

roi_init = frame_init[0:1080, 1000:1350]

# Get the width and height of the frame
frame_height, frame_width = frame_init.shape[:2]

# Debug information about the frame size
print(f"Frame width: {frame_width}, Frame height: {frame_height}")

# Define the codec and create VideoWriter object
fourcc = cv.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 file
out = cv.VideoWriter(video_output_path, fourcc, 30.0, (frame_width, frame_height))
image_recog = image_recognition_singlecam.image_recognition()
XYZ = XYZ_realworld.XYZ_realworld()
while True:
    ret, frame = cam.read()
    if not ret:
        print("Video đã kết thúc hoặc không thể đọc frame.")
        break
    roi_frame = frame[0:1080, 1000:1350]
    #img_roi_otsu = image_recog.calculateDifference_Otsu(roi_frame, roi_init)
    #cv2.imshow("dff", img_roi_otsu)
    obj_count, detected_points, img_output = image_recog.run_detection(roi_frame, roi_init)
    #out.write(img_output)
    xyz_real_value = image_recog.get_XYZ_real()
    full_frame = cv2.resize(frame,(0,0),fx=0.5,fy=0.5 )
    print(full_frame.shape)
    #cv2.imshow('frame', full_frame)
    
    xyz_real_value = image_recog.get_XYZ_real()
    #cv2.imshow('frame', frame)
    (x, y, z) , yaw_value, area = xyz_real_value
    home_pos = [x[0], y[0], z[0], 0, 0, 0]
    print(home_pos)
    print("yaw",yaw_value[2])
    print ("Area: ", area)
    
    
    k = cv2.waitKey(1)
    if k % 256 == 27:  # ESC pressed
        print("Exiting...")
        break
    elif k % 256 == 32:
        # SPACE pressed Captures an Image
        img_name1 = imgdir + imgprefix1 + "_{}.jpg".format(img_counter)
        cv2.imwrite(img_name1, img_output)
        '''
        img_name2 = imgdir + imgprefix2 + "_{}.jpg".format(img_counter)
        cv2.imwrite(img_name2, roi_frame)
        
        img_name3 = imgdir + imgprefix3 + "_{}.jpg".format(img_counter)
        cv2.imwrite(img_name3, img_gray)
        
        img_name4 = imgdir + imgprefix4 + "_{}.jpg".format(img_counter)
        cv2.imwrite(img_name4, diff_img)
        '''
        
        
        #print(imgprefix + "_{} written!".format(img_counter))
        img_counter += 1
