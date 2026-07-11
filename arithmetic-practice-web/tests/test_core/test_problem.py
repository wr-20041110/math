"""Problem 核心类单元测试。"""
import pytest
from core.operators import Addition, Subtraction
from core.problem import Problem
from core.constraints import (
    OperandRangeConstraint,
    SumLimitConstraint,
    NonNegativeDiffConstraint,
)


class TestProblemCreation:
    """题目创建测试。"""

    def test_create_addition_problem(self):
        p = Problem(15, 7, Addition())
        assert p.left == 15
        assert p.right == 7
        assert p.operator.symbol == "+"

    def test_create_subtraction_problem(self):
        p = Problem(88, 21, Subtraction())
        assert p.left == 88
        assert p.right == 21
        assert p.operator.symbol == "-"

    def test_reject_non_operator_type(self):
        with pytest.raises(TypeError):
            Problem(1, 2, "+")  # type: ignore


class TestProblemAnswer:
    """答案计算测试。"""

    def test_addition_answer(self):
        p = Problem(44, 23, Addition())
        assert p.answer == 67

    def test_subtraction_answer(self):
        p = Problem(88, 21, Subtraction())
        assert p.answer == 67

    def test_mixed_answer(self):
        problems = [
            Problem(50, 30, Addition()),
            Problem(80, 35, Subtraction()),
        ]
        answers = [p.answer for p in problems]
        assert answers == [80, 45]


class TestProblemEquality:
    """相等性和哈希测试。"""

    def test_same_problems_equal(self):
        p1 = Problem(15, 7, Addition())
        p2 = Problem(15, 7, Addition())
        assert p1 == p2
        assert hash(p1) == hash(p2)

    def test_different_left_not_equal(self):
        p1 = Problem(15, 7, Addition())
        p2 = Problem(16, 7, Addition())
        assert p1 != p2

    def test_different_operator_not_equal(self):
        p1 = Problem(15, 7, Addition())
        p2 = Problem(15, 7, Subtraction())
        assert p1 != p2

    def test_commutative_not_equal(self):
        """加法交换律不视为相同题。"""
        p1 = Problem(3, 5, Addition())
        p2 = Problem(5, 3, Addition())
        assert p1 != p2


class TestProblemValidation:
    """约束校验测试。"""

    def test_all_constraints_pass(self):
        p = Problem(15, 7, Addition())
        constraints = [
            OperandRangeConstraint(0, 100),
            SumLimitConstraint(100),
            NonNegativeDiffConstraint(),
        ]
        # 不应抛出异常
        p.validate_against(constraints)

    def test_operand_range_violation(self):
        p = Problem(150, 7, Addition())
        constraints = [OperandRangeConstraint(0, 100)]
        with pytest.raises(ValueError):
            p.validate_against(constraints)

    def test_sum_limit_violation(self):
        p = Problem(80, 50, Addition())  # 130 > 100
        constraints = [SumLimitConstraint(100)]
        with pytest.raises(ValueError):
            p.validate_against(constraints)

    def test_negative_diff_violation(self):
        p = Problem(10, 20, Subtraction())  # -10 < 0
        constraints = [NonNegativeDiffConstraint()]
        with pytest.raises(ValueError):
            p.validate_against(constraints)


class TestProblemString:
    """字符串表示测试。"""

    def test_str_representation(self):
        p = Problem(15, 7, Addition())
        assert "15" in str(p)
        assert "+" in str(p)
        assert "7" in str(p)

    def test_expression_property(self):
        p = Problem(15, 7, Addition())
        assert p.expression == "15+7="


class TestProblemImmutability:
    """不可变性测试。"""

    def test_frozen_dataclass(self):
        p = Problem(15, 7, Addition())
        with pytest.raises(Exception):
            p.left = 20  # type: ignore
