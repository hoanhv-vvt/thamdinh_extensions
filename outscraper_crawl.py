from outscraper import OutscraperClient
import requests
import os

API_KEY = 'YzM2YzJkZTcwNzc2NDUxOTg5MjZmYmQyNjJhMWYyMjd8OWZmYTFkMTIzMQ'
ADDRESS = '213/12 Nguyễn Gia Trí, Phường 25, Bình Thạnh'

# Khởi tạo
client = OutscraperClient(api_key=API_KEY)

# Lấy tối đa 20 ảnh
results = client.google_maps_photos(
    ADDRESS,
    photosLimit=1,
    language='vi'
)

# Download từng ảnh
if results and len(results[0]) > 0:
    os.makedirs('images', exist_ok=True)
    
    for idx, photo in enumerate(results[0], 1):
        photo_url = photo.get('photo_url')
        
        if photo_url:
            response = requests.get(photo_url)
            
            if response.status_code == 200:
                filename = f'images/photo_{idx}.jpg'
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ {filename}")
