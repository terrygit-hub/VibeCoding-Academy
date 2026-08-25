"""生成教学用销售示例数据（教程作者内部工具，不属于教学内容）。

- example/data/sales_simple.csv：约 100 行干净数据，第 1 章用
- 固定随机种子，输出确定性，可随时重新生成同样内容
- 编码 utf-8-sig：保证学生用 Excel 双击打开中文不乱码

用法：python tools/make_sales_data.py
"""

import csv
import random
import sys
from pathlib import Path

# Windows 终端默认 GBK 编码，打印 ¥ 等字符会报错——强制切换 UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

random.seed(42)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "example" / "data" / "sales_simple.csv"

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

SALESPeople = ["王小明", "李婷", "张伟", "陈静", "刘洋", "赵蕾"]

# 2025-07-01 ~ 2025-09-30 共 92 天
DATES = [f"2025-07-{d:02d}" for d in range(1, 32)] + \
        [f"2025-08-{d:02d}" for d in range(1, 32)] + \
        [f"2025-09-{d:02d}" for d in range(1, 31)]


def make_row(i: int) -> list:
    region = random.choice(list(REGION_CITY))
    city = random.choice(REGION_CITY[region])
    category = random.choice(list(PRODUCTS))
    product, price = random.choice(PRODUCTS[category])
    # 文件类单价低买得多，设备类单价高买得少——数据更像真实世界
    qty = random.randint(5, 40) if category == "办公文具" else random.randint(1, 8)
    return [
        f"SO-2025-{i:04d}",
        random.choice(DATES),
        region,
        city,
        category,
        product,
        random.choice(SALESPeople),
        qty,
        f"{price:.1f}",
        f"{round(qty * price, 2):.2f}",
    ]


HEADER = ["订单编号", "订单日期", "地区", "城市", "产品类别", "产品名", "销售员", "数量", "单价", "金额"]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = [make_row(i) for i in range(1, 101)]
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)
    total = sum(float(r[9]) for r in rows)
    print(f"已生成 {OUT}（{len(rows)} 行，总销售额 ¥{total:,.0f}）")


if __name__ == "__main__":
    main()
