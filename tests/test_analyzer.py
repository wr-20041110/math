"""
Analyzer 单元测试 —— 成绩分析 + 弱项识别 + 针对性练习。

覆盖：
  - 弱项统计（错误率计算）
  - 空数据集处理
  - 针对性练习生成
  - 摘要统计
"""

import pytest
from src.analyzer import Analyzer
from src.models import Exercise, Score
from src.operators import Addition as Add, Subtraction as Sub
from src.problem import Problem


@pytest.fixture
def exercise_map():
    """构建包含已知弱项的习题映射。"""
    e1 = Exercise(exercise_id="EX-001", exercise_type="mixed",
                  problems=[
                      Problem(15, 7, Add()),     # index 1 - 弱项
                      Problem(88, 21, Sub()),    # index 2 - 弱项
                      Problem(22, 33, Add()),    # index 3 - 弱项
                      Problem(44, 23, Add()),    # index 4
                      Problem(67, 45, Sub()),    # index 5
                  ])
    e2 = Exercise(exercise_id="EX-002", exercise_type="mixed",
                  problems=[
                      Problem(15, 7, Add()),     # index 1 - 弱项
                      Problem(88, 21, Sub()),    # index 2 - 弱项
                      Problem(50, 30, Add()),    # index 3
                      Problem(22, 33, Add()),    # index 4 - 弱项
                      Problem(99, 50, Sub()),    # index 5
                  ])
    return {e1.exercise_id: e1, e2.exercise_id: e2}


@pytest.fixture
def scores_with_weakness():
    """模拟成绩：某些题反复出错。"""
    return [
        Score(exercise_id="EX-001", student="Test",
              total=5, correct=3, wrong=2, percentage=60.0,
              wrong_indices=[1, 2]),
        Score(exercise_id="EX-002", student="Test",
              total=5, correct=4, wrong=1, percentage=80.0,
              wrong_indices=[1]),
    ]


class TestAnalyzerWeakProblems:
    """弱项识别测试。"""

    def test_find_weak_problems(self, exercise_map, scores_with_weakness):
        analyzer = Analyzer(scores_with_weakness)
        weak = analyzer.find_weak_problems(exercise_map)

        assert len(weak) > 0

        # 15+7 错了 2 次 (index 1 in both exercises)
        w15_7 = next(w for w in weak if w["num1"] == 15 and w["operator"] == "+")
        assert w15_7["wrong_count"] == 2
        assert w15_7["total_attempts"] == 2
        assert w15_7["error_rate"] == 1.0

        # 88-21 错了 1 次
        w88_21 = next(w for w in weak if w["num1"] == 88)
        assert w88_21["wrong_count"] == 1

    def test_find_weak_with_min_error_rate(self, exercise_map, scores_with_weakness):
        """min_error_rate 过滤。"""
        analyzer = Analyzer(scores_with_weakness)
        weak = analyzer.find_weak_problems(exercise_map, min_error_rate=1.0)
        # 只有 100% 错误率的题目
        assert all(w["error_rate"] >= 1.0 for w in weak)

    def test_top_n_limit(self, exercise_map, scores_with_weakness):
        """top_n 限制。"""
        analyzer = Analyzer(scores_with_weakness)
        weak = analyzer.find_weak_problems(exercise_map, top_n=1)
        assert len(weak) <= 1

    def test_empty_scores(self, exercise_map):
        """空成绩列表。"""
        analyzer = Analyzer([])
        weak = analyzer.find_weak_problems(exercise_map)
        assert weak == []


class TestTargetedPractice:
    """针对性练习生成。"""

    def test_generates_practice(self, exercise_map, scores_with_weakness):
        analyzer = Analyzer(scores_with_weakness)
        problems = analyzer.generate_targeted_practice(
            exercise_map, count=5, seed=42
        )
        assert len(problems) == 5
        # 所有题目应唯一
        ids = {(p.num1, p.num2, p.operator.symbol) for p in problems}
        assert len(ids) == 5

    def test_all_problems_valid(self, exercise_map, scores_with_weakness):
        analyzer = Analyzer(scores_with_weakness)
        problems = analyzer.generate_targeted_practice(
            exercise_map, count=10, seed=42
        )
        for p in problems:
            assert 0 <= p.num1 <= 100
            assert 0 <= p.num2 <= 100
            assert 0 <= p.answer <= 100

    def test_no_weakness_fallback(self, exercise_map):
        """没有弱项时应 fallback 到混合练习。"""
        analyzer = Analyzer([])  # 无成绩 → 无弱项
        problems = analyzer.generate_targeted_practice(
            exercise_map, count=10, seed=42
        )
        assert len(problems) == 10


class TestSummary:
    """摘要统计测试。"""

    def test_empty_summary(self):
        analyzer = Analyzer([])
        s = analyzer.summary()
        assert s["total_sessions"] == 0
        assert s["avg_percentage"] == 0.0

    def test_summary_with_scores(self, scores_with_weakness):
        analyzer = Analyzer(scores_with_weakness)
        s = analyzer.summary()
        assert s["total_sessions"] == 2
        assert s["total_problems_done"] == 10
        assert s["avg_percentage"] == 70.0
        assert s["best"] == 80.0
        assert s["worst"] == 60.0
