from apify_client import ApifyClient
import requests
import time

# 1. Khởi tạo client với API Token
client = ApifyClient('...')

# 2. Cấu hình Input cho Actor (Google Maps Scraper)
run_input = {
    "searchStringsArray": [
        "213/12 Nguyễn Gia Trí, Phường 25, Bình Thạnh",
    ],
    "maxCrawledPlaces": 10, # Giới hạn số lượng
    "language": "vi",
    "includeImages": True,  # Bắt buộc bật để lấy ảnh
}

# 3. Chạy Actor và chờ kết quả
# Đã sửa tên Actor từ "compass/google-maps-scraper" thành "apify/google-maps-scraper"
print("Đang crawl...")
run = client.actor("compass/crawler-google-places").call(run_input=run_input)

# 4. Lấy dữ liệu từ Dataset
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    address = item.get('address')
    images = item.get('imageUrls', [])
    print(f"Địa chỉ: {address}")
    print(f"Tìm thấy {len(images)} ảnh.")

    import requests
    import os

    # Tạo thư mục lưu trữ ảnh
    os.makedirs("images", exist_ok=True)

    for i, url in enumerate(images):
        start = time.time()
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Tạo tên file an toàn từ địa chỉ
                safe_address = "".join(c for c in str(address) if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_')
                filename = f"images/{safe_address[:50]}_{i}.jpg"
                
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"Lưu ảnh {i+1}/{len(images)}: {filename}")
        except Exception as e:
            print(f"Lỗi khi tải ảnh {url}: {str(e)}")
        end = time.time()
        print(f"Thời gian tải ảnh {i+1}/{len(images)}: {end - start:.2f} giây")
