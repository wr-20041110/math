"""
ExerciseRepository —— 数据仓库（Extract Class 重构）。

重构前: PracticeManager 直接耦合 CsvHandler，混合了业务逻辑和数据访问。
重构后: Repository 模式隔离数据访问，PracticeManager(App) 只关心业务逻辑。

这是 Repository 模式的简化实现。
"""

import os
import logging
from typing import Dict, List, Optional
from pathlib import Path

from ..models.exercise import Exercise
from ..models.score import Score
from .csv_handler import CsvHandler

logger = logging.getLogger(__name__)


class ExerciseRepository:
    """习题数据仓库。

    封装 Exercise 和 Score 的持久化操作，
    提供内存缓存加速重复访问。
    """

    def __init__(self, data_dir: str = "data"):
        self._base = Path(data_dir)
        self._exercise_dir = self._base / "exercises"
        self._answer_dir = self._base / "answers"
        self._score_dir = self._base / "scores"
        self._analysis_dir = self._base / "analysis"

        for d in [self._exercise_dir, self._answer_dir, self._score_dir, self._analysis_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self._handler = CsvHandler()
        self._exercise_cache: Dict[str, Exercise] = {}

    # ------------------------------------------------------------------
    # 习题存取
    # ------------------------------------------------------------------

    def save_exercise(self, exercise: Exercise) -> str:
        path = self._handler.save_exercise(exercise, str(self._exercise_dir))
        self._exercise_cache[exercise.exercise_id] = exercise
        return path

    def find_exercise(self, exercise_id: str) -> Exercise:
        """查找习题（缓存优先，回退到文件系统）。"""
        if exercise_id in self._exercise_cache:
            return self._exercise_cache[exercise_id]

        filepath = self._exercise_dir / f"{exercise_id}.csv"
        if filepath.is_file():
            exercise = self._handler.load_exercise(str(filepath))
            self._exercise_cache[exercise_id] = exercise
            return exercise

        raise FileNotFoundError(
            f"找不到习题 '{exercise_id}'。已缓存: {list(self._exercise_cache.keys())}"
        )

    def cached_exercises(self) -> Dict[str, Exercise]:
        return dict(self._exercise_cache)

    # ------------------------------------------------------------------
    # 成绩存取
    # ------------------------------------------------------------------

    def save_scores(self, scores: List[Score]) -> str:
        path = str(self._score_dir / "scores.csv")
        return self._handler.save_scores(scores, path)

    def load_scores(self) -> List[Score]:
        path = self._score_dir / "scores.csv"
        if path.is_file():
            return self._handler.load_scores(str(path))
        return []

    # ------------------------------------------------------------------
    # 答案存取
    # ------------------------------------------------------------------

    def save_answers(self, answer_sheet, directory: Optional[str] = None) -> str:
        target = directory or str(self._answer_dir)
        return self._handler.save_answers(answer_sheet, target)

    def load_answers(self, filepath: str):
        return self._handler.load_answers(filepath)
