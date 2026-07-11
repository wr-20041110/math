"""
共享测试Fixtures —— 为所有测试模块提供测试数据和工具。

Fixture目录：
  - temp_db: 临时数据库仓库
  - sample_students: 3个预注册学生
  - sample_problems: 10道混合题
  - sample_exercise: 完整习题集
  - sample_scores: 5组成绩数据
"""

import os
import sys
import tempfile
import pytest

# 将 src 目录加入 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))


@pytest.fixture
def db_path():
    """临时数据库文件路径。"""
    fd, path = tempfile.mkstemp(suffix='.db', prefix='test_mathpractice_')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def repo(db_path):
    """创建临时数据库仓库（自动清理）。"""
    from db.connection import ConnectionManager
    from db.repository import DatabaseRepository

    ConnectionManager.reset()
    r = DatabaseRepository(db_path)
    yield r
    r.reset()
    r.close()
    ConnectionManager.reset()


@pytest.fixture
def sample_students(repo):
    """预注册3个测试学生，返回 [id1, id2, id3]。"""
    return [
        repo.register_student("Alice", "三年级"),
        repo.register_student("Bob", "三年级"),
        repo.register_student("Charlie", "四年级"),
    ]


@pytest.fixture
def sample_problems():
    """10道混合加减法题。"""
    from core.operators import Addition, Subtraction
    from core.problem import Problem
    return [
        Problem(15, 7, Addition()),      # 15+7=22
        Problem(44, 23, Addition()),     # 44+23=67
        Problem(88, 21, Subtraction()),  # 88-21=67
        Problem(55, 10, Subtraction()),  # 55-10=45
        Problem(30, 50, Addition()),     # 30+50=80
        Problem(99, 44, Subtraction()),  # 99-44=55
        Problem(12, 8, Addition()),      # 12+8=20
        Problem(80, 20, Subtraction()),  # 80-20=60
        Problem(3, 97, Addition()),      # 3+97=100
        Problem(100, 0, Subtraction()),  # 100-0=100
    ]


@pytest.fixture
def sample_exercise(sample_problems):
    """完整习题集。"""
    from models.exercise import Exercise
    return Exercise(
        exercise_id="EX-TEST-001",
        exercise_type="mixed",
        problems=sample_problems,
    )


@pytest.fixture
def sample_answer_sheet(sample_exercise):
    """全对答卷。"""
    from models.answer import AnswerSheet
    return AnswerSheet(
        exercise_id=sample_exercise.exercise_id,
        student="Alice",
        answers={i: p.answer for i, p in enumerate(sample_exercise.problems, 1)},
    )


@pytest.fixture
def sample_answer_sheet_errors(sample_exercise):
    """含3个错误的答卷（第2、5、8题错）。"""
    from models.answer import AnswerSheet
    answers = {}
    for i, p in enumerate(sample_exercise.problems, 1):
        if i in (2, 5, 8):
            answers[i] = p.answer + 1  # 故意错误
        else:
            answers[i] = p.answer
    return AnswerSheet(
        exercise_id=sample_exercise.exercise_id,
        student="Bob",
        answers=answers,
    )


@pytest.fixture
def sample_score(sample_exercise):
    """一次评分结果（80%正确率）。"""
    from models.score import Score
    return Score(
        exercise_id=sample_exercise.exercise_id,
        student="Alice",
        total=10,
        correct=8,
        wrong=2,
        percentage=80.0,
        wrong_indices=[3, 7],
    )


@pytest.fixture
def operators():
    """默认运算符列表。"""
    from core.operators import Addition, Subtraction
    return [Addition(), Subtraction()]


@pytest.fixture
def constraints():
    """默认约束列表。"""
    from core.constraints import (
        OperandRangeConstraint,
        SumLimitConstraint,
        NonNegativeDiffConstraint,
    )
    return [
        OperandRangeConstraint(0, 100),
        SumLimitConstraint(100),
        NonNegativeDiffConstraint(),
    ]


@pytest.fixture
def generator(operators, constraints):
    """默认题目生成器（固定种子）。"""
    from core.generator import ProblemGenerator
    return ProblemGenerator(operators, constraints, seed=42)
