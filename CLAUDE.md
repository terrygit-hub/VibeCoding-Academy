# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目是什么

面向非软件专业人士（会 Excel、零编程、没用过命令行的职场人员）的 AI 辅助编程（vibe coding）教学项目。8 章教程，每章 30–60 分钟，自学 2–3 周。主线工具 Claude Code，贯穿示例为 Python 销售数据分析（第 1 章静态 HTML 报告 → 第 4 章 Streamlit 看板）。

## 仓库结构

- `tutorials/` — 每章一个独立 HTML（ch0.html … ch7.html）+ index.html 目录页。零构建工具、零外部依赖，双击即看
- `tutorials/assets/style.css` — 全站唯一样式表，token 定义在 `:root`
- `example/` — 示例项目参考实现（学生克隆后跟着章节自己动手写，example/ 里放的是参考答案）
- `tools/` — 教程作者的内部工具（生成示例数据），不属于教学内容，不向学生讲解

## 常用命令

- 生成示例数据：`python tools/make_sales_data.py`（确定性输出，固定随机种子）
- 第 0 章环境自检：`python example/scripts/check_env.py`
- 第 1 章报告脚本（参考实现）：`python example/ch1_report.py`，输出 `example/report.html`（已 gitignore）
- 章节里程碑 tag：`ch0-setup`、`ch1-done`、…（example/ 演进到该章状态时打）

## 写作规范（所有章节 HTML 必须遵守）

### 每章固定结构

1. 章首：提交图进度导航（8 节点，当前章 HEAD 指针）+ 章标题
2. 正文：口语化中文叙述，工具名/命令保留英文，每章一个贯穿的生活化类比
3. 章末三件套，顺序固定：
   - 「动手做」练习（在 example/ 上就地操作，`<details>` 可折叠参考过程）
   - 「自测 3 题」（`<details>` 可折叠答案，不评分）
   - 「翻车急救箱」（该章 3–5 种常见报错 + 排查步骤）
4. 章尾：上一章/下一章导航

### 视觉 token（唯一定义处：tutorials/assets/style.css 的 :root）

- 纸白 `#FAF6EF` 页面底色 ｜ 墨青 `#1F3A4D` 标题与正文 ｜ 暖橙 `#E8630A` 强调/链接/进度 ｜ 青瓷绿 `#2E7D6B` 辅助（自测、成功态） ｜ 代码块深蓝黑 `#1E2A38` ｜ 次级灰褐 `#8A8175`
- 系统字体栈（"Microsoft YaHei" / "Segoe UI"），代码用 Cascadia Code / Consolas
- 代码块统一带终端窗口外壳（三色圆点 + 标题条），命令行前缀 `$`
- SVG 插图：扁平几何 + 圆角 + 柔和投影，一律内联，无外链图片
- 图表规则（已用 dataviz 校验脚本验证）：图表永远**单系列单色相（橙 #E8630A）**；青瓷绿只作界面强调色（自测框、成功态），**绝不用作数据系列色**（色度低于地板，会读成灰）；条形图细条 + 数据端 4px 圆角 + 条末直接标数值；数字右对齐等宽字体
- v1 不做暗色模式、不引入任何 JS 库/外链字体（保证离线双击可用）

### AI 对话呈现

- 对话示范用 HTML 对话气泡（`.chat-user` / `.chat-ai` / `.chat-term` 三种样式），不用真实截图
- 真实截图只用于「终端长什么样」这类界面认知场景
- 内容红线：不绑定单一模型供应商（双路径：官方订阅 / 国内端点 `ANTHROPIC_BASE_URL`），示范气泡中不出现具体模型品牌名

### 内容红线

- 版本敏感内容（安装步骤、下载地址）只出现在第 0 章，标注「最后验证日期」
- 验证只教轻量方式（跑起来 + 让 AI 写检查），不教 pytest
- git 协作教学：单人扮演 Alice/Bob 双角色（两个克隆目录），远端用 GitHub
- 示例数据：`sales_simple.csv`（~100 行，干净，utf-8-sig 编码保证 Excel 打开不乱码）；`sales_2024.xlsx`（~1000 行，脏数据按章节解锁，后续章节制作）

## 流程约定

- 本仓库自身用 git 开发、按章节打 tag——教程怎么教 git，我们就怎么用 git（吃自己的狗粮）
- 教程 HTML 改动后至少在本机浏览器验证一次再提交
