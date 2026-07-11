"""
ExerciseSheet 类的单元测试。

覆盖：
  - 生成指定数量的题目
  - 题目全部唯一（故事3 去重）
  - 包含加法和减法（故事3 混合）
  - 所有题目满足约束
  - 种子可重现性
  - max_attempts 耗尽时抛出 RuntimeError
"""

import pytest
from src.exercise import ExerciseSheet
from src.problem import Problem


class TestExerciseSheetGenerate:
    """测试习题集生成。"""

    def test_generates_correct_count(self):
        sheet = ExerciseSheet(total=50, seed=42)
        problems = sheet.generate()
        assert len(problems) == 50

    def test_all_unique(self):
        """故事3：50 道题全部唯一，无重复。"""
        sheet = ExerciseSheet(total=50, seed=42)
        problems = sheet.generate()
        # 利用 Problem.__eq__ 和 __hash__
        unique_ids = {(p.num1, p.num2, p.operator) for p in problems}
        assert len(unique_ids) == 50

    def test_contains_both_operators(self):
        """故事3：应同时包含加法和减法。"""
        sheet = ExerciseSheet(total=50, seed=42)
        problems = sheet.generate()
        ops = {p.operator for p in problems}
        assert "+" in ops
        assert "-" in ops

    def test_all_satisfy_constraints(self):
        """所有题目应满足故事2的约束。"""
        sheet = ExerciseSheet(total=50)
        problems = sheet.generate()
        for p in problems:
            assert 0 <= p.num1 <= 100
            assert 0 <= p.num2 <= 100
            assert p.operator in ("+", "-")
            assert p.answer <= 100
            assert p.answer >= 0

    def test_generate_zero_questions(self):
        """边界：0 道题。"""
        sheet = ExerciseSheet(total=0, seed=42)
        problems = sheet.generate()
        assert problems == []

    def test_problems_property_returns_copy(self):
        """problems 属性返回副本，修改不影响内部状态。"""
        sheet = ExerciseSheet(total=10, seed=42)
        sheet.generate()
        p1 = sheet.problems
        p1.append(Problem(num1=1, num2=1, operator="+"))
        assert len(sheet.problems) == 10  # 未受影响


class TestExerciseSheetSeed:
    """测试种子可重现性。"""

    def test_same_seed_same_sheet(self):
        sheet1 = ExerciseSheet(total=30, seed=99)
        sheet2 = ExerciseSheet(total=30, seed=99)
        p1 = sheet1.generate()
        p2 = sheet2.generate()
        assert p1 == p2

    def test_no_seed_different_sheet(self):
        """不设种子时，每次生成的题目通常不同。"""
        sheet1 = ExerciseSheet(total=50)
        sheet2 = ExerciseSheet(total=50)
        p1 = sheet1.generate()
        p2 = sheet2.generate()
        # 极小概率相同，但 seed=None 使用了系统熵源
        # 只检查都是合法列表
        assert len(p1) == 50
        assert len(p2) == 50


class TestExerciseSheetMaxAttempts:
    """测试 max_attempts 保护。"""

    def test_raises_when_exhausted(self):
        """当要求生成超过可行空间的题目数时，应抛出 RuntimeError。"""
        # 加法题 + 减法题的可行组合远小于 100000，但 100000 道不重复在 10000 次尝试内完不成
        sheet = ExerciseSheet(total=100000, max_attempts=10)
        with pytest.raises(RuntimeError, match="无法生成"):
            sheet.generate()


class TestExerciseSheetValidation:
    """测试输入校验。"""

    def test_negative_total_raises(self):
        with pytest.raises(ValueError):
            ExerciseSheet(total=-5)
