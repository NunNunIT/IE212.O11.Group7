# [IE212.O11.Group7] - Tên đề tài

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
Nội dung TEXT TEXT viết sau

**Data Source**: https://cseweb.ucsd.edu/~jmcauley/datasets.html#google_local

**In collaboration with**: [Shiyi Hua](https://www.linkedin.com/in/shiyi-letty-hua-2a7117129/), [Ziyuan Yan](https://www.linkedin.com/in/ziyuan-esther-yan-664732132/)

**Models**:
Nội dung

## Hướng dẫn cài đặt - Running
### B1: Clone repo 

```
git clone https://github.com/NunNunIT/IE212.O11.Group7.git  
```
### B2: Tải dataset
Vì dataset quá lớn nên có thể không clone 3 file dataset về được. Thực hiện các bước sau

**Lưu ý:** Phải tải về trong thư mục ```data```

Truy cập: https://jmcauley.ucsd.edu/data/googlelocal/
- users.clean.json.gz
- reviews.clean.json.gz
- places.clean.json.gz

Hoặc 

Truy cập https://cseweb.ucsd.edu/~jmcauley/datasets.html#google_local

Tìm kiếm Crtl + F: 
``` 
Google Local Reviews (2018) 
```
Tải các file về


### B3: Truy cập vào file model.ipynb trong thư mục model

Chạy file

### B4: Visualization bằng RStudio
- Cài đặt RSTUDIO
    - B1: Truy cập https://cran.r-project.org/ và lựa chọn phiên bản phù hợp
    - B2: Truy cập https://posit.co/download/rstudio-desktop/ và lựa chọn phiên bản phù hợp
    - B3: Chạy phần mềm RStudio
    - B4: Open File -> Chọn file Visualization.Rmd
    - B5: Tại tab console log, copy đoạn mã dưới đây và enter
      ```
      install.packages("readr")
      install.packages("tidyverse")
      install.packages("rkafka")
      install.packages("leaflet")
      install.packages("googleway")
      install.packages("ggmap")
      install.packages("ggimage")
      ```
    - B5: Chọn Knit to HTML (Biểu tượng cuộn len màu xanh dương) và đợi

## Sản phẩm - 
File report
Nhận định blah blah
 
## Tham khảo - References
Translation-based factorization machines for sequential recommendation
Rajiv Pasricha, Julian McAuley
RecSys, 2018
[pdf](https://cseweb.ucsd.edu/~jmcauley/pdfs/recsys18a.pdf)

Translation-based recommendation
Ruining He, Wang-Cheng Kang, Julian McAuley
RecSys, 2017
[pdf](https://cseweb.ucsd.edu/~jmcauley/pdfs/recsys17.pdf)
