"""
Constraint 抽象基类及其子类的单元测试。

覆盖 OOP 原则：
  - OCP（开放-封闭）：新增约束子类无需修改已有约束
  - SRP（单一职责）：每个约束只检查一个维度
  - 策略模式：约束互相独立，可自由组合
"""

import pytest
from src.constraints import (
    Constraint,
    OperandRangeConstraint,
    SumLimitConstraint,
    NonNegativeDiffConstraint,
)
from src.operators import Addition, Subtraction
from src.problem import Problem


def make_add(a: int, b: int) -> Problem:
    return Problem(num1=a, num2=b, operator=Addition())


def make_sub(a: int, b: int) -> Problem:
    return Problem(num1=a, num2=b, operator=Subtraction())


# ---------------------------------------------------------------------------
# 不能实例化抽象基类
# ---------------------------------------------------------------------------

def test_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        Constraint()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# OperandRangeConstraint
# ---------------------------------------------------------------------------

class TestOperandRangeConstraint:
    """操作数范围约束。"""

    def test_both_in_range(self):
        c = OperandRangeConstraint(0, 100)
        assert c.check(make_add(50, 30))

    def test_num1_out_of_range(self):
        c = OperandRangeConstraint(0, 100)
        # 直接构造会被 Problem.__post_init__ 拦截?
        # 我们在这里只测 check 逻辑
        p = Problem(num1=150, num2=30, operator=Addition())
        # 注意：Problem 没有范围校验（由 Constraint 负责）
        assert not c.check(p)

    def test_num2_out_of_range(self):
        c = OperandRangeConstraint(0, 100)
        p = Problem(num1=30, num2=150, operator=Addition())
        assert not c.check(p)

    def test_boundary_values(self):
        c = OperandRangeConstraint(0, 100)
        assert c.check(make_add(0, 0))
        assert c.check(make_add(100, 0))
        assert c.check(make_add(0, 100))

    def test_custom_range(self):
        c = OperandRangeConstraint(0, 50)
        assert c.check(make_add(50, 0))
        assert not c.check(make_add(51, 0))

    def test_description(self):
        c = OperandRangeConstraint(0, 100)
        assert "0" in c.description and "100" in c.description


# ---------------------------------------------------------------------------
# SumLimitConstraint
# ---------------------------------------------------------------------------

class TestSumLimitConstraint:
    """和上限约束。"""

    def test_sum_within_limit(self):
        c = SumLimitConstraint(100)
        assert c.check(make_add(60, 40))

    def test_sum_exceeds_limit(self):
        c = SumLimitConstraint(100)
        assert not c.check(make_add(60, 50))

    def test_sum_exactly_limit(self):
        c = SumLimitConstraint(100)
        assert c.check(make_add(0, 100))

    def test_ignores_subtraction(self):
        """对减法题始终返回 True（不检查）。"""
        c = SumLimitConstraint(100)
        assert c.check(make_sub(150, 50))  # 大数减法也通过

    def test_custom_limit(self):
        c = SumLimitConstraint(50)
        assert c.check(make_add(25, 25))
        assert not c.check(make_add(30, 30))

    def test_description(self):
        c = SumLimitConstraint(100)
        assert "100" in c.description


# ---------------------------------------------------------------------------
# NonNegativeDiffConstraint
# ---------------------------------------------------------------------------

class TestNonNegativeDiffConstraint:
    """非负差约束。"""

    def test_diff_non_negative(self):
        c = NonNegativeDiffConstraint()
        assert c.check(make_sub(80, 20))

    def test_diff_negative(self):
        c = NonNegativeDiffConstraint()
        assert not c.check(make_sub(5, 10))

    def test_diff_zero(self):
        c = NonNegativeDiffConstraint()
        assert c.check(make_sub(50, 50))

    def test_ignores_addition(self):
        """对加法题始终返回 True。"""
        c = NonNegativeDiffConstraint()
        assert c.check(make_add(200, 300))

    def test_description(self):
        c = NonNegativeDiffConstraint()
        assert "0" in c.description or "≥" in c.description


# ---------------------------------------------------------------------------
# 策略组合测试（OCP 验证）
# ---------------------------------------------------------------------------

class TestConstraintComposition:
    """约束可自由组合（策略模式 + OCP）。"""

    def test_multiple_constraints_all_pass(self):
        constraints = [
            OperandRangeConstraint(0, 100),
            SumLimitConstraint(100),
            NonNegativeDiffConstraint(),
        ]
        p = make_add(30, 40)
        p.validate(constraints)  # 不应抛出

    def test_multiple_constraints_one_fails(self):
        constraints = [
            OperandRangeConstraint(0, 100),
            SumLimitConstraint(100),
        ]
        p = make_add(80, 30)
        with pytest.raises(ValueError, match="违反约束"):
            p.validate(constraints)

    def test_constraint_repr(self):
        c = OperandRangeConstraint(0, 100)
        assert "OperandRangeConstraint" in repr(c)
