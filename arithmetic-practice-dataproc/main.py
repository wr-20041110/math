#!/usr/bin/env python3
"""
口算练习系统 —— 主入口（故事6：交互菜单版）。

功能：
  1. 生成习题  → 批量生成练习题，保存为 CSV 文件
  2. 批改答卷  → 导入答案 CSV，自动判题打分
  3. 成绩分析  → 统计历史成绩，识别弱项题目
  4. 针对性练习 → 根据弱项生成定制题目
  5. 交互练习  → 小明直接在电脑上答题，即时批改
  0. 退出

用法:
    python main.py
"""

import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.practice_manager import PracticeManager
from src.exercise_builder import EXERCISE_TYPES
from src.grader import Grader


# =========================================================================
# 配置
# =========================================================================

DATA_DIR = "data"
DEFAULT_COUNT = 50
DEFAULT_COLS = 5


# =========================================================================
# 菜单显示
# =========================================================================

def show_menu() -> None:
    """显示主菜单。"""
    print()
    print("=" * 50)
    print("           口算练习系统")
    print("=" * 50)
    print("  1. 生成习题       — 批量生成练习题，保存为 CSV")
    print("  2. 批改答卷       — 导入答案文件，自动判题打分")
    print("  3. 成绩分析       — 查看历史成绩，识别弱项题目")
    print("  4. 针对性练习     — 根据弱项生成定制练习题")
    print("  5. 交互练习       — 直接在电脑上做口算练习")
    print("  0. 退出")
    print("=" * 50)


def get_choice() -> int:
    """获取用户选择（含输入校验）。"""
    while True:
        try:
            raw = input("请选择 (0-5): ").strip()
            if raw == "":
                continue
            choice = int(raw)
            if 0 <= choice <= 5:
                return choice
            print("  [!] 请输入 0-5 之间的数字。")
        except ValueError:
            print("  [!] 输入无效，请输入数字。")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0


# =========================================================================
# 功能实现
# =========================================================================

def do_generate(pm: PracticeManager) -> None:
    """功能1：生成习题。"""
    print()
    print("--- 生成习题 ---")
    print("  习题类型: 1) 加法  2) 减法  3) 混合")
    type_map = {"1": "addition", "2": "subtraction", "3": "mixed"}
    while True:
        t = input("  请选择类型 (1-3, 回车=3): ").strip()
        if t == "":
            t = "3"
        if t in type_map:
            ex_type = type_map[t]
            break
        print("  [!] 请输入 1-3。")

    try:
        raw = input(f"  题目数量 (回车={DEFAULT_COUNT}): ").strip()
        count = int(raw) if raw else DEFAULT_COUNT
    except ValueError:
        print(f"  [!] 输入无效，使用默认值 {DEFAULT_COUNT}")
        count = DEFAULT_COUNT

    print(f"  正在生成 {count} 道{EXERCISE_TYPES[ex_type]['label']}...")
    rng = random.Random()
    exercise, path = pm.generate_exercise(
        exercise_type=ex_type,
        count=count,
        seed=rng.randint(0, 99999),
    )
    print()
    print(f"  [OK] 习题已生成: {exercise.exercise_id}")
    print(f"       类型: {exercise.exercise_type}  题目数: {exercise.total}")
    print(f"       保存至: {path}")
    print()
    for i, p in enumerate(exercise.problems, 1):
        end = "\t" if i % DEFAULT_COLS != 0 else "\n"
        print(f"  {p}", end=end)
    print()
    input("  按回车返回主菜单...")


def do_grade(pm: PracticeManager) -> None:
    """功能2：批改答卷。"""
    print()
    print("--- 批改答卷 ---")
    print("  请将答案 CSV 文件放入 data/answers/ 目录。")
    print("  文件名格式: EX-xxx_answers.csv")
    filepath = input("  答案文件路径 (如 data/answers/EX-xxx_answers.csv): ").strip()

    if not filepath:
        print("  [!] 未输入文件路径，已取消。")
        input("  按回车返回主菜单...")
        return

    if not os.path.isfile(filepath):
        print(f"  [!] 文件不存在: {filepath}")
        input("  按回车返回主菜单...")
        return

    pm.load_scores()
    try:
        score = pm.grade_answers(filepath)
        print()
        print(f"  [OK] 批改完成")
        print(f"       学生: {score.student}")
        print(f"       总题数: {score.total}")
        print(f"       正确: {score.correct}  错误: {score.wrong}")
        print(f"       得分: {score.percentage}%")
        if score.wrong_indices:
            print(f"       错题索引: {score.wrong_indices}")
    except Exception as e:
        print(f"  [!] 批改失败: {e}")
    input("  按回车返回主菜单...")


def do_analyze(pm: PracticeManager) -> None:
    """功能3：成绩分析。"""
    print()
    print("--- 成绩分析 ---")
    pm.load_scores()
    result = pm.analyze()
    summary = result["summary"]

    print()
    print("  === 成绩摘要 ===")
    print(f"  练习次数: {summary['total_sessions']}")
    print(f"  总做题数: {summary['total_problems_done']}")
    print(f"  总正确数: {summary['total_correct']}")
    print(f"  平均得分: {summary['avg_percentage']}%")
    print(f"  最佳: {summary['best']}%  最差: {summary['worst']}%")
    print()

    weak = result["weak_problems"]
    if weak:
        print(f"  === 弱项题目 (Top {min(len(weak), 10)}) ===")
        print(f"  {'题目':<12} {'正确答案':<8} {'错误次数':<8} {'错误率':<8}")
        print(f"  {'-' * 40}")
        for w in weak[:10]:
            prob = f"{w['num1']}{w['operator']}{w['num2']}"
            print(f"  {prob:<12} {w['correct_answer']:<8} "
                  f"{w['wrong_count']:<8} {w['error_rate']:.0%}")
    else:
        print("  [OK] 没有发现弱项题目！")
    print()
    input("  按回车返回主菜单...")


