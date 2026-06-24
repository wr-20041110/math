"""
Problem 类的单元测试。

覆盖 OOP 原则：
  - 封装：私有属性通过 property 暴露
  - 抽象数据类型（ADT）：定义明确的操作集
  - DIP：依赖 Operator 抽象，不依赖具体运算符类
  - 不可变性：frozen dataclass
"""

import pytest
from src.problem import Problem
from src.operators import Operator, Addition, Subtraction
from src.constraints import OperandRangeConstraint, SumLimitConstraint, NonNegativeDiffConstraint


class TestProblemCreation:
    """测试 Problem 构造。"""

    def test_valid_addition(self):
        p = Problem(num1=30, num2=50, operator=Addition())
        assert p.num1 == 30
        assert p.num2 == 50
        assert p.operator.symbol == "+"

    def test_valid_subtraction(self):
        p = Problem(num1=80, num2=20, operator=Subtraction())
        assert p.num1 == 80
        assert p.num2 == 20
        assert p.operator.symbol == "-"

    def test_invalid_operator_type(self):
        with pytest.raises(TypeError, match="operator 必须是 Operator"):
            Problem(num1=10, num2=5, operator="+")  # type: ignore[arg-type]

    def test_frozen_immutable(self):
        """frozen dataclass：构造后不可修改。"""
        p = Problem(num1=10, num2=5, operator=Addition())
        with pytest.raises(Exception):
            p.num1 = 20  # type: ignore[misc]


class TestProblemAnswer:
    """测试 answer 属性（多态调用 Operator.apply()）。"""

    def test_addition_answer(self):
        p = Problem(num1=44, num2=23, operator=Addition())
        assert p.answer == 67

    def test_subtraction_answer(self):
        p = Problem(num1=88, num2=21, operator=Subtraction())
        assert p.answer == 67

    def test_polymorphic_answer(self):
        """answer 通过 Operator 多态计算，无需 if/else。"""
        ops: list[Operator] = [Addition(), Subtraction()]
        for op in ops:
            p = Problem(num1=50, num2=30, operator=op)
            expected = 80 if op.symbol == "+" else 20
            assert p.answer == expected


class TestProblemEquality:
    """测试相等性与哈希（故事3 去重基础）。"""

    def test_same_problems_equal(self):
        p1 = Problem(num1=44, num2=23, operator=Addition())
        p2 = Problem(num1=44, num2=23, operator=Addition())
        assert p1 == p2
        assert hash(p1) == hash(p2)

    def test_different_operator_not_equal(self):
        p1 = Problem(num1=44, num2=23, operator=Addition())
        p2 = Problem(num1=44, num2=23, operator=Subtraction())
        assert p1 != p2

    def test_commutative_not_equal(self):
        """故事3：32+22 和 22+32 视为不同题。"""
        p1 = Problem(num1=32, num2=22, operator=Addition())
        p2 = Problem(num1=22, num2=32, operator=Addition())
        assert p1 != p2

    def test_set_dedup(self):
        p1 = Problem(num1=44, num2=23, operator=Addition())
        p2 = Problem(num1=44, num2=23, operator=Addition())
        assert len({p1, p2}) == 1

    def test_set_commutative_both_kept(self):
        p1 = Problem(num1=32, num2=22, operator=Addition())
        p2 = Problem(num1=22, num2=32, operator=Addition())
        assert len({p1, p2}) == 2

    def test_not_equal_to_non_problem(self):
        p = Problem(num1=1, num2=2, operator=Addition())
        assert p != "1+2="
        assert p != 42


class TestProblemStr:
    """测试字符串表示。"""

    def test_addition_str(self):
        p = Problem(num1=48, num2=7, operator=Addition())
        assert str(p) == "48+7="

    def test_subtraction_str(self):
        p = Problem(num1=88, num2=21, operator=Subtraction())
        assert str(p) == "88-21="


class TestProblemValidation:
    """测试 Problem.validate() —— 策略模式校验。"""

    def test_all_constraints_pass(self):
        constraints = [
            OperandRangeConstraint(0, 100),
            SumLimitConstraint(100),
            NonNegativeDiffConstraint(),
        ]
        p = Problem(num1=30, num2=40, operator=Addition())
        p.validate(constraints)  # 不应抛出

    def test_range_violation(self):
        constraints = [OperandRangeConstraint(0, 100)]
        p = Problem(num1=200, num2=10, operator=Addition())
        with pytest.raises(ValueError, match="违反约束"):
            p.validate(constraints)

    def test_sum_limit_violation(self):
        constraints = [SumLimitConstraint(100)]
        p = Problem(num1=80, num2=30, operator=Addition())
        with pytest.raises(ValueError, match="违反约束"):
            p.validate(constraints)

    def test_negative_diff_violation(self):
        constraints = [NonNegativeDiffConstraint()]
        p = Problem(num1=5, num2=10, operator=Subtraction())
        with pytest.raises(ValueError, match="违反约束"):
            p.validate(constraints)
