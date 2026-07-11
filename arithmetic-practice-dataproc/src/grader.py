"""
Grader —— 自动判题打分器。

契约式编程（Design by Contract）：
  前置条件 (preconditions):
    - exercise 非空
    - answer_sheet 非空
    - answer_sheet 的答案数应与 exercise 题目数一致

  后置条件 (postconditions):
    - Score.correct + Score.wrong == Score.total
    - 0.0 <= Score.percentage <= 100.0
    - len(Score.wrong_indices) == Score.wrong

  不变量 (invariants):
    - wrong_indices 中的每个索引确实对应一道答错的题
    - 每道题的批改结果确定（正确/错误）
"""

from typing import List, Tuple
from datetime import datetime

from .models import Exercise, AnswerSheet, Score, Problem


class Grader:
    """自动判题器。

    逐题比对标准答案与学生答案，生成评分结果。
    所有契约检查内置于 Score 的 __post_init__ 中。
    """

    def grade(self, exercise: Exercise, answer_sheet: AnswerSheet) -> Score:
        """批改一份答卷。

        前置条件检查（防御性编程 —— 快速失败）。

        Args:
            exercise: 习题集。
            answer_sheet: 学生答卷。

        Returns:
            Score 实例。

        Raises:
            ValueError: 前置条件不满足。
        """
        # ---------- 前置条件 ----------
        if not exercise.problems:
            raise ValueError("前置条件失败: 习题集为空")
        if not answer_sheet.answers:
            raise ValueError("前置条件失败: 答卷为空")

        # 答案数与题目数一致性检查
        ans_count = len(answer_sheet.answers)
        prob_count = exercise.total
        if ans_count != prob_count:
            # 列出缺失和多余的索引
            expected_indices = set(range(1, prob_count + 1))
            actual_indices = set(answer_sheet.answers.keys())
            missing = sorted(expected_indices - actual_indices)
            extra = sorted(actual_indices - expected_indices)
            msg = (
                f"前置条件失败: 答案数({ans_count})与题目数({prob_count})不匹配。"
            )
            if missing:
                msg += f" 缺失索引: {missing}"
            if extra:
                msg += f" 多余索引: {extra}"
            raise ValueError(msg)

        # ---------- 逐题批改 ----------
        correct = 0
        wrong = 0
        wrong_indices: List[int] = []

        for i in range(1, prob_count + 1):
            problem = exercise.get_problem(i)
            student_ans = answer_sheet.get_answer(i)

            if student_ans is None:
                wrong += 1
                wrong_indices.append(i)
                continue

            if student_ans == problem.answer:
                correct += 1
            else:
                wrong += 1
                wrong_indices.append(i)

        # ---------- 计算百分比 ----------
        percentage = round((correct / prob_count) * 100, 1) if prob_count > 0 else 0.0

        # ---------- 构造 Score（后置条件 + 不变量由 Score.__post_init__ 保证）----------
        score = Score(
            exercise_id=exercise.exercise_id,
            student=answer_sheet.student,
            total=prob_count,
            correct=correct,
            wrong=wrong,
            percentage=percentage,
            wrong_indices=wrong_indices,
            graded_at=datetime.now(),
        )

        return score

    def batch_grade(
        self, exercises_and_answers: List[Tuple[Exercise, AnswerSheet]]
    ) -> List[Score]:
        """批量批改。

        Args:
            exercises_and_answers: (Exercise, AnswerSheet) 对的列表。

        Returns:
            Score 列表。
        """
        return [self.grade(ex, ans) for ex, ans in exercises_and_answers]
