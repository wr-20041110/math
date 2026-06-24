"""约束策略 —— 策略模式 + OCP（重构：Extract Method + 表驱动）。"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .problem import Problem


class Constraint(ABC):
    """约束抽象基类。"""

    @abstractmethod
    def is_satisfied(self, problem: "Problem") -> bool:
        """检查 problem 是否满足本约束。

        重构后改名 check → is_satisfied，语义更清晰。
        """
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """人类可读的约束描述。"""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class OperandRangeConstraint(Constraint):
    """操作数范围约束。"""

    def __init__(self, min_val: int = 0, max_val: int = 100) -> None:
        self.min_val = min_val
        self.max_val = max_val

    def is_satisfied(self, problem: "Problem") -> bool:
        return self.min_val <= problem.left <= self.max_val \
           and self.min_val <= problem.right <= self.max_val

    @property
    def description(self) -> str:
        return f"操作数范围 [{self.min_val}, {self.max_val}]"


class SumLimitConstraint(Constraint):
    """和上限约束（仅对加法生效）。"""

    def __init__(self, limit: int = 100) -> None:
        self.limit = limit

    def is_satisfied(self, problem: "Problem") -> bool:
        if problem.operator.symbol != "+":
            return True
        return problem.left + problem.right <= self.limit

    @property
    def description(self) -> str:
        return f"加法结果 ≤ {self.limit}"


class NonNegativeDiffConstraint(Constraint):
    """非负差约束（仅对减法生效）。"""

    def is_satisfied(self, problem: "Problem") -> bool:
        if problem.operator.symbol != "-":
            return True
        return problem.left - problem.right >= 0

    @property
    def description(self) -> str:
        return "减法结果 ≥ 0"


# ---------------------------------------------------------------------------
# 约束工厂表 —— 表驱动
# ---------------------------------------------------------------------------

def default_constraints(operand_max: int = 100, sum_limit: int = 100) -> list[Constraint]:
    """创建默认约束集（工厂方法）。

    重构：将分散在各处的约束创建集中到工厂方法。
    """
    return [
        OperandRangeConstraint(0, operand_max),
        SumLimitConstraint(sum_limit),
        NonNegativeDiffConstraint(),
    ]
