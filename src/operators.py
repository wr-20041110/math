"""运算符策略体系 —— 抽象基类 + 具体策略（策略模式 + 多态）。"""
from abc import ABC, abstractmethod


class Operator(ABC):
    """运算符抽象基类。"""

    @property
    @abstractmethod
    def symbol(self) -> str:
        ...

    @abstractmethod
    def apply(self, a: int, b: int) -> int:
        ...

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class Addition(Operator):
    @property
    def symbol(self) -> str:
        return "+"

    def apply(self, a: int, b: int) -> int:
        return a + b


class Subtraction(Operator):
    @property
    def symbol(self) -> str:
        return "-"

    def apply(self, a: int, b: int) -> int:
        return a - b
