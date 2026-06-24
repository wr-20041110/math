"""运算符策略 —— 策略模式 + 多态（重构：Pull Up Method）。"""
from abc import ABC, abstractmethod


class Operator(ABC):
    """运算符抽象基类（重构后：增加 __repr__ 和错误校验）。"""

    @property
    @abstractmethod
    def symbol(self) -> str:
        """运算符号。"""
        ...

    @abstractmethod
    def apply(self, left: int, right: int) -> int:
        """对两个操作数执行运算。

        Args:
            left: 左操作数。
            right: 右操作数。

        Returns:
            int: 运算结果。
        """
        ...

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class Addition(Operator):
    """加法策略。

    >>> Addition().apply(44, 23)
    67
    """

    @property
    def symbol(self) -> str:
        return "+"

    def apply(self, left: int, right: int) -> int:
        return left + right


class Subtraction(Operator):
    """减法策略。

    注意：允许负结果（由 Constraint 层控制合法性）。
    >>> Subtraction().apply(88, 21)
    67
    """

    @property
    def symbol(self) -> str:
        return "-"

    def apply(self, left: int, right: int) -> int:
        return left - right


# ---------------------------------------------------------------------------
# 运算符注册表 —— 表驱动（重构：Replace Conditional with Table Lookup）
# ---------------------------------------------------------------------------

_OPERATOR_REGISTRY: dict[str, Operator] = {
    "+": Addition(),
    "-": Subtraction(),
}


def get_operator(symbol: str) -> Operator:
    """根据符号获取 Operator 实例（查表法替代条件分支）。

    Raises:
        KeyError: 无效运算符符号。
    """
    op = _OPERATOR_REGISTRY.get(symbol)
    if op is None:
        raise KeyError(f"无效的运算符符号: '{symbol}'。支持: {list(_OPERATOR_REGISTRY.keys())}")
    return op


def registered_symbols() -> list[str]:
    """返回已注册的运算符符号列表。"""
    return list(_OPERATOR_REGISTRY.keys())
