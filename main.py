#!/usr/bin/env python3
"""
口算练习系统（数据处理版）—— 主入口。

完整的习题生成 → 答卷批改 → 成绩分析 → 针对性练习流程。

用法:
    python main.py generate --type mixed --count 50
    python main.py grade --answers data/answers/EX-xxx_answers.csv
    python main.py analyze
    python main.py target --count 20
    python main.py demo                    # 运行完整演示流程
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.practice_manager import PracticeManager
from src.exercise_builder import EXERCISE_TYPES


def cmd_generate(args: argparse.Namespace) -> None:
    """生成习题并保存 CSV。"""
    pm = PracticeManager(data_dir=args.data_dir)
    exercise, path = pm.generate_exercise(
        exercise_type=args.type,
        count=args.count,
        seed=args.seed,
    )
    print(f"[OK] 习题已生成: {exercise.exercise_id}")
    print(f"   类型: {exercise.exercise_type}")
    print(f"   题目数: {exercise.total}")
    print(f"   保存至: {path}")
    print()

    for i, p in enumerate(exercise.problems, 1):
        end = "\t" if i % 5 != 0 else "\n"
        print(f"{p}", end=end)
    print()


def cmd_grade(args: argparse.Namespace) -> None:
    """批改答卷。"""
    pm = PracticeManager(data_dir=args.data_dir)
    pm.load_scores()

    score = pm.grade_answers(args.answers)
    print(f"[OK] 批改完成: {score.exercise_id}")
    print(f"   学生: {score.student}")
    print(f"   总题数: {score.total}")
    print(f"   正确: {score.correct}  错误: {score.wrong}")
    print(f"   得分: {score.percentage}%")
    if score.wrong_indices:
        print(f"   错题索引: {score.wrong_indices}")


def cmd_analyze(args: argparse.Namespace) -> None:
    """分析成绩。"""
    pm = PracticeManager(data_dir=args.data_dir)
    pm.load_scores()
    result = pm.analyze()

    summary = result["summary"]
    print("[== 成绩摘要 ==]")
    print(f"   练习次数: {summary['total_sessions']}")
    print(f"   总做题数: {summary['total_problems_done']}")
    print(f"   总正确数: {summary['total_correct']}")
    print(f"   平均得分: {summary['avg_percentage']}%")
    print(f"   最佳: {summary['best']}%  最差: {summary['worst']}%")
    print()

    weak = result["weak_problems"]
    if weak:
        print(f"[!!] 弱项题目 (Top {len(weak)}):")
        print(f"   {'题目':<12} {'正确答案':<8} {'错误次数':<8} {'错误率':<8}")
        print(f"   {'-' * 40}")
        for w in weak:
            prob = f"{w['num1']}{w['operator']}{w['num2']}"
            print(
                f"   {prob:<12} {w['correct_answer']:<8} "
                f"{w['wrong_count']:<8} {w['error_rate']:.0%}"
            )
    else:
        print("   [OK] 没有发现弱项题目！")


def cmd_target(args: argparse.Namespace) -> None:
    """生成针对性练习。"""
    pm = PracticeManager(data_dir=args.data_dir)
    pm.load_scores()
    exercise = pm.generate_targeted_practice(
        count=args.count,
        seed=args.seed,
    )
    print(f"[>>] 针对性练习: {exercise.exercise_id}")
    print(f"   题目数: {exercise.total}")
    print()
    for i, p in enumerate(exercise.problems, 1):
        end = "\t" if i % 5 != 0 else "\n"
        print(f"{p}", end=end)
    print()


def cmd_demo(args: argparse.Namespace) -> None:
    """完整演示流程。

    模拟华经理生成习题 → 小明答题 → 妈妈录入 → 华经理批改 → 分析 → 针对性练习。
    """
    import random

    rng = random.Random(42)
    pm = PracticeManager(data_dir=args.data_dir)

    print("=" * 60)
    print("  口算练习系统 —— 完整演示")
    print("=" * 60)

    # 步骤1: 生成习题
    print("\n-- 步骤1: 华经理生成习题 --")
    for ex_type in ["addition", "subtraction", "mixed"]:
        label = EXERCISE_TYPES[ex_type]["label"]
        exercise, path = pm.generate_exercise(
            exercise_type=ex_type, count=10, seed=42
        )
        print(f"   [{label}] {exercise.exercise_id} -> {path}")
        ex_for_demo = exercise

    # 步骤2: 模拟答题
    print("\n-- 步骤2: 小明做题 + 妈妈录入答案 --")
    exercise = ex_for_demo
    answers: dict = {}
    for i, p in enumerate(exercise.problems, 1):
        if rng.random() < 0.9:
            answers[i] = p.answer
        else:
            answers[i] = p.answer + rng.choice([-3, -2, -1, 1, 2, 3])
    print(f"   习题 {exercise.exercise_id}: {exercise.total} 题")
    print(f"   小明作答完成，妈妈已录入")

    # 步骤3: 批改打分
    print("\n-- 步骤3: 华经理批改打分 --")
    score = pm.grade_from_data(
        exercise_id=exercise.exercise_id,
        student="XiaoMing",
        answers_dict=answers,
    )
    print(f"   总题数: {score.total}")
    print(f"   正确: {score.correct}  错误: {score.wrong}")
    print(f"   得分: {score.percentage}%")
    if score.wrong_indices:
        print(f"   错题: {score.wrong_indices}")
        for idx in score.wrong_indices:
            p = exercise.get_problem(idx)
            student_ans = answers[idx]
            print(f"     #{idx}: {p}{student_ans} (正确: {p.answer})")

    # 步骤4: 模拟更多练习
    print("\n-- 步骤4: 模拟多次练习（生成成绩历史）--")
    for day in range(3):
        ex, _ = pm.generate_exercise(exercise_type="mixed", count=10, seed=42 + day)
        ans = {}
        for i, p in enumerate(ex.problems, 1):
            key = (p.num1, p.operator.symbol, p.num2)
            if key in [(15, "+", 7), (88, "-", 21), (22, "+", 33)]:
                ans[i] = p.answer + rng.choice([-2, -1, 1, 2])
            else:
                ans[i] = p.answer if rng.random() < 0.92 else p.answer + 1
        sc = pm.grade_from_data(ex.exercise_id, "XiaoMing", ans)
        print(f"   Day {day + 1}: {ex.exercise_id} -> {sc.percentage}%")

    # 步骤5: 分析
    print("\n-- 步骤5: 成绩分析 --")
    result = pm.analyze()
    s = result["summary"]
    print(f"   总练习次数: {s['total_sessions']}")
    print(f"   平均得分: {s['avg_percentage']}%")

    weak = result["weak_problems"]
    if weak:
        print(f"   弱项题目:")
        for w in weak[:5]:
            print(f"     {w['num1']}{w['operator']}{w['num2']} "
                  f"错{w['wrong_count']}次 错误率{w['error_rate']:.0%}")

    # 步骤6: 针对性练习
    print("\n-- 步骤6: 生成针对性练习 --")
    targeted = pm.generate_targeted_practice(count=10, seed=99)
    print(f"   {targeted.exercise_id}: {targeted.total} 题")
    for i, p in enumerate(targeted.problems, 1):
        end = "\t" if i % 5 != 0 else "\n"
        print(f"   {p}", end=end)
    print()

    print("=" * 60)
    print("  演示完成！数据已保存至 data/ 目录")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="口算练习系统（数据处理版）",
    )
    parser.add_argument("--data-dir", default="data", help="数据存储目录（默认 data）")

    sub = parser.add_subparsers(dest="command", help="子命令")

    # generate
    p_gen = sub.add_parser("generate", help="生成习题")
    p_gen.add_argument("--type", default="mixed",
                       choices=list(EXERCISE_TYPES.keys()), help="习题类型")
    p_gen.add_argument("--count", type=int, default=50, help="题目数量")
    p_gen.add_argument("--seed", type=int, default=None, help="随机种子")

    # grade
    p_grade = sub.add_parser("grade", help="批改答卷")
    p_grade.add_argument("--answers", required=True, help="答案 CSV 文件路径")

    # analyze
    sub.add_parser("analyze", help="分析成绩")

    # target
    p_target = sub.add_parser("target", help="生成针对性练习")
    p_target.add_argument("--count", type=int, default=20, help="题目数量")
    p_target.add_argument("--seed", type=int, default=None, help="随机种子")

    # demo
    sub.add_parser("demo", help="运行完整演示流程")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "grade":
        cmd_grade(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "target":
        cmd_target(args)
    elif args.command == "demo":
        cmd_demo(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
