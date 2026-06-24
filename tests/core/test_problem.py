"""
TDD 风格测试 —— Problem 类。

TDD 红-绿-重构循环:
  1. RED:   先写失败的测试
  2. GREEN: 编写最小代码让测试通过
  3. REFACTOR: 在测试保护下重构

本测试文件展示 TDD 流程：每个测试方法名描述行为，
assert 精确验证预期结果。
"""
import pytest
from mathpractice.core.problem import Problem
from mathpractice.core.operators import Addition, Subtraction
from mathpractice.core.constraints import OperandRangeConstraint, SumLimitConstraint


class TestProblemTDD:
    """TDD: Problem 类行为规约。"""

    # ── RED → GREEN: 构造 ──
    def test_should_create_addition_problem(self):
        """TDD: 应能创建加法题。"""
        p = Problem(left=30, right=50, operator=Addition())
        assert p.left == 30
        assert p.right == 50
        assert p.operator.symbol == "+"

    def test_should_reject_non_operator_type(self):
        """TDD: 应拒绝非 Operator 类型。"""
        with pytest.raises(TypeError, match="Operator"):
            Problem(left=10, right=5, operator="+")  # type: ignore

    # ── RED → GREEN: 计算 ──
    def test_should_compute_addition_answer(self):
        """TDD: 应正确计算加法答案。"""
        p = Problem(left=44, right=23, operator=Addition())
        assert p.answer == 67

    def test_should_compute_subtraction_answer(self):
        """TDD: 应正确计算减法答案。"""
        p = Problem(left=88, right=21, operator=Subtraction())
        assert p.answer == 67

    # ── RED → GREEN: 校验 ──
    def test_should_pass_when_constraints_satisfied(self):
        """TDD: 满足所有约束时不抛异常。"""
        p = Problem(left=30, right=40, operator=Addition())
        p.validate_against([SumLimitConstraint(100)])

    def test_should_raise_when_constraint_violated(self):
        """TDD: 违反约束时应抛出 ValueError。"""
        p = Problem(left=80, right=30, operator=Addition())
        with pytest.raises(ValueError, match="违反约束"):
            p.validate_against([SumLimitConstraint(100)])

    # ── RED → GREEN: 相等性 ──
    def test_should_consider_same_problems_equal(self):
        """TDD: 相同参数应相等。"""
        p1 = Problem(left=44, right=23, operator=Addition())
        p2 = Problem(left=44, right=23, operator=Addition())
        assert p1 == p2

    def test_should_consider_commutative_different(self):
        """TDD: 32+22 和 22+32 不同。"""
        p1 = Problem(left=32, right=22, operator=Addition())
        p2 = Problem(left=22, right=32, operator=Addition())
        assert p1 != p2

    # ── RED → GREEN: 字符串表示 ──
    def test_should_format_as_expression(self):
        """TDD: 应格式化为算式字符串。"""
        p = Problem(left=48, right=7, operator=Addition())
        assert p.expression == "48+7="
        assert str(p) == "48+7="

    def test_should_be_immutable(self):
        """TDD: frozen dataclass 不可修改。"""
        p = Problem(left=10, right=5, operator=Addition())
        with pytest.raises(Exception):
            p.left = 20  # type: ignore
