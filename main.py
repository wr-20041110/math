#!/usr/bin/env python3
"""
口算练习生成器 —— 主入口。

故事1 → 故事2 → 故事3 的完整实现：
  生成 50 道 100 以内的加减法口算题，
  自动计算答案，无重复题目，混合加减法，
  每行 5 题，整齐排列。

用法:
    python main.py                  # 默认：50 题，不显示答案
    python main.py --answers        # 50 题 + 答案
    python main.py -n 20 -a         # 20 题 + 答案
    python main.py --seed 42        # 可重现的随机题目
"""

import argparse
import sys
import os

# 确保 src 目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.generator import ProblemGenerator
from src.exercise import ExerciseSheet
from src.formatter import Formatter


def main() -> None:
    parser = argparse.ArgumentParser(
        description="口算练习生成器 —— 生成 100 以内加减法练习题",
    )
    parser.add_argument(
        "-n", "--total",
        type=int,
        default=50,
        help="题目数量（默认 50）",
    )
    parser.add_argument(
        "-a", "--answers",
        action="store_true",
        help="在算式后显示答案",
    )
    parser.add_argument(
        "-c", "--cols",
        type=int,
        default=5,
        help="每行列数（默认 5）",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="随机种子（用于重现结果）",
    )

    args = parser.parse_args()

    # 1. 生成习题集（含去重）
    sheet = ExerciseSheet(total=args.total, seed=args.seed)
    try:
        problems = sheet.generate()
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. 格式化输出
    formatter = Formatter(cols=args.cols, show_answer=args.answers)
    output = formatter.format(problems)

    # 3. 打印
    print(output)


if __name__ == "__main__":
    main()
