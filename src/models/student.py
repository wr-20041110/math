"""StudentRecord —— 学生成绩档案模型。"""
from dataclasses import dataclass, field
from typing import List
from .score import Score


@dataclass
class StudentRecord:
    """学生成绩档案（可变，持续追加）。"""
    name: str
    scores: List[Score] = field(default_factory=list)

    def record(self, score: Score) -> None:     # 重构后改名 add_score → record
        self.scores.append(score)

    @property
    def session_count(self) -> int:             # 重构后改名 total_exercises → session_count
        return len(self.scores)

    @property
    def average_score(self) -> float:            # 重构后改名 average_percentage → average_score
        if not self.scores:
            return 0.0
        return sum(s.percentage for s in self.scores) / len(self.scores)
