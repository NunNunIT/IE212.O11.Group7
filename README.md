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

## Bộ dữ liệu
Dữ liệu được thu thập bằng công cụ có sẵn trên trang web https://console.apify.com/

Sử dụng 2 công cụ:
- Lấy dữ liệu địa điểm: ```Google Maps Scraper```
- Lấy dữ liệu đánh giá: ```Google Maps Reviews Scraper```

Dữ liệu thu thập được bao gồm:

- ```data_vi_tphcm/places_HCM_2024.json.gz```: Đây là dữ liệu chứa các địa điểm được tính từ năm 30/01/2024 trở về trước
- ```data_vi_tphcm/reviews_HCM_before_31_01_2024.jsonl.gz```: Đây là dữ liệu chứa các đánh giá của các địa điểm được tính từ 30/01/2024 trở về trước
- ```data_vi_tphcm/reviews_HCM_after_31_01_2024.jsonl.gz```: Đây là dữ liệu chứa các đánh giá của các địa điểm được tính từ 30/01/2024 đến 04/02/2024. Đây cũng chính là bộ dữ liệu được ```producer``` sử dụng để gửi dữ liệu.

Dữ liệu kết quả bao gồm:

- ```data_result/places_results.jsonl.gz```: Đây là dữ liệu chứa các địa điểm được tính từ năm 30/01/2024 trở về trước đã được xử lý.
- ```data_result/review_results.jsonl.gz```: Đây là dữ liệu chứa các đánh giá của các địa điểm được tính từ 30/01/2024 trở về trước đã được xử lý

Dữ liệu có thể tải tại đây: https://drive.google.com/drive/folders/1cPzsr6DJnKSKsKvxrmfRsA0HQgQwn6SQ?usp=drive_link

## Hướng dẫn cài đặt - Running
### Yêu cầu cài đặt trên máy:
* Python
* MongoDB
* Kafka
* 
### B1: Clone repo này về máy với câu lệnh sau:
```
git clone https://github.com/NunNunIT/IE212.O11.Group7.git  
```
### B2: Tải dữ liệu về thư mục ```data_vi_tphcm```
Truy cập https://drive.google.com/drive/folders/1cPzsr6DJnKSKsKvxrmfRsA0HQgQwn6SQ?usp=drive_link và tải 3 file về

Đảm bảo rằng được lưu đúng thư mục ```data_vi_tphcm```

Kết quả sẽ được như này

![image](https://github.com/NunNunIT/IE212.O11.Group7/assets/145759907/6c809140-f78f-4f03-a69f-cdbfc6658154)


### B3: Chạy tệp 'requirements.txt' để cài đặt các package cần thiết
```
pip install -r requirements.txt
```
### B4: Xây dựng cơ sở dữ liệu trên mongoDB 
Truy cập vào thư mục ```data_result```
```
cd data_result
```
Chạy đoạn lệnh sau để xây dựng cơ sở dữ liệu trên MongoDB
```
python mongoDB.py 
```
Líc này ta sẽ được cơ sở dữ liệu như sau
![image](https://github.com/NunNunIT/IE212.O11.Group7/assets/145759907/019e7fbc-efc6-403b-978b-0ee7c640fb13)

### B5: Chạy zookeeper, server kafka
* cd đến thư mục kafka, sau đó thực hiện câu lệnh sau
```
bin\windows\zookeeper-server-start.bat config\zookeeper.properties
```
* mở thêm 1 terminal cd đến thư mục kafka, sau đó thực hiện câu lệnh sau
```
bin\windows\kafka-server-start.bat config\server.properties
```

### B6: Chạy producer và consumer
- Truy cập vào thư mục ```streaming```
- Mở file ```producer.ipynb``` và chạy hết tất cả các cell
    - Lúc này, producer sẽ gửi được các dữ liệu như sau
![image](https://github.com/NunNunIT/IE212.O11.Group7/assets/145759907/d382b58e-7cbf-4a11-92dd-842648b7e4f3)

- Mở file ```consumer.ipynb``` và chạy hết tất cả các cell
    - Lúc này, producer sẽ nhận dữ liệu từ producer và xử lý. Sau đó sẽ thêm records mới vào mongoDB collection ```reviews```
![image](https://github.com/NunNunIT/IE212.O11.Group7/assets/145759907/8cbd6b56-07ec-4f9e-891e-04f2b6ee791c)

### B7: Visualization
- Truy cập vào thư mục ```visualization_app```
```
cd visualization_app
```
- Chạy đoạn lệnh sau 
```
python app.py 
```
Lúc này đây, trang web đã được hoạt động
### B8: Mở website có 2 cách 
* Cách 1: Ctrl + Click vào đường link http://127.0.0.1:8050/ trên terminal
* Cách 2: Mở trình duyệt bất kỳ và dán đường dẫn sau http://127.0.0.1:8050/

## Ảnh app visualization
![Screenshot_8-2-2024_14731_127 0 0 1](https://github.com/NunNunIT/IE212.O11.Group7/assets/145759907/6bb6e810-4f24-49db-9db2-7fe6d03a45ab)

# Thanks