def do_target(pm: PracticeManager) -> None:
    """功能4：针对性练习。"""
    print()
    print("--- 针对性练习 ---")

    try:
        raw = input(f"  题目数量 (回车=20): ").strip()
        count = int(raw) if raw else 20
    except ValueError:
        print("  [!] 输入无效，使用默认值 20")
        count = 20

    pm.load_scores()
    exercise = pm.generate_targeted_practice(count=count)
    print()
    print(f"  [>>] 针对性练习: {exercise.exercise_id}")
    print(f"       题目数: {exercise.total}")
    print()
    for i, p in enumerate(exercise.problems, 1):
        end = "\t" if i % DEFAULT_COLS != 0 else "\n"
        print(f"  {p}", end=end)
    print()
    input("  按回车返回主菜单...")


def do_interactive(pm: PracticeManager) -> None:
    """功能5：交互练习 — 小明直接在电脑上答题，即时批改。"""
    print()
    print("=" * 50)
    print("           交互练习")
    print("=" * 50)
    print("  请在电脑上完成口算题，输入答案后按回车。")
    print("  做完所有题目后自动批改打分。")
    print()

    # 选择练习类型
    print("  习题类型: 1) 加法  2) 减法  3) 混合")
    type_map = {"1": "addition", "2": "subtraction", "3": "mixed"}
    while True:
        t = input("  请选择类型 (1-3, 回车=3): ").strip()
        if t == "":
            t = "3"
        if t in type_map:
            ex_type = type_map[t]
            break
        print("  [!] 请输入 1-3。")

    try:
        raw = input("  题目数量 (回车=20): ").strip()
        count = int(raw) if raw else 20
    except ValueError:
        count = 20

    # 生成题目
    print()
    print(f"  正在生成 {count} 道{EXERCISE_TYPES[ex_type]['label']}...")
    rng = random.Random()
    exercise, _ = pm.generate_exercise(exercise_type=ex_type, count=count,
                                        seed=rng.randint(0, 99999))

    # 逐题练习
    print(f"\n  === 开始练习 ({exercise.exercise_id}) ===\n")
    answers: dict = {}
    grader = Grader()

    for i, p in enumerate(exercise.problems, 1):
        # 显示进度条
        progress = f"[{i}/{exercise.total}]"
        prompt_text = f"  {progress} 第{i}题: {p}"

        while True:
            try:
                raw = input(prompt_text).strip()
                if raw == "":
                    print("  [!] 请输入答案。")
                    continue
                student_ans = int(raw)
                answers[i] = student_ans
                break
            except ValueError:
                print("  [!] 请输入有效整数。")

    # 即时批改
    print()
    print("  --- 批改结果 ---")
    correct_count = 0
    for i, p in enumerate(exercise.problems, 1):
        student_ans = answers.get(i)
        right_ans = p.answer
        if student_ans == right_ans:
            print(f"  第{i}题: {p}{student_ans}  ✓")
            correct_count += 1
        else:
            print(f"  第{i}题: {p}{student_ans}  ✗  正确答案: {right_ans}")

    total = exercise.total
    wrong_count = total - correct_count
    percentage = round((correct_count / total) * 100, 1)

    # 保存成绩
    from src.models import AnswerSheet
    answer_sheet = AnswerSheet(
        exercise_id=exercise.exercise_id,
        student="XiaoMing",
        answers=answers,
    )
    score = grader.grade(exercise, answer_sheet)
    score_path = os.path.join(pm._score_dir, "scores.csv")
    from src.csv_handler import CsvHandler
    CsvHandler().save_scores([score], score_path)
    pm._analyzer.add_scores([score])

    # 显示总分
    print(f"\n  ============== 成绩单 ==============")
    print(f"  总题数: {total}")
    print(f"  正确: {correct_count}  错误: {wrong_count}")
    print(f"  得分: {percentage}%")

    if percentage == 100:
        print(f"  ☆ 太棒了，全部正确！☆")
    elif percentage >= 80:
        print(f"  ★ 做得不错，继续加油！★")
    else:
        print(f"  ▲ 还需要多加练习哦！▲")
    print(f"  ====================================")

    input("\n  按回车返回主菜单...")


# =========================================================================
# 主入口
# =========================================================================

def main() -> None:
    """程序主入口 —— 循环菜单模式。"""
    pm = PracticeManager(data_dir=DATA_DIR)
    pm.load_scores()

    print()
    print("=" * 50)
    print("           口算练习系统")
    print("           欢迎使用！")
    print("=" * 50)

    while True:
        show_menu()
        choice = get_choice()
        print()

        if choice == 0:
            print("  再见！")
            print()
            break
        elif choice == 1:
            do_generate(pm)
        elif choice == 2:
            do_grade(pm)
        elif choice == 3:
            do_analyze(pm)
        elif choice == 4:
            do_target(pm)
        elif choice == 5:
            do_interactive(pm)


if __name__ == "__main__":
    main()
