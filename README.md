﻿# attendance_sytem_python


Dự án hệ thống điểm danh sử dụng Python với các thư viện chính như Flask (web framework), OpenCV (xử lý ảnh), face_recognition (nhận diện khuôn mặt), Plotly (vẽ biểu đồ tương tác) và các thư viện hỗ trợ khác.

---

## Mục lục

- [Giới thiệu](#giới-thiệu)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Cách chạy dự án](#cách-chạy-dự-án)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
- [Liên hệ](#liên-hệ)

---

## Giới thiệu

Dự án này cho phép điểm danh tự động bằng nhận diện khuôn mặt thông qua webcam hoặc video, hiển thị kết quả điểm danh, và trực quan hóa dữ liệu điểm danh bằng biểu đồ Plotly.

---

## Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (Python package manager)
- Webcam (nếu sử dụng tính năng nhận diện khuôn mặt trực tiếp)

---

## Cài đặt

1. **Clone dự án về máy:**

```bash
git clone https://github.com/vihackeriue/attendance_sytem_python.git
cd attendance_sytem_python
pip install flask opencv-python face_recognition plotly numpy pandas
