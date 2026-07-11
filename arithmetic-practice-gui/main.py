#!/usr/bin/env python3
"""
口算练习系统 GUI v3.0 —— 启动入口。

用法:
    python main.py            # 启动 GUI
    python main.py --cli      # 命令行模式
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from gui.app import MathPracticeApp


def main() -> None:
    root = tk.Tk()

    # 设置样式
    style = ttk.Style()
    style.theme_use("clam")  # 跨平台一致外观

    app = MathPracticeApp(root)  # noqa: F841 — 持有引用防止 GC

    # 窗口居中
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
