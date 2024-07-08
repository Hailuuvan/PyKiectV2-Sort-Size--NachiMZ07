import socket
import time
import math
import cv2 as cv
import numpy as np

from threading import Thread

# Các hằng số và khởi tạo socket
PORT_NUM = 48952
SEND_DATA_SIZE = 8
SEND_BUFFER_LEN = SEND_DATA_SIZE * 6
REC_DATA_SIZE = 12
REC_DATA_NUM = 7
REC_IO_DATA_SIZE = 3
REC_BUFFER_LEN = REC_DATA_SIZE * 6 + REC_IO_DATA_SIZE + REC_DATA_NUM

# Các hằng số cho các chế độ di chuyển
MACHINE_ABS_LINEAR = 1
MACHINE_ABS_JOINT = 2
MACHINE_REALATIVE_LINEAR = 3
MACHINE_REALATIVE_JOINT = 4
JOINT_ABS_LINEAR = 5
JOINT_ABS_JOINT = 6
JOINT_REALATIVE_LINEAR = 7
JOINT_REALATIVE_JOINT = 8
OPEN_COMPRESSED_AIR = 9
CLOSE_COMPRESSED_AIR = 10

def tool_coordinate(sock):
    while True:
        M = "P"
        M = bytes(M, 'utf-8')
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
        time.sleep(0.1)  # Đợi một chút trước khi lấy dữ liệu mới

def move_robot(move_coord, move_mode, sock):
    M = bytes("A", 'utf-8')
    signal = "busy"
    while True:
        sock.sendall(M)
        signal = sock.recv(3)
        if signal == b'REA':
            break
    x = "{0:8.2f}".format(move_coord[0])
    y = "{0:8.2f}".format(move_coord[1])
    z = "{0:8.2f}".format(move_coord[2])
    r = "{0:8.2f}".format(move_coord[3])
    p = "{0:8.2f}".format(move_coord[4])
    ya = "{0:8.2f}".format(move_coord[5])
    mode = "{:0>3d}".format(move_mode)
    message = x + y + z + r + p + ya + mode
    message = bytes(message, 'utf-8')
    sock.sendall(message)
    M = bytes("A", 'utf-8')
    signal = "busy"
    while True:
        signal = sock.recv(3)
        if signal == b'FIN':
            break

def IO_robot(move_mode, sock):
    M = bytes("A", 'utf-8')
    signal = "busy"
    while True:
        sock.sendall(M)
        signal = sock.recv(3)
        if signal == b'REA':
            break
    x = "{0:8.2f}".format(0)
    y = "{0:8.2f}".format(0)
    z = "{0:8.2f}".format(0)
    r = "{0:8.2f}".format(0)
    p = "{0:8.2f}".format(0)
    ya = "{0:8.2f}".format(0)
    mode = "{:0>3d}".format(move_mode)
    message = x + y + z + r + p + ya + mode
    message = bytes(message, 'utf-8')
    sock.sendall(message)
    M = bytes("A", 'utf-8')
    signal = "busy"
    while True:
        signal = sock.recv(3)
        if signal == b'FIN':
            break

def P_R(cem):
    R = np.array([[ -0.0004,    0.7677,   -0.0234], [-0.7720,    0.0017,   -0.0788], [-0.0057,    0.0072,   -0.9816]]) 
    T = np.array([[ -547.5366], [323.6443], [854.3569]])
    P = np.matmul(R,cem)
    P = np.add(P,T)
    return P

def main():
    # Khởi tạo socket và kết nối
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('192.168.1.1', PORT_NUM)
    sock.connect(server_address)

    print("done connect")

    # Khởi tạo và bắt đầu luồng cập nhật thông tin vị trí công cụ
    tool_thread = Thread(target=tool_coordinate, args=(sock,))
    tool_thread.daemon = True  # Đặt luồng này là daemon để nó tự động kết thúc khi chương trình chính kết thúc
    tool_thread.start()

    while True:
        print("Point 1")
        home_pos = [237, -280, 400, 0, 0, -180]
        move_robot(home_pos, 1, sock)  # Di chuyển robot đến vị trí home_pos
        print("done position")
        print("Point 2")
        for y in np.arange(-280, -480, -5):
            home_pos[1] = y
            move_robot(home_pos, 1, sock)
            time.sleep(0.1)  # Đợi một chút trước khi di chuyển tiếp
            print("Moving to y =", y)
        print("done position")

if __name__ == "__main__":
    main()
