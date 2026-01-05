# 🗺️ Google Maps Image Crawler

Công cụ crawl ảnh từ Google Maps sử dụng Playwright - **HOÀN TOÀN MIỄN PHÍ**, không cần API key.

## ✨ Tính năng

- ✅ Crawl ảnh từ Google Maps chỉ với địa chỉ
- ✅ Tự động tìm kiếm và trích xuất ảnh chất lượng cao
- ✅ Hỗ trợ CLI và chế độ interactive
- ✅ Retry logic khi tải ảnh thất bại
- ✅ Tên file tự động từ địa chỉ
- ✅ Không cần API key, không tốn phí

## 📦 Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cài đặt Playwright browser

```bash
playwright install chromium
```

## 🚀 Sử dụng

### Chế độ Interactive (Dễ nhất)

```bash
python main.py
```

Sau đó nhập địa chỉ và các thông số khi được hỏi.

### Chế độ CLI

```bash
# Cơ bản
python main.py --address "285 Khuất Duy Tiến, Hà Nội"

# Tùy chỉnh số lượng ảnh và thư mục output
python main.py --address "Hồ Gươm, Hà Nội" --max-images 50 --output my_images

# Hiển thị browser khi crawl (để debug)
python main.py --address "Chùa Một Cột, Hà Nội" --show-browser
```

### Sử dụng trong code Python

```python
import asyncio
from google_maps_crawler import crawl_google_maps

# Crawl ảnh
success_count = asyncio.run(
    crawl_google_maps(
        address="285 Khuất Duy Tiến, Hà Nội",
        max_images=20,
        output_dir="images",
        headless=True
    )
)

print(f"Đã tải {success_count} ảnh")
```

## 📝 Tham số

| Tham số | Mô tả | Mặc định |
|---------|-------|----------|
| `--address`, `-a` | Địa chỉ cần tìm trên Google Maps | (bắt buộc) |
| `--max-images`, `-m` | Số lượng ảnh tối đa cần tải | 20 |
| `--output`, `-o` | Thư mục lưu ảnh | `images` |
| `--show-browser` | Hiển thị browser khi crawl | False |

## 📂 Cấu trúc thư mục

```
Crawl_images/
├── google_maps_crawler.py  # Module chính
├── utils.py                # Các hàm tiện ích
├── main.py                 # Entry point CLI
├── requirements.txt        # Dependencies
├── README.md              # Tài liệu này
└── images/                # Thư mục chứa ảnh đã tải (tự động tạo)
```

## 🔧 Các module

### `google_maps_crawler.py`
- `GoogleMapsCrawler`: Class chính để crawl ảnh
- `crawl_google_maps()`: Helper function async

### `utils.py`
- `sanitize_filename()`: Tạo tên file an toàn từ địa chỉ
- `ensure_dir()`: Tạo thư mục nếu chưa tồn tại
- `download_image_with_retry()`: Tải ảnh với retry logic
- `get_image_extension()`: Lấy extension từ URL
- `format_file_size()`: Format kích thước file

## ⚠️ Lưu ý

- Cần kết nối internet để crawl
- Tốc độ crawl phụ thuộc vào kết nối mạng
- Google Maps có thể giới hạn số lượng request nếu crawl quá nhiều
- Nên sử dụng headless mode (mặc định) để tăng tốc độ

## 🆚 So sánh với các phương pháp khác

| Phương pháp | Chi phí | Độ tin cậy | Tốc độ |
|-------------|---------|------------|--------|
| **Playwright (này)** | ✅ Miễn phí | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Outscraper API | ❌ Trả phí | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Apify | ❌ Trả phí | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Google Places API | 💰 Free tier | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 📄 License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.
