"""Score —— 成绩模型（契约式编程 + 不变量检查）。"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class Score:
    """一次评分结果。

    契约不变量:
      - correct + wrong == total
      - 0.0 <= percentage <= 100.0
      - len(wrong_indices) == wrong
    """
    exercise_id: str
    student: str
    total: int
    correct: int
    wrong: int
    percentage: float
    wrong_indices: List[int] = field(default_factory=list)
    graded_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self._check_invariants()

    def _check_invariants(self) -> None:
        """契约不变量检查（Extract Method 重构）。"""
        if self.correct + self.wrong != self.total:
            raise ValueError(
                f"契约违反: correct({self.correct}) + wrong({self.wrong}) "
                f"!= total({self.total})"
            )
        if not (0.0 <= self.percentage <= 100.0):
            raise ValueError(
                f"契约违反: percentage({self.percentage}) 不在 [0, 100]"
            )
        if len(self.wrong_indices) != self.wrong:
            raise ValueError(
                f"契约违反: wrong_indices 长度({len(self.wrong_indices)}) "
                f"!= wrong({self.wrong})"
            )
