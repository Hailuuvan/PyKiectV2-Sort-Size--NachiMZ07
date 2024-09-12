# -Sort-products-by-size-with-Nachi-robot-and-kinectV2

## Tổng quan 
Bài viết này sẽ trình bày việc sử dụng robot Nachi Mz07 kết hợp với hệ thống Camera Kinect để theo dõi và xử lý các vật trên băng tải. Hệ thống sẽ sử dụng xử lý ảnh để cung cấp thông tin về vị trí và kích thước của vật. Bộ điều khiển robot sẽ xử lý các thông tin này để điều khiển robot gắp và phân loại sản phẩm một cách chính xác và hiệu quả.
<img src="https://imgur.com/a/FYh6SG4">
## Camera Calibration
initial_camera_calibration.py sử dụng thư viện openCV để tiến hành calib bằng chessboard

camera_data là nơi lưu trữ các tập tin hiệu chuẩn máy ảnh.

initial_perspective_calibration.py cho phép bạn hiệu chỉnh máy ảnh theo góc nhìn VÀ cho phép bạn kiểm tra độ chính xác của hiệu chỉnh.

## Xử lý ảnh
image_recognition_singlecam.py cho phép trích xuất nền và phát hiện theo dõi đối tượng.

XYZ_realdworldxyz.py lấy các điểm ảnh u,v của vật thể được phát hiện và chuyển đổi chúng thành tọa độ thế giới thực.
## Robot 
run_playback_box.py chạy robot nachi mz07 bằng socket communication (TCP/IP)
