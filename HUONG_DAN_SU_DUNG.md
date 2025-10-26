# Hướng dẫn sử dụng Crawler Căn hộ Chung cư

## 🎯 Mục đích

Crawler này giúp bạn thu thập thông tin về căn hộ chung cư từ batdongsan.com.vn tại:
- **Hà Nội**
- **TP. Hồ Chí Minh**

## 📋 Cài đặt

### Bước 1: Cài đặt Crawl4AI

```bash
pip install crawl4ai
```

### Bước 2: Setup Crawl4AI

```bash
crawl4ai-setup
```

Hoặc cài đặt từ file requirements:

```bash
pip install -r requirements.txt
crawl4ai-setup
```

## 🚀 Sử dụng nhanh

### Cách 1: Script đơn giản (Recommended)

Chạy script mới nhất để crawl cả Hà Nội và TP.HCM:

```bash
python crawl_chung_cu_hn_hcm.py
```

Script này sẽ:
- ✅ Crawl căn hộ chung cư tại Hà Nội
- ✅ Crawl căn hộ chung cư tại TP.HCM
- ✅ Lưu dữ liệu riêng cho mỗi thành phố
- ✅ Tạo file tổng hợp
- ✅ Hiển thị thống kê chi tiết

### Cách 2: Script đơn giản với cấu hình tùy chỉnh

```bash
python crawl_batdongsan_simple.py
```

Chỉnh sửa các thông số trong file:
- `URL`: Thay đổi URL muốn crawl
- `NUM_PAGES`: Số trang cần crawl
- `OUTPUT_FILE`: Tên file output

### Cách 3: Script nâng cao

```bash
python crawl_batdongsan.py
```

## 📁 Dữ liệu đầu ra

Tất cả dữ liệu được lưu trong thư mục `crawled_data/`:

```
crawled_data/
├── chung_cu_ha_noi_20241026_140530.json      # Dữ liệu Hà Nội
├── chung_cu_hcm_20241026_140545.json         # Dữ liệu TP.HCM
└── chung_cu_tong_hop_20241026_140545.json    # Dữ liệu tổng hợp
```

## 📊 Cấu trúc dữ liệu

Mỗi căn hộ chứa thông tin:

```json
{
  "title": "Bán căn hộ chung cư...",
  "link": "https://batdongsan.com.vn/...",
  "price": "3.5 tỷ",
  "area": "85 m²",
  "location": "Cầu Giấy, Hà Nội",
  "bedrooms": "3 PN",
  "toilets": "2 toilet",
  "description": "Mô tả chi tiết...",
  "image": "https://...",
  "publish_date": "Hôm nay"
}
```

## ⚙️ Tùy chỉnh

### Thay đổi số trang crawl

Mở file `crawl_chung_cu_hn_hcm.py` và tìm:

```python
NUM_PAGES = 5  # Thay đổi số này
```

### Crawl các loại bất động sản khác

Có thể crawl nhiều loại khác nhau bằng cách thay đổi URL:

```python
# Cho thuê căn hộ Hà Nội
"https://batdongsan.com.vn/cho-thue-can-ho-chung-cu-ha-noi"

# Bán nhà riêng TP.HCM
"https://batdongsan.com.vn/ban-nha-rieng-tp-hcm"

# Cho thuê văn phòng
"https://batdongsan.com.vn/cho-thue-van-phong"

# Bán đất nền
"https://batdongsan.com.vn/ban-dat-nen"
```

## 🔧 Khắc phục sự cố

### Lỗi: Không crawl được dữ liệu

1. **Kiểm tra kết nối internet**
2. **Thử chạy với headless=False** để xem browser:
   ```python
   crawler = ChungCuCrawler(headless=False)
   ```
3. **Kiểm tra URL có đúng không**
4. **CSS selectors có thể đã thay đổi** - cần update trong code

### Lỗi: Trang load chậm

Tăng thời gian chờ:

```python
delay_before_return_html=5  # Tăng từ 2 lên 5 giây
```

### Lỗi: crawl4ai not found

```bash
pip install --upgrade crawl4ai
crawl4ai-setup
```

## 📈 Thống kê

Script sẽ tự động hiển thị:
- 📊 Tổng số căn hộ
- 📍 Top 10 địa điểm
- 💰 Số căn hộ có thông tin giá
- 📐 Số căn hộ có thông tin diện tích
- 🛏️  Phân bổ theo số phòng ngủ

## ⚠️ Lưu ý quan trọng

1. **Tuân thủ robots.txt** của website
2. **Không crawl quá nhanh** - script đã có delay tự động
3. **Sử dụng dữ liệu có đạo đức** - chỉ cho mục đích cá nhân/nghiên cứu
4. **CSS selectors có thể thay đổi** khi website cập nhật

## 💡 Tips

- Chạy vào ban đêm để tránh traffic cao
- Bắt đầu với số trang nhỏ (2-3 trang) để test
- Kiểm tra file output trước khi crawl số lượng lớn
- Backup dữ liệu thường xuyên

## 🆘 Cần hỗ trợ?

Tham khảo thêm trong file:
- `BATDONGSAN_CRAWLER_README.md` - Hướng dẫn chi tiết
- `crawl_batdongsan.py` - Code mẫu nâng cao
- `crawl_batdongsan_simple.py` - Code mẫu đơn giản

## 📝 Examples

### Example 1: Crawl nhanh 2 trang

```python
import asyncio
from crawl_chung_cu_hn_hcm import ChungCuCrawler

async def quick_crawl():
    crawler = ChungCuCrawler(headless=True)

    properties = await crawler.crawl_pages(
        base_url="https://batdongsan.com.vn/ban-can-ho-chung-cu-ha-noi",
        num_pages=2,
        city_name="Hà Nội"
    )

    crawler.save_json(properties, "quick_test.json")
    crawler.print_statistics(properties, "Test")

asyncio.run(quick_crawl())
```

### Example 2: Crawl nhiều thành phố

```python
cities = {
    "Hà Nội": "https://batdongsan.com.vn/ban-can-ho-chung-cu-ha-noi",
    "TP.HCM": "https://batdongsan.com.vn/ban-can-ho-chung-cu-tp-hcm",
    "Đà Nẵng": "https://batdongsan.com.vn/ban-can-ho-chung-cu-da-nang",
}

for city, url in cities.items():
    properties = await crawler.crawl_pages(url, num_pages=3, city_name=city)
    crawler.save_json(properties, f"{city.lower()}.json")
```

## ✅ Checklist

- [ ] Đã cài đặt crawl4ai
- [ ] Đã chạy crawl4ai-setup
- [ ] Đã test với 1-2 trang
- [ ] Đã kiểm tra file output
- [ ] Đã điều chỉnh NUM_PAGES phù hợp
- [ ] Sẵn sàng crawl!

---

**Chúc bạn crawl data thành công! 🎉**
