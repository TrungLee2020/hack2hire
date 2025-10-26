"""
Script để crawl thông tin căn hộ chung cư tại Hà Nội và TP.HCM
Crawl apartment information in Hanoi and Ho Chi Minh City

Usage:
    python crawl_chung_cu_hn_hcm.py

Tính năng:
- Crawl căn hộ chung cư tại Hà Nội
- Crawl căn hộ chung cư tại TP.HCM
- Xuất dữ liệu riêng cho mỗi thành phố
- Xuất dữ liệu tổng hợp
- Thống kê chi tiết
"""

import asyncio
import json
import os
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


class ChungCuCrawler:
    """Crawler cho căn hộ chung cư Hà Nội và TP.HCM"""

    def __init__(self, headless: bool = True):
        """
        Khởi tạo crawler

        Args:
            headless: Chạy browser ẩn (mặc định: True)
        """
        self.browser_config = BrowserConfig(
            headless=headless,
            verbose=True,
            java_script_enabled=True
        )
        self.output_dir = "crawled_data"
        os.makedirs(self.output_dir, exist_ok=True)

    def get_schema(self):
        """
        Schema để trích xuất thông tin căn hộ

        Returns:
            dict: CSS extraction schema
        """
        return {
            "name": "Căn hộ chung cư",
            "baseSelector": "div.re__card-full",
            "fields": [
                {
                    "name": "title",
                    "selector": "a.pr-title",
                    "type": "text",
                },
                {
                    "name": "link",
                    "selector": "a.pr-title",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "price",
                    "selector": "span.re__card-config-price",
                    "type": "text",
                },
                {
                    "name": "area",
                    "selector": "span.re__card-config-area",
                    "type": "text",
                },
                {
                    "name": "location",
                    "selector": "div.re__card-location",
                    "type": "text",
                },
                {
                    "name": "bedrooms",
                    "selector": "span.re__card-config-bedroom",
                    "type": "text",
                },
                {
                    "name": "toilets",
                    "selector": "span.re__card-config-toilet",
                    "type": "text",
                },
                {
                    "name": "description",
                    "selector": "div.re__card-description",
                    "type": "text",
                },
                {
                    "name": "image",
                    "selector": "img.re__card-image",
                    "type": "attribute",
                    "attribute": "src"
                },
                {
                    "name": "publish_date",
                    "selector": "span.re__card-published-info-date",
                    "type": "text",
                }
            ]
        }

    async def crawl_pages(self, base_url: str, num_pages: int, city_name: str):
        """
        Crawl nhiều trang

        Args:
            base_url: URL cơ sở
            num_pages: Số trang cần crawl
            city_name: Tên thành phố (để hiển thị)

        Returns:
            List các căn hộ
        """
        print(f"\n{'='*70}")
        print(f"Đang crawl căn hộ chung cư tại {city_name}")
        print(f"URL: {base_url}")
        print(f"Số trang: {num_pages}")
        print(f"{'='*70}\n")

        all_properties = []
        extraction_strategy = JsonCssExtractionStrategy(self.get_schema())

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for page_num in range(1, num_pages + 1):
                # Xây dựng URL cho mỗi trang
                if page_num == 1:
                    url = base_url
                else:
                    url = f"{base_url}/p{page_num}"

                print(f"📄 Trang {page_num}/{num_pages}: {url}")

                crawler_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    extraction_strategy=extraction_strategy,
                    wait_until="networkidle",
                    delay_before_return_html=2
                )

                try:
                    result = await crawler.arun(url=url, config=crawler_config)

                    if result.success:
                        try:
                            properties = json.loads(result.extracted_content)
                            all_properties.extend(properties)
                            print(f"   ✅ Tìm thấy {len(properties)} căn hộ")
                        except json.JSONDecodeError as e:
                            print(f"   ❌ Lỗi parse JSON: {e}")
                    else:
                        print(f"   ❌ Không crawl được trang này")
                        if page_num > 1:
                            # Có thể đã hết trang
                            break

                except Exception as e:
                    print(f"   ❌ Lỗi: {e}")

                # Delay giữa các trang
                if page_num < num_pages:
                    await asyncio.sleep(2)

        print(f"\n✅ Hoàn thành! Tổng cộng: {len(all_properties)} căn hộ từ {city_name}\n")
        return all_properties

    def save_json(self, data, filename):
        """
        Lưu dữ liệu ra file JSON

        Args:
            data: Dữ liệu cần lưu
            filename: Tên file
        """
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath

    def print_statistics(self, properties, city_name):
        """
        In thống kê

        Args:
            properties: Danh sách căn hộ
            city_name: Tên thành phố
        """
        print(f"\n{'='*70}")
        print(f"📊 THỐNG KÊ - {city_name.upper()}")
        print(f"{'='*70}")
        print(f"Tổng số căn hộ: {len(properties)}")

        # Thống kê theo địa điểm
        locations = {}
        for prop in properties:
            loc = prop.get('location', 'Không rõ')
            if loc:
                loc = loc.strip()
                locations[loc] = locations.get(loc, 0) + 1

        if locations:
            print(f"\n📍 Top 10 địa điểm nhiều căn hộ nhất:")
            sorted_locs = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]
            for i, (loc, count) in enumerate(sorted_locs, 1):
                print(f"   {i}. {loc}: {count} căn hộ")

        # Thống kê giá
        prices_with_values = []
        for prop in properties:
            price_str = prop.get('price', '')
            if price_str and price_str.strip():
                prices_with_values.append(price_str)

        print(f"\n💰 Căn hộ có thông tin giá: {len(prices_with_values)}/{len(properties)}")

        # Thống kê diện tích
        areas = [p.get('area', '') for p in properties if p.get('area')]
        print(f"📐 Căn hộ có thông tin diện tích: {len(areas)}/{len(properties)}")

        # Thống kê phòng ngủ
        bedrooms_count = {}
        for prop in properties:
            br = prop.get('bedrooms', '').strip()
            if br:
                bedrooms_count[br] = bedrooms_count.get(br, 0) + 1

        if bedrooms_count:
            print(f"\n🛏️  Phân bổ theo số phòng ngủ:")
            sorted_br = sorted(bedrooms_count.items(), key=lambda x: x[1], reverse=True)
            for br, count in sorted_br:
                print(f"   {br}: {count} căn hộ")


