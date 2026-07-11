#!/usr/bin/env python3
"""
口算练习系统（全功能版）—— CLI 主入口。

用法:
    python main.py setup                    # 初始化数据库
    python main.py student add <name> [grade]  # 注册学生
    python main.py student list             # 列出学生
    python main.py generate --type mixed [--count 20]  # 生成习题
    python main.py grade <exercise_id> <student>  # 提交答案+判题
    python main.py overview                 # 全班概览
    python main.py weak [--top 15]          # 弱项分析
    python main.py progress <student>       # 学生进步
    python main.py stats                    # 数据库统计
    python main.py export-word <exercise_id> [--output file.docx]  # 导出Word
    python main.py export-chart <student>   # 导出图表
    python main.py demo                     # 完整演示
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from app import Application


def main() -> None:
    parser = argparse.ArgumentParser(
        description="口算练习系统（全功能版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # setup
    subparsers.add_parser("setup", help="初始化数据库")

    # student
    stu_parser = subparsers.add_parser("student", help="学生管理")
    stu_sub = stu_parser.add_subparsers(dest="sub")
    stu_add = stu_sub.add_parser("add", help="注册学生")
    stu_add.add_argument("name", help="学生姓名")
    stu_add.add_argument("grade", nargs="?", default="", help="年级/班级")
    stu_sub.add_parser("list", help="列出所有学生")

    # generate
    gen_parser = subparsers.add_parser("generate", help="生成习题")
    gen_parser.add_argument("--type", default="mixed",
                            choices=["addition", "subtraction", "mixed"],
                            help="习题类型")
    gen_parser.add_argument("--count", type=int, default=20, help="题目数量")

    # grade
    grade_parser = subparsers.add_parser("grade", help="提交答案并判题")
    grade_parser.add_argument("exercise_id", help="习题ID")
    grade_parser.add_argument("student", help="学生姓名")

    # overview
    subparsers.add_parser("overview", help="全班成绩概览")

    # weak
    weak_parser = subparsers.add_parser("weak", help="弱项分析")
    weak_parser.add_argument("--top", type=int, default=15, help="显示前N个")

    # progress
    prog_parser = subparsers.add_parser("progress", help="学生进步轨迹")
    prog_parser.add_argument("student", help="学生姓名")

    # stats
    subparsers.add_parser("stats", help="数据库统计")

    # export-word
    export_w = subparsers.add_parser("export-word", help="导出习题为Word文档")
    export_w.add_argument("exercise_id", help="习题ID")
    export_w.add_argument("--output", "-o", default=None, help="输出文件路径")

    # export-chart
    export_c = subparsers.add_parser("export-chart", help="导出学生成绩图表")
    export_c.add_argument("student", help="学生姓名")
    export_c.add_argument("--output", "-o", default=None, help="输出目录")

    # demo
    subparsers.add_parser("demo", help="运行完整演示")

    # web
    subparsers.add_parser("web", help="启动Web服务")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    app = Application()

    if args.command == "setup":
        print("[OK] 数据库已初始化 (data/mathpractice.db)")

    elif args.command == "student":
        if args.sub == "add":
            sid = app.register_student(args.name, args.grade)
            print(f"[OK] 学生已注册: ID={sid}")
        elif args.sub == "list":
            for s in app.list_students():
                print(f"  ID={s['id']:<4} {s['name']:<10} {s['grade']}")
        else:
            print("用法: student add <name> [grade]  或  student list")

    elif args.command == "generate":
        ex = app.generate_and_save(args.type, args.count)
        print(f"[OK] 习题已生成: {ex.exercise_id} ({ex.problem_count} 题)")
        for i, p in enumerate(ex.problems, 1):
            end = "\t" if i % 5 != 0 else "\n"
            print(f"{p}", end=end)
        print()

    elif args.command == "grade":
        import random
        rng = random.Random(42)
        ex = app.load_exercise(args.exercise_id)
        answers = {}
        for i, p in enumerate(ex.problems, 1):
            answers[i] = p.answer if rng.random() < 0.85 else p.answer + rng.choice([-2, -1, 1, 2])
        result = app.submit_and_grade(args.exercise_id, args.student, answers)
        print(f"[OK] 判题完成: {result['correct']}/{result['total']} 正确, 得分 {result['percentage']}%")
        if result["wrong_indices"]:
            print(f"   错题: {result['wrong_indices']}")

    elif args.command == "overview":
        rows = app.class_overview()
        print(f"{'姓名':<10} {'练习次数':<8} {'平均分':<8} {'最佳':<6} {'最差':<6}")
        print("-" * 40)
        for r in rows:
            print(f"{r['name']:<10} {r['total_sessions']:<8} {r['avg_score']:<8} "
                  f"{r['best_score']:<6} {r['worst_score']:<6}")

    elif args.command == "weak":
        rows = app.weak_problems(args.top)
        print(f"{'题目':<12} {'正确答案':<8} {'尝试':<6} {'错误':<6} {'错误率':<8}")
        print("-" * 42)
        for r in rows:
            prob = f"{r['left_operand']}{r['operator']}{r['right_operand']}"
            print(f"{prob:<12} {r['correct_answer']:<8} {r['total_attempts']:<6} "
                  f"{r['wrong_count']:<6} {r['error_rate']}%")

    elif args.command == "progress":
        try:
            rows = app.student_progress(args.student)
            if not rows:
                print(f"  {args.student} 暂无练习记录")
            else:
                print(f"  {args.student} 的练习记录:")
                for r in rows:
                    print(f"    {r['exercise_id']}: {r['correct']}/{r['total']} ({r['percentage']}%)")
        except ValueError as e:
            print(f"[ERROR] {e}")

    elif args.command == "stats":
        s = app.stats()
        print(f"学生: {s.get('student_count', 0)}  习题集: {s.get('exercise_count', 0)}")
        print(f"题目: {s.get('problem_count', 0)}  答案: {s.get('answer_count', 0)}")
        print(f"成绩: {s.get('score_count', 0)}")

    elif args.command == "export-word":
        from export.word_exporter import WordExporter
        ex = app.load_exercise(args.exercise_id)
        output_path = args.output or f"data/exports/{args.exercise_id}.docx"
        os.makedirs(os.path.dirname(output_path) or "data/exports", exist_ok=True)
        exporter = WordExporter()
        exporter.export_exercise(ex, output_path)
        print(f"[OK] Word文档已导出: {output_path}")

    elif args.command == "export-chart":
        from chart.chart_renderer import ChartRenderer
        try:
            progress = app.student_progress(args.student)
            if not progress:
                print(f"  {args.student} 暂无练习记录，无法生成图表")
                return
            output_dir = args.output or "data/charts"
            renderer = ChartRenderer(output_dir)
            path = renderer.plot_score_trend(progress, args.student)
            print(f"[OK] 成绩趋势图已保存: {path}")
        except ValueError as e:
            print(f"[ERROR] {e}")

    elif args.command == "demo":
        _run_demo(app)

    elif args.command == "web":
        print("启动Web服务...")
        print("请使用: python run_web.py")
        print("或: flask --app src.web run")

    else:
        parser.print_help()


def _run_demo(app: Application) -> None:
    """完整演示。"""
    import random
    rng = random.Random(42)

    print("=" * 50)
    print("  口算练习系统 —— 全功能版演示")
    print("=" * 50)

    # 注册学生
    print("\n-- 注册学生 --")
    for name in ["小明", "小红", "小刚"]:
        sid = app.register_student(name, "三年级1班")
        print(f"  {name}: ID={sid}")

    # 生成习题
    print("\n-- 生成习题 --")
    ex = app.generate_and_save("mixed", count=15)
    print(f"  {ex.exercise_id}: {ex.problem_count} 题")

    # 模拟答题
    print("\n-- 模拟答题 & 判题 --")
    for name in ["小明", "小红", "小刚"]:
        answers = {}
        for i, p in enumerate(ex.problems, 1):
            err_rate = 0.1 if name == "小红" else 0.2 if name == "小明" else 0.35
            answers[i] = p.answer if rng.random() > err_rate \
                else p.answer + rng.choice([-2, -1, 1, 2])
        result = app.submit_and_grade(ex.exercise_id, name, answers)
        print(f"  {name}: {result['correct']}/{result['total']} ({result['percentage']}%)")

    # 再来一轮
    ex2 = app.generate_and_save("mixed", count=15)
    for name in ["小明", "小红", "小刚"]:
        answers = {}
        for i, p in enumerate(ex2.problems, 1):
            answers[i] = p.answer if rng.random() > 0.15 \
                else p.answer + rng.choice([-2, -1, 1, 2])
        result = app.submit_and_grade(ex2.exercise_id, name, answers)
        print(f"  {name} (Round 2): {result['correct']}/{result['total']} ({result['percentage']}%)")

    # 全班概览
    print("\n-- 全班概览 --")
    for r in app.class_overview():
        print(f"  {r['name']:<8} 练习{r['total_sessions']}次  均分{r['avg_score']}%")

    # 弱项分析
    print("\n-- 弱项分析 (Top 5) --")
    for r in app.weak_problems(5):
        print(f"  {r['left_operand']}{r['operator']}{r['right_operand']} "
              f"错{r['wrong_count']}次 错误率{r['error_rate']}%")

    # 统计
    s = app.stats()
    print(f"\n-- 数据库统计 --")
    print(f"  学生{s['student_count']} 习题集{s['exercise_count']} "
          f"题目{s['problem_count']} 答案{s['answer_count']} 成绩{s['score_count']}")

    print("\n" + "=" * 50)
    print("  演示完成！数据保存在 data/mathpractice.db")
    print("  使用 'python run_web.py' 启动Web界面")
    print("=" * 50)


if __name__ == "__main__":
    main()
