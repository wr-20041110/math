"""Problem 类 —— 口算题数据模型（封装 + ADT）。"""
from dataclasses import dataclass, field
from typing import List
from .operators import Operator
from .constraints import Constraint


@dataclass(frozen=True)
class Problem:
    num1: int
    num2: int
    operator: Operator
    _validated: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.operator, Operator):
            raise TypeError(f"operator 必须是 Operator 实例，实际为 {type(self.operator)}")

    @property
    def answer(self) -> int:
        return self.operator.apply(self.num1, self.num2)

    def validate(self, constraints: List[Constraint]) -> None:
        for c in constraints:
            if not c.check(self):
                raise ValueError(
                    f"题目 {self} 违反约束：{c.description}。"
                    f"参数: num1={self.num1}, num2={self.num2}"
                )

    def __str__(self) -> str:
        return f"{self.num1}{self.operator.symbol}{self.num2}="

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Problem):
            return NotImplemented
        return (self.num1 == other.num1 and self.num2 == other.num2
                and self.operator.symbol == other.operator.symbol)

    def __hash__(self) -> int:
        return hash((self.num1, self.num2, self.operator.symbol))
