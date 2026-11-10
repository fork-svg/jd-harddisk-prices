#!/usr/bin/env python3
"""
生成历史测试数据
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# 基础价格数据
BASE_PRICES = {
    "100012043938": {"base": 650, "variance": 50, "name": "西部数据 4TB 蓝盘", "category": "机械硬盘", "brand": "西部数据", "capacity": "4TB"},
    "100008915038": {"base": 380, "variance": 30, "name": "西部数据 2TB 蓝盘", "category": "机械硬盘", "brand": "西部数据", "capacity": "2TB"},
    "100012043934": {"base": 950, "variance": 50, "name": "西部数据 6TB 蓝盘", "category": "机械硬盘", "brand": "西部数据", "capacity": "6TB"},
    "100098264478": {"base": 1400, "variance": 100, "name": "西部数据 8TB 蓝盘", "category": "机械硬盘", "brand": "西部数据", "capacity": "8TB"},
    "100012345678": {"base": 2700, "variance": 200, "name": "西部数据 16TB 蓝盘", "category": "机械硬盘", "brand": "西部数据", "capacity": "16TB"},
    "100008915050": {"base": 720, "variance": 50, "name": "希捷 4TB 酷鹰监控级", "category": "机械硬盘", "brand": "希捷", "capacity": "4TB"},
    "100098264479": {"base": 1500, "variance": 100, "name": "希捷 8TB 酷鹰监控级", "category": "机械硬盘", "brand": "希捷", "capacity": "8TB"},
    "100012345679": {"base": 2900, "variance": 200, "name": "希捷 16TB 酷鹰监控级", "category": "机械硬盘", "brand": "希捷", "capacity": "16TB"},
    "100012043960": {"base": 850, "variance": 50, "name": "三星 1TB 970 EVO Plus", "category": "固态硬盘", "brand": "三星", "capacity": "1TB"},
    "100012043962": {"base": 1600, "variance": 100, "name": "三星 2TB 970 EVO Plus", "category": "固态硬盘", "brand": "三星", "capacity": "2TB"},
    "100012043980": {"base": 600, "variance": 50, "name": "西部数据 1TB SN570", "category": "固态硬盘", "brand": "西部数据", "capacity": "1TB"},
    "100098264480": {"base": 3200, "variance": 200, "name": "三星 4TB 870 EVO", "category": "固态硬盘", "brand": "三星", "capacity": "4TB"},
}


def generate_day_data(date_str: str) -> dict:
    """生成某一天的价格数据"""
    products = []

    for product_id, info in BASE_PRICES.items():
        # 生成带有轻微趋势的价格
        price = info["base"] + random.uniform(-info["variance"], info["variance"])
        price = round(price, 2)

        # 80% 有货
        in_stock = random.random() > 0.2

        product_data = {
            "id": product_id,
            "name": info["name"],
            "category": info["category"],
            "brand": info["brand"],
            "capacity": info["capacity"],
            "url": f"https://item.jd.com/{product_id}.html",
            "price": price if in_stock else None,
            "original_price": round(price * 1.1, 2) if random.random() > 0.5 and in_stock else None,
            "in_stock": in_stock,
            "coupon": round(random.uniform(10, 50), 2) if random.random() > 0.7 and in_stock else None,
            "promotion": random.choice(["满减活动", "限时折扣", "会员专享价"]) if random.random() > 0.8 and in_stock else None,
        }
        products.append(product_data)

    return {
        "date": date_str,
        "timestamp": f"{date_str}T10:00:00.000000",
        "source": "simulated",
        "products": products
    }


def main():
    """生成过去30天的历史数据"""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    today = datetime.now()

    # 生成过去30天的数据
    for i in range(30, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        data_file = data_dir / f"{date_str}.json"

        # 如果文件不存在，生成数据
        if not data_file.exists():
            data = generate_day_data(date_str)
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"生成数据: {date_str}")

    print("✅ 历史数据生成完成")


if __name__ == "__main__":
    main()
