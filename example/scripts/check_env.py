"""第 0 章环境自检脚本：检查这门课需要的东西都装好了没有。

用法（在本仓库根目录下）：
    python example/scripts/check_env.py

全绿就可以放心进入第 1 章；有红色 ❌ 就按提示修复后重跑。
"""

import importlib.util
import shutil
import subprocess
import sys

# Windows 终端默认编码可能不是 UTF-8，强制切换，保证中文和图标正常显示
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

results = []  # (状态, 名称, 说明, 修复提示)  状态: ok / warn / fail


def check_python() -> None:
    v = sys.version_info
    if v >= (3, 10):
        results.append(("ok", f"Python {v.major}.{v.minor}.{v.micro}", "版本满足要求（3.10 以上）", ""))
    else:
        results.append(("fail", f"Python {v.major}.{v.minor}.{v.micro}", "版本太旧，需要 3.10 以上",
                        "去 python.org 重新下载最新版安装"))


def check_pip() -> None:
    try:
        import pip  # noqa: F401
        results.append(("ok", "pip", "Python 的软件安装器已就绪", ""))
    except ImportError:
        results.append(("fail", "pip", "没有找到 pip", "重新运行 python.org 安装包，勾选 pip 组件"))


def check_module(name: str, pip_name: str, why: str) -> None:
    if importlib.util.find_spec(name):
        results.append(("ok", f"Python 库 {name}", why, ""))
    else:
        results.append(("fail", f"Python 库 {name}", "还没有安装",
                        f"运行：pip install {pip_name}"))


def check_command(cmd: str, how: str) -> None:
    if shutil.which(cmd):
        results.append(("ok", f"命令 {cmd}", "已安装，终端里能找到", ""))
    else:
        results.append(("fail", f"命令 {cmd}", "终端里找不到这个命令",
                        f"{how}；装完记得【关闭并重新打开】终端再试"))


def check_github() -> None:
    """网络检查只提醒不拦路——访问不稳是国内常见问题，教程里有对策。"""
    import socket
    try:
        socket.create_connection(("github.com", 443), timeout=4).close()
        results.append(("ok", "GitHub 连接", "网络可以访问 github.com", ""))
    except OSError:
        results.append(("warn", "GitHub 连接", "暂时连不上 github.com（国内网络常见）",
                        "不影响前几章学习；第 0 章急救箱里有加速办法"))


def main() -> None:
    print()
    print("=" * 52)
    print("  Vibe Coding 学院 · 环境自检")
    print("=" * 52)
    print()

    check_python()
    check_pip()
    check_module("pandas", "pandas", "读写 Excel/CSV 表格的主力库")
    check_module("openpyxl", "openpyxl", "读写 .xlsx 文件需要（后面章节用）")
    check_command("git", "去 git-scm.com 下载安装 Git")
    check_command("claude", "按第 0 章教程安装 Claude Code")
    check_github()

    icon = {"ok": "✅", "warn": "⚠️ ", "fail": "❌"}
    for status, name, note, fix in results:
        print(f"{icon[status]} {name}")
        print(f"     {note}")
        if fix:
            print(f"     修复：{fix}")
        print()

    fails = sum(1 for r in results if r[0] == "fail")
    warns = sum(1 for r in results if r[0] == "warn")
    print("-" * 52)
    if fails == 0 and warns == 0:
        print("🎉 全部通过！你可以进入第 1 章了。")
    elif fails == 0:
        print("✅ 必需项全部通过（有 ⚠️ 提醒不影响开始学习）。")
    else:
        print(f"还有 {fails} 项没通过。按上面的「修复」提示处理后，重新运行本脚本。")
    print()

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
