#!/usr/bin/env python3
"""
京东硬盘价格监控 - 价格抓取脚本

目前使用模拟数据，因为京东有严格的反爬机制。
要接入真实数据，请实现 get_real_price() 函数。

可选的数据源：
1. 京东联盟 API（需要注册）
2. 第三方价格 API（如慢慢买、购物党）
3. 浏览器自动化（playwright/selenium）
"""

import json
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 基础价格数据（模拟真实价格范围）
BASE_PRICES = {
    "100012043938": {"min": 599, "max": 699, "name": "西部数据 4TB 蓝盘"},
    "100008915038": {"min": 349, "max": 399, "name": "西部数据 2TB 蓝盘"},
    "100012043934": {"min": 899, "max": 999, "name": "西部数据 6TB 蓝盘"},
    "100098264478": {"min": 1299, "max": 1499, "name": "西部数据 8TB 蓝盘"},
    "100012345678": {"min": 2599, "max": 2899, "name": "西部数据 16TB 蓝盘"},
    "100008915050": {"min": 649, "max": 749, "name": "希捷 4TB 酷鹰监控级"},
    "100098264479": {"min": 1399, "max": 1599, "name": "希捷 8TB 酷鹰监控级"},
    "100012345679": {"min": 2799, "max": 3099, "name": "希捷 16TB 酷鹰监控级"},
    "100012043960": {"min": 799, "max": 899, "name": "三星 1TB 970 EVO Plus"},
    "100012043962": {"min": 1499, "max": 1699, "name": "三星 2TB 970 EVO Plus"},
    "100012043980": {"min": 549, "max": 649, "name": "西部数据 1TB SN570"},
    "100098264480": {"min": 2999, "max": 3299, "name": "三星 4TB 870 EVO"},
}


def get_simulated_price(product_id: str) -> dict:
    """
    生成模拟价格数据

    模拟真实的价格波动：
    - 在基础价格范围内随机波动
    - 有时会有促销价格
    - 偶尔缺货
    """
    if product_id not in BASE_PRICES:
        return None

    base = BASE_PRICES[product_id]

    # 90% 概率有货
    in_stock = random.random() > 0.1

    if not in_stock:
        return {
            "price": None,
            "original_price": None,
            "in_stock": False,
            "coupon": None,
            "promotion": None,
        }

    # 生成价格
    price = round(random.uniform(base["min"], base["max"]), 2)

    # 30% 概率有优惠
    has_coupon = random.random() > 0.7
    coupon = round(random.uniform(10, 50), 2) if has_coupon else None

    # 20% 概率有促销活动
    has_promotion = random.random() > 0.8
    promotions = [
        "满减活动",
        "限时折扣",
        "会员专享价",
        "闪购特价",
        None
    ]
    promotion = random.choice(promotions) if has_promotion else None

    # 原价（通常比现价高）
    original_price = round(price * random.uniform(1.1, 1.3), 2) if random.random() > 0.5 else None

    return {
        "price": price,
        "original_price": original_price,
        "in_stock": True,
        "coupon": coupon,
        "promotion": promotion,
    }


def get_real_price(product_id: str) -> dict:
    """
    获取真实价格 - 需要实现

    可选方案：
    1. 京东联盟 API
    2. 第三方价格 API
    3. 浏览器自动化

    返回格式：
    {
        "price": 599.00,
        "original_price": 699.00,
        "in_stock": True,
        "coupon": 20.00,
        "promotion": "满减活动",
    }
    """
    # TODO: 实现真实价格获取
    # 示例：使用京东联盟 API
    # from jd_union_api import JDUnionAPI
    # api = JDUnionAPI(app_key="xxx", app_secret="xxx")
    # return api.get_product_price(product_id)

    return None


