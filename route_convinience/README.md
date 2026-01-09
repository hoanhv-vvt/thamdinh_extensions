# Route Evaluation API

REST API để đánh giá vị trí nhà dựa trên khoảng cách và thời gian từ công ty và phòng gym sử dụng **Goong Maps API**.

## Tính năng

✨ **Geocoding**: Chuyển đổi địa chỉ văn bản thành tọa độ  
📏 **Tính khoảng cách**: Sử dụng Goong Maps Distance Matrix API  
⏱️ **Tính thời gian**: Thời gian di chuyển dự kiến  
⚙️ **Thang điểm tùy chỉnh**: Cấu hình thang điểm qua file `.env`  

## Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd route_convinience
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình file .env
```bash
# Tạo file .env từ template
cp .env.example .env

# Chỉnh sửa file .env
nano .env
```

**File .env:**
```bash
GOONG_API_KEY=your_goong_api_key_here
MAX_SCALE=5  # Thang điểm tối đa (5, 10, 100, etc.)
```

### 4. Lấy Goong Maps API Key

1. Truy cập: https://account.goong.io
2. Đăng ký/đăng nhập
3. Tạo API key cho REST API
4. Copy key vào file `.env`

## Chạy ứng dụng

### Chạy API Server

```bash
# Cách 1: Chạy trực tiếp
python api.py

# Cách 2: Chạy với uvicorn
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: `http://localhost:8000`

### Chạy script test

```bash
# Test với địa điểm mặc định
python get_3_point.py

# Test với 10 địa điểm ở Hà Nội
python test_hanoi.py

# Test với các thang điểm khác nhau
python test_scales.py
```

## API Documentation

### Interactive Docs
Sau khi chạy server, truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### 1. Health Check
```bash
GET http://localhost:8000/
```

**Response:**
```json
{
  "status": "running",
  "message": "Route Evaluation API is running"
}
```

#### 2. Evaluate Location
```bash
POST http://localhost:8000/evaluate
```

**Request Body:**
```json
{
  "work_address": "Đại học Thương Mại, Hà Nội",
  "home_address": "Công viên Cầu Giấy, Hà Nội",
  "gym_address": "Bến xe Mỹ Đình, Hà Nội",
  "api_key": "optional_if_set_in_env",
  "max_scale": 5
}
```

**Response:**
```json
{
  "evaluation": 4.22,
  "G": 4.11,
  "T": 4.42
}
```

### Giải thích kết quả

- **evaluation**: Điểm đánh giá tổng (0 - MAX_SCALE)
  - Công thức: `(0.65 × G) + (0.35 × T)`
  - Càng cao = vị trí càng thuận tiện
  - MAX_SCALE là điểm tối đa khi nhà nằm giữa công ty và gym

- **G**: Điểm dựa trên khoảng cách (0 - MAX_SCALE)
  - `dRate = dis_workhome / (dis_workgym + dis_homegym)`
  - `G = MAX_SCALE × dRate`

- **T**: Điểm dựa trên thời gian (0 - MAX_SCALE)
  - `tRate = time_workhome / (time_workgym + time_homegym)`
  - `T = MAX_SCALE × tRate`

### Thang điểm tùy chỉnh

Bạn có thể thay đổi thang điểm theo 3 cách:

**1. Qua file .env (Khuyến nghị)**
```bash
# .env
MAX_SCALE=10  # Thang 10
```

**2. Qua API request**
```json
{
  "work_address": "...",
  "home_address": "...",
  "gym_address": "...",
  "max_scale": 100  // Override thành thang 100
}
```

**3. Trực tiếp trong code**
```python
evaluation, G, T, dRate, tRate = calculate_points_G_n_T(
    ...,
    max_scale=10  # Thang 10
)
```

## Ví dụ sử dụng

### Với curl
```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "work_address": "Đại học Thương Mại, Hà Nội",
    "home_address": "Công viên Cầu Giấy, Hà Nội",
    "gym_address": "Bến xe Mỹ Đình, Hà Nội"
  }'
```

### Với Python
```python
import requests

url = "http://localhost:8000/evaluate"
data = {
    "work_address": "Đại học Thương Mại, Hà Nội",
    "home_address": "Công viên Cầu Giấy, Hà Nội",
    "gym_address": "Bến xe Mỹ Đình, Hà Nội",
    "max_scale": 10  # Optional
}

response = requests.post(url, json=data)
result = response.json()

print(f"Điểm đánh giá: {result['evaluation']}/10")
```

### Import vào project khác
```python
from get_3_point import RouteCalculator, calculate_points_G_n_T

# Khởi tạo
calculator = RouteCalculator(api_key='your_key')

# Geocode 3 địa chỉ
locations = calculator.geocode_multiple_addresses([
    "địa chỉ 1",
    "địa chỉ 2", 
    "địa chỉ 3"
])

# Tính khoảng cách và thời gian
distances, times = calculator.get_distances_and_times(
    locations[0], 
    locations[1], 
    locations[2],
    vehicle='bike'
)

# Tính điểm đánh giá
evaluation, G, T, dRate, tRate = calculate_points_G_n_T(
    distances['1->2'], times['1->2'],
    distances['2->3'], times['2->3'],
    distances['1->3'], times['1->3'],
    max_scale=5
)
```

## Cấu trúc thư mục

```
route_convinience/
├── api.py                 # FastAPI server
├── get_3_point.py         # Core logic - RouteCalculator class
├── test_hanoi.py          # Test với 10 địa điểm ở Hà Nội
├── test_scales.py         # Test các thang điểm khác nhau
├── requirements.txt       # Python dependencies
├── .env.example          # Template cho .env
├── .env                  # API key (không commit)
├── .gitignore            # Git ignore rules
└── README.md             # Documentation
```

## Error Handling

API trả về HTTP status codes:

- `200`: Success
- `400`: Bad request (thiếu API key hoặc địa chỉ không hợp lệ)
- `500`: Internal server error

**Error Response:**
```json
{
  "detail": "Error message here"
}
```

## Lưu ý bảo mật

⚠️ **QUAN TRỌNG:**
- File `.env` đã được thêm vào `.gitignore`
- **KHÔNG BAO GIỜ** commit file `.env` vào Git
- Chỉ commit file `.env.example` (không chứa API key thật)
- Mỗi môi trường nên có file `.env` riêng

## Changelog

### v1.1.0 (2026-01-09)
- ✨ Thêm tính năng thang điểm tùy chỉnh (`MAX_SCALE`)
- ⚙️ Cấu hình qua file `.env`
- 📝 Cập nhật API để hỗ trợ `max_scale` parameter
- 🧪 Thêm test scripts cho nhiều kịch bản

### v1.0.0
- 🎉 Release đầu tiên
- 🗺️ Tích hợp Goong Maps API
- 📊 Tính toán đánh giá vị trí nhà
- 🚀 REST API với FastAPI

## License

MIT License

## Support

Nếu gặp vấn đề, vui lòng tạo issue trên GitHub hoặc liên hệ qua email.
