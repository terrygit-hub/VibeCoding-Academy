"""生成教学用销售示例数据（教程作者内部工具，不属于教学内容）。

- example/data/sales_simple.csv：100 行干净数据，第 1 章用
- example/data/sales_2024.xlsx：2024 全年约 1000 行，刻意埋了脏数据，第 2 章起用：
    · 文本格式的日期（约 60 行）     → 第 2 章「按月汇总」撞上
    · 产品类别拼写不一致（约 40 行） → 第 2 章「按类别汇总」撞上
    · 缺失地区（12 行）             → 第 4 章「按地区筛选」撞上
    · 完全重复的订单（6 笔）         → 第 6 章「数据体检」发现
    · 金额 ≠ 数量 × 单价（8 行）     → 第 6 章「数据体检」发现
- 固定随机种子，输出确定性，可随时重新生成同样内容
- sales_simple.csv 用 utf-8-sig：保证学生用 Excel 双击打开中文不乱码

用法：python tools/make_sales_data.py
"""

import csv
import random
import sys
from datetime import date
from pathlib import Path

import openpyxl

# Windows 终端默认 GBK，打印 ¥ 会报错，切换成 UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

random.seed(42)

ROOT = Path(__file__).resolve().parent.parent
OUT_SIMPLE = ROOT / "example" / "data" / "sales_simple.csv"
OUT_2024 = ROOT / "example" / "data" / "sales_2024.xlsx"

# 地区 → 城市
REGION_CITY = {
    "华北": ["北京", "天津", "石家庄"],
    "华东": ["上海", "杭州", "南京"],
    "华南": ["广州", "深圳", "厦门"],
    "西南": ["成都", "重庆", "昆明"],
}

# 产品类别 → (产品名, 单价)
PRODUCTS = {
    "办公文具": [("中性笔", 3.5), ("笔记本", 12.0), ("便利贴", 8.0), ("文件夹", 6.5)],
    "办公设备": [("机械键盘", 399.0), ("无线鼠标", 129.0), ("显示器支架", 259.0), ("升降桌", 1599.0)],
    "耗材": [("A4纸", 28.0), ("墨盒", 210.0), ("硒鼓", 320.0), ("订书机钉", 5.0)],
}

# 第 2 章的雷：同一个人录入了类别「简称」
CATEGORY_TYPO = {"办公文具": "文具", "办公设备": "设备", "耗材": "消耗品"}

SALESPeople = ["王小明", "李婷", "张伟", "陈静", "刘洋", "赵蕾"]

HEADER = ["订单编号", "订单日期", "地区", "城市", "产品类别", "产品名", "销售员", "数量", "单价", "金额"]

# 2025-07-01 ~ 2025-09-30 共 92 天（simple 数据用）
DATES_2025 = [f"2025-07-{d:02d}" for d in range(1, 32)] + \
             [f"2025-08-{d:02d}" for d in range(1, 32)] + \
             [f"2025-09-{d:02d}" for d in range(1, 31)]


def pick_order() -> tuple:
    """随机生成一笔订单的各个维度（不含编号、日期）。"""
    region = random.choice(list(REGION_CITY))
    city = random.choice(REGION_CITY[region])
    category = random.choice(list(PRODUCTS))
    product, price = random.choice(PRODUCTS[category])
    qty = random.randint(5, 40) if category == "办公文具" else random.randint(1, 8)
    return region, city, category, product, price, qty


def make_row(i: int) -> list:
    region, city, category, product, price, qty = pick_order()
    return [
        f"SO-2025-{i:04d}",
        random.choice(DATES_2025),
        region,
        city,
        category,
        product,
        random.choice(SALESPeople),
        qty,
        f"{price:.1f}",
        f"{round(qty * price, 2):.2f}",
    ]


def make_row_2024(i: int) -> list:
    """2024 年订单，保留真实类型（date / 数字），脏数据按固定规则埋。"""
    region, city, category, product, price, qty = pick_order()
    month, day = random.randint(1, 12), random.randint(1, 28)
    amount = round(qty * price, 2)

    # 雷①：文本格式的日期（约 1/17 的行）
    if i % 17 == 3:
        order_date = f"2024/{month}/{day}"          # 字符串，不是日期
    else:
        order_date = date(2024, month, day)          # 真日期

    # 雷②：类别写成了简称（约 1/25 的行）
    if i % 25 == 7:
        category = CATEGORY_TYPO[category]

    # 雷③：地区漏填（固定挑 12 行）
    if i in (97, 193, 301, 409, 512, 598, 701, 766, 812, 889, 934, 977):
        region, city = None, None

    # 雷④：金额录错（固定挑 8 行，多打了 3 成或少打了 2 成）
    if i in (66, 210, 358, 471, 600, 733, 846, 958):
        amount = round(amount * (1.3 if i % 4 == 0 else 0.8), 2)

    return [
        f"SO-2024-{i:04d}",
        order_date,
        region,
        city,
        category,
        product,
        random.choice(SALESPeople),
        qty,
        price,
        amount,
    ]


def write_simple() -> None:
    OUT_SIMPLE.parent.mkdir(parents=True, exist_ok=True)
    rows = [make_row(i) for i in range(1, 101)]
    with open(OUT_SIMPLE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)
    total = sum(float(r[9]) for r in rows)
    print(f"已生成 {OUT_SIMPLE.name}（{len(rows)} 行，总销售额 ¥{total:,.0f}）")


def write_2024() -> None:
    rows = [make_row_2024(i) for i in range(1, 1001)]
    # 雷⑤：整行完全重复的订单（把第 120、260、400、540、680、820 行原样再录一遍）
    for dup in (120, 260, 400, 540, 680, 820):
        rows.append(list(rows[dup - 1]))

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "销售流水"
    ws.append(HEADER)
    for r in rows:
        ws.append(r)
    wb.save(OUT_2024)
    print(f"已生成 {OUT_2024.name}（{len(rows)} 行）")


def main() -> None:
    write_simple()
    write_2024()


if __name__ == "__main__":
    main()
