import image_recognition_singlecam
import XYZ_realworld
import socket
import time
import math
import cv2 as cv
import numpy as np
import cv2
import pyodbc
cam = cv.VideoCapture(r'D:\DATN\FinalProject\Calibrun\Captures\angle1.mp4')
# cam = cv.VideoCapture(0)
bg = cv2.imread(r'D:\DATN\FinalProject\Calib\Captures\CapF_0.jpg')
ob = cv2.imread(r'D:\DATN\FinalProject\Calib\Captures\CapF_1.jpg')
# Đọc và lấy frame đầu tiên
ret, frame_init = cam.read()
image_recog = image_recognition_singlecam.image_recognition()
XYZ = XYZ_realworld.XYZ_realworld()
#print(detected_points)

roi_init = frame_init[0:1080, 1000:1350]

X = []
T = []

while True:
    ret, frame = cam.read()
    if not ret:
        print("Video đã kết thúc hoặc không thể đọc frame.")
        break
    roi_frame = frame[0:1080, 1000:1350]
    
    obj_count, detected_points, img_output = image_recog.run_detection(roi_frame, roi_init)

    xyz_real_value = image_recog.get_XYZ_real()
    
    cv2.imshow('frame', frame)
    # Lấy giá trị xyz, roll, area tu get_XYZ_real() cua siglecam
    (x, y, z) , yaw_value, area = xyz_real_value
    
    # Chuyển list yaw_value sang array 
    cnvt_arr = np.array(yaw_value)
    
    Roll =  cnvt_arr[2]
    home_pos = [x[0], y[0], z[0], 0, 0, Roll]
    #print("Area:", area)
    if y[0] != 0:
        timestamps = time.time()
        X.append(y[0])
        # Tính khoảng cách di chuyển giữa các delta_y liên tiếp
        delta_s = np.diff(X, axis=0)
        delta_time = 0.02
        T.append(timestamps)
        delta_t = np.diff(T, axis=0)
        delta_v = delta_s/delta_time
        
        #print("Time stamp", T)
        #print("delta_S:", delta_s)
        #print("delta_T:", delta_t)
        #print("Velocity:", delta_v)
    
    print(home_pos)

    k = cv2.waitKey(1)
    if k % 256 == 27:  # ESC pressed
        print("Exiting...")
        break
print("Velocity:", delta_v[-1])


