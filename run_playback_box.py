import socket
import time
import math
import cv2 
import numpy as np
import pyodbc
from pykinect2 import PyKinectV2, PyKinectRuntime

import image_recognition_singlecam
import XYZ_realworld

import threading 
# define constants for socket commnuncation
PORT_NUM = 48952
SEND_DATA_SIZE = 8
SEND_BUFFER_LEN = SEND_DATA_SIZE * 6
REC_DATA_SIZE = 12
REC_DATA_NUM = 7
REC_IO_DATA_SIZE = 3
REC_BUFFER_LEN = REC_DATA_SIZE * 6 + REC_IO_DATA_SIZE + REC_DATA_NUM

# define a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #  tùy chọn socket.AF_INET (để sử dụng IPv4) và socket.SOCK_STREAM (để sử dụng giao thức TCP)
server_address = (('192.168.1.1', PORT_NUM))

MACHINE_ABS_LINEAR = 1  # MOVE BY ABS COORDINATE VALUE RESPECT MACHINE COORDINATE FRAME USING LINEAR INTERPOLATION
MACHINE_ABS_JOINT = 2  # ...
MACHINE_REALATIVE_LINEAR = 3  # ...
MACHINE_REALATIVE_JOINT = 4  # MOVE BY REALATIVE COORDINATE VALUE RESPECT MACHINE COORDINATE FRAME USING JOINT INTERPOLATION

JOINT_ABS_LINEAR = 5  # MOVE BY ABS COORDINATE VALUE RESPECT JOINT COORDINATE FRAME USING LINEAR INTERPOLATION
JOINT_ABS_JOINT = 6  # ...
JOINT_REALATIVE_LINEAR = 7  # ...
JOINT_REALATIVE_JOINT = 8  # MOVE BY REALATIVE COORDINATE VALUE RESPECT JOINT COORDINATE FRAME USING JOINT INTERPOLATION

OPEN_COMPRESSED_AIR = 9
ClOSE_COMPRESSED_AIR = 10
def socket_initalize(): # Hàm này được sử dụng để khởi tạo kết nối socket với máy chủ có địa chỉ và cổng được xác định trước.
    # server_address = (('localhost', PORT_NUM))
    print('Connecting to {} port {}'.format(*server_address))
    # Connect the socket to the port where the server is listening

    sock.connect(server_address)


def tool_coordinate(): # Hàm này gửi yêu cầu lấy thông tin vị trí của công cụ của robot và sau đó in thông tin này ra màn hình
    M = "P"
    M = bytes(M, 'utf-8')
    # M = M.decode('utf-8')
    sock.sendall(M)
    data = sock.recv(1024)
    data = data.decode("utf-8")
    data = data.split(",")
    print("-----------------------")
    print("Current Tool Position")
    print("-----------------------")

    print(data[0])
    print(data[1])
    print(data[2])
    print('Roll :  ', data[3])
    print('Pitch:  ', data[4])
    print('Yaw  :  ', data[5])

def move_robot(move_coord, move_mode):
    # wait for machine 'REA'DY status
    M = bytes("A", 'utf-8')
    signal = "busy"
    while True:
        sock.sendall(M)
        signal = sock.recv(3)
        if signal == b'REA':
            break
    # data preparation
    x = "{0:8.2f}".format(move_coord[0])
    y = "{0:8.2f}".format(move_coord[1])
    z = "{0:8.2f}".format(move_coord[2])
    r = "{0:8.2f}".format(move_coord[3])
    p = "{0:8.2f}".format(move_coord[4])
    ya = "{0:8.2f}".format(move_coord[5])
    mode = "{:0>3d}".format(move_mode)
    # binding data and converting
    message = x + y + z + r + p + ya + mode
    message = bytes(message, 'utf-8')
    # send
    sock.sendall(message)
    # wait for machine 'FIN'ISH status
    M = bytes("A", 'utf-8')
    signal = "busy"
    while True:
        signal = sock.recv(3)
        if signal == b'FIN':
            break
def IO_robot(move_mode): # hàm này dùng để điều khiển các I/O (Input/Output) của robot.
    # wait for machine 'REA'DY status
    M = bytes("A", 'utf-8')
    signal = "busy"
    while True:
        sock.sendall(M)
        signal = sock.recv(3)
        if signal == b'REA':
            break
    # data preparation
    x = "{0:8.2f}".format(0)
    y = "{0:8.2f}".format(0)
    z = "{0:8.2f}".format(0)
    r = "{0:8.2f}".format(0)
    p = "{0:8.2f}".format(0)
    ya = "{0:8.2f}".format(0)
    mode = "{:0>3d}".format(move_mode)
    # binding data and converting
    message = x + y + z + r + p + ya + mode
    message = bytes(message, 'utf-8')
    # send
    sock.sendall(message)
    # wait for machine 'FIN'ISH status
    M = bytes("A", 'utf-8')
    signal = "busy"
    while True:
        signal = sock.recv(3)
        if signal == b'FIN':
            break


