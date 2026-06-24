"""
PracticeManager —— 练习管理外观类（Facade）。

对外提供统一接口：
  - generate_exercise(): 生成习题并保存 CSV
  - grade_answers(): 加载答案 CSV → 判题打分 → 保存成绩
  - analyze(): 分析成绩 → 弱项报告
  - targeted_practice(): 针对弱项生成练习

协调子系统：ExerciseBuilder, CsvHandler, Grader, Analyzer
"""

import os
from typing import Dict, List, Optional, Tuple

from .models import Exercise, AnswerSheet, Score
from .generator import ProblemGenerator
from .constraints import Constraint
from .exercise_builder import ExerciseBuilder
from .csv_handler import CsvHandler
from .grader import Grader
from .analyzer import Analyzer


class PracticeManager:
    """练习管理外观。

    封装了习题生成、CSV 读写、判题打分、成绩分析的完整流程。
    """

    def __init__(self, data_dir: str = "data"):
        """初始化管理器。

        Args:
            data_dir: 数据存储根目录。
        """
        self._data_dir = data_dir
        self._exercise_dir = os.path.join(data_dir, "exercises")
        self._answer_dir = os.path.join(data_dir, "answers")
        self._score_dir = os.path.join(data_dir, "scores")
        self._analysis_dir = os.path.join(data_dir, "analysis")

        # 确保目录存在
        for d in [self._exercise_dir, self._answer_dir, self._score_dir, self._analysis_dir]:
            os.makedirs(d, exist_ok=True)

        self._handler = CsvHandler()
        self._grader = Grader()
        self._analyzer = Analyzer()
        self._exercise_cache: Dict[str, Exercise] = {}

    # ------------------------------------------------------------------
    # 公有 API
    # ------------------------------------------------------------------

    def generate_exercise(
        self,
        exercise_type: str = "mixed",
        count: int = 50,
        seed: Optional[int] = None,
    ) -> Tuple[Exercise, str]:
        """生成习题并保存为 CSV。

        Args:
            exercise_type: 习题类型。
            count: 题目数量。
            seed: 随机种子。

        Returns:
            (Exercise, csv_path)。
        """
        exercise = ExerciseBuilder.build(
            exercise_type=exercise_type,
            count=count,
            seed=seed,
        )
        csv_path = self._handler.save_exercise(exercise, self._exercise_dir)
        self._exercise_cache[exercise.exercise_id] = exercise
        return exercise, csv_path

    def grade_answers(self, answer_csv_path: str) -> Score:
        """加载答案 CSV → 判题打分 → 保存成绩。

        Args:
            answer_csv_path: 答案 CSV 文件路径。

        Returns:
            Score 实例。
        """
        # 1. 加载答案
        answer_sheet = self._handler.load_answers(answer_csv_path)

        # 2. 加载对应的习题（优先从缓存，否则从文件加载）
        exercise = self._get_exercise(answer_sheet.exercise_id)

        # 3. 判题
        score = self._grader.grade(exercise, answer_sheet)

        # 4. 保存成绩
        score_path = os.path.join(self._score_dir, "scores.csv")
        self._handler.save_scores([score], score_path)

        # 5. 添加到分析器
        self._analyzer.add_scores([score])

        return score

    def grade_from_data(
        self,
        exercise_id: str,
        student: str,
        answers_dict: Dict[int, int],
    ) -> Score:
        """直接从内存数据判题（无需 CSV 文件）。

        Args:
            exercise_id: 习题 ID。
            student: 学生姓名。
            answers_dict: {题号: 学生答案} 的字典。

        Returns:
            Score 实例。
        """
        exercise = self._get_exercise(exercise_id)
        answer_sheet = AnswerSheet(
            exercise_id=exercise_id,
            student=student,
            answers=answers_dict,
        )
        score = self._grader.grade(exercise, answer_sheet)

        score_path = os.path.join(self._score_dir, "scores.csv")
        self._handler.save_scores([score], score_path)
        self._analyzer.add_scores([score])

        return score

    def analyze(self) -> Dict:
        """分析成绩，返回弱项报告 + 摘要。

        Returns:
            {
                "summary": {...},
                "weak_problems": [...],
            }
        """
        return {
            "summary": self._analyzer.summary(),
            "weak_problems": self._analyzer.find_weak_problems(self._exercise_cache),
        }

    def generate_targeted_practice(
        self, count: int = 20, seed: Optional[int] = None
    ) -> Exercise:
        """针对弱项生成练习。

        Returns:
            Exercise 实例。
        """
        problems = self._analyzer.generate_targeted_practice(
            self._exercise_cache, count=count, seed=seed
        )
        exercise = Exercise(
            exercise_id=f"EX-TARGETED-{len(self._exercise_cache) + 1:03d}",
            exercise_type="targeted",
            problems=problems,
        )
        csv_path = self._handler.save_exercise(exercise, self._exercise_dir)
        self._exercise_cache[exercise.exercise_id] = exercise
        return exercise

    def load_scores(self) -> List[Score]:
        """加载历史成绩。"""
        score_path = os.path.join(self._score_dir, "scores.csv")
        if os.path.isfile(score_path):
            scores = self._handler.load_scores(score_path)
            self._analyzer.add_scores(scores)
            return scores
        return []

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _get_exercise(self, exercise_id: str) -> Exercise:
        """获取习题（缓存优先，否则扫描目录加载）。"""
        if exercise_id in self._exercise_cache:
            return self._exercise_cache[exercise_id]

        # 从文件加载
        filepath = os.path.join(self._exercise_dir, f"{exercise_id}.csv")
        if os.path.isfile(filepath):
            exercise = self._handler.load_exercise(filepath)
            self._exercise_cache[exercise_id] = exercise
            return exercise

        raise FileNotFoundError(
            f"找不到习题 '{exercise_id}'。已缓存: {list(self._exercise_cache.keys())}"
        )
