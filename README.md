# [IE212.O11.Group7] - Location Recommendation System based on Google Review Rating Prediction

* Trường Đại học Công nghệ Thông tin, Đại học Quốc gia Thành phố Hồ Chí Minh (ĐHQG-HCM)
* Khoa: Khoa học và kỹ thuật thông tin (KTTT)
* GVHD: TS. Đỗ Trọng Hợp
* Nhóm sinh viên thực hiện: Nhóm 7

## Danh sách thành viên
|STT | Họ tên | MSSV| Chức vụ |
|:---:|:-------------:|:-----:|:-----:|
|1. 	| Đặng Huỳnh Vĩnh Tân | 21520442| Nhóm trưởng (Leader)|
|2. 	| Nguyễn Thị Hồng Nhung | 21522436
|3. 	| Nguyễn Viết Kha		|	21520949
|4.  | Nguyễn Huy Hoàng | 21522093

##  Giới thiệu - Introduction
Trong đồ án này, chúng tôi thực hiện xây dựng hệ khuyến nghị nhằm gợi ý địa điểm dựa trên dự đoán điểm đánh giá của các nhận xét trên Google. Chúng tôi sử dụng tập dữ liệu tự thu thập trên các địa bàn ở Thành Phố Hồ Chí Minh để thực hiện và huấn luyện mô hình. Chúng tôi sử dụng mô hình hồi quy để huấn luyện mô hình sau đó dữ liệu này sẽ qua Spark Streaming và Spark SQL để xử lý, truy vấn và trích xuất dữ liệu, và được lưu vào hệ quản trị cơ sở dữ liệu MongoDB. Sau sử dụng mô hình k-Nearest Neighbors (kNN) với thuật toán "Brute Force" để tìm các địa điểm gần nhất.

## Hướng dẫn cài đặt - Running
### Yêu cầu cài đặt trên máy:
* Python
* MongoDB
* Kafka
* 
### B1: Clone repo về máy
```
git clone https://github.com/NunNunIT/IE212.O11.Group7.git  
```
### B2: Chạy tệp 'requirements.txt'
```
pip install -r requirements.txt
```
### B3: Chạy zookeeper, server 
* cd đến thư mục kafka
```
bin\windows\zookeeper-server-start.bat config\zookeeper.properties
```
* mở thêm 1 terminal cd đến thư mục kafka
```
bin\windows\kafka-server-start.bat config\server.properties
```

### B4: Chạy 'producer.ipynb', 'consumer.ipynb' trong thư mục 'src'

### B5: Chạy 'mongoDB.py'
```
cd data_result
```
```
python mongoDB.py 
```

### B6: Chạy 'app.py'
```
cd visualization_app
```
```
python app.py 
```
### B7: Mở website có 2 cách 
* Cách 1: Ctrl + Click vào đường link http://127.0.0.1:8050/ trên terminal
* Cách 2: Mở trình duyệt bất kỳ và dán đường dẫn sau http://127.0.0.1:8050/
