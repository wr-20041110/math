#!/usr/bin/env python3
"""
口算练习系统（数据库版）—— 主入口。

用法:
    python main.py setup                    # 初始化数据库
    python main.py student add <name>       # 注册学生
    python main.py student list             # 列出学生
    python main.py generate --type mixed    # 生成习题
    python main.py grade <exercise_id> <student>  # 提交答案+判题
    python main.py overview                 # 全班概览
    python main.py weak                     # 弱项分析
    python main.py progress <student>       # 学生进步
    python main.py stats                    # 数据库统计
    python main.py demo                     # 完整演示
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from app import Application


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    cmd = args[0]
    app = Application()

    if cmd == "setup":
        print("[OK] 数据库已初始化 (data/mathpractice.db)")

    elif cmd == "student" and len(args) >= 2:
        sub = args[1]
        if sub == "add" and len(args) >= 3:
            sid = app.register_student(args[2], args[3] if len(args) > 3 else "")
            print(f"[OK] 学生已注册: ID={sid}")
        elif sub == "list":
            for s in app.list_students():
                print(f"  ID={s['id']:<4} {s['name']:<10} {s['grade']}")

    elif cmd == "generate":
        ex_type = args[2] if len(args) > 2 and args[1] == "--type" else "mixed"
        count = int(args[4]) if len(args) > 4 and args[3] == "--count" else 20
        ex = app.generate_and_save(ex_type, count)
        print(f"[OK] 习题已生成: {ex.exercise_id} ({ex.problem_count} 题)")
        for i, p in enumerate(ex.problems, 1):
            end = "\t" if i % 5 != 0 else "\n"
            print(f"{p}", end=end)
        print()

    elif cmd == "grade" and len(args) >= 3:
        import random
        rng = random.Random(42)
        ex_id = args[1]
        name = args[2]
        # 模拟答案（如果未从文件提供）
        ex = app.repo.load_exercise(ex_id)
        answers = {}
        for i, p in enumerate(ex.problems, 1):
            answers[i] = p.answer if rng.random() < 0.85 else p.answer + rng.choice([-2, -1, 1, 2])
        result = app.submit_and_grade(ex_id, name, answers)
        print(f"[OK] 判题完成: {result['correct']}/{result['total']} 正确, 得分 {result['percentage']}%")
        if result["wrong_indices"]:
            print(f"   错题: {result['wrong_indices']}")

    elif cmd == "overview":
        rows = app.class_overview()
        print(f"{'姓名':<10} {'练习次数':<8} {'平均分':<8} {'最佳':<6} {'最差':<6}")
        print("-" * 40)
        for r in rows:
            print(f"{r['name']:<10} {r['total_sessions']:<8} {r['avg_score']:<8} {r['best_score']:<6} {r['worst_score']:<6}")

    elif cmd == "weak":
        rows = app.weak_problems(15)
        print(f"{'题目':<12} {'正确答案':<8} {'尝试':<6} {'错误':<6} {'错误率':<8}")
        print("-" * 42)
        for r in rows:
            prob = f"{r['left_operand']}{r['operator']}{r['right_operand']}"
            print(f"{prob:<12} {r['correct_answer']:<8} {r['total_attempts']:<6} {r['wrong_count']:<6} {r['error_rate']}%")

    elif cmd == "progress" and len(args) >= 2:
        rows = app.student_progress(args[1])
        print(f"  {args[1]} 的练习记录:")
        for r in rows:
            print(f"    {r['exercise_id']}: {r['correct']}/{r['total']} ({r['percentage']}%)")

    elif cmd == "stats":
        s = app.stats()
        print(f"学生: {s.get('student_count', 0)}  习题集: {s.get('exercise_count', 0)}")
        print(f"题目: {s.get('problem_count', 0)}  答案: {s.get('answer_count', 0)}")
        print(f"成绩: {s.get('score_count', 0)}")

    elif cmd == "demo":
        _run_demo(app)

    else:
        print(__doc__)


def _run_demo(app: Application) -> None:
    """完整演示。"""
    import random
    rng = random.Random(42)

    print("=" * 50)
    print("  口算练习系统 —— 数据库版演示")
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

    # 模拟 3 个学生答题
    print("\n-- 模拟答题 & 判题 --")
    for name in ["小明", "小红", "小刚"]:
        answers = {}
        for i, p in enumerate(ex.problems, 1):
            # 各人错误率不同
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
            answers[i] = p.answer if rng.random() > 0.15 else p.answer + rng.choice([-2, -1, 1, 2])
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

    # 数据库统计
    s = app.stats()
    print(f"\n-- 数据库统计 --")
    print(f"  学生{s['student_count']} 习题集{s['exercise_count']} "
          f"题目{s['problem_count']} 答案{s['answer_count']} 成绩{s['score_count']}")

    print("\n" + "=" * 50)
    print("  演示完成！数据保存在 data/mathpractice.db")
    print("=" * 50)


if __name__ == "__main__":
    main()
