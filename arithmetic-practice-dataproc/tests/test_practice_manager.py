"""
PracticeManager 集成测试 —— 外观模式 + 端到端流程。

覆盖：
  - 习题生成 → CSV 保存
  - CSV 答案加载 → 判题打分
  - 成绩分析 → 针对性练习
"""

import os
import pytest
from src.practice_manager import PracticeManager
from src.csv_handler import CsvHandler


@pytest.fixture
def pm(temp_dir):
    """在临时目录中创建 PracticeManager。"""
    return PracticeManager(data_dir=temp_dir)


class TestGenerateExercise:
    def test_generate_mixed(self, pm):
        ex, path = pm.generate_exercise("mixed", count=10, seed=42)
        assert ex.total == 10
        assert os.path.isfile(path)

    def test_generate_addition(self, pm):
        ex, path = pm.generate_exercise("addition", count=5, seed=42)
        for p in ex.problems:
            assert p.operator.symbol == "+"

    def test_generate_subtraction(self, pm):
        ex, path = pm.generate_exercise("subtraction", count=5, seed=42)
        for p in ex.problems:
            assert p.operator.symbol == "-"


class TestGradeFromData:
    """从内存数据判题。"""

    def test_grade_correct_answers(self, pm):
        # 先生成习题
        ex, _ = pm.generate_exercise("mixed", count=5, seed=42)
        # 构造全部正确的答案
        answers = {i + 1: p.answer for i, p in enumerate(ex.problems)}
        score = pm.grade_from_data(ex.exercise_id, "XiaoMing", answers)
        assert score.total == 5
        assert score.correct == 5
        assert score.wrong == 0
        assert score.percentage == 100.0

    def test_grade_with_errors(self, pm):
        ex, _ = pm.generate_exercise("mixed", count=5, seed=42)
        answers = {}
        for i, p in enumerate(ex.problems):
            idx = i + 1
            # 第 1 题故意错
            answers[idx] = p.answer + 1 if idx == 1 else p.answer
        score = pm.grade_from_data(ex.exercise_id, "XiaoMing", answers)
        assert score.wrong == 1
        assert 1 in score.wrong_indices


class TestAnalyze:
    def test_analyze_with_history(self, pm):
        """多次练习后分析。"""
        for day in range(3):
            ex, _ = pm.generate_exercise("mixed", count=5, seed=day)
            answers = {i + 1: p.answer for i, p in enumerate(ex.problems)}
            pm.grade_from_data(ex.exercise_id, "XiaoMing", answers)

        result = pm.analyze()
        assert result["summary"]["total_sessions"] == 3
        assert result["summary"]["avg_percentage"] == 100.0

    def test_analyze_empty(self, pm):
        result = pm.analyze()
        assert result["summary"]["total_sessions"] == 0


class TestTargetedPractice:
    def test_generate_targeted(self, pm):
        """先造弱项再针对性出题。"""
        for day in range(2):
            ex, _ = pm.generate_exercise("addition", count=5, seed=day)
            answers = {}
            for i, p in enumerate(ex.problems):
                idx = i + 1
                # 对第一题故意答错
                if idx == 1 and day == 0:
                    answers[idx] = 999
                elif idx == 1 and day == 1:
                    answers[idx] = 998
                else:
                    answers[idx] = p.answer
            pm.grade_from_data(ex.exercise_id, "XiaoMing", answers)

        targeted = pm.generate_targeted_practice(count=5, seed=99)
        assert targeted.total == 5
        assert targeted.exercise_type == "targeted"


class TestLoadScores:
    def test_load_empty(self, pm):
        scores = pm.load_scores()
        assert scores == []

    def test_load_after_grading(self, pm):
        ex, _ = pm.generate_exercise("mixed", count=5, seed=42)
        answers = {i + 1: p.answer for i, p in enumerate(ex.problems)}
        pm.grade_from_data(ex.exercise_id, "XiaoMing", answers)

        scores = pm.load_scores()
        assert len(scores) >= 1
