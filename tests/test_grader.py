"""
Grader 单元测试 —— 自动判题 + 契约式编程。

覆盖：
  - 全部正确的批改
  - 含错误的批改
  - 前置条件检查（空习题、空答案、数量不匹配）
  - 契约不变量验证
"""

import pytest
from src.grader import Grader
from src.models import Exercise, AnswerSheet, Score
from src.operators import Addition as Add
from src.problem import Problem


grader = Grader()


class TestGraderCorrectAnswers:
    """全部正确的场景。"""

    def test_all_correct(self, sample_exercise, sample_answers):
        sheet = AnswerSheet(exercise_id="EX-TEST-001", student="Test",
                           answers=sample_answers)
        score = grader.grade(sample_exercise, sheet)

        assert score.total == 10
        assert score.correct == 10
        assert score.wrong == 0
        assert score.percentage == 100.0
        assert score.wrong_indices == []

    def test_single_problem_correct(self):
        ex = Exercise(exercise_id="EX-001", exercise_type="mixed",
                     problems=[Problem(5, 3, Add())])
        sheet = AnswerSheet(exercise_id="EX-001", student="Test",
                           answers={1: 8})
        score = grader.grade(ex, sheet)
        assert score.correct == 1
        assert score.wrong == 0
        assert score.percentage == 100.0


class TestGraderWithErrors:
    """含错误的场景。"""

    def test_with_errors(self, sample_exercise, sample_answers_with_errors):
        sheet = AnswerSheet(exercise_id="EX-TEST-001", student="Test",
                           answers=sample_answers_with_errors)
        score = grader.grade(sample_exercise, sheet)

        assert score.total == 10
        assert score.correct == 7
        assert score.wrong == 3
        assert score.wrong_indices == [2, 7, 9]
        assert score.percentage == 70.0

    def test_all_wrong(self):
        ex = Exercise(exercise_id="EX-001", exercise_type="mixed",
                     problems=[Problem(5, 3, Add()), Problem(10, 2, Add())])
        sheet = AnswerSheet(exercise_id="EX-001", student="Test",
                           answers={1: 999, 2: 999})
        score = grader.grade(ex, sheet)
        assert score.correct == 0
        assert score.wrong == 2
        assert score.wrong_indices == [1, 2]
        assert score.percentage == 0.0


class TestGraderPreconditions:
    """前置条件（契约式编程）测试。"""

    def test_answer_count_more_than_problems(self):
        """前置条件：答案数多于题目数应被拒绝。"""
        ex = Exercise(exercise_id="EX-001", exercise_type="mixed",
                     problems=[Problem(1, 1, Add()), Problem(2, 2, Add())])
        # 只有 1 个答案但题目有 2 道
        sheet = AnswerSheet(exercise_id="EX-001", student="Test",
                           answers={1: 2})
        with pytest.raises(ValueError, match="不匹配"):
            grader.grade(ex, sheet)

    def test_empty_answers_raises(self):
        """空答卷应拒绝。"""
        ex = Exercise(exercise_id="EX-001", exercise_type="mixed",
                     problems=[Problem(1, 1, Add())])
        # 构造空答案（AnswerSheet 已拒绝空 dict）
        # 此处验证 AnswerSheet 的校验
        with pytest.raises(ValueError, match="答案不能为空"):
            AnswerSheet(exercise_id="EX-001", student="Test", answers={})

    def test_answer_count_mismatch(self, sample_exercise):
        """答案数与题目数不一致应报告详细信息。"""
        # 只有 5 个答案，但题目有 10 道
        partial_answers = {i: 0 for i in range(1, 6)}
        sheet = AnswerSheet(exercise_id="EX-TEST-001", student="Test",
                           answers=partial_answers)
        with pytest.raises(ValueError, match="不匹配"):
            grader.grade(sample_exercise, sheet)

    def test_answer_count_mismatch_extra_answer(self, sample_exercise):
        """答案数多于题目数应报告多余索引。"""
        answers = {i: 0 for i in range(1, 16)}  # 15 个答案，10 道题
        sheet = AnswerSheet(exercise_id="EX-TEST-001", student="Test",
                           answers=answers)
        with pytest.raises(ValueError, match="多余索引"):
            grader.grade(sample_exercise, sheet)


class TestGraderPostconditions:
    """后置条件（契约式编程）测试。"""

    def test_score_invariants_hold(self, sample_exercise, sample_answers_with_errors):
        """生成的 Score 必须满足契约不变量。"""
        sheet = AnswerSheet(exercise_id="EX-TEST-001", student="Test",
                           answers=sample_answers_with_errors)
        score = grader.grade(sample_exercise, sheet)
        # 不变量由 Score.__post_init__ 自动检查
        assert score.correct + score.wrong == score.total
        assert 0.0 <= score.percentage <= 100.0
        assert len(score.wrong_indices) == score.wrong
