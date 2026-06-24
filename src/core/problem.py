"""Problem —— 口算题数据模型（重构：Rename Field + Extract Method）。"""
from dataclasses import dataclass, field
from typing import List
from .operators import Operator
from .constraints import Constraint


@dataclass(frozen=True)
class Problem:
    """一道口算题。

    重构变更:
      - num1/num2 → left/right（语义更清晰）
      - check() → is_satisfied()（Constraint 侧）
      - 引入 validate_against() 替代独立 validate()
    """

    left: int        # 重构前: num1
    right: int       # 重构前: num2
    operator: Operator
    _validated: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.operator, Operator):
            raise TypeError(
                f"operator 必须是 Operator 实例，实际为 {type(self.operator).__name__}"
            )

    # ------------------------------------------------------------------
    # 计算属性
    # ------------------------------------------------------------------

    @property
    def answer(self) -> int:
        """多态调用 Operator.apply() 计算答案。"""
        return self.operator.apply(self.left, self.right)

    @property
    def expression(self) -> str:
        """返回算式字符串，如 '15+7='。"""
        return f"{self.left}{self.operator.symbol}{self.right}="

    # ------------------------------------------------------------------
    # 校验 —— 策略模式
    # ------------------------------------------------------------------

    def validate_against(self, constraints: List[Constraint]) -> None:
        """根据约束列表校验合法性。

        Raises:
            ValueError: 违反任一约束时。
        """
        for c in constraints:
            if not c.is_satisfied(self):
                raise ValueError(
                    f"题目 {self.expression} 违反约束: {c.description}。"
                    f"参数: left={self.left}, right={self.right}"
                )

    # ------------------------------------------------------------------
    # 协议方法
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return self.expression

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Problem):
            return NotImplemented
        return (self.left == other.left
                and self.right == other.right
                and self.operator.symbol == other.operator.symbol)

    def __hash__(self) -> int:
        return hash((self.left, self.right, self.operator.symbol))
