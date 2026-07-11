"""
DatabaseRepository —— 数据库仓库（CRUD + 业务查询）。

封装所有数据库操作，提供面向对象的 API。
所有方法使用参数化查询防止 SQL 注入。
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Tuple

from .connection import ConnectionManager
from .schema import create_schema
from . import queries as q

logger = logging.getLogger(__name__)


class DatabaseRepository:
    """数据库仓库。

    封装 students / exercises / problems / answers / scores 的 CRUD 操作，
    以及弱项分析、全班概览等业务查询。
    """

    def __init__(self, db_path: str = "data/mathpractice.db"):
        self._cm = ConnectionManager(db_path)
        create_schema(self._cm.connection)
        logger.info("数据库已初始化: %s", db_path)

    @property
    def conn(self) -> sqlite3.Connection:
        return self._cm.connection

    # ==================================================================
    # 学生管理
    # ==================================================================

    def register_student(self, name: str, grade: str = "") -> int:
        """注册学生，返回 ID（已存在则返回已有 ID）。"""
        with self._cm.transaction() as c:
            c.execute(q.INSERT_STUDENT, (name, grade))
            row = c.execute(q.FIND_STUDENT_BY_NAME, (name,)).fetchone()
            return row["id"] if row else 0

    def list_students(self) -> List[sqlite3.Row]:
        return self.conn.execute(q.LIST_ALL_STUDENTS).fetchall()

    def find_student(self, name: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(q.FIND_STUDENT_BY_NAME, (name,)).fetchone()

    # ==================================================================
    # 习题管理
    # ==================================================================

    def save_exercise(self, exercise) -> str:
        """保存习题及其所有题目到数据库。

        Args:
            exercise: Exercise 对象。

        Returns:
            exercise_id。
        """
        with self._cm.transaction() as c:
            c.execute(q.INSERT_EXERCISE, (
                exercise.exercise_id, exercise.exercise_type, exercise.problem_count
            ))
            for i, p in enumerate(exercise.problems, 1):
                c.execute(q.INSERT_PROBLEM, (
                    exercise.exercise_id, i, p.left, p.operator.symbol,
                    p.right, p.answer,
                ))
        logger.info("习题已保存: %s (%d 题)", exercise.exercise_id, exercise.problem_count)
        return exercise.exercise_id

    def load_exercise(self, exercise_id: str):
        """从数据库加载习题。"""
        from models.exercise import Exercise
        from core.problem import Problem
        from core.operators import get_operator

        ex_row = self.conn.execute(q.FIND_EXERCISE_BY_ID, (exercise_id,)).fetchone()
        if not ex_row:
            raise ValueError(f"习题不存在: {exercise_id}")

        prob_rows = self.conn.execute(q.FIND_PROBLEMS_BY_EXERCISE, (exercise_id,)).fetchall()
        problems = []
        for row in prob_rows:
            op = get_operator(row["operator"])
            problems.append(Problem(
                left=row["left_operand"], right=row["right_operand"], operator=op,
            ))

        from datetime import datetime
        return Exercise(
            exercise_id=ex_row["id"],
            exercise_type=ex_row["type"],
            problems=problems,
            created_at=datetime.fromisoformat(ex_row["created_at"])
            if ex_row["created_at"] else datetime.now(),
        )

    def list_recent_exercises(self, limit: int = 20) -> List[sqlite3.Row]:
        return self.conn.execute(q.LIST_EXERCISES, (limit,)).fetchall()

    # ==================================================================
    # 答案提交 + 自动判题
    # ==================================================================

    def submit_answers(self, exercise_id: str, student_id: int,
                       answers: Dict[int, int]) -> Dict:
        """提交答案并自动判题。

        逐题比对 student_answer vs correct_answer，
        将结果写入 answers 表，统计总分写入 scores 表。

        Args:
            exercise_id: 习题 ID。
            student_id: 学生 ID。
            answers: {problem_index: student_answer}。

        Returns:
            判题结果 dict: {total, correct, wrong, percentage, wrong_indices}。
        """
        prob_rows = self.conn.execute(
            q.FIND_PROBLEMS_BY_EXERCISE, (exercise_id,)
        ).fetchall()

        correct_count = 0
        wrong_indices = []

        with self._cm.transaction() as c:
            for row in prob_rows:
                idx = row["problem_index"]
                correct_ans = row["correct_answer"]
                student_ans = answers.get(idx)
                is_correct = 1 if student_ans == correct_ans else 0

                if is_correct:
                    correct_count += 1
                else:
                    wrong_indices.append(idx)

                c.execute(q.INSERT_ANSWER, (
                    exercise_id, student_id, idx,
                    student_ans if student_ans is not None else -1,
                    is_correct,
                ))

            total = len(prob_rows)
            wrong = total - correct_count
            percentage = round((correct_count / total) * 100, 1) if total > 0 else 0.0

            c.execute(q.INSERT_SCORE, (
                exercise_id, student_id, total, correct_count, wrong, percentage,
            ))

        result = {
            "total": total, "correct": correct_count, "wrong": wrong,
            "percentage": percentage, "wrong_indices": wrong_indices,
        }
        logger.info("判题完成: %s 学生=%d 得分=%.1f%%", exercise_id, student_id, percentage)
        return result

    # ==================================================================
    # 分析查询
    # ==================================================================

    def class_overview(self) -> List[sqlite3.Row]:
        """全班成绩概览。"""
        return self.conn.execute(q.CLASS_OVERVIEW).fetchall()

    def weak_problems_analysis(self, top_n: int = 20) -> List[sqlite3.Row]:
        """全局弱项分析（跨所有学生）。"""
        return self.conn.execute(q.WEAK_PROBLEMS_ANALYSIS, (top_n,)).fetchall()

    def student_progress(self, student_id: int) -> List[sqlite3.Row]:
        """学生个人进步轨迹。"""
        return self.conn.execute(q.STUDENT_PROGRESS, (student_id,)).fetchall()

    def student_weak_problems(self, student_id: int, top_n: int = 20) -> List[sqlite3.Row]:
        """学生个人弱项。"""
        return self.conn.execute(q.STUDENT_WEAK_PROBLEMS, (student_id, top_n)).fetchall()

    def student_scores(self, student_id: int) -> List[sqlite3.Row]:
        """学生所有成绩。"""
        return self.conn.execute(q.FIND_SCORES_BY_STUDENT, (student_id,)).fetchall()

    def database_stats(self) -> sqlite3.Row:
        """数据库统计信息。"""
        return self.conn.execute(q.DATABASE_STATS).fetchone()

    # ==================================================================
    # 工具方法
    # ==================================================================

    def reset(self) -> None:
        """清空所有数据（测试用）。"""
        from .schema import drop_schema
        drop_schema(self.conn)
        create_schema(self.conn)

    def close(self) -> None:
        self._cm.close()
