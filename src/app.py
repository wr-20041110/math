"""
Application —— 数据库版应用外观。

集成核心服务 + 数据库仓库，提供统一的业务 API。
"""

import logging
from typing import Dict, List, Optional, Tuple

from core.operators import Addition, Subtraction
from core.constraints import OperandRangeConstraint, SumLimitConstraint, NonNegativeDiffConstraint
from core.generator import ProblemGenerator
from models.exercise import Exercise
from services.exercise_builder import ExerciseBuilder
from db.repository import DatabaseRepository

logger = logging.getLogger(__name__)


class Application:
    """数据库版应用外观。"""

    def __init__(self, db_path: str = "data/mathpractice.db", seed: Optional[int] = None):
        self._operators = [Addition(), Subtraction()]
        self._constraints = [
            OperandRangeConstraint(0, 100),
            SumLimitConstraint(100),
            NonNegativeDiffConstraint(),
        ]
        self._generator = ProblemGenerator(self._operators, self._constraints, seed=seed)
        self._repo = DatabaseRepository(db_path)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )

    # ------------------------------------------------------------------
    # 学生
    # ------------------------------------------------------------------

    def register_student(self, name: str, grade: str = "") -> int:
        return self._repo.register_student(name, grade)

    def list_students(self) -> list:
        return self._repo.list_students()

    # ------------------------------------------------------------------
    # 习题
    # ------------------------------------------------------------------

    def generate_and_save(self, exercise_type: str = "mixed",
                          count: int = 50, seed: Optional[int] = None) -> Exercise:
        """生成习题并保存到数据库。"""
        gen = ProblemGenerator(self._operators, self._constraints, seed=seed)
        problems = gen.generate_unique(count)

        exercise = ExerciseBuilder.build(exercise_type, count, seed)
        # 用实际生成的 problems 覆盖
        exercise = Exercise(
            exercise_id=exercise.exercise_id,
            exercise_type=exercise_type,
            problems=problems,
        )
        self._repo.save_exercise(exercise)
        return exercise

    # ------------------------------------------------------------------
    # 答题判题
    # ------------------------------------------------------------------

    def submit_and_grade(self, exercise_id: str, student_name: str,
                         answers: Dict[int, int]) -> Dict:
        """学生提交答案并自动判题。"""
        student = self._repo.find_student(student_name)
        if not student:
            sid = self._repo.register_student(student_name)
        else:
            sid = student["id"]

        return self._repo.submit_answers(exercise_id, sid, answers)

    # ------------------------------------------------------------------
    # 分析
    # ------------------------------------------------------------------

    def class_overview(self) -> list:
        return self._repo.class_overview()

    def weak_problems(self, top_n: int = 20) -> list:
        return self._repo.weak_problems_analysis(top_n)

    def student_progress(self, student_name: str) -> list:
        student = self._repo.find_student(student_name)
        if not student:
            raise ValueError(f"学生不存在: {student_name}")
        return self._repo.student_progress(student["id"])

    def student_weak(self, student_name: str, top_n: int = 20) -> list:
        student = self._repo.find_student(student_name)
        if not student:
            raise ValueError(f"学生不存在: {student_name}")
        return self._repo.student_weak_problems(student["id"], top_n)

    def stats(self) -> dict:
        row = self._repo.database_stats()
        return dict(row) if row else {}

    @property
    def repo(self) -> DatabaseRepository:
        return self._repo
