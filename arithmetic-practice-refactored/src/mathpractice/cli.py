"""
CLI —— 命令行接口（Extract Class 重构）。

重构前: 所有 CLI 逻辑混在 main.py 中。
重构后: 独立的 cli.py，使用 argparse 子命令，
        main.py 只负责入口调度。
"""

import argparse
import sys

from .config import Config
from .app import Application
from .services.exercise_builder import EXERCISE_TYPES


def build_parser() -> argparse.ArgumentParser:
    """构建命令行解析器（Extract Method）。"""
    parser = argparse.ArgumentParser(
        description="口算练习系统（重构版）",
    )
    parser.add_argument("--data-dir", default="data", help="数据存储目录")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    sub = parser.add_subparsers(dest="command", help="子命令")

    # generate
    p = sub.add_parser("generate", help="生成习题")
    p.add_argument("--type", default="mixed", choices=list(EXERCISE_TYPES.keys()))
    p.add_argument("--count", type=int, default=50)
    p.add_argument("--seed", type=int, default=None)

    # grade
    p = sub.add_parser("grade", help="批改答卷")
    p.add_argument("--answers", required=True, help="答案 CSV 路径")

    # analyze
    sub.add_parser("analyze", help="成绩分析")

    # target
    p = sub.add_parser("target", help="针对性练习")
    p.add_argument("--count", type=int, default=20)
    p.add_argument("--seed", type=int, default=None)

    # demo
    sub.add_parser("demo", help="完整演示")

    return parser


def run(args: argparse.Namespace) -> None:
    """执行 CLI 命令。"""
    cfg = Config(
        data_dir=args.data_dir,
        log_level=args.log_level,
    )
    app = Application(cfg)

    if args.command == "generate":
        exercise, path = app.generate_exercise(
            exercise_type=getattr(args, "type", "mixed"),
            count=getattr(args, "count", 50),
            seed=getattr(args, "seed", None),
        )
        print(f"[OK] 习题已生成: {exercise.exercise_id}")
        print(f"   类型: {exercise.exercise_type}  题目数: {exercise.problem_count}")
        print(f"   保存至: {path}")
        print(app.reporter.format_problem_grid(exercise.problems, cfg.display_cols))

    elif args.command == "grade":
        app.load_history()
        score = app.grade_from_file(args.answers)
        print(app.reporter.format_score_detail(score))

    elif args.command == "analyze":
        app.load_history()
        result = app.analyze()
        print(app.reporter.format_summary(result["summary"]))
        print()
        print(app.reporter.format_weak_problems(result["weak_problems"]))

    elif args.command == "target":
        app.load_history()
        exercise = app.generate_targeted_practice(
            count=getattr(args, "count", 20),
            seed=getattr(args, "seed", None),
        )
        print(f"[>>] 针对性练习: {exercise.exercise_id} ({exercise.problem_count} 题)")
        print(app.reporter.format_problem_grid(exercise.problems, cfg.display_cols))

    elif args.command == "demo":
        _run_demo(app, cfg)

    else:
        build_parser().print_help()


def _run_demo(app: Application, cfg: Config) -> None:
    """完整演示流程（Extract Method 重构）。"""
    import random
    rng = random.Random(42)

    print("=" * 60)
    print("  口算练习系统 —— 完整演示（重构版）")
    print("=" * 60)

    # 步骤1: 生成习题
    print("\n-- 步骤1: 华经理生成习题 --")
    for ex_type in ["addition", "subtraction", "mixed"]:
        label = EXERCISE_TYPES[ex_type]["label"]
        ex, path = app.generate_exercise(ex_type, count=10, seed=42)
        print(f"   [{label}] {ex.exercise_id}")
        demo_ex = ex

    # 步骤2: 模拟答题
    print("\n-- 步骤2: 小明做题 + 妈妈录入 --")
    answers = {}
    for i, p in enumerate(demo_ex.problems, 1):
        answers[i] = p.answer if rng.random() < 0.9 \
            else p.answer + rng.choice([-3, -2, -1, 1, 2, 3])
    print(f"   习题 {demo_ex.exercise_id}: {demo_ex.problem_count} 题")

    # 步骤3: 批改
    print("\n-- 步骤3: 华经理批改 --")
    score = app.grade_from_dict(demo_ex.exercise_id, "XiaoMing", answers)
    print(f"   正确: {score.correct}  错误: {score.wrong}  得分: {score.percentage}%")

    # 步骤4: 模拟多次练习
    print("\n-- 步骤4: 模拟多次练习 --")
    for day in range(3):
        ex, _ = app.generate_exercise("mixed", count=10, seed=42 + day)
        ans = {}
        for i, p in enumerate(ex.problems, 1):
            key = (p.left, p.operator.symbol, p.right)
            if key in [(15, "+", 7), (88, "-", 21), (22, "+", 33)]:
                ans[i] = p.answer + rng.choice([-2, -1, 1, 2])
            else:
                ans[i] = p.answer if rng.random() < 0.92 else p.answer + 1
        sc = app.grade_from_dict(ex.exercise_id, "XiaoMing", ans)
        print(f"   Day {day + 1}: {ex.exercise_id} -> {sc.percentage}%")

    # 步骤5: 分析
    print("\n-- 步骤5: 成绩分析 --")
    result = app.analyze()
    print(f"   总练习: {result['summary']['total_sessions']}  平均: {result['summary']['avg_percentage']}%")
    for w in result["weak_problems"][:5]:
        print(f"     {w['left']}{w['operator']}{w['right']} 错{w['wrong_count']}次")

    # 步骤6: 针对性练习
    print("\n-- 步骤6: 针对性练习 --")
    targeted = app.generate_targeted_practice(count=10, seed=99)
    print(f"   {targeted.exercise_id}: {targeted.problem_count} 题")
    print(app.reporter.format_problem_grid(targeted.problems, cfg.display_cols))

    print("\n" + "=" * 60)
    print("  演示完成！")
    print("=" * 60)
