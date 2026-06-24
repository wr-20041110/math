"""约束验证体系 —— 抽象基类 + 具体约束（策略模式 + OCP）。"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .problem import Problem


class Constraint(ABC):
    @abstractmethod
    def check(self, problem: "Problem") -> bool:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class OperandRangeConstraint(Constraint):
    def __init__(self, min_val: int = 0, max_val: int = 100) -> None:
        self._min = min_val
        self._max = max_val

    def check(self, problem: "Problem") -> bool:
        return self._min <= problem.num1 <= self._max and self._min <= problem.num2 <= self._max

    @property
    def description(self) -> str:
        return f"操作数范围 [{self._min}, {self._max}]"


class SumLimitConstraint(Constraint):
    def __init__(self, limit: int = 100) -> None:
        self._limit = limit

    def check(self, problem: "Problem") -> bool:
        if problem.operator.symbol == "+":
            return problem.num1 + problem.num2 <= self._limit
        return True

    @property
    def description(self) -> str:
        return f"加法结果 ≤ {self._limit}"


class NonNegativeDiffConstraint(Constraint):
    def check(self, problem: "Problem") -> bool:
        if problem.operator.symbol == "-":
            return problem.num1 - problem.num2 >= 0
        return True

    @property
    def description(self) -> str:
        return "减法结果 ≥ 0"
