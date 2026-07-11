"""pytest fixtures —— 测试数据工厂。"""

import pytest
import tempfile
import os
from datetime import datetime
from typing import List

from src.operators import Addition, Subtraction
from src.problem import Problem
from src.models import Exercise, AnswerSheet, Score


@pytest.fixture
def sample_problems() -> List[Problem]:
    """10 道样本题目。"""
    return [
        Problem(num1=15, num2=7, operator=Addition()),
        Problem(num1=22, num2=33, operator=Addition()),
        Problem(num1=88, num2=21, operator=Subtraction()),
        Problem(num1=44, num2=23, operator=Addition()),
        Problem(num1=55, num2=9, operator=Subtraction()),
        Problem(num1=3, num2=86, operator=Addition()),
        Problem(num1=67, num2=45, operator=Subtraction()),
        Problem(num1=90, num2=10, operator=Addition()),
        Problem(num1=100, num2=0, operator=Subtraction()),
        Problem(num1=38, num2=47, operator=Addition()),
    ]


@pytest.fixture
def sample_exercise(sample_problems) -> Exercise:
    """样本习题集。"""
    return Exercise(
        exercise_id="EX-TEST-001",
        exercise_type="mixed",
        problems=sample_problems,
        created_at=datetime(2026, 6, 24, 10, 30, 0),
    )


@pytest.fixture
def sample_answers() -> dict:
    """样本答案（全部正确）。"""
    return {
        1: 22,   # 15+7
        2: 55,   # 22+33
        3: 67,   # 88-21
        4: 67,   # 44+23
        5: 46,   # 55-9
        6: 89,   # 3+86
        7: 22,   # 67-45
        8: 100,  # 90+10
        9: 100,  # 100-0
        10: 85,  # 38+47
    }


@pytest.fixture
def sample_answers_with_errors() -> dict:
    """样本答案（含 3 个错误）。"""
    return {
        1: 22,   # 15+7=22 正确
        2: 54,   # 22+33=55 错误！(答了54)
        3: 67,   # 88-21=67 正确
        4: 67,   # 44+23=67 正确
        5: 46,   # 55-9=46 正确
        6: 89,   # 3+86=89 正确
        7: 21,   # 67-45=22 错误！(答了21)
        8: 100,  # 90+10=100 正确
        9: 99,   # 100-0=100 错误！(答了99)
        10: 85,  # 38+47=85 正确
    }


@pytest.fixture
def sample_answer_sheet(sample_answers) -> AnswerSheet:
    """样本答卷。"""
    return AnswerSheet(
        exercise_id="EX-TEST-001",
        student="XiaoMing",
        answers=sample_answers,
        submitted_at=datetime(2026, 6, 24, 20, 0, 0),
    )


@pytest.fixture
def sample_score() -> Score:
    """样本成绩。"""
    return Score(
        exercise_id="EX-TEST-001",
        student="XiaoMing",
        total=10,
        correct=8,
        wrong=2,
        percentage=80.0,
        wrong_indices=[2, 7],
        graded_at=datetime(2026, 6, 24, 21, 0, 0),
    )


@pytest.fixture
def temp_dir():
    """临时目录（测试后自动清理）。"""
    with tempfile.TemporaryDirectory() as d:
        yield d
