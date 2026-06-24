"""Exercise —— 习题集模型（Extract Class 重构）。"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from ..core.problem import Problem

_VALID_TYPES = ("addition", "subtraction", "mixed", "targeted")


@dataclass(frozen=True)
class Exercise:
    """一次习题集。"""
    exercise_id: str
    exercise_type: str
    problems: List[Problem]
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if self.exercise_type not in _VALID_TYPES:
            raise ValueError(
                f"无效的习题类型: '{self.exercise_type}'。支持: {_VALID_TYPES}"
            )
        if not self.problems:
            raise ValueError("习题不能为空")

    @property
    def problem_count(self) -> int:     # 重构后改名 total → problem_count
        return len(self.problems)

    def get_problem(self, index: int) -> Problem:
        """按 1-based 索引获取题目。"""
        if not (1 <= index <= len(self.problems)):
            raise IndexError(f"索引 {index} 超出范围 [1, {len(self.problems)}]")
        return self.problems[index - 1]
