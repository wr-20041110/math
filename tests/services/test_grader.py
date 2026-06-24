"""TDD 测试 —— Grader 判题器。"""
import pytest
from mathpractice.services.grader import Grader
from mathpractice.models.exercise import Exercise
from mathpractice.models.answer import AnswerSheet
from mathpractice.core.problem import Problem
from mathpractice.core.operators import Addition


class TestGraderTDD:
    def test_should_grade_all_correct_as_100_percent(self):
        """TDD: 全部正确 → 100%。"""
        ex = Exercise(exercise_id="EX-001", exercise_type="mixed",
                     problems=[Problem(5, 3, Addition())])
        sheet = AnswerSheet(exercise_id="EX-001", student="Test", answers={1: 8})
        score = Grader().evaluate(ex, sheet)
        assert score.correct == 1
        assert score.wrong == 0
        assert score.percentage == 100.0

    def test_should_grade_wrong_answer(self):
        """TDD: 答错应计入 wrong_indices。"""
        ex = Exercise(exercise_id="EX-001", exercise_type="mixed",
                     problems=[Problem(5, 3, Addition())])
        sheet = AnswerSheet(exercise_id="EX-001", student="Test", answers={1: 999})
        score = Grader().evaluate(ex, sheet)
        assert score.correct == 0
        assert score.wrong == 1
        assert 1 in score.wrong_indices

    def test_should_reject_mismatched_answer_count(self):
        """TDD: 答案数 != 题目数 → ValueError。"""
        ex = Exercise(exercise_id="EX-001", exercise_type="mixed",
                     problems=[Problem(1, 1, Addition()), Problem(2, 2, Addition())])
        sheet = AnswerSheet(exercise_id="EX-001", student="Test", answers={1: 2})
        with pytest.raises(ValueError, match="不匹配"):
            Grader().evaluate(ex, sheet)