socket_initalize()  # Khởi tạo kết nối socket.
tool_coordinate()  # Lấy thông tin vị trí của công cụ của robot.
print("done connect")
def truncate(self, n, decimals=0):
    n=float(n)
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier
# >>==================================== VISION============================================<<
# Initialize Kinect
kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color)
image_recog = image_recognition_singlecam.image_recognition()
XYZ = XYZ_realworld.XYZ_realworld()


# New size
new_width = 1920
new_height = int(new_width / 16 * 9)

def convert_RGBA_to_RGB(image_RGBA):
    # Creates an empty array the same size as the input image, but with only 3 color channels
    image_RGB = np.zeros((image_RGBA.shape[0], image_RGBA.shape[1], 3), dtype=np.uint8)

    # Sao chép dữ liệu từ 3 kênh màu đầu tiên (R, G, B) của hình ảnh RGBA sang hình ảnh RGB
    image_RGB[:,:,0:3] = image_RGBA[:,:,0:3]
    
    return image_RGB
# Lưu 5 frame gần nhất 
frame_buffer = []
while len(frame_buffer) < 5:
    if kinect.has_new_color_frame():
        color_frame = kinect.get_last_color_frame()
        color_image = color_frame.reshape((kinect.color_frame_desc.Height, kinect.color_frame_desc.Width, 4)).astype(np.uint8)
        frame_buffer.append(convert_RGBA_to_RGB(color_image))

# Chọn frame cuối cùng làm frame ban đầu
frame_init = frame_buffer[-1]
roi_init = frame_init[0:1080, 1000:1350]

buffer_size = 10
frames_buffer = []

count_box1 = 0
count_box2 = 0
count = 0
Box = 0

#===============================>>CLOUD<<===========================
# Thông tin kết nối tới SQL Server
server = 'DESKTOP-DELLCUA\SQLEXPRESS'
database = 'FinalProject'
username = 'sa'
password = 'scadanhom7'

# Chuỗi kết nối
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Tạo kết nối
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

