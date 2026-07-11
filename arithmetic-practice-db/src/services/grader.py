"""Grader —— 自动判题器（契约式编程）。"""
import logging
from datetime import datetime
from typing import List, Tuple
from models.exercise import Exercise
from models.answer import AnswerSheet
from models.score import Score

logger = logging.getLogger(__name__)


class Grader:
    """自动判题器。

    重构变更:
      - 引入 logging 替代 print 调试
      - 方法改名 grade_answers → evaluate（语义更清晰）
    """

    def evaluate(self, exercise: Exercise, answer_sheet: AnswerSheet) -> Score:
        """批改一份答卷并生成评分。

        前置条件:
          - 答案数必须与题目数一致

        Raises:
            ValueError: 前置条件不满足。
        """
        self._check_preconditions(exercise, answer_sheet)

        correct = 0
        wrong_indices: List[int] = []

        for i in range(1, exercise.problem_count + 1):
            problem = exercise.get_problem(i)
            student_ans = answer_sheet.get_answer(i)

            if student_ans is None or student_ans != problem.answer:
                wrong_indices.append(i)
            else:
                correct += 1

        wrong = len(wrong_indices)
        percentage = round((correct / exercise.problem_count) * 100, 1) \
            if exercise.problem_count > 0 else 0.0

        logger.info(
            "批改完成: %s 学生=%s 正确=%d/%d 得分=%.1f%%",
            exercise.exercise_id, answer_sheet.student,
            correct, exercise.problem_count, percentage,
        )

        return Score(
            exercise_id=exercise.exercise_id,
            student=answer_sheet.student,
            total=exercise.problem_count,
            correct=correct,
            wrong=wrong,
            percentage=percentage,
            wrong_indices=wrong_indices,
            graded_at=datetime.now(),
        )

    # ------------------------------------------------------------------
    # 前置条件检查 —— Extract Method
    # ------------------------------------------------------------------

    @staticmethod
    def _check_preconditions(exercise: Exercise, answer_sheet: AnswerSheet) -> None:
        """验证判题前置条件。"""
        ans_count = len(answer_sheet.answers)
        prob_count = exercise.problem_count

        if ans_count != prob_count:
            expected = set(range(1, prob_count + 1))
            actual = set(answer_sheet.answers.keys())
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            msg = f"前置条件失败: 答案数({ans_count})与题目数({prob_count})不匹配。"
            if missing:
                msg += f" 缺失索引: {missing}"
            if extra:
                msg += f" 多余索引: {extra}"
            raise ValueError(msg)
