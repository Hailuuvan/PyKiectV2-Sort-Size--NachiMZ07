import socket
import time
import math
import cv2 as cv
import numpy as np

from threading import Thread
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

def get_robot_speed():
    # Gửi yêu cầu lấy thông tin về tốc độ của robot
    M = "O"
    M = bytes(M, 'utf-8')
    sock.sendall(M)
    
    # Nhận dữ liệu về tốc độ từ robot
    data = sock.recv(1024)
    data = data.decode("utf-8")
    speed = str(data)
    
    return speed

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

def P_R(cem): # Hàm này tính toán vị trí thực tế (real-world position) của robot dựa trên một vị trí trong hình ảnh (dựa trên một phép biến đổi ma trận).
    R = np.array([[ -0.0004,    0.7677,   -0.0234], [-0.7720,    0.0017,   -0.0788], [-0.0057,    0.0072,   -0.9816]]) 
    T = np.array([[ -547.5366], [323.6443], [854.3569]])
    P = np.matmul(R,cem)
    P = np.add(P,T)
    return P

socket_initalize()  # Khởi tạo kết nối socket.
tool_coordinate()  # Lấy thông tin vị trí của công cụ của robot.
print("done connect")

count = 0
while True:
    tool_coordinate()
    # Sử dụng hàm để lấy thông tin về tốc độ của robot
    #speed = get_robot_speed()
    #print (speed)
    #print("Point 1")
    start = time.time()
    home_pos = [376, 0, 342, 0, 0, -180]
    # move_robot(home_pos, 1, -5, 284, 180, 0, 0]
    # move_robot(home_pos, 1)
    # home_pos = [151.899, -300.445, 300.832, 0, 0, 0]
    move_robot(home_pos, 3) # Di chuyển robot đến một vị trí cụ thể (home_pos).
    print("Point 1")
    stop = time.time()
    home_pos = [76, -432, 415, 0, 0, -180]
    move_robot(home_pos, 3)
    print(home_pos)

    home_pos = [46.73, -415.57, 360, 0, 0, -180]
    move_robot(home_pos, 3)
    print(home_pos)
    
    print("Thời gian về là: " + str(stop -start))

    start1 = time.time()
    home_pos = [376, -550, 342, 0, 0, -180]
    # move_robot(home_pos, 1, -5, 284, 180, 0, 0]
    # move_robot(home_pos, 1)
    # home_pos = [151.899, -300.445, 300.832, 0, 0, 0]
    move_robot(home_pos, 3) # Di chuyển robot đến một vị trí cụ thể (home_pos).
    print("Point 2")
    stop1 = time.time()

    print("Thời gian đi là: " + str(stop1 -start1))
    count = count+1
    print(str(count)+"--------------------------------------")
    ###
    # Lấy giá trị data[2]
    ###

    #home_pos = [237, -380, 400, 0, 0, -180]
    #move_robot(home_pos, 1) 

    #home_pos = [237, -380, 380, 0, 0, -180]
    #move_robot(home_pos, 1) 

    #IO_robot(10)

    #home_pos = [237, -380, 400, 0, 0, -180]
    #move_robot(home_pos, 1) 

    #home_pos = [237, -480, 400, 0, 0, -180]
    #move_robot(home_pos, 1) 

    #IO_robot(9)
        # move_robot(home_pos, 1, -5, 284, 180, 0, 0]
        # move_robot(home_pos, 1)
        # home_pos = [151.899, -300.445, 300.832, 0, 0, 0]
    #move_robot(home_pos, 5) 
    #print("done position")    
     

    



