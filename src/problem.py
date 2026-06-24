"""
Problem 类 —— 表示一道口算题（算式 + 答案）。

故事1 → 故事2 → 故事3 的迭代产物：
  - 故事1：仅存储 num1, operator, num2
  - 故事2：增加 answer 自动计算
  - 故事3：增加 __eq__ / __hash__ 以支持去重
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    """一道口算题。

    Attributes:
        num1: 左操作数 (0-100)
        num2: 右操作数 (0-100)
        operator: 运算符，'+' 或 '-'
        answer: 计算结果（由构造时自动计算）
    """

    num1: int
    num2: int
    operator: str

    def __post_init__(self):
        """校验字段合法性。由于是 frozen dataclass，用 object.__setattr__ 绕过。"""
        if self.operator not in ("+", "-"):
            raise ValueError(f"运算符必须是 '+' 或 '-'，实际为 '{self.operator}'")
        if not (0 <= self.num1 <= 100):
            raise ValueError(f"num1 必须在 0-100 之间，实际为 {self.num1}")
        if not (0 <= self.num2 <= 100):
            raise ValueError(f"num2 必须在 0-100 之间，实际为 {self.num2}")

        # 故事2 约束：加法结果 ≤ 100，减法结果 ≥ 0
        if self.operator == "+" and self.num1 + self.num2 > 100:
            raise ValueError(
                f"加法结果不能超过 100: {self.num1} + {self.num2} = {self.num1 + self.num2}"
            )
        if self.operator == "-" and self.num1 - self.num2 < 0:
            raise ValueError(
                f"减法结果不能为负数: {self.num1} - {self.num2} = {self.num1 - self.num2}"
            )

    @property
    def answer(self) -> int:
        """计算并返回答案。"""
        if self.operator == "+":
            return self.num1 + self.num2
        else:
            return self.num1 - self.num2

    def __str__(self) -> str:
        """返回算式字符串，如 "48+7=" 或 "88-21="。"""
        return f"{self.num1}{self.operator}{self.num2}="

    def __eq__(self, other: object) -> bool:
        """两个 Problem 相等当且仅当 num1、num2、operator 完全相同。

        注意：32+22= 和 22+32= 在加法交换意义下结果相同，但被视为不同题目。
        故事3 中已明确：这两道题不应出现在同一套练习中。
        """
        if not isinstance(other, Problem):
            return NotImplemented
        return (
            self.num1 == other.num1
            and self.num2 == other.num2
            and self.operator == other.operator
        )

    def __hash__(self) -> int:
        """哈希值基于 (num1, num2, operator)，支持在 set/dict 中去重。"""
        return hash((self.num1, self.num2, self.operator))
