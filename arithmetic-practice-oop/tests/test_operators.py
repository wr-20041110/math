"""
Operator 抽象基类及其子类的单元测试。

覆盖 OOP 原则：
  - 多态：Operator 引用可指向任意子类，apply() 行为不同
  - LSP（里氏代换）：子类可透明替换基类
  - 抽象：Operator 是抽象基类，不可直接实例化
"""

import pytest
from src.operators import Operator, Addition, Subtraction


# ---------------------------------------------------------------------------
# 不能实例化抽象基类
# ---------------------------------------------------------------------------

def test_cannot_instantiate_abstract():
    """Operator 是抽象基类，不可直接实例化。"""
    with pytest.raises(TypeError):
        Operator()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# 多态测试：统一接口，不同行为
# ---------------------------------------------------------------------------

class TestAddition:
    """Addition 策略测试。"""

    def test_symbol(self):
        op = Addition()
        assert op.symbol == "+"

    def test_apply(self):
        op = Addition()
        assert op.apply(44, 23) == 67

    def test_apply_zero(self):
        op = Addition()
        assert op.apply(0, 0) == 0

    def test_apply_boundary(self):
        op = Addition()
        assert op.apply(0, 100) == 100

    def test_str_repr(self):
        op = Addition()
        assert str(op) == "+"
        assert "Addition" in repr(op)


class TestSubtraction:
    """Subtraction 策略测试。"""

    def test_symbol(self):
        op = Subtraction()
        assert op.symbol == "-"

    def test_apply(self):
        op = Subtraction()
        assert op.apply(88, 21) == 67

    def test_apply_zero(self):
        op = Subtraction()
        assert op.apply(50, 50) == 0

    def test_apply_negative(self):
        """减法允许负结果（由 Constraint 层控制）。"""
        op = Subtraction()
        assert op.apply(3, 10) == -7

    def test_str_repr(self):
        op = Subtraction()
        assert str(op) == "-"
        assert "Subtraction" in repr(op)


# ---------------------------------------------------------------------------
# 里氏代换原则（LSP）测试
# ---------------------------------------------------------------------------

class TestLSP:
    """验证里氏代换原则：子类可替换基类而不改变程序正确性。"""

    def _use_operator(self, op: Operator, a: int, b: int) -> int:
        """接受 Operator 抽象类型，与具体子类无关。"""
        return op.apply(a, b)

    def test_addition_substitution(self):
        result = self._use_operator(Addition(), 30, 40)
        assert result == 70

    def test_subtraction_substitution(self):
        result = self._use_operator(Subtraction(), 80, 30)
        assert result == 50

    def test_interchangeable(self):
        """同一段逻辑使用不同 Operator 子类，行为正确切换。"""
        ops: list[Operator] = [Addition(), Subtraction()]
        results = [op.apply(60, 20) for op in ops]
        assert results == [80, 40]


# ---------------------------------------------------------------------------
# 策略模式验证：运行时替换
# ---------------------------------------------------------------------------

class TestStrategyPattern:
    """验证策略模式：可在运行时替换算法。"""

    def test_runtime_strategy_swap(self):
        op = Addition()
        assert op.apply(10, 5) == 15
        # 切换到减法策略
        op = Subtraction()
        assert op.apply(10, 5) == 5

    def test_strategy_equality(self):
        """同类型策略的不同实例行为一致。"""
        a1, a2 = Addition(), Addition()
        assert a1.apply(10, 20) == a2.apply(10, 20)
