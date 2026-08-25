"""第 4 章参考实现：把 data/sales_2024.xlsx 变成一个能点、能筛的交互看板。

和第 1 章的 report.html 不同：报告是「拍好的照片」，看板是「直播间」——
你在侧边栏点一下，全部数字和图表立刻跟着变。

这是参考答案——第 4 章里你自己用 AI 写一份，卡住时再来对照。

用法（在本仓库根目录）：
    python -m streamlit run example/ch4_dashboard.py
浏览器会自动打开 http://localhost:8501，按 Ctrl+C 结束。
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Windows 终端默认 GBK，打印 ¥ 会报错，切换成 UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "sales_2024.xlsx"


# ---------- 1. 读数据 + 洗数据 ----------

# 类别简称 → 标准类别（口径来自第 2 章：「文具」=「办公文具」……）
CATEGORY_MAP = {"文具": "办公文具", "设备": "办公设备", "消耗品": "耗材"}


@st.cache_data  # 数据只读一次，点筛选器时不重复读盘
def load_data() -> pd.DataFrame:
    df = pd.read_excel(DATA)

    # 雷①：一部分订单日期是 "2024/3/5" 这样的文本，统一解析成真日期（第 2 章撞过）
    df["订单日期"] = pd.to_datetime(df["订单日期"], errors="coerce")

    # 雷②：类别有简称写法，按口径统一（第 2 章撞过）
    df["产品类别"] = df["产品类别"].replace(CATEGORY_MAP)

    # 雷③：12 笔订单没填地区——本章筛选器撞上的雷。
    # 怎么处理是业务决定：这里归入「未填写」并保留在数据里（而不是悄悄扔掉）
    df["地区"] = df["地区"].fillna("未填写")
    df["城市"] = df["城市"].fillna("未填写")

    # 已知但先不动的雷（第 6 章「数据体检」才处理）：
    #   · 有 6 笔完全重复的订单
    #   · 有 8 笔金额 ≠ 数量 × 单价
    return df


# ---------- 2. 页面骨架 ----------

st.set_page_config(page_title="2024 销售看板", page_icon="📊", layout="wide")
st.title("📊 2024 年销售看板")
st.caption("数据来源：sales_2024.xlsx · 点左侧筛选器，全页联动")

df = load_data()

with st.expander("这份看板替你洗了哪些数据？"):
    st.markdown(
        "- **日期**：59 行文本格式日期（如 `2024/3/5`）已解析为真日期\n"
        "- **类别**：简称（文具/设备/消耗品）已按口径归入三大类\n"
        "- **地区**：12 笔未填地区的订单归入「未填写」，没有删除\n"
        "- **没动的**：6 笔重复订单、8 笔金额对不上的订单——留到第 6 章体检"
    )

# ---------- 3. 侧边栏筛选器 ----------

with st.sidebar:
    st.header("🎯 筛选器")

    regions = sorted(df["地区"].unique())
    pick_regions = st.multiselect("地区", regions, default=regions)

    month_min, month_max = st.slider("月份范围", 1, 12, (1, 12))

    cats = sorted(df["产品类别"].unique())
    pick_cats = st.multiselect("产品类别", cats, default=cats)

# 用筛选条件切出「在视野里」的数据
view = df[
    df["地区"].isin(pick_regions)
    & df["订单日期"].dt.month.between(month_min, month_max)
    & df["产品类别"].isin(pick_cats)
]

# ---------- 4. KPI 卡 ----------

c1, c2, c3 = st.columns(3)
c1.metric("总销售额", f"¥{view['金额'].sum():,.0f}")
c2.metric("订单数", f"{len(view):,} 笔")
c3.metric("平均订单额", f"¥{view['金额'].mean():,.0f}")

# ---------- 5. 图表（单系列，一律橙色） ----------

st.subheader("月度走势")
monthly = view.groupby(view["订单日期"].dt.month)["金额"].sum()
st.bar_chart(monthly, color="#E8630A", x_label="月份", y_label="销售额（元）")

left, right = st.columns(2)
with left:
    st.subheader("按地区")
    st.bar_chart(view.groupby("地区")["金额"].sum().sort_values(ascending=False),
                 color="#E8630A")
with right:
    st.subheader("按产品类别")
    st.bar_chart(view.groupby("产品类别")["金额"].sum().sort_values(ascending=False),
                 color="#E8630A")

# ---------- 6. 销售员排行 ----------

st.subheader("销售员排行")
rank = (
    view.groupby("销售员")
    .agg(订单数=("订单编号", "count"), 销售额=("金额", "sum"))
    .sort_values("销售额", ascending=False)
    .reset_index()
)
rank.insert(0, "名次", range(1, len(rank) + 1))
st.dataframe(
    rank.set_index("名次"),
    column_config={
        "销售额": st.column_config.NumberColumn(format="¥ %d"),
        "订单数": st.column_config.NumberColumn(format="%d 笔"),
    },
    width="stretch",
)

st.caption("第 4 章参考实现 · ch4_dashboard.py —— 你用 AI 写的那份，长什么样都可以，功能对就行")
