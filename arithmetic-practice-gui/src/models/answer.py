"""AnswerSheet —— 答卷模型（Extract Class 重构）。"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass(frozen=True)
class AnswerSheet:
    """一份学生答卷。"""
    exercise_id: str
    student: str
    answers: Dict[int, int]  # {problem_index: student_answer}
    submitted_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.answers:
            raise ValueError("答案不能为空")

    def get_answer(self, problem_index: int) -> Optional[int]:
        return self.answers.get(problem_index)
