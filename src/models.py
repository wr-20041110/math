"""
数据模型层 —— Exercise, AnswerSheet, Score, StudentRecord。

设计要点：
  - 数据建模：将业务概念映射为类型化数据结构
  - 不可变性：使用 dataclass(frozen=True) 防止意外修改
  - 类型标注：完整的类型提示支持 IDE 和静态检查
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from .problem import Problem


@dataclass(frozen=True)
class Exercise:
    """一次习题集。

    Attributes:
        exercise_id: 唯一标识，如 'EX-20260624-001'
        exercise_type: 习题类型 'addition' | 'subtraction' | 'mixed'
        problems: Problem 列表（按索引顺序）
        created_at: 创建时间
    """
    exercise_id: str
    exercise_type: str
    problems: List[Problem]
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        valid_types = ("addition", "subtraction", "mixed", "targeted")
        if self.exercise_type not in valid_types:
            raise ValueError(
                f"无效的习题类型: '{self.exercise_type}'。支持: {valid_types}"
            )
        if not self.problems:
            raise ValueError("习题不能为空")

    @property
    def total(self) -> int:
        return len(self.problems)

    def get_problem(self, index: int) -> Problem:
        """按索引（1-based）获取题目。"""
        if not (1 <= index <= len(self.problems)):
            raise IndexError(f"索引 {index} 超出范围 [1, {len(self.problems)}]")
        return self.problems[index - 1]


@dataclass(frozen=True)
class AnswerSheet:
    """一份答卷。

    Attributes:
        exercise_id: 对应的习题 ID
        student: 学生姓名
        answers: 索引 → 学生答案的映射（1-based index）
        submitted_at: 提交时间
    """
    exercise_id: str
    student: str
    answers: Dict[int, int]  # {problem_index: student_answer}
    submitted_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.answers:
            raise ValueError("答案不能为空")

    def get_answer(self, problem_index: int) -> Optional[int]:
        """获取某道题的学生答案，无则返回 None。"""
        return self.answers.get(problem_index)


@dataclass(frozen=True)
class Score:
    """一次评分结果。

    契约不变量：correct + wrong == total
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
        # 契约不变量检查
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


@dataclass
class StudentRecord:
    """学生成绩档案（可变，持续追加）。

    Attributes:
        name: 学生姓名
        scores: 历史成绩列表
    """
    name: str
    scores: List[Score] = field(default_factory=list)

    def add_score(self, score: Score) -> None:
        self.scores.append(score)

    @property
    def total_exercises(self) -> int:
        return len(self.scores)

    @property
    def average_percentage(self) -> float:
        if not self.scores:
            return 0.0
        return sum(s.percentage for s in self.scores) / len(self.scores)

    def get_weak_problems(self, min_error_rate: float = 0.5) -> Dict[str, int]:
        """获取错误率超过阈值的弱项题目。

        使用 Counter 统计每道题的总出错次数。
        返回 {(num1,operator,num2): wrong_count}
        """
        from collections import Counter
        counter: Counter = Counter()
        attempt_counter: Counter = Counter()

        for score in self.scores:
            # 这里需要能反向查找到题目。我们在 Analyzer 层做这件事。
            pass

        return dict(counter)
