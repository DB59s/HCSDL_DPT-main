# Hệ Thống Nhận Dạng Ảnh Đồi Núi - Tổng Quan Triển Khai

Tài liệu này cung cấp tổng quan chi tiết về việc triển khai hệ thống nhận dạng ảnh đồi núi của chúng tôi.

## Tổng Quan Hệ Thống

Chúng tôi đã triển khai một hệ thống toàn diện để nhận dạng ảnh đồi núi và tìm kiếm tương đồng:
1. Trích xuất các đặc trưng có ý nghĩa từ ảnh đồi núi
2. Lưu trữ vector đặc trưng hiệu quả
3. Tìm kiếm ảnh đồi núi tương tự dựa trên ảnh truy vấn
4. Trực quan hóa cả quá trình trích xuất đặc trưng và kết quả tìm kiếm tương đồng

## Chi Tiết Triển Khai

### 1. Trích Xuất Đặc Trưng (`mountain_feature_extractor.py`)

Hệ thống trích xuất đặc trưng của chúng tôi nắm bắt nhiều khía cạnh của ảnh đồi núi:

#### a. Đặc trưng màu sắc
- Biểu đồ màu HSV (32 bins cho mỗi kênh)
- Biểu diễn tốt hơn cho cảnh quan thiên nhiên so với RGB
- Tách biệt tông màu (hue) khỏi độ sáng (value) và độ bão hòa (saturation)

#### b. Đặc trưng cạnh
- Mật độ cạnh đo lường tỷ lệ các pixel cạnh trong ảnh
- Biểu đồ hướng cạnh nắm bắt các hình dạng và góc độ chiếm ưu thế
- Đặc biệt hiệu quả cho các đường núi và đường viền

#### c. Đặc trưng kết cấu
- HOG (Biểu đồ độ dốc hướng) nắm bắt các mẫu kết cấu cục bộ
- Hiệu quả để phân biệt giữa bề mặt đá, tuyết hoặc thực vật
- Cung cấp thông tin không gian về phân bố kết cấu

#### d. Đặc trưng đường chân trời
- Phát hiện đường viền núi nổi bật trên nền trời
- Nắm bắt đường nét hình dạng tổng thể của núi
- Bao gồm các chỉ số về độ gồ ghề của đường chân trời và chiều cao trung bình

#### e. Entropy
- Đo lường độ phức tạp tổng thể của ảnh
- Giá trị cao hơn chỉ ra cảnh núi phức tạp, chi tiết hơn
- Đóng vai trò như đặc trưng toàn cục bổ sung cho các đặc trưng cục bộ

### 2. Lưu Trữ và Quản Lý Đặc Trưng (`extract_all_features.py`)

Các đặc trưng được trích xuất từ tất cả ảnh trong bộ dữ liệu và lưu trữ theo hai định dạng:
- Định dạng nhị phân (pickle) để tải và xử lý hiệu quả
- Định dạng CSV để dễ dàng kiểm tra và phân tích

Ngoài ra, chúng tôi tạo ra các trực quan hóa của quá trình trích xuất đặc trưng cho một số ảnh được chọn, hiển thị:
- Ảnh gốc
- Biểu đồ màu sắc
- Phát hiện cạnh
- Độ lớn độ dốc
- Phát hiện đường chân trời
- Bản đồ entropy

### 3. Tìm Kiếm Tương Đồng (`similarity_search.py`)

Cài đặt tìm kiếm tương đồng của chúng tôi:
- Chuẩn hóa vector đặc trưng để đảm bảo kích thước nhất quán
- Sử dụng khoảng cách Euclidean để đo lường độ tương đồng giữa các vector đặc trưng
- Loại trừ ảnh truy vấn khỏi kết quả nếu nó nằm trong cơ sở dữ liệu
- Xếp hạng kết quả theo khoảng cách tăng dần (độ tương đồng giảm dần)
- Trực quan hóa ảnh truy vấn cùng với các ảnh phù hợp nhất

### 4. Chuẩn Hóa và Tính Toán Khoảng Cách

Để xử lý các vector đặc trưng có độ dài khác nhau:
- Xác định độ dài vector đặc trưng phổ biến nhất trong cơ sở dữ liệu
- Vector dài hơn sẽ bị cắt ngắn và vector ngắn hơn sẽ được đệm bằng số 0
- Khoảng cách Euclidean được tính toán trên các vector đã được chuẩn hóa

Cách tiếp cận này đảm bảo rằng chúng ta có thể so sánh bất kỳ ảnh đồi núi nào với cơ sở dữ liệu của chúng tôi, ngay cả khi quá trình trích xuất đặc trưng tạo ra các vector có độ dài khác nhau.

## Kết Quả và Hiệu Suất

Hệ thống thành công trong việc:
- Trích xuất các đặc trưng có ý nghĩa từ tất cả 100 ảnh đồi núi
- Tạo ra các trực quan hóa đặc trưng làm nổi bật các khía cạnh khác nhau của ảnh
- Tìm kiếm ảnh đồi núi tương tự dựa trên sự tương đồng về đặc trưng
- Xử lý mạnh mẽ các vector đặc trưng có kích thước khác nhau

Độ đo khoảng cách hiệu quả nắm bắt sự tương đồng trực quan, như được chứng minh bởi các kết quả hiển thị trong các trực quan hóa tương đồng.

## Cải Tiến Tiềm Năng

Các cải tiến trong tương lai có thể bao gồm:
1. Gán trọng số đặc trưng để tăng tầm quan trọng cho một số loại đặc trưng nhất định
2. Kỹ thuật giảm chiều (PCA, t-SNE) để cải thiện hiệu quả
3. Độ đo tương đồng nâng cao hơn (khoảng cách Mahalanobis, độ tương đồng cô-sin)
4. Các phương pháp học máy (SVM, mạng nơ-ron) cho phân loại
5. Giao diện người dùng tương tác để khám phá cơ sở dữ liệu ảnh đồi núi

## Kết Luận

Hệ thống nhận dạng ảnh đồi núi của chúng tôi đã triển khai thành công các chức năng cần thiết để trích xuất đặc trưng và tìm kiếm ảnh đồi núi tương tự. Sự kết hợp giữa các đặc trưng màu sắc, cạnh, kết cấu, đường chân trời và entropy cung cấp một biểu diễn mạnh mẽ về ảnh đồi núi, cho phép tìm kiếm tương đồng hiệu quả. 