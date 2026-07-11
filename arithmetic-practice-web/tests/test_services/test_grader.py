"""Grader 评分器单元测试。"""
import pytest
from core.operators import Addition, Subtraction
from core.problem import Problem
from models.exercise import Exercise
from models.answer import AnswerSheet
from services.grader import Grader


class TestGraderBasic:
    """基本评分测试。"""

    def setup_method(self):
        self.grader = Grader()

    def _make_exercise(self, problems):
        return Exercise("EX-TEST", "mixed", problems)

    def _make_answer_sheet(self, exercise_id, student, answers):
        return AnswerSheet(exercise_id, student, answers)

    def test_all_correct_scoring(self):
        """全部正确 → 100分。"""
        problems = [
            Problem(5, 3, Addition()),
            Problem(10, 20, Addition()),
        ]
        ex = self._make_exercise(problems)
        sheet = self._make_answer_sheet("EX-TEST", "Alice", {1: 8, 2: 30})

        score = self.grader.evaluate(ex, sheet)
        assert score.total == 2
        assert score.correct == 2
        assert score.wrong == 0
        assert score.percentage == 100.0
        assert score.wrong_indices == []

    def test_with_errors(self):
        """含错误 → 正确率和错题索引。"""
        problems = [
            Problem(80, 20, Subtraction()),
            Problem(55, 10, Subtraction()),
            Problem(30, 50, Addition()),
        ]
        ex = self._make_exercise(problems)
        sheet = self._make_answer_sheet("EX-TEST", "Bob", {
            1: 60,   # 正确: 80-20=60
            2: 44,   # 错误: 55-10=45
            3: 90,   # 错误: 30+50=80
        })

        score = self.grader.evaluate(ex, sheet)
        assert score.total == 3
        assert score.correct == 1
        assert score.wrong == 2
        assert 2 in score.wrong_indices
        assert 3 in score.wrong_indices

    def test_all_wrong(self):
        """全部错误 → 0分。"""
        problems = [Problem(1, 1, Addition())]
        ex = self._make_exercise(problems)
        sheet = self._make_answer_sheet("EX-TEST", "Charlie", {1: 999})

        score = self.grader.evaluate(ex, sheet)
        assert score.percentage == 0.0
        assert score.correct == 0

    def test_single_problem(self):
        """单题测试。"""
        problems = [Problem(15, 7, Addition())]
        ex = self._make_exercise(problems)
        sheet = self._make_answer_sheet("EX-TEST", "Alice", {1: 22})

        score = self.grader.evaluate(ex, sheet)
        assert score.total == 1
        assert score.correct == 1


class TestGraderPreconditions:
    """前置条件测试。"""

    def setup_method(self):
        self.grader = Grader()

    def test_answer_count_mismatch(self):
        """答案数量不匹配。"""
        problems = [Problem(5, 3, Addition()), Problem(10, 20, Addition())]
        ex = Exercise("EX-TEST", "mixed", problems)
        sheet = AnswerSheet("EX-TEST", "Alice", {1: 8})  # 只有1个答案

        with pytest.raises(ValueError):
            self.grader.evaluate(ex, sheet)

    def test_empty_answers(self):
        """空答案拒绝。"""
        with pytest.raises(ValueError):
            AnswerSheet("EX-TEST", "Alice", {})


class TestScoreInvariants:
    """评分结果契约测试。"""

    def test_correct_plus_wrong_equals_total(self, sample_score):
        assert sample_score.correct + sample_score.wrong == sample_score.total

    def test_percentage_range(self, sample_score):
        assert 0.0 <= sample_score.percentage <= 100.0

    def test_wrong_indices_length(self, sample_score):
        assert len(sample_score.wrong_indices) == sample_score.wrong
