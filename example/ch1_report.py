"""第 1 章参考实现：把 data/sales_simple.csv 变成一张网页报告。

这是「AI 帮你写出来的代码」长什么样 的参考答案——
第 1 章里你自己用 Claude Code 写一份，卡住时再来对照。

用法（在本仓库根目录）：
    python example/ch1_report.py
生成 example/report.html，双击用浏览器打开即可。
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Windows 终端默认 GBK，打印 ¥ 会报错，切换成 UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "sales_simple.csv"
OUT = BASE / "report.html"


# ---------- 1. 读数据 ----------

def load_data() -> pd.DataFrame:
    # utf-8-sig：跳过文件开头的 BOM 标记（Excel 另存的 CSV 常带），
    # 不加的话第一列列名会读出看不见的乱字符
    return pd.read_csv(DATA, encoding="utf-8-sig")


# ---------- 2. 算汇总 ----------

def kpi(df: pd.DataFrame) -> dict:
    return {
        "总销售额": f"¥{df['金额'].sum():,.0f}",
        "订单数": f"{len(df):,} 笔",
        "平均订单额": f"¥{df['金额'].mean():,.0f}",
    }


def by_region(df: pd.DataFrame) -> pd.Series:
    return df.groupby("地区")["金额"].sum().sort_values()


def by_category(df: pd.DataFrame) -> pd.Series:
    return df.groupby("产品类别")["金额"].sum().sort_values()


def top_sales(df: pd.DataFrame) -> pd.DataFrame:
    t = df.groupby("销售员").agg(订单数=("订单编号", "count"), 销售额=("金额", "sum"))
    t["占比"] = t["销售额"] / t["销售额"].sum() * 100
    return t.sort_values("销售额", ascending=False)


# ---------- 3. 拼 HTML 片段 ----------

def tile(label: str, value: str) -> str:
    return f'<div class="tile"><div class="tile-label">{label}</div><div class="tile-value">{value}</div></div>'


def bar_group(title: str, data: pd.Series) -> str:
    """单色横向条形图：同一指标只用一种颜色，条末直接标数值。"""
    peak = data.max()
    rows = []
    for name, value in data.items():
        width = value / peak * 100
        rows.append(f"""
        <div class="bar-row">
          <div class="bar-name">{name}</div>
          <div class="bar-track"><div class="bar-fill" style="width:{width:.1f}%" title="{name}：¥{value:,.0f}（{value / data.sum() * 100:.1f}%）"></div></div>
          <div class="bar-value">¥{value:,.0f}</div>
        </div>""")
    return f'<section><h2>{title}</h2>{"".join(rows)}</section>'


def sales_table(t: pd.DataFrame) -> str:
    body = "".join(
        f"<tr><td>{i + 1}</td><td>{name}</td><td class='num'>{r['订单数']:,.0f}</td>"
        f"<td class='num'>¥{r['销售额']:,.0f}</td><td class='num'>{r['占比']:.1f}%</td></tr>"
        for i, (name, r) in enumerate(t.iterrows())
    )
    return f"""
    <section><h2>销售员排行</h2>
    <table>
      <thead><tr><th>名次</th><th>销售员</th><th class="num">订单数</th><th class="num">销售额</th><th class="num">占比</th></tr></thead>
      <tbody>{body}</tbody>
    </table></section>"""


# ---------- 4. 组装整页 ----------

CSS = """
:root { --paper:#FAF6EF; --ink:#1F3A4D; --ink-soft:#4A6375; --orange:#E8630A;
        --teal:#2E7D6B; --line:#E5DCCB; --card:#FFFFFF; }
* { box-sizing: border-box; }
body { margin:0; background:var(--paper); color:var(--ink);
       font-family:"Segoe UI","Microsoft YaHei",system-ui,sans-serif; line-height:1.8; }
.wrap { max-width:820px; margin:0 auto; padding:48px 28px 64px; }
h1 { font-size:30px; margin:0 0 6px; }
.meta { color:var(--ink-soft); font-size:13.5px; margin-bottom:36px;
        font-family:Consolas,monospace; }
.tiles { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:28px 0 8px; }
.tile { background:var(--card); border:1px solid var(--line); border-radius:14px;
        padding:18px 20px; box-shadow:0 6px 18px rgba(31,58,77,.10); }
.tile-label { font-size:13px; color:var(--ink-soft); }
.tile-value { font-size:26px; font-weight:800; color:var(--ink); }
section h2 { font-size:19px; margin:36px 0 14px; }
.bar-row { display:grid; grid-template-columns:5em 1fr 6.5em; gap:12px; align-items:center; margin:9px 0; }
.bar-name { font-size:14.5px; text-align:right; color:var(--ink); }
.bar-track { background:#F1E9DA; border-radius:4px; height:22px; }
.bar-fill { background:var(--orange); height:22px; border-radius:0 4px 4px 0; min-width:2px; }
.bar-value { font-family:Consolas,monospace; font-size:13.5px; color:var(--ink-soft); }
table { width:100%; border-collapse:collapse; background:var(--card);
        border-radius:10px; overflow:hidden; box-shadow:0 6px 18px rgba(31,58,77,.10); }
th { background:var(--ink); color:var(--paper); font-size:13px; text-align:left; padding:9px 14px; }
td { padding:9px 14px; border-top:1px solid var(--line); font-size:14.5px; }
td.num, th.num { text-align:right; font-family:Consolas,monospace; }
tbody tr:nth-child(even) { background:#FBF8F1; }
footer { margin-top:44px; padding-top:16px; border-top:1px dashed var(--line);
         color:#8A8175; font-size:12.5px; font-family:Consolas,monospace; }
@media (max-width:640px){ .tiles{grid-template-columns:1fr} .bar-row{grid-template-columns:4em 1fr 5.5em} }
"""


def build_html(df: pd.DataFrame) -> str:
    tiles = "".join(tile(k, v) for k, v in kpi(df).items())
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>销售数据报告</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <h1>📊 销售数据报告</h1>
  <p class="meta">数据来源：sales_simple.csv（100 笔订单） · 生成时间：{datetime.now():%Y-%m-%d %H:%M}</p>
  <div class="tiles">{tiles}</div>
  {bar_group("按地区", by_region(df))}
  {bar_group("按产品类别", by_category(df))}
  {sales_table(top_sales(df))}
  <footer>由 ch1_report.py 自动生成 · Vibe Coding 学院 第 1 章</footer>
</div>
</body>
</html>"""


def main() -> None:
    df = load_data()
    OUT.write_text(build_html(df), encoding="utf-8")
    print(f"✓ 报告已生成：{OUT}")
    print(f"  总销售额 ¥{df['金额'].sum():,.0f} · 共 {len(df)} 笔订单 · 双击 report.html 用浏览器打开")


if __name__ == "__main__":
    main()
