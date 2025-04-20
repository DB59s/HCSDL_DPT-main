# Hệ Thống Tìm Kiếm Ảnh Núi

Hệ thống này cho phép tìm kiếm và so sánh ảnh núi dựa trên các đặc trưng trực quan. Hệ thống sử dụng nhiều phương pháp trích xuất đặc trưng khác nhau để mô tả ảnh núi và tìm kiếm các ảnh tương tự.

## Yêu Cầu Hệ Thống

- Python 3.6 trở lên
- MongoDB Atlas đã được cấu hình
- Các thư viện Python cần thiết (cài đặt bằng pip):
  ```
  pip install numpy opencv-python scikit-image scikit-learn matplotlib scipy pymongo
  ```

## Cấu Trúc Thư Mục

```
2/
├── mountain_feature_extractor.py  # Mã nguồn chính
├── mountain_images/              # Thư mục chứa ảnh núi
├── feature_visualization/        # Thư mục chứa kết quả trích xuất đặc trưng
├── search_results/              # Thư mục chứa kết quả tìm kiếm
└── README.md                    # Tài liệu hướng dẫn
```

## Cách Sử Dụng

### 1. Chuẩn Bị Dữ Liệu

- Đặt ảnh núi vào thư mục `mountain_images/`
- Đảm bảo ảnh có định dạng jpg hoặc png
- Ảnh nên có kích thước đồng nhất (khuyến nghị 800x600 pixels)

### 2. Chạy Hệ Thống

```bash
# Trích xuất đặc trưng từ một ảnh
python mountain_feature_extractor.py mountain_images/ten_anh.jpg

# Trích xuất đặc trưng từ tất cả ảnh trong thư mục
python mountain_feature_extractor.py mountain_images/
```

### 3. Xử Lý Cơ Sở Dữ Liệu

```bash
# Tạo cơ sở dữ liệu từ các đặc trưng đã trích xuất
python mountain_feature_extractor.py --create-db

# Cập nhật cơ sở dữ liệu với ảnh mới
python mountain_feature_extractor.py --update-db mountain_images/ten_anh_moi.jpg
```

### 4. Tìm Kiếm Ảnh Tương Tự

```bash
# Tìm 3 ảnh tương tự nhất
python mountain_feature_extractor.py --search mountain_images/ten_anh_tim_kiem.jpg --top 3
```

## Các Đặc Trưng Được Sử Dụng

Hệ thống sử dụng nhiều đặc trưng khác nhau để mô tả ảnh núi:

1. **Histogram Màu Sắc**: Mô tả phân bố màu sắc trong ảnh
2. **Đặc Trưng Cạnh**: Phát hiện và mô tả các cạnh trong ảnh
3. **Đặc Trưng Kết Cấu**: Sử dụng HOG để mô tả kết cấu bề mặt
4. **Đặc Trưng Đường Chân Trời**: Phát hiện và mô tả đường chân trời núi
5. **Entropy**: Đo lường độ phức tạp của ảnh

## Cấu Trúc Cơ Sở Dữ Liệu MongoDB

Cơ sở dữ liệu lưu trữ thông tin về ảnh và đặc trưng của chúng:

```json
{
  "image_id": "unique_id",
  "filename": "ten_anh.jpg",
  "features": {
    "color_histogram": [...],
    "edge_features": [...],
    "texture_features": [...],
    "skyline_features": [...],
    "entropy": 0.0
  },
  "metadata": {
    "size": [width, height],
    "date_added": "timestamp"
  }
}
```

## Đánh Giá Kết Quả

Hệ thống sử dụng khoảng cách Euclidean để tính toán độ tương đồng giữa các ảnh. Kết quả tìm kiếm được sắp xếp theo độ tương đồng giảm dần.

## Lưu Ý

- Chất lượng ảnh đầu vào ảnh hưởng đến độ chính xác của kết quả
- Thời gian xử lý phụ thuộc vào kích thước và số lượng ảnh
- Nên sử dụng ảnh có độ tương phản tốt để phát hiện đặc trưng chính xác hơn 