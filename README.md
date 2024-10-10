# -Sort-products-by-size-with-Nachi-robot-and-kinectV2

## Tổng quan 
Bài viết này sẽ trình bày việc sử dụng robot Nachi Mz07 kết hợp với hệ thống Camera Kinect để theo dõi và xử lý các vật trên băng tải. Hệ thống sẽ sử dụng xử lý ảnh để cung cấp thông tin về vị trí và kích thước của vật. Bộ điều khiển robot sẽ xử lý các thông tin này để điều khiển robot gắp và phân loại sản phẩm một cách chính xác và hiệu quả.

<img src="https://github.com/user-attachments/assets/1d8da7a8-d4c9-4b6f-9c0e-2d017d574936" alt="image" width="420" height="594"/>  <img src="https://github.com/user-attachments/assets/0f994760-4a41-4c56-8a37-51437d8a882f" alt="image" width="400" height="470"/> 

## Camera Calibration
initial_camera_calibration.py sử dụng thư viện openCV để tiến hành calib bằng chessboard với thư viện openCV

https://youtu.be/6bInEJoaXcs?si=ZZjm1SabFMTv2ck

camera_data là nơi lưu trữ các tập tin hiệu chuẩn máy ảnh với các thông số
- Ma trận nội máy ảnh: A
- Ma trận ngoại máy ảnh: vecto xoay: R_matrix, vecto tịnh tiến: P_matrix
- Ma trận biến dạng: dist

initial_perspective_calibration.py cho phép bạn hiệu chỉnh máy ảnh theo góc nhìn VÀ cho phép bạn kiểm tra độ chính xác của hiệu chỉnh.
<img src="https://github.com/user-attachments/assets/9b5bb771-984a-4b65-8dbe-890c472ff852" alt="image" width="480" height="270"/>


## Xử lý ảnh
image_recognition_singlecam.py cho phép trích xuất nền và phát hiện theo dõi đối tượng.
Thuật toán được sử dụng:
Trừ nền để phát hiện vật 

<img src="https://github.com/user-attachments/assets/806de522-ce67-459b-9e91-967caa6b26bc" alt="image" width="200" height="480"/> <img src="https://github.com/user-attachments/assets/b464fd6c-ea67-493e-a767-832242adb13e" alt="image" width="200" height="480"/> <img src="https://github.com/user-attachments/assets/0f495574-4738-40b6-beca-20fa1644105f" alt="image" width="200" height="480"/> 

https://youtu.be/Gbukzy9y9cw?si=_Ta6uk0iaHcdQyAm 

XYZ_realdworldxyz.py lấy các điểm ảnh u,v của vật thể được phát hiện và chuyển đổi chúng thành tọa độ thế giới thực.
## Robot 
run_playback_box.py chạy robot nachi mz07 bằng socket communication (TCP/IP)

## Video
Video vận hành của hệ thống tự động hóa tích hợp robot
https://youtu.be/x3ea0XP4V-4?si=l6ZuuDo3SCizVely 

## SQL sever
Quy trình thu thập dữ liệu bằng SQL Server

<img src="https://github.com/user-attachments/assets/178fc908-009b-40a3-bbf9-7252e1824d19" alt="image" width="350" height="300"/>

