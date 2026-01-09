# 🗺️ Google Maps Image Crawler - Chrome Extension

Chrome extension để crawl và tải ảnh từ Google Maps một cách dễ dàng.

## ✨ Tính năng

- 📍 Nhập địa chỉ và tự động mở Google Maps  
- 🔇 **Chạy trong background tab** - tab không được focus (nhưng vẫn visible trong tab bar)
- 📸 Tự động crawl ảnh từ địa điểm (bao gồm Street View và ảnh người dùng)
- 💾 Hiển thị ảnh trong extension popup
- 📁 **Tùy chỉnh thư mục lưu ảnh** (mới!)
- 🎯 Tùy chỉnh số lượng ảnh tối đa
- 📊 Hiển thị tiến trình và kết quả chi tiết
- 🗂️ **Hiển thị đường dẫn thư mục lưu** (mới!)
- 📂 **Nút mở thư mục Downloads** (mới!)
- 🎨 Giao diện đẹp, hiện đại

## 📦 Cài đặt

### Bước 1: Tải Extension

Extension nằm trong thư mục:
```
/home/hoanhv/Desktop/Crawl_images/extensions/google-maps-crawler/
```

### Bước 2: Load Extension vào Chrome

1. Mở Chrome và truy cập: `chrome://extensions/`
2. Bật **Developer mode** (góc trên bên phải)
3. Click **Load unpacked** (Tải tiện ích đã giải nén)
4. Chọn thư mục `google-maps-crawler`
5. Extension sẽ xuất hiện trong thanh công cụ

## 🚀 Cách sử dụng

### Sử dụng cơ bản

1. **Click vào icon extension** trên thanh công cụ Chrome
2. **Nhập địa chỉ** cần tìm (ví dụ: "213/12 Nguyễn Gia Trí, Phường 25, Bình Thạnh")
3. **Chọn số ảnh tối đa** (mặc định: 20)
4. **Tùy chọn: Nhập tên thư mục con** (ví dụ: "google_maps_images")
   - Để trống = lưu trực tiếp vào Downloads
   - Nhập tên = tạo thư mục con trong Downloads
5. **Click "Bắt đầu Crawl"**
6. Extension sẽ:
   - Mở background tab với Google Maps (tab không được focus)
   - Tìm kiếm địa chỉ
   - Tự động crawl ảnh  
   - Hiển thị ảnh trong popup
   - Tự động đóng tab khi hoàn thành
7. **Click "Mở thư mục Downloads"** để xem ảnh đã tải

### Kết quả

- Ảnh sẽ được lưu vào:
  - **Thư mục Downloads mặc định** (nếu để trống)
  - **Thư mục con trong Downloads** (nếu nhập tên thư mục)
- Tên file: `google_maps_<địa_chỉ>_001.jpg`, `google_maps_<địa_chỉ>_002.jpg`, ...
- Chất lượng ảnh: Cao (2048x2048 hoặc tốt hơn)
- Extension hiển thị đường dẫn thư mục lưu trong kết quả
- Click nút "Mở thư mục Downloads" để xem ảnh ngay

## 🔧 Cấu trúc Extension

```
google-maps-crawler/
├── manifest.json          # Cấu hình extension (Manifest V3)
├── popup.html            # Giao diện popup
├── popup.css             # Styling cho popup
├── popup.js              # Logic popup
├── content.js            # Script crawl ảnh (inject vào Google Maps)
├── background.js         # Service worker
├── icons/                # Icons extension
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md             # Tài liệu này
```

## 🛠️ Chi tiết kỹ thuật

### Permissions

Extension yêu cầu các quyền sau:
- `tabs`: Mở và quản lý tab Google Maps
- `downloads`: Tải ảnh về máy
- `storage`: Lưu cài đặt người dùng
- `activeTab`: Tương tác với trang Google Maps
- Host permissions: `https://www.google.com/maps/*`

### Cách hoạt động

1. **Popup** (`popup.js`):
   - Nhận input từ người dùng
   - Tạo background tab với Google Maps (`active: false`)
   - Gửi message đến content script trong tab
   - Nhận URLs ảnh và hiển thị kết quả
   - Tự động đóng tab khi hoàn thành

2. **Content Script** (`content.js`):
   - Inject vào trang Google Maps
   - Scroll để load thêm ảnh (nếu cần)
   - Trích xuất URLs ảnh chất lượng cao trực tiếp từ DOM
   - Gửi URLs về popup

3. **Background Service Worker** (`background.js`):
   - Quản lý lifecycle của extension (đơn giản)
   - Xử lý download ảnh nếu cần
   - Inject vào trang Google Maps
   - Tìm và click vào photo gallery
   - Scroll để load thêm ảnh
   - Trích xuất URLs ảnh chất lượng cao
   - Gửi URLs về popup

3. **Background Service Worker** (`background.js`):
   - Quản lý lifecycle của extension
   - Điều phối message giữa popup và content script
   - Monitor download progress

### Chiến lược crawl ảnh

Extension sử dụng 2 chiến lược:

1. **Chiến lược 1**: Tìm và click vào photo thumbnails để mở gallery
2. **Chiến lược 2**: Tìm và click vào tab "Photos"

Sau đó:
- Scroll để load thêm ảnh
- Lọc bỏ logo, icon, marker
- Chỉ lấy ảnh từ Google CDN (googleusercontent.com, ggpht.com, etc.)
- Tạo URLs chất lượng cao (2048x2048)

## ⚠️ Lưu ý

- Extension hoạt động tốt nhất với các địa điểm có nhiều ảnh
- Một số địa điểm có thể không có ảnh hoặc Street View
- Google Maps có thể thay đổi cấu trúc HTML, ảnh hưởng đến việc crawl
- Tốc độ crawl phụ thuộc vào tốc độ mạng và số lượng ảnh

## 🐛 Troubleshooting

### Extension không hoạt động

1. Kiểm tra Developer mode đã bật chưa
2. Reload extension tại `chrome://extensions/`
3. Kiểm tra Console để xem lỗi (F12 > Console)

### Không tìm thấy ảnh

- Địa điểm có thể không có ảnh
- Thử địa chỉ khác hoặc địa điểm nổi tiếng hơn
- Kiểm tra xem Google Maps có hiển thị ảnh không

### Download bị lỗi

- Kiểm tra quyền Downloads của extension
- Kiểm tra dung lượng ổ đĩa
- Thử giảm số lượng ảnh tối đa

## 📝 Phát triển

### Chạy ở chế độ development

1. Load extension như hướng dẫn ở trên
2. Mở Console để debug:
   - Popup: Click chuột phải vào popup > Inspect
   - Content script: F12 trên trang Google Maps
   - Background: `chrome://extensions/` > Background page

### Sửa đổi code

Sau khi sửa code:
1. Lưu file
2. Quay lại `chrome://extensions/`
3. Click icon reload của extension
4. Test lại

## 📄 License

Free to use and modify.

## 🙏 Credits

Dựa trên script Python `playwright_crawl.py` và được chuyển đổi thành Chrome extension.
