"""
Application —— 统一应用外观（整合数据库 + 新功能）。

集成核心服务 + 数据库仓库 + Word导出 + 图表 + Web，
提供统一的业务 API。
"""

import logging
from typing import Dict, List, Optional

from core.operators import Addition, Subtraction
from core.constraints import (
    OperandRangeConstraint,
    SumLimitConstraint,
    NonNegativeDiffConstraint,
)
from core.generator import ProblemGenerator
from models.exercise import Exercise
from services.exercise_builder import ExerciseBuilder
from db.repository import DatabaseRepository

logger = logging.getLogger(__name__)


class Application:
    """口算练习系统应用外观。

    整合所有子系统，对外提供简洁的业务 API。
    支持 CLI 和 Web 两种使用方式。
    """

    def __init__(self, db_path: str = "data/mathpractice.db", seed: Optional[int] = None):
        self._operators = [Addition(), Subtraction()]
        self._constraints = [
            OperandRangeConstraint(0, 100),
            SumLimitConstraint(100),
            NonNegativeDiffConstraint(),
        ]
        self._generator = ProblemGenerator(self._operators, self._constraints, seed=seed)
        self._repo = DatabaseRepository(db_path)
        self._db_path = db_path

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )

    # ------------------------------------------------------------------
    # 学生管理
    # ------------------------------------------------------------------

    def register_student(self, name: str, grade: str = "") -> int:
        """注册学生，返回 ID。"""
        return self._repo.register_student(name, grade)

    def list_students(self) -> list:
        """列出所有学生。"""
        return self._repo.list_students()

    def find_student(self, name: str):
        """按姓名查找学生。"""
        return self._repo.find_student(name)

    # ------------------------------------------------------------------
    # 习题生成
    # ------------------------------------------------------------------

    def generate_and_save(self, exercise_type: str = "mixed",
                          count: int = 50, seed: Optional[int] = None) -> Exercise:
        """生成习题并保存到数据库。"""
        gen = ProblemGenerator(self._operators, self._constraints, seed=seed)
        problems = gen.generate_unique(count)

        exercise = ExerciseBuilder.build(exercise_type, count, seed)
        exercise = Exercise(
            exercise_id=exercise.exercise_id,
            exercise_type=exercise_type,
            problems=problems,
        )
        self._repo.save_exercise(exercise)
        logger.info("习题已生成: %s (%d题)", exercise.exercise_id, count)
        return exercise

    def load_exercise(self, exercise_id: str) -> Exercise:
        """从数据库加载习题。"""
        return self._repo.load_exercise(exercise_id)

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
    # 成绩分析
    # ------------------------------------------------------------------

    def class_overview(self) -> list:
        """全班成绩概览。"""
        return self._repo.class_overview()

    def weak_problems(self, top_n: int = 20) -> list:
        """全局弱项分析。"""
        return self._repo.weak_problems_analysis(top_n)

    def student_progress(self, student_name: str) -> list:
        """学生个人进步轨迹。"""
        student = self._repo.find_student(student_name)
        if not student:
            raise ValueError(f"学生不存在: {student_name}")
        return self._repo.student_progress(student["id"])

    def student_weak(self, student_name: str, top_n: int = 20) -> list:
        """学生个人弱项。"""
        student = self._repo.find_student(student_name)
        if not student:
            raise ValueError(f"学生不存在: {student_name}")
        return self._repo.student_weak_problems(student["id"], top_n)

    def stats(self) -> dict:
        """数据库统计信息。"""
        row = self._repo.database_stats()
        return dict(row) if row else {}

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------

    @property
    def repo(self) -> DatabaseRepository:
        return self._repo

    @property
    def db_path(self) -> str:
        return self._db_path

    @property
    def operators(self) -> list:
        return list(self._operators)

    @property
    def constraints(self) -> list:
        return list(self._constraints)