if __name__ == '__main__':
    home_pos = [237, -280, 400, 0, 0, -180]
    print(home_pos)
    print("done position")
    move_robot(home_pos, 1)
    while True:
        start_time = time.time()
        print("Thoi gian bat dau : "+ str(start_time))
        toggle_time = 2  # 4 giây
        while True:
            # Kiểm tra xem có frame mới từ camera Kinect không
            if kinect.has_new_color_frame() and (time.time() - start_time < toggle_time):
                start_xla=time.time()
                # Nhận frame mới nhất từ camera Kinect
                color_frame = kinect.get_last_color_frame()
                
                # Chuyển đổi dữ liệu frame từ ctypes sang numpy array
                color_image = color_frame.reshape((kinect.color_frame_desc.Height, kinect.color_frame_desc.Width, 4)).astype(np.uint8)
                
                frame_RGB = convert_RGBA_to_RGB(color_image)
                
                # Resize hình ảnh để hiển thị với kích thước mới
                resized_image = cv2.resize(color_image, (new_width, new_height))
                
                roi_frame = frame_RGB[0:1080, 1000:1350]
                
                #image_recog.run_detection(roi_frame, roi_init)
                obj_count, detected_points, img_output = image_recog.run_detection(roi_frame, roi_init)
                # Đợi một lượng thời gian nhỏ trước khi xử lý frame tiếp theo
                cv2.waitKey(100)
                stop_xla=time.time()
                print("Come here........")
                print("Thời gian xử lý ảnh:"+str(stop_xla-start_xla))
                # Gửi dữ liệu đếm vào SQL sever
                #lngValue2 = count_box2
                sql_insert_query3 = """INSERT INTO CycleTime (Name, Value, Time) VALUES (?, ?, GETDATE())"""
                strh = stop_xla-start_xla
                cursor.execute(sql_insert_query3, 'xla', truncate(strh,4))
                # Lưu thay đổi vào cơ sở dữ liệu
                conn.commit()
                # Hiển thị hình ảnh
                # cv2.imshow("Kinect Color", resized_image)
                xyz_real_value = image_recog.get_XYZ_real()
                #cv2.imshow('frame', frame)
                (x, y, z) , yaw_value, area = xyz_real_value
                # Chuyển list yaw_value sang array 
                cnvt_arr = np.array(yaw_value)


                off_time = time.time()
                print("Thoi gian ket thuc : "+ str(off_time))
                
                 
                timming = off_time - start_time
                print("Thoi gian chay: ",timming)

                if timming > toggle_time:
                    print("Exiting...")
                    break

                k = cv2.waitKey(1)
                if k%256 == 27:              # ESC pressed to exit
                    print("Exiting...")
                    #move_robot(home_pos, 1)
                    print("Done")
                    
                    break

            
            # Array <>= float (compare)
            
            Roll =  cnvt_arr[2]
            #print(cnvt_arr)
            #print(type(yaw_value[2]))
            #delta_y = 12.5*10*0.85
            t_lin = 0
            delta_y = 100
            print(delta_y)
            y2 = y[0]*10 - delta_y
            z2 = 324
            y_h = -280
            z_h = 400
            v_lin = 125
            v_bangtai = 40
            
            distance = np.sqrt((y2 - y_h) ** 2 + (z2 - z_h) ** 2)
            
            t2 = distance / v_lin
            start_qtdc= time.time()
            home_pos = [x[0]*10, y[0]*10 - delta_y, 370, Roll , 0, -180]
            print(home_pos)
            
            t1 = delta_y / v_bangtai
            

            #home_pos = [x[0]*10, y[0]*10, 370, 0, 0, -180]
            #print(home_pos)
                
            # Di chuyển robot đến một vị trí cụ thể (home_pos).
            frames_buffer.append(resized_image)

            # Kiểm tra kích thước của buffer và giải phóng bộ nhớ nếu cần thiết
            if len(frames_buffer) > buffer_size:
                # Xử lý dữ liệu hoặc thực hiện các thao tác cần thiết trên buffer
                # Giải phóng bộ nhớ của các frame cũ
                frames_buffer.pop(0)
                color_frame = None
        print("distance: ",distance)    
        print("t2: " , t2)
        print("t1: ", t1)
        start_rb = time.time()       
        
        print(" Area: ", area)
        #------------------ phan loai -------------------
        if area == 110:
            count_box1 = count_box1  + 1 
            print("-------- Box 1-----------")
            Box = 1
            # Gửi dữ liệu đếm vào SQL sever
            lngValue1 = count_box1
            sql_insert_query1 = """INSERT INTO data_cloud (Name, Value, Time) VALUES (?, ?, GETDATE())"""
            cursor.execute(sql_insert_query1, 'Large', lngValue1)
            # Lưu thay đổi vào cơ sở dữ liệu
            conn.commit()
            print("Record inserted successfully.")
            
            
        elif area == 75:
            count_box2 = count_box2  + 1 
            print("-------- Box 2-----------")
            Box = 2
            # Gửi dữ liệu đếm vào SQL sever
            lngValue2 = count_box2
            sql_insert_query2 = """INSERT INTO data_cloud (Name, Value, Time) VALUES (?, ?, GETDATE())"""
            cursor.execute(sql_insert_query2, 'Small', lngValue2)
            # Lưu thay đổi vào cơ sở dữ liệu
            conn.commit()
            print("Record inserted successfully.")
            
        #------------------------------------------------

        
        if obj_count > 0:
            count= count +1
            print("-----------Số vật đã đếm:   ", count)
            while True:
                #------------------an toan--------------------
                if y[0]*10- delta_y <= -548:
                    IO_robot(15)
                    print(" Vuot qua gia tri y cho phep!!!")
 
                    break
                #####
                time_rb= time.time() 
                print(".....Start.....")
                print(home_pos)
                move_robot(home_pos, 3)

                if (time_rb - start_rb ) >= np.abs(t1-t2)-0.8:
                    
                    #home_pos = [x[0]*10, y[0]*10, 370, Roll, 0, -180]
                    #print(home_pos)
                    #move_robot(home_pos, 5)

                    home_pos = [x[0]*10, y[0]*10 - delta_y , 324, Roll, 0, -180]
                    print(home_pos)
                    move_robot(home_pos, 3)
                    print("done Point 1")
                    
                    
                    #-----------------di chuyển theo------------------------
                    home_pos = [x[0]*10, y[0]*10 - delta_y - 50, 324, Roll, 0, -180]
                    move_robot(home_pos, 6)


                    IO_robot(10)
                    print("Open IO")

                    home_pos = [x[0]*10, y[0]*10- delta_y - 50, 400, Roll, 0, -180]
                    print(home_pos)
                    move_robot(home_pos, 3)
                    


                    #home_pos = [46.73, -415.57, 360, 0, 0, -180]
                    #print(home_pos)
                    #print("done position")
                    #move_robot(home_pos, 3)
                    
                    #if count >= 4:
                    #   home_pos = [48.24, -502.52, 360, 0, 0, -180]
                    #   print(home_pos)
                    #   print("done position")
                    #   move_robot(home_pos, 3)

                    print(" Box = ", Box)
                    
                    #---------------------------------------
                    if Box == 1:
                        print("Count Box 1 = ", count_box1)
                        '''
                        home_pos = [95.07, -341.52, 400, 0, 0, -180]
                        print(home_pos)
                        print("done position")
                        move_robot(home_pos, 1)
                        '''
                        IO_robot(13)
                        if count_box1 %4 == 1:
                            home_pos = [95.07, -341.52, 400, 0, 0, -180]
                            move_robot(home_pos, 1)

                            home_pos = [95.07, -341.52, 236.4, 0, 0, -180]
                            print(home_pos)
                            print("Box 1: ",(count_box1 ))
                            move_robot(home_pos, 1)

                        if count_box1 %4 == 2:
                            home_pos = [-33.25, -341.52, 400, 0, 0, -180]
                            move_robot(home_pos, 1)

                            home_pos = [-33.25, -341.52, 236.4, 0, 0, -180]
                            print(home_pos)
                            print("Box 1: ",(count_box1) )
                            move_robot(home_pos, 1)

                        if count_box1 %4 == 3:
                            home_pos = [95.07, -341.52, 400, 0, 0, -180]
                            move_robot(home_pos, 1)

                            home_pos = [95.07, -341.52, 275.17, 0, 0, -180]
                            print(home_pos)
                            print("Box 1: ", (count_box1 ))
                            move_robot(home_pos, 1)

                        if count_box1 %4 == 0:
                            home_pos = [-33.25, -341.52, 400, 0, 0, -180]
                            move_robot(home_pos, 1)

                            home_pos = [-33.25, -341.52, 275.17, 0, 0, -180]
                            print(home_pos)
                            print("Box 1: ", (count_box1 ))
                            move_robot(home_pos, 1)
                        
                        IO_robot(9)
                        print("Closed IO")
                        
                    
                        home_pos = [95.07, -341.52, 400, 0, 0, -180]
                        print(home_pos)
                        print("done position")
                        move_robot(home_pos, 1)


                    #----------------------------------------
                    if Box == 2:
                        print("Count Box 2 = ", count_box2)
                        IO_robot(14)
                        home_pos = [60.25, -543.9, 400, 0, 0, -180]
                        print(home_pos)
                        print("done position")
                        move_robot(home_pos, 1)
                        
                        if count_box2 %3 == 1:
                            home_pos = [60.25, -543.9, 231.89, 0, 0, -180]
                            print(home_pos)
                            print("Box 2: ",(count_box2))
                            move_robot(home_pos, 1)
                        
                        if count_box2 %3 == 2:
                            home_pos = [60.25, -543.9, 275.2, 0, 0, -180]
                            print(home_pos)
                            print("Box 2: ",(count_box2) )
                            move_robot(home_pos, 1)

                        if count_box2 %3 == 0:
                            home_pos = [60.25, -543.9, 315.12, 0, 0, -180]
                            print(home_pos)
                            print("Box 2: ", (count_box2))
                            move_robot(home_pos, 1)

                        IO_robot(9)
                        print("Closed IO")
                        
                        home_pos = [60.25, -543.9, 400, 0, 0, -180]
                        print(home_pos)
                        print("done position")
                        move_robot(home_pos, 1)

                
                    #----------------------------------------

                    #if count == 4:
                        #home_pos = [-67.39, -447.74, 300, 0, 0, -180]
                        #print(home_pos)
                        
                        #move_robot(home_pos, 1)
                        #home_pos = [-67.39, -447.74, 230, 0, 0, -180]
                        #print(home_pos)
                        #print("done position ", (count))
                        #move_robot(home_pos, 1)
                    
                    ######

                    #--------- HOME-----------
                    home_pos = [237, -280, 400, 0, 0, -180]
                    print(home_pos)
                    print("Home")
                    move_robot(home_pos, 1)
                    #-------------------------
                    stop_qtdc= time.time()

                    print("Quá trình di chuyển: "+str(stop_qtdc-start_qtdc))

                    print("Done.....")

                    break
                
            
cv2.destroyAllWindows()   
            
            