async def main():
    """
    Hàm chính - Crawl căn hộ chung cư Hà Nội và TP.HCM
    """
    print("\n" + "="*70)
    print("🏢 CRAWLER THÔNG TIN CĂN HỘ CHUNG CƯ HÀ NỘI & TP.HCM")
    print("="*70)

    crawler = ChungCuCrawler(headless=True)

    # ========================================
    # CẤU HÌNH
    # ========================================

    # Số trang cần crawl cho mỗi thành phố
    NUM_PAGES = 5  # Thay đổi số này để crawl nhiều hoặc ít trang hơn

    # URLs
    HANOI_URL = "https://batdongsan.com.vn/ban-can-ho-chung-cu-ha-noi"
    HCM_URL = "https://batdongsan.com.vn/ban-can-ho-chung-cu-tp-hcm"

    # ========================================
    # CRAWL HÀ NỘI
    # ========================================

    hanoi_properties = await crawler.crawl_pages(
        base_url=HANOI_URL,
        num_pages=NUM_PAGES,
        city_name="Hà Nội"
    )

    # Lưu dữ liệu Hà Nội
    if hanoi_properties:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hanoi_file = crawler.save_json(
            hanoi_properties,
            f"chung_cu_ha_noi_{timestamp}.json"
        )
        print(f"💾 Đã lưu dữ liệu Hà Nội: {hanoi_file}")
        crawler.print_statistics(hanoi_properties, "Hà Nội")
    else:
        print("⚠️  Không có dữ liệu Hà Nội")

    # ========================================
    # CRAWL TP.HCM
    # ========================================

    hcm_properties = await crawler.crawl_pages(
        base_url=HCM_URL,
        num_pages=NUM_PAGES,
        city_name="TP. Hồ Chí Minh"
    )

    # Lưu dữ liệu TP.HCM
    if hcm_properties:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hcm_file = crawler.save_json(
            hcm_properties,
            f"chung_cu_hcm_{timestamp}.json"
        )
        print(f"💾 Đã lưu dữ liệu TP.HCM: {hcm_file}")
        crawler.print_statistics(hcm_properties, "TP. Hồ Chí Minh")
    else:
        print("⚠️  Không có dữ liệu TP.HCM")

    # ========================================
    # TỔNG HỢP
    # ========================================

    if hanoi_properties or hcm_properties:
        # Tổng hợp tất cả
        all_properties = {
            "timestamp": datetime.now().isoformat(),
            "total_count": len(hanoi_properties) + len(hcm_properties),
            "hanoi": {
                "count": len(hanoi_properties),
                "properties": hanoi_properties
            },
            "hcm": {
                "count": len(hcm_properties),
                "properties": hcm_properties
            }
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_file = crawler.save_json(
            all_properties,
            f"chung_cu_tong_hop_{timestamp}.json"
        )

        print(f"\n{'='*70}")
        print(f"📊 TỔNG KẾT")
        print(f"{'='*70}")
        print(f"Hà Nội: {len(hanoi_properties)} căn hộ")
        print(f"TP.HCM: {len(hcm_properties)} căn hộ")
        print(f"Tổng cộng: {len(hanoi_properties) + len(hcm_properties)} căn hộ")
        print(f"\n💾 File tổng hợp: {combined_file}")
        print(f"{'='*70}\n")

        # Hiển thị mẫu
        if hanoi_properties:
            print("📋 Mẫu căn hộ Hà Nội:")
            print(json.dumps(hanoi_properties[0], ensure_ascii=False, indent=2))
            print()

        if hcm_properties:
            print("📋 Mẫu căn hộ TP.HCM:")
            print(json.dumps(hcm_properties[0], ensure_ascii=False, indent=2))
            print()

    print("✅ Hoàn thành!")


if __name__ == "__main__":
    asyncio.run(main())
