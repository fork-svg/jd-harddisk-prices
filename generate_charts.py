#!/usr/bin/env python3
"""
生成历史价格曲线图
"""

import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
import os

# 使用英文标签避免中文字体问题
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def load_historical_data(data_dir: Path) -> dict:
    """加载历史价格数据"""
    data = {}

    for json_file in sorted(data_dir.glob("*.json")):
        with open(json_file, 'r', encoding='utf-8') as f:
            day_data = json.load(f)
            date_str = day_data.get('date', json_file.stem)

            for product in day_data.get('products', []):
                if product.get('in_stock') and product.get('price'):
                    product_id = product['id']
                    if product_id not in data:
                        data[product_id] = {
                            'name': product['name'],
                            'category': product['category'],
                            'brand': product['brand'],
                            'capacity': product['capacity'],
                            'dates': [],
                            'prices': []
                        }

                    data[product_id]['dates'].append(datetime.strptime(date_str, '%Y-%m-%d'))
                    data[product_id]['prices'].append(product['price'])

    return data


def generate_individual_charts(data: dict, output_dir: Path):
    """为每个产品生成单独的价格曲线图"""
    output_dir.mkdir(exist_ok=True)

    for product_id, product_data in data.items():
        if len(product_data['dates']) < 2:
            continue  # 至少需要2个数据点才能画图

        fig, ax = plt.subplots(figsize=(12, 6))

        # 绘制价格曲线
        ax.plot(product_data['dates'], product_data['prices'],
                marker='o', linewidth=2, markersize=6, color='#2196F3')

        # 设置标题和标签
        title = f"{product_data['name']}\nPrice History"
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price (CNY)', fontsize=12)

        # 格式化X轴日期
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # 添加网格
        ax.grid(True, linestyle='--', alpha=0.6)

        # 设置Y轴范围（留出一些空间）
        min_price = min(product_data['prices']) * 0.95
        max_price = max(product_data['prices']) * 1.05
        ax.set_ylim(min_price, max_price)

        # 添加当前价格标注
        current_price = product_data['prices'][-1]
        current_date = product_data['dates'][-1]
        ax.annotate(f'¥{current_price:.2f}',
                   xy=(current_date, current_price),
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                   fontsize=10, fontweight='bold')

        # 添加统计信息
        avg_price = sum(product_data['prices']) / len(product_data['prices'])
        min_p = min(product_data['prices'])
        max_p = max(product_data['prices'])

        stats_text = f'Avg: CNY{avg_price:.2f}\nMin: CNY{min_p:.2f}\nMax: CNY{max_p:.2f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        # 保存图片
        safe_name = f"{product_id}_{product_data['capacity']}".replace(' ', '_')
        fig.savefig(output_dir / f"{safe_name}.png", dpi=150, bbox_inches='tight')
        plt.close(fig)


def generate_summary_chart(data: dict, output_dir: Path):
    """生成所有产品的价格对比总览图"""
    if not data:
        return

    # 按类别分组
    categories = {}
    for product_id, product_data in data.items():
        if len(product_data['dates']) < 2:
            continue

        category = product_data['category']
        if category not in categories:
            categories[category] = []

        categories[category].append((product_id, product_data))

    if not categories:
        return

    # 计算子图数量
    num_categories = len(categories)
    fig, axes = plt.subplots(num_categories, 1, figsize=(14, 5 * num_categories))

    if num_categories == 1:
        axes = [axes]

    colors = plt.cm.Set3.colors

    for idx, (category, products) in enumerate(categories.items()):
        ax = axes[idx]

        for (product_id, product_data), color in zip(products, colors):
            label = f"{product_data['brand']} {product_data['capacity']}"
            ax.plot(product_data['dates'], product_data['prices'],
                   marker='o', linewidth=2, markersize=5,
                   label=label, color=color)

        ax.set_title(f'{category} - Price Comparison', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Price (CNY)', fontsize=11)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='best', fontsize=9)

    plt.tight_layout()
    fig.savefig(output_dir / "all_products_comparison.png", dpi=150, bbox_inches='tight')
    plt.close(fig)


def generate_trend_analysis(data: dict, output_dir: Path):
    """生成价格趋势分析图"""
    if not data:
        return

    # 按容量分组
    capacity_groups = {}
    for product_id, product_data in data.items():
        if len(product_data['dates']) < 2:
            continue

        capacity = product_data['capacity']
        if capacity not in capacity_groups:
            capacity_groups[capacity] = []

        capacity_groups[capacity].append(product_data)

    if not capacity_groups:
        return

    # 选择有数据的容量
    capacities = sorted(capacity_groups.keys(),
                       key=lambda x: int(x.replace('TB', '')) if 'TB' in x else 0)

    if not capacities:
        return

    # 绘制每TB价格趋势
    fig, ax = plt.subplots(figsize=(14, 8))

    for capacity in capacities[:6]:  # 最多显示6个容量
        products = capacity_groups[capacity]
        capacity_num = float(capacity.replace('TB', ''))

        for product_data in products:
            # 计算每TB价格
            per_tb_prices = [p / capacity_num for p in product_data['prices']]

            label = f"{capacity} {product_data['brand']}"
            ax.plot(product_data['dates'], per_tb_prices,
                   marker='s', linewidth=2, markersize=6,
                   label=label)

    ax.set_title('Price per TB Trend', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price per TB (CNY)', fontsize=12)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='best', fontsize=10)

    plt.tight_layout()
    fig.savefig(output_dir / "price_per_tb_trend.png", dpi=150, bbox_inches='tight')
    plt.close(fig)


def main():
    """主函数"""
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    charts_dir = base_dir / "charts"

    print("加载历史价格数据...")
    data = load_historical_data(data_dir)

    if not data:
        print("没有找到历史数据")
        return

    print(f"找到 {len(data)} 个产品的历史数据")

    print("生成单独产品价格曲线...")
    generate_individual_charts(data, charts_dir)

    print("生成产品价格对比图...")
    generate_summary_chart(data, charts_dir)

    print("生成每TB价格趋势图...")
    generate_trend_analysis(data, charts_dir)

    print(f"✅ 图表已保存到: {charts_dir}")


if __name__ == "__main__":
    main()
