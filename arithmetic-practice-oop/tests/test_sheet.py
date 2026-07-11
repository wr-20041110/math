"""
ExerciseSheet 外观类（Facade）的集成测试。

覆盖：
  - 外观模式：简化客户端对子系统的调用
  - 端到端：从生成到显示的完整流程
  - 统计信息
  - 自定义运算符/约束组合
"""

import pytest
from src.sheet import ExerciseSheet
from src.operators import Addition, Subtraction
from src.constraints import OperandRangeConstraint, SumLimitConstraint
from src.problem import Problem


class TestExerciseSheetBasic:
    """基本功能测试。"""

    def test_default_creation(self):
        sheet = ExerciseSheet(seed=42)
        assert sheet is not None

    def test_render_returns_string(self):
        sheet = ExerciseSheet(total=10, seed=42)
        output = sheet.render()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_has_correct_row_count(self):
        """10 题、5 列 → 2 行。"""
        sheet = ExerciseSheet(total=10, cols=5, seed=42)
        output = sheet.render()
        assert len(output.split("\n")) == 2

    def test_no_answers(self):
        sheet = ExerciseSheet(total=10, seed=42, show_answers=False)
        output = sheet.render()
        assert "=" in output
        # 不应包含答案数字跟在 = 后（极简检查）
        assert not any(c.isdigit() for c in output.split("=")[1][:1] if output.split("=")[1])

    def test_with_answers(self):
        sheet = ExerciseSheet(total=10, seed=42, show_answers=True)
        output = sheet.render()
        # 带答案输出应有 "=数字" 的模式
        assert "=0" in output or any(f"={i}" in output for i in range(1, 101))

    def test_generates_unique_problems(self):
        sheet = ExerciseSheet(total=50, seed=42)
        sheet.generate()
        problems = sheet.get_problems()
        ids = {(p.num1, p.num2, p.operator.symbol) for p in problems}
        assert len(ids) == 50


class TestExerciseSheetStats:
    """统计信息测试。"""

    def test_stats_total(self):
        sheet = ExerciseSheet(total=30, seed=42)
        sheet.generate()
        assert sheet.stats["total"] == 30

    def test_stats_mix(self):
        sheet = ExerciseSheet(total=50, seed=42)
        sheet.generate()
        s = sheet.stats
        assert s["addition"] + s["subtraction"] == 50
        assert s["addition"] > 0
        assert s["subtraction"] > 0

    def test_stats_answer_range(self):
        sheet = ExerciseSheet(total=20, seed=42)
        sheet.generate()
        s = sheet.stats
        assert 0 <= s["min_answer"] <= s["max_answer"] <= 100


class TestExerciseSheetCustomization:
    """自定义策略组合测试。"""

    def test_addition_only(self):
        """只使用加法运算符。"""
        sheet = ExerciseSheet(
            total=20,
            seed=42,
            operators=[Addition()],
            show_answers=False,
        )
        sheet.generate()
        for p in sheet.get_problems():
            assert p.operator.symbol == "+"

    def test_subtraction_only(self):
        """只使用减法运算符。"""
        sheet = ExerciseSheet(
            total=20,
            seed=42,
            operators=[Subtraction()],
            show_answers=False,
        )
        sheet.generate()
        for p in sheet.get_problems():
            assert p.operator.symbol == "-"

    def test_custom_constraints(self):
        """自定义约束：加法结果 ≤ 50。"""
        sheet = ExerciseSheet(
            total=20,
            seed=42,
            operators=[Addition()],
            constraints=[
                OperandRangeConstraint(0, 100),
                SumLimitConstraint(50),
            ],
        )
        sheet.generate()
        for p in sheet.get_problems():
            assert p.answer <= 50

    def test_get_problems_without_generate(self):
        """未显式 generate() 时自动生成。"""
        sheet = ExerciseSheet(total=10, seed=42)
        problems = sheet.get_problems()
        assert len(problems) == 10


class TestExerciseSheetEdge:
    """边界测试。"""

    def test_zero_questions(self):
        sheet = ExerciseSheet(total=0, seed=42)
        sheet.generate()
        assert sheet.stats["total"] == 0

    def test_negative_total_raises(self):
        with pytest.raises(ValueError):
            ExerciseSheet(total=-5)

    def test_seed_reproducibility(self):
        s1 = ExerciseSheet(total=20, seed=123, show_answers=True)
        s2 = ExerciseSheet(total=20, seed=123, show_answers=True)
        assert s1.render() == s2.render()
