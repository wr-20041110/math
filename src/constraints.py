"""
约束验证体系 —— 抽象基类 + 可组合的具体约束（策略模式 + OCP）。

设计原则：
  - OCP（开放-封闭）：新增约束子类即可扩展，无需修改已有约束或使用方。
  - SRP（单一职责）：每个约束子类只检查一个维度的合法性。
  - ISP（接口隔离）：Constraint 只定义 check() 和 description，无冗余方法。

组合使用：
  约束对象放入列表，遍历检查 —— 实现声明式规则组合。
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .problem import Problem


class Constraint(ABC):
    """约束抽象基类。

    定义一个合法性规则，子类实现具体的数学约束。
    所有约束均可独立组合，体现策略模式思想。
    """

    @abstractmethod
    def check(self, problem: "Problem") -> bool:
        """检查 problem 是否满足本约束。

        Args:
            problem: 待检查的 Problem 实例。

        Returns:
            True 表示合法，False 表示违反约束。
        """
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """人类可读的约束描述，用于错误消息。"""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class OperandRangeConstraint(Constraint):
    """操作数范围约束：两个操作数必须在 [min_val, max_val] 内。

    故事1 的隐含约束：操作数 ∈ [0, 100]。
    """

    def __init__(self, min_val: int = 0, max_val: int = 100) -> None:
        self._min = min_val
        self._max = max_val

    def check(self, problem: "Problem") -> bool:
        return (
            self._min <= problem.num1 <= self._max
            and self._min <= problem.num2 <= self._max
        )

    @property
    def description(self) -> str:
        return f"操作数范围 [{self._min}, {self._max}]"


class SumLimitConstraint(Constraint):
    """和上限约束：加法结果不能超过 limit。

    故事2 需求：num1 + num2 ≤ 100。

    注意：对减法无意义（始终 check 通过），
    因为约束检测是声明式的，由 Generator 统一调用。
    """

    def __init__(self, limit: int = 100) -> None:
        self._limit = limit

    def check(self, problem: "Problem") -> bool:
        if problem.operator.symbol == "+":
            return problem.num1 + problem.num2 <= self._limit
        # 非加法题不受此约束
        return True

    @property
    def description(self) -> str:
        return f"加法结果 ≤ {self._limit}"


class NonNegativeDiffConstraint(Constraint):
    """非负差约束：减法结果不能为负数。

    故事2 需求：num1 - num2 ≥ 0。

    注意：对加法无意义（始终 check 通过）。
    """

    def check(self, problem: "Problem") -> bool:
        if problem.operator.symbol == "-":
            return problem.num1 - problem.num2 >= 0
        # 非减法题不受此约束
        return True

    @property
    def description(self) -> str:
        return "减法结果 ≥ 0"
