from serpapi import GoogleSearch
from urllib.parse import urlsplit, parse_qsl
import os
import json
import requests

class SerpAPIPhotoDownloader:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def find_place_data_id(self, address):
        """Tìm data_id của địa điểm từ địa chỉ"""
        params = {
            'api_key': self.api_key,
            'engine': 'google_maps',
            'q': address,
            'type': 'search',
            'hl': 'vi'
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Lấy result đầu tiên
        if 'local_results' in results and len(results['local_results']) > 0:
            first_result = results['local_results'][0]
            return {
                'title': first_result.get('title'),
                'data_id': first_result.get('data_id'),
                'address': first_result.get('address')
            }
        else:
            print(f"Không tìm thấy địa điểm cho: {address}")
            return None
    
    def get_all_photos(self, data_id, category_id=None):
        """Lấy tất cả photos của địa điểm"""
        params = {
            'api_key': self.api_key,
            'engine': 'google_maps_photos',
            'data_id': data_id,
            'hl': 'vi'
        }
        
        # Thêm category filter nếu cần
        # category_id='CgIgARICCAI' -> Street View & 360°
        if category_id:
            params['category_id'] = category_id
        
        search = GoogleSearch(params)
        all_photos = []
        
        # Pagination - lấy tất cả trang
        while True:
            page_results = search.get_dict()
            
            if 'photos' in page_results:
                all_photos.extend(page_results['photos'])
                print(f"Đã lấy {len(page_results['photos'])} ảnh, tổng: {len(all_photos)}")
            
            # Kiểm tra có trang tiếp không
            if 'next' in page_results.get('serpapi_pagination', {}):
                # Update params cho trang tiếp theo
                next_page_url = page_results['serpapi_pagination']['next']
                search.params_dict.update(
                    dict(parse_qsl(urlsplit(next_page_url).query))
                )
            else:
                break
        
        return all_photos
    
    def download_photos(self, photos, output_dir='downloads'):
        """Tải ảnh về local"""
        os.makedirs(output_dir, exist_ok=True)
        
        downloaded = []
        for idx, photo in enumerate(photos, 1):
            try:
                # Lấy URL ảnh gốc (full resolution)
                image_url = photo.get('image')
                
                if not image_url:
                    continue
                
                # Download ảnh
                response = requests.get(image_url, timeout=10)
                
                if response.status_code == 200:
                    filename = f"{output_dir}/photo_{idx:03d}.jpg"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded.append({
                        'filename': filename,
                        'url': image_url,
                        'thumbnail': photo.get('thumbnail'),
                        'user': photo.get('user', {}).get('name', 'Unknown')
                    })
                    
                    print(f"✓ Tải thành công: {filename}")
                else:
                    print(f"✗ Lỗi tải ảnh {idx}: {response.status_code}")
            
            except Exception as e:
                print(f"✗ Lỗi: {e}")
        
        return downloaded

# ===== SỬ DỤNG =====
if __name__ == "__main__":
    # API key của bạn
    API_KEY = "26af8a04d32206fd2d15c0488f188f2bd67bb2ecb724f06bc30c3bd1ff4a34b0"
    
    # Địa chỉ cần tìm
    address = "213/12 Nguyễn Gia Trí, Phường 25, Bình Thạnh"
    
    downloader = SerpAPIPhotoDownloader(API_KEY)
    
    # Bước 1: Tìm data_id của địa điểm
    print(f"[1] Đang tìm địa điểm: {address}...")
    place_info = downloader.find_place_data_id(address)
    
    if not place_info:
        exit()
    
    print(f"✓ Tìm thấy: {place_info['title']}")
    print(f"  Địa chỉ: {place_info['address']}")
    print(f"  Data ID: {place_info['data_id']}")
    
    # Bước 2: Lấy tất cả photos
    print(f"\n[2] Đang lấy photos...")
    photos = downloader.get_all_photos(place_info['data_id'])
    print(f"✓ Tổng cộng: {len(photos)} ảnh")
    
    # Bước 3: Download ảnh
    print(f"\n[3] Đang tải ảnh...")
    downloaded = downloader.download_photos(photos[:20])  # Giới hạn 20 ảnh
    
    # Lưu metadata
    with open('downloads/metadata.json', 'w', encoding='utf-8') as f:
        json.dump({
            'place': place_info,
            'total_photos': len(photos),
            'downloaded': downloaded
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Hoàn tất! Đã tải {len(downloaded)} ảnh vào thư mục 'downloads/'")