def fetch_prices(use_real: bool = False) -> list:
    """获取所有产品的价格"""
    # 读取产品列表
    products_file = Path(__file__).parent / "products.json"
    with open(products_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    for product in data["products"]:
        if not product.get("enabled", True):
            continue

        product_id = product["id"]

        if use_real:
            price_data = get_real_price(product_id)
            if price_data is None:
                # 如果真实数据获取失败，使用模拟数据
                print(f"警告: 无法获取 {product_id} 的真实价格，使用模拟数据")
                price_data = get_simulated_price(product_id)
        else:
            price_data = get_simulated_price(product_id)

        if price_data:
            results.append({
                "id": product_id,
                "name": product["name"],
                "category": product["category"],
                "brand": product["brand"],
                "capacity": product["capacity"],
                "url": product["url"],
                **price_data,
            })

    return results


def save_daily_data(prices: list, date: str = None):
    """保存每日价格数据"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    data = {
        "date": date,
        "timestamp": datetime.now().isoformat(),
        "source": "real" if False else "simulated",
        "products": prices,
    }

    output_file = data_dir / f"{date}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已保存价格数据到: {output_file}")
    return output_file


def generate_markdown(prices: list, date: str = None) -> str:
    """生成 Markdown 格式的价格表格"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    lines = [
        "# 京东硬盘价格监控",
        "",
        f"## 最新价格 ({date})",
        "",
        "**数据来源**: 模拟数据（京东有反爬机制，需要接入真实 API）",
        "",
        "### 机械硬盘",
        "",
        "| 产品 | 容量 | 当前价格 | 原价 | 优惠 | 状态 |",
        "|------|------|----------|------|------|------|",
    ]

    # 机械硬盘
    hdd_prices = [p for p in prices if p["category"] == "机械硬盘"]
    for p in hdd_prices:
        if p["in_stock"]:
            price_str = f"¥{p['price']:.2f}" if p["price"] else "-"
            orig_str = f"~~¥{p['original_price']:.2f}~~" if p.get("original_price") else "-"
            discount_parts = []
            if p.get("coupon"):
                discount_parts.append(f"券¥{p['coupon']:.0f}")
            if p.get("promotion"):
                discount_parts.append(p["promotion"])
            discount_str = " ".join(discount_parts) if discount_parts else "-"
            status_str = "✅ 有货"
        else:
            price_str = "-"
            orig_str = "-"
            discount_str = "-"
            status_str = "❌ 缺货"

        name_link = f"[{p['name']}]({p['url']})"
        lines.append(f"| {name_link} | {p['capacity']} | {price_str} | {orig_str} | {discount_str} | {status_str} |")

    lines.extend([
        "",
        "### 固态硬盘",
        "",
        "| 产品 | 容量 | 当前价格 | 原价 | 优惠 | 状态 |",
        "|------|------|----------|------|------|------|",
    ])

    # 固态硬盘
    ssd_prices = [p for p in prices if p["category"] == "固态硬盘"]
    for p in ssd_prices:
        if p["in_stock"]:
            price_str = f"¥{p['price']:.2f}" if p["price"] else "-"
            orig_str = f"~~¥{p['original_price']:.2f}~~" if p.get("original_price") else "-"
            discount_parts = []
            if p.get("coupon"):
                discount_parts.append(f"券¥{p['coupon']:.0f}")
            if p.get("promotion"):
                discount_parts.append(p["promotion"])
            discount_str = " ".join(discount_parts) if discount_parts else "-"
            status_str = "✅ 有货"
        else:
            price_str = "-"
            orig_str = "-"
            discount_str = "-"
            status_str = "❌ 缺货"

        name_link = f"[{p['name']}]({p['url']})"
        lines.append(f"| {name_link} | {p['capacity']} | {price_str} | {orig_str} | {discount_str} | {status_str} |")

    lines.extend([
        "",
        "---",
        "",
        "## 📈 价格趋势图",
        "",
        "### 产品价格对比",
        "",
        "![所有产品价格对比](./charts/all_products_comparison.png)",
        "",
        "### 每TB价格趋势",
        "",
        "![每TB价格趋势](./charts/price_per_tb_trend.png)",
        "",
        "### 单独产品历史价格",
        "",
        "查看 [charts/](./charts/) 目录获取每个产品的详细价格曲线图。",
        "",
        "---",
        "",
        "## 历史价格数据",
        "",
        "查看 [data/](./data/) 目录获取历史价格 JSON 数据。",
        "",
        "---",
        "",
        f"*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
    ])

    return "\n".join(lines)


def main():
    """主函数"""
    # 检查参数
    use_real = "--real" in sys.argv

    print(f"京东硬盘价格监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据源: {'真实数据' if use_real else '模拟数据'}")
    print()

    # 获取价格
    prices = fetch_prices(use_real=use_real)

    if not prices:
        print("错误: 没有获取到价格数据")
        sys.exit(1)

    # 保存数据
    date = datetime.now().strftime("%Y-%m-%d")
    save_daily_data(prices, date)

    # 生成 README
    readme_content = generate_markdown(prices, date)
    readme_file = Path(__file__).parent / "README.md"
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"已更新 README.md")

    # 打印摘要
    print()
    print("=" * 60)
    print("价格摘要:")
    print("=" * 60)

    for p in prices[:5]:
        status = "✅" if p["in_stock"] else "❌"
        price_str = f"¥{p['price']:.2f}" if p["in_stock"] and p["price"] else "缺货"
        print(f"{status} {p['name']}: {price_str}")

    if len(prices) > 5:
        print(f"... 还有 {len(prices) - 5} 个产品")


if __name__ == "__main__":
    main()
