"""
Problem 类 —— 口算题的数据模型（封装 + 抽象数据类型）。

设计原则：
  - 封装：操作数为私有属性，通过 property 暴露只读访问。
  - 依赖倒转（DIP）：依赖 Operator 抽象而非具体运算符类。
  - ADT：定义明确的操作集合（answer、__eq__、__hash__、__str__）。

与故事1-3 版本的差异：
  - operator 从 str 变为 Operator 对象（多态替代条件判断）
  - validate() 接受 Constraint 列表（策略模式替代硬编码校验）
"""

from dataclasses import dataclass, field
from typing import List

from .operators import Operator
from .constraints import Constraint


@dataclass(frozen=True)
class Problem:
    """一道口算题。

    使用 Operator 对象（而非字符串）表示运算符，
    支持多态调用 apply() 计算答案。

    Attributes:
        num1: 左操作数。
        num2: 右操作数。
        operator: 运算符策略对象（Operator 子类实例）。
    """

    num1: int
    num2: int
    operator: Operator

    # 非数据字段，不由 __init__ 接受
    _validated: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """构造后校验。"""
        if not isinstance(self.operator, Operator):
            raise TypeError(
                f"operator 必须是 Operator 实例，实际为 {type(self.operator)}"
            )

    # ------------------------------------------------------------------
    # 公共属性
    # ------------------------------------------------------------------

    @property
    def answer(self) -> int:
        """通过多态调用 Operator.apply() 计算答案。

        无需 if/else 判断运算符类型 —— 策略模式消除条件分支。
        """
        return self.operator.apply(self.num1, self.num2)

    # ------------------------------------------------------------------
    # 校验
    # ------------------------------------------------------------------

    def validate(self, constraints: List[Constraint]) -> None:
        """根据约束列表校验本题合法性。

        使用策略模式：遍历约束策略列表，逐一检查。
        违反任一约束则抛出 ValueError。

        Args:
            constraints: Constraint 子类实例列表。

        Raises:
            ValueError: 违反某个约束时。
        """
        for c in constraints:
            if not c.check(self):
                raise ValueError(
                    f"题目 {self} 违反约束：{c.description}。"
                    f"参数: num1={self.num1}, num2={self.num2}"
                )

    # ------------------------------------------------------------------
    # 协议方法
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return f"{self.num1}{self.operator.symbol}{self.num2}="

    def __eq__(self, other: object) -> bool:
        """基于 (num1, num2, operator) 判断相等。

        故事3 需求：32+22 和 22+32 视为不同题目，
        因为它们的 (num1, num2, operator) 三元组不同。
        """
        if not isinstance(other, Problem):
            return NotImplemented
        return (
            self.num1 == other.num1
            and self.num2 == other.num2
            and self.operator.symbol == other.operator.symbol
        )

    def __hash__(self) -> int:
        """哈希基于三元组，支持 set 去重。"""
        return hash((self.num1, self.num2, self.operator.symbol))
