"""第 6 章参考实现：给 data/sales_2024.xlsx 做一次「数据体检」。

体检 = 不改一个字，只检查、只报告。查出的问题怎么处理是业务口径，
由人决定（第 6 章正文会带着你逐项裁决），裁决完再让 AI 动手修。

这是参考答案——第 6 章里你自己让 AI 写一份，卡住时再来对照。

用法（在本仓库根目录）：
    python example/ch6_data_check.py                        # 体检原始数据
    python example/ch6_data_check.py data/sales_2024_clean.xlsx  # 体检清洗后的数据
输出一份控制台体检报告：✅ 通过 / ⚠️ 提醒 / ❌ 必须处理。
"""

import sys
from pathlib import Path

import pandas as pd

# Windows 终端默认 GBK，打印 ¥ 会报错，切换成 UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
# 没给参数就体检原始数据；也可以指定别的文件（比如清洗后的新文件）
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "data" / "sales_2024.xlsx"


def line(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    df = pd.read_excel(DATA)
    print(f"📋 数据体检报告 · {DATA.name}")
    print(f"共 {len(df)} 行 × {len(df.columns)} 列")

    # ---------- 1. 整行完全重复的订单 ----------
    line("① 重复订单")
    dup_all = df[df.duplicated(keep=False)].sort_values("订单编号")
    if len(dup_all):
        ids = dup_all["订单编号"].unique()
        print(f"❌ 发现 {len(dup_all) // 2} 组整行完全重复（{len(dup_all)} 行）：")
        for i in ids:
            print(f"   {i}")
    else:
        print("✅ 无重复")

    # ---------- 2. 金额 ≠ 数量 × 单价 ----------
    line("② 金额校验（业务规则：金额 = 数量 × 单价）")
    should_be = df["数量"] * df["单价"]
    bad = df[(df["金额"] - should_be).abs() > 0.01]
    if len(bad):
        print(f"❌ {len(bad)} 行金额对不上（可能是录入错）：")
        for _, r in bad.iterrows():
            print(f"   {r['订单编号']}：录的 ¥{r['金额']:,.2f}，应为 ¥{should_be[r.name]:,.2f}")
    else:
        print("✅ 全部相符")

    # ---------- 3. 缺失值 ----------
    line("③ 缺失值（每列空了几个格子）")
    miss = df.isna().sum()
    miss = miss[miss > 0]
    if len(miss):
        for col, n in miss.items():
            print(f"⚠️ {col}：缺 {n} 行")
    else:
        print("✅ 无缺失")

    # ---------- 4. 日期格式 ----------
    line("④ 日期格式（应为真日期，不是文本）")
    n_text = df["订单日期"].map(lambda v: isinstance(v, str)).sum()
    if n_text:
        print(f"⚠️ {n_text} 行日期是文本（如 2024/3/5），按月汇总前需统一解析")
    else:
        print("✅ 全部是真日期")

    # ---------- 5. 类别口径 ----------
    line("⑤ 类别口径（应只有 3 类）")
    for cat, n in df["产品类别"].value_counts().items():
        mark = "✅" if cat in ("办公文具", "办公设备", "耗材") else "⚠️ 简称，需按口径归并"
        print(f"   {mark} {cat}：{n} 行")

    print("\n体检结束：以上每一条怎么处理，都是你的业务决定；决定好了再让 AI 动手。")


if __name__ == "__main__":
    main()
