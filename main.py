#!/usr/bin/env python3
"""
口算练习生成器（OOP 版）—— 主入口。

基于面向对象设计原则和设计模式重构：
  - 策略模式：Operator 和 DisplayStrategy
  - 迭代器模式：ProblemCollection / ProblemIterator
  - 外观模式：ExerciseSheet

用法:
    python main.py                  # 默认：50 题，无答案，5 列
    python main.py --answers        # 50 题 + 答案
    python main.py -n 20 -a         # 20 题 + 答案
    python main.py --seed 42 -a     # 可重现
    python main.py --stats          # 显示统计信息
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.sheet import ExerciseSheet


def main() -> None:
    parser = argparse.ArgumentParser(
        description="口算练习生成器（OOP 版）—— 100 以内加减法练习题",
    )
    parser.add_argument("-n", "--total", type=int, default=50, help="题目数量（默认 50）")
    parser.add_argument("-a", "--answers", action="store_true", help="显示答案")
    parser.add_argument("-c", "--cols", type=int, default=5, help="每行列数（默认 5）")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")

    args = parser.parse_args()

    # 使用外观模式：一行创建习题集
    sheet = ExerciseSheet(
        total=args.total,
        cols=args.cols,
        show_answers=args.answers,
        seed=args.seed,
    )

    try:
        output = sheet.render()
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    print(output)

    if args.stats:
        s = sheet.stats
        print(f"\n--- 统计 ---")
        print(f"总数: {s['total']}  加法: {s['addition']}  减法: {s['subtraction']}")
        print(f"答案范围: {s['min_answer']} ~ {s['max_answer']}")


if __name__ == "__main__":
    main()
