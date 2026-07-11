"""
运算符策略体系 —— 抽象基类 + 具体策略（策略模式 + 多态）。

设计原则：
  - OCP（开放-封闭）：新增运算符（如乘法）只需添加子类，无需修改已有代码。
  - LSP（里氏代换）：Add / Subtract 可透明替换 Operator。
  - SRP（单一职责）：每个子类只负责一种运算规则。

模式：
  策略模式 —— Operator 定义算法接口，子类封装具体算法。
"""

from abc import ABC, abstractmethod


class Operator(ABC):
    """运算符抽象基类。

    定义运算符的公共接口：apply() 执行运算，symbol 返回符号。
    子类必须实现这两个抽象方法。
    """

    @property
    @abstractmethod
    def symbol(self) -> str:
        """返回运算符的文本符号，如 '+'、'-'。"""
        ...

    @abstractmethod
    def apply(self, a: int, b: int) -> int:
        """对两个操作数执行运算，返回结果。"""
        ...

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class Addition(Operator):
    """加法策略。

    >>> add = Addition()
    >>> add.symbol
    '+'
    >>> add.apply(44, 23)
    67
    """

    @property
    def symbol(self) -> str:
        return "+"

    def apply(self, a: int, b: int) -> int:
        return a + b


class Subtraction(Operator):
    """减法策略。

    >>> sub = Subtraction()
    >>> sub.symbol
    '-'
    >>> sub.apply(88, 21)
    67
    """

    @property
    def symbol(self) -> str:
        return "-"

    def apply(self, a: int, b: int) -> int:
        return a - b
