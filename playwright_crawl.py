import os
import re
import requests
import time
import asyncio
from pathlib import Path
from typing import List, Optional
from playwright.async_api import async_playwright, Page, Browser

def sanitize_filename(address: str, max_length: int = 100) -> str:
    safe_name = re.sub(r'[^\w\s-]', '', address)
    safe_name = re.sub(r'\s+', '_', safe_name)
    safe_name = re.sub(r'_+', '_', safe_name)
    safe_name = safe_name.strip('_')[:max_length]
    return safe_name if safe_name else 'unknown_location'

def ensure_dir(path: str) -> Path:
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def download_image_with_retry(url: str, filepath: str, max_retries: int = 3, timeout: int = 10) -> bool:
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            if os.path.getsize(filepath) > 0:
                return True
            else:
                os.remove(filepath)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1 * (attempt + 1))
                continue
            else:
                print(f"❌ Lỗi tải ảnh {url}: {str(e)}")
                return False
    return False

def get_image_extension(url: str) -> str:
    match = re.search(r'\.(jpg|jpeg|png|gif|webp)', url.lower())
    if match:
        return f".{match.group(1)}"
    return ".jpg"


class GoogleMapsCrawler:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await context.new_page()
        self.page.set_default_timeout(60000)
        
    async def close(self):
        if self.page: await self.page.close()
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()
            
    async def search_address(self, address: str) -> bool:
        try:
            print(f"🔍 Đang tìm kiếm: {address}")
            await self.page.goto('https://www.google.com/maps', wait_until='domcontentloaded')
            await self.page.wait_for_timeout(3000)
            search_box = await self.page.wait_for_selector('input#searchboxinput')
            await search_box.fill(address)
            await search_box.press('Enter')
            await self.page.wait_for_timeout(5000)
            try:
                await self.page.wait_for_selector('[role="main"]', timeout=10000)
                print("✅ Tìm thấy địa điểm")
                return True
            except:
                print("❌ Không tìm thấy địa điểm")
                return False
        except Exception as e:
            print(f"❌ Lỗi khi tìm kiếm: {str(e)}")
            return False
            
    async def extract_image_urls(self, max_images: int = 20) -> List[str]:
        image_urls = []
        try:
            print("📸 Đang tìm ảnh...")
            await self.page.wait_for_timeout(3000)
            
            # Chiến lược 1: Tìm và click vào ảnh thumbnail để mở gallery
            print("🔍 Tìm ảnh thumbnail trên trang...")
            
            # Tìm các button ảnh (thường có aria-label chứa "photo" hoặc class chứa "photo")
            photo_thumbnail_selectors = [
                'button[jsaction*="photo"]',
                'button[aria-label*="Photo"]',
                'button[aria-label*="photo"]',
                'button[aria-label*="Ảnh"]',
                'a[href*="photo"]',
                '[role="img"]',
                'img[src*="googleusercontent"]',
            ]
            
            photo_found = False
            for selector in photo_thumbnail_selectors:
                try:
                    thumbnails = await self.page.query_selector_all(selector)
                    print(f"  Tìm thấy {len(thumbnails)} elements với selector: {selector[:50]}")
                    
                    for thumb in thumbnails[:5]:  # Thử 5 thumbnail đầu tiên
                        try:
                            # Kiểm tra xem có phải ảnh thực sự không
                            src = await thumb.get_attribute('src') if await thumb.get_attribute('src') else ''
                            
                            # Bỏ qua logo, icon, street view
                            if any(skip in src.lower() for skip in ['logo', 'icon', 'marker', 'streetview']):
                                continue
                            
                            # Click vào thumbnail
                            print(f"  🖱️  Click vào ảnh để mở gallery...")
                            await thumb.click()
                            await self.page.wait_for_timeout(2000)
                            photo_found = True
                            break
                        except:
                            continue
                    
                    if photo_found:
                        break
                except:
                    continue
            
            if not photo_found:
                print("ℹ️ Không tìm thấy ảnh thumbnail, thử tìm Photos tab...")
                
                # Chiến lược 2: Click vào Photos tab
                photo_button_selectors = [
                    'button[aria-label*="Photo"]',
                    'button[aria-label*="Ảnh"]',
                    '[role="tab"]:has-text("Photos")',
                    '[role="tab"]:has-text("Ảnh")'
                ]
                
                for selector in photo_button_selectors:
                    try:
                        photo_button = await self.page.wait_for_selector(selector, timeout=3000)
                        if photo_button:
                            print(f"✅ Tìm thấy nút Photos, đang click...")
                            await photo_button.click()
                            await self.page.wait_for_timeout(3000)
                            photo_found = True
                            break
                    except:
                        continue
            
            if not photo_found:
                print("⚠️ Địa điểm này có thể không có ảnh người dùng tải lên")
                print("ℹ️ Thử tìm ảnh từ trang chính...")
            
            print(f"⏳ Đang thu thập URLs (tối đa {max_images} ảnh)...")
            
            # Thu thập URLs từ gallery hoặc trang chính
            for scroll_num in range(15):  # Tăng số lần scroll
                images = await self.page.query_selector_all('img')
                
                if scroll_num == 0:
                    print(f"  Tìm thấy {len(images)} thẻ img trên trang")
                
                for img in images:
                    try:
                        src = await img.get_attribute('src')
                        if not src:
                            continue
                        
                        # Bỏ qua các loại ảnh không cần thiết (logo, icon, marker)
                        skip_keywords = [
                            'logo', 'icon', 'marker', 'branding',
                            '/maps/vt/',  # Map tiles (bản đồ)
                        ]
                        
                        if any(skip in src.lower() for skip in skip_keywords):
                            continue
                        
                        # Lấy ảnh từ Google CDN (bao gồm cả Street View và ảnh người dùng)
                        # Chấp nhận: googleusercontent.com, ggpht.com, streetviewpixels (Street View)
                        if not any(cdn in src for cdn in ['googleusercontent.com', 'ggpht.com', 'streetviewpixels', 'googleapis.com/v1/thumbnail']):
                            continue
                        
                        # Bỏ qua ảnh quá nhỏ (icon)
                        if '=s0' in src or '=w48' in src or '=h48' in src:
                            continue
                        
                        # Tạo URL chất lượng cao
                        if '=' in src:
                            base_url = src.split('=')[0]
                            # Đối với Street View, giữ nguyên parameters hoặc tăng kích thước
                            if 'streetviewpixels' in src or 'thumbnail' in src:
                                high_quality_url = src.replace('w203-h100', 'w1200-h600').replace('w408-h200', 'w1200-h600')
                            else:
                                high_quality_url = f"{base_url}=w2048-h2048"
                        else:
                            high_quality_url = src
                        
                        if high_quality_url not in image_urls:
                            image_urls.append(high_quality_url)
                            
                            # Hiển thị loại ảnh
                            img_type = "Street View" if 'streetview' in src.lower() or 'thumbnail' in src.lower() else "Photo"
                            print(f"  ✅ Tìm thấy {img_type} {len(image_urls)}/{max_images}")
                            
                            if len(image_urls) >= max_images:
                                break
                    except:
                        continue
                
                if len(image_urls) >= max_images:
                    break
                
                # Scroll xuống
                await self.page.evaluate('window.scrollBy(0, 800)')
                await self.page.wait_for_timeout(1000)
                
                # Scroll trong gallery nếu có
                try:
                    await self.page.evaluate('''
                        const gallery = document.querySelector('[role="dialog"], .gallery, [class*="photo"]');
                        if (gallery) gallery.scrollBy(0, 500);
                    ''')
                except:
                    pass
                
                # Thử nhấn mũi tên next trong gallery
                if photo_found and len(image_urls) < max_images:
                    try:
                        next_button = await self.page.query_selector('button[aria-label*="Next"], button[aria-label*="next"]')
                        if next_button:
                            await next_button.click()
                            await self.page.wait_for_timeout(1500)
                    except:
                        pass
            
            print(f"✅ Tổng cộng tìm thấy {len(image_urls)} ảnh")
            
            if len(image_urls) == 0:
                print("\n⚠️ KHÔNG TÌM THẤY ẢNH!")
                print("Có thể do:")
                print("  - Địa điểm này không có ảnh hoặc Street View")
                print("  - Google Maps đã thay đổi cấu trúc HTML")
                print("  - Cần thử địa chỉ khác")
            else:
                print(f"\nℹ️ Đã tìm thấy {len(image_urls)} ảnh (bao gồm Street View và ảnh người dùng)")
            
            return image_urls[:max_images]
        except Exception as e:
            print(f"❌ Lỗi khi trích xuất ảnh: {str(e)}")
            import traceback
            traceback.print_exc()
            return image_urls
            
    def download_images(self, urls: List[str], output_dir: str, address: str) -> int:
        if not urls:
            print("⚠️ Không có ảnh để tải")
            return 0
        
        dir_path = ensure_dir(output_dir)
        safe_name = sanitize_filename(address)
        print(f"\n📥 Đang tải {len(urls)} ảnh...")
        success_count = 0
        
        for idx, url in enumerate(urls, 1):
            ext = get_image_extension(url)
            filepath = dir_path / f"{safe_name}_{idx:03d}{ext}"
            print(f"  [{idx}/{len(urls)}] Đang tải...", end=' ')
            
            if download_image_with_retry(url, str(filepath)):
                success_count += 1
                print("✅")
            else:
                print("❌")
        
        print(f"✅ Hoàn thành! Đã tải {success_count}/{len(urls)} ảnh vào {output_dir}")
        return success_count
        
    async def crawl(self, address: str, max_images: int = 20, output_dir: str = 'images') -> int:
        if not await self.search_address(address): return 0
        urls = await self.extract_image_urls(max_images)
        return self.download_images(urls, output_dir, address)


async def crawl_google_maps(address: str, max_images: int = 20, output_dir: str = 'images', headless: bool = True) -> int:
    async with GoogleMapsCrawler(headless=headless) as crawler:
        return await crawler.crawl(address, max_images, output_dir)

if __name__ == '__main__':
    # Địa chỉ cần crawl
    address = "213/12 Nguyễn Gia Trí, Phường 25, Bình Thạnh"
    
    if address:
        max_imgs = 20
        output = 'images'
        
        print("=" * 60)
        print(f"📍 Địa chỉ: {address}")
        print(f"📸 Số ảnh tối đa: {max_imgs}")
        print(f"📁 Output: {output}")
        print(f"ℹ️  Sẽ tải cả Street View và ảnh người dùng")
        print("=" * 60 + "\n")
        
        try:
            start = time.time()
            count = asyncio.run(crawl_google_maps(address, max_imgs, output, headless=False))
            print(f"\n🎉 Đã tải {count} ảnh.")
            print(f"⏱️  Thời gian: {time.time() - start:.2f} giây")
        except KeyboardInterrupt:
            print("\n⚠️ Đã hủy.")
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
