"""
数据模型单元测试 —— Exercise, AnswerSheet, Score, StudentRecord。

覆盖：
  - 数据建模：正确的构造与属性访问
  - 数据校验：非法输入拒绝
  - 不变量：Score 的 correct+wrong==total
"""

import pytest
from datetime import datetime
from src.models import Exercise, AnswerSheet, Score, StudentRecord
from src.operators import Addition as Add, Subtraction as Sub
from src.problem import Problem


class TestExercise:
    def test_valid_creation(self, sample_exercise):
        assert sample_exercise.exercise_id == "EX-TEST-001"
        assert sample_exercise.exercise_type == "mixed"
        assert sample_exercise.total == 10

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="无效的习题类型"):
            Exercise(exercise_id="EX-001", exercise_type="invalid",
                     problems=[Problem(1, 1, Add())])

    def test_empty_problems_raises(self):
        with pytest.raises(ValueError, match="习题不能为空"):
            Exercise(exercise_id="EX-001", exercise_type="mixed", problems=[])

    def test_targeted_type_accepted(self):
        """targeted 类型（针对性练习）应被接受。"""
        ex = Exercise(exercise_id="EX-T-001", exercise_type="targeted",
                      problems=[Problem(1, 2, Add())])
        assert ex.exercise_type == "targeted"

    def test_get_problem(self, sample_exercise):
        p = sample_exercise.get_problem(1)
        assert p.num1 == 15
        assert p.num2 == 7
        assert p.operator.symbol == "+"

    def test_get_problem_out_of_range(self, sample_exercise):
        with pytest.raises(IndexError):
            sample_exercise.get_problem(0)
        with pytest.raises(IndexError):
            sample_exercise.get_problem(11)

    def test_frozen_immutable(self, sample_exercise):
        with pytest.raises(Exception):
            sample_exercise.exercise_id = "hacked"  # type: ignore[misc]


class TestAnswerSheet:
    def test_valid_creation(self, sample_answer_sheet):
        assert sample_answer_sheet.exercise_id == "EX-TEST-001"
        assert sample_answer_sheet.student == "XiaoMing"
        assert len(sample_answer_sheet.answers) == 10

    def test_empty_answers_raises(self):
        with pytest.raises(ValueError, match="答案不能为空"):
            AnswerSheet(exercise_id="EX-001", student="Test", answers={})

    def test_get_answer(self, sample_answer_sheet):
        assert sample_answer_sheet.get_answer(1) == 22
        assert sample_answer_sheet.get_answer(99) is None

    def test_frozen_immutable(self, sample_answer_sheet):
        with pytest.raises(Exception):
            sample_answer_sheet.student = "hacked"  # type: ignore[misc]


class TestScore:
    """Score 的契约式编程验证。"""

    def test_valid_creation(self, sample_score):
        assert sample_score.exercise_id == "EX-TEST-001"
        assert sample_score.percentage == 80.0
        assert sample_score.wrong_indices == [2, 7]

    def test_invariant_correct_plus_wrong_equals_total(self):
        """契约不变量：correct + wrong == total。"""
        with pytest.raises(ValueError, match="契约违反"):
            Score(exercise_id="EX-001", student="Test",
                  total=10, correct=7, wrong=2, percentage=70.0, wrong_indices=[1, 2])

    def test_invariant_percentage_range(self):
        """契约不变量：percentage ∈ [0, 100]。"""
        with pytest.raises(ValueError, match="契约违反"):
            Score(exercise_id="EX-001", student="Test",
                  total=10, correct=11, wrong=-1, percentage=110.0, wrong_indices=[])

    def test_invariant_wrong_indices_length(self):
        """契约不变量：wrong_indices 长度 == wrong。"""
        with pytest.raises(ValueError, match="契约违反"):
            Score(exercise_id="EX-001", student="Test",
                  total=10, correct=8, wrong=2, percentage=80.0, wrong_indices=[1, 2, 3])

    def test_perfect_score(self):
        s = Score(exercise_id="EX-001", student="Test",
                  total=10, correct=10, wrong=0, percentage=100.0, wrong_indices=[])
        assert s.percentage == 100.0
        assert s.wrong_indices == []

    def test_zero_score(self):
        s = Score(exercise_id="EX-001", student="Test",
                  total=10, correct=0, wrong=10, percentage=0.0,
                  wrong_indices=list(range(1, 11)))
        assert s.percentage == 0.0


class TestStudentRecord:
    def test_empty_record(self):
        r = StudentRecord(name="XiaoMing")
        assert r.total_exercises == 0
        assert r.average_percentage == 0.0

    def test_add_score(self, sample_score):
        r = StudentRecord(name="XiaoMing")
        r.add_score(sample_score)
        assert r.total_exercises == 1
        assert r.average_percentage == 80.0

    def test_multiple_scores(self, sample_score):
        r = StudentRecord(name="XiaoMing")
        r.add_score(sample_score)
        s2 = Score(exercise_id="EX-002", student="XiaoMing",
                   total=10, correct=9, wrong=1, percentage=90.0, wrong_indices=[5])
        r.add_score(s2)
        assert r.total_exercises == 2
        assert r.average_percentage == 85.0
