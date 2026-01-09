# Route Evaluation API

REST API để đánh giá vị trí nhà dựa trên khoảng cách và thời gian từ công ty và phòng gym.

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy API Server

### Cách 1: Sử dụng environment variable

```bash
export GOONG_API_KEY='your_goong_api_key'
python api.py
```

### Cách 2: Chạy với uvicorn

```bash
export GOONG_API_KEY='your_goong_api_key'
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: `http://localhost:8000`

## API Endpoints

### 1. Health Check

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

### 2. Evaluate Location

```bash
POST http://localhost:8000/evaluate
```

**Request Body:**
```json
{
  "work_address": "Đại học Thương Mại, Hà Nội",
  "home_address": "Công viên Cầu Giấy, Hà Nội",
  "gym_address": "Bến xe Mỹ Đình, Hà Nội",
  "api_key": "your_goong_api_key"  // Optional nếu đã set env
}
```

**Response:**
```json
{
  "evaluation": 4.22,
  "G": 4.11,
  "T": 4.42,
  "dRate": 0.8222,
  "tRate": 0.8839,
  "distances": {
    "work_home": 1.5,
    "home_gym": 2.3,
    "work_gym": 3.2
  },
  "times": {
    "work_home": 8.5,
    "home_gym": 12.3,
    "work_gym": 18.5
  }
}
```

## Giải thích Response

- **evaluation**: Điểm đánh giá tổng (0-5) - càng cao càng tốt
  - Công thức: `(0.65 × G) + (0.35 × T)`
  - 5.0 là điểm tối đa (nhà nằm giữa công ty và gym)

- **G**: Điểm dựa trên khoảng cách (0-5)
  - Dựa trên tỷ lệ: `dRate = dis_workhome / (dis_workgym + dis_homegym)`
  - G = 5 × dRate

- **T**: Điểm dựa trên thời gian (0-5)
  - Dựa trên tỷ lệ: `tRate = time_workhome / (time_workgym + time_homegym)`
  - T = 5 × tRate

- **dRate**: Tỷ lệ khoảng cách (0-1)
- **tRate**: Tỷ lệ thời gian (0-1)
- **distances**: Khoảng cách (km) giữa các điểm
- **times**: Thời gian di chuyển (phút) giữa các điểm

## Ví dụ sử dụng với curl

```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "work_address": "Đại học Thương Mại, Hà Nội",
    "home_address": "Công viên Cầu Giấy, Hà Nội",
    "gym_address": "Bến xe Mỹ Đình, Hà Nội"
  }'
```

## Ví dụ sử dụng với Python

```python
import requests

url = "http://localhost:8000/evaluate"
data = {
    "work_address": "Đại học Thương Mại, Hà Nội",
    "home_address": "Công viên Cầu Giấy, Hà Nội",
    "gym_address": "Bến xe Mỹ Đình, Hà Nội",
    "api_key": "your_goong_api_key"  # Optional
}

response = requests.post(url, json=data)
result = response.json()

print(f"Điểm đánh giá: {result['evaluation']}/5")
print(f"Điểm khoảng cách (G): {result['G']}/5")
print(f"Điểm thời gian (T): {result['T']}/5")
```

## Interactive API Documentation

Sau khi chạy server, bạn có thể truy cập:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Tại đây bạn có thể test API trực tiếp trong browser!

## Error Handling

API sẽ trả về HTTP status codes:

- `200`: Success
- `400`: Bad request (thiếu API key hoặc địa chỉ không hợp lệ)
- `500`: Internal server error

**Error Response:**
```json
{
  "detail": "Error message here"
}
```
