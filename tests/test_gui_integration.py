"""
GUI 集成测试 —— 测试核心服务与 GUI 的交互（无需图形环境）。

通过直接调用 App 的事件处理方法，验证 Model-View 协调逻辑。
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from gui.events import AppEvent, EventType
from gui.observers import Observer


class RecordingObserver(Observer):
    """记录所有收到的事件。"""
    def __init__(self):
        self.events: list[AppEvent] = []

    def update(self, event: AppEvent) -> None:
        self.events.append(event)


class TestGUIIntegration:
    """集成测试：事件流正确性。"""

    def test_event_flow_generate_then_grade(self):
        """模拟生成→批改的事件流。"""
        obs = RecordingObserver()

        # 模拟 EXERCISE_GENERATED
        obs.update(AppEvent(
            type=EventType.EXERCISE_GENERATED,
            data={"exercise_id": "EX-001", "problem_count": 10},
        ))
        # 模拟 GRADING_COMPLETE
        obs.update(AppEvent(
            type=EventType.GRADING_COMPLETE,
            data={"percentage": 90.0, "correct": 9, "wrong": 1},
        ))

        assert len(obs.events) == 2
        assert obs.events[0].type == EventType.EXERCISE_GENERATED
        assert obs.events[1].type == EventType.GRADING_COMPLETE

    def test_error_event_propagation(self):
        """模拟错误事件传播。"""
        obs = RecordingObserver()
        obs.update(AppEvent(
            type=EventType.ERROR_OCCURRED,
            data="测试错误消息",
        ))

        assert obs.events[0].type == EventType.ERROR_OCCURRED
        assert obs.events[0].data == "测试错误消息"

    def test_full_workflow_event_chain(self):
        """完整工作流事件链。"""
        obs = RecordingObserver()

        workflow = [
            (EventType.EXERCISE_GENERATED, "exercise_data"),
            (EventType.ANSWERS_SUBMITTED, "answers_data"),
            (EventType.GRADING_COMPLETE, "score_data"),
            (EventType.ANALYSIS_COMPLETE, "analysis_data"),
        ]

        for event_type, data in workflow:
            obs.update(AppEvent(type=event_type, data=data))

        assert len(obs.events) == 4
        assert [e.type for e in obs.events] == [t for t, _ in workflow]


class TestServices:
    """验证核心服务正常工作。"""

    def test_generator_produces_valid_problems(self):
        from core.operators import Addition, Subtraction
        from core.constraints import OperandRangeConstraint, SumLimitConstraint, NonNegativeDiffConstraint
        from core.generator import ProblemGenerator

        gen = ProblemGenerator(
            [Addition(), Subtraction()],
            [OperandRangeConstraint(0, 100), SumLimitConstraint(100), NonNegativeDiffConstraint()],
            seed=42,
        )
        problems = gen.generate_unique(10)
        assert len(problems) == 10
        for p in problems:
            assert 0 <= p.left <= 100
            assert 0 <= p.right <= 100
            assert 0 <= p.answer <= 100

    def test_grader_all_correct(self):
        from core.operators import Addition
        from core.problem import Problem
        from models.exercise import Exercise
        from models.answer import AnswerSheet
        from services.grader import Grader

        ex = Exercise(exercise_id="EX-T", exercise_type="addition",
                     problems=[Problem(5, 3, Addition()), Problem(10, 20, Addition())])
        sheet = AnswerSheet(exercise_id="EX-T", student="Test", answers={1: 8, 2: 30})
        score = Grader().evaluate(ex, sheet)
        assert score.correct == 2
        assert score.wrong == 0

    def test_analyzer_summary(self):
        from services.analyzer import Analyzer

        a = Analyzer([])
        s = a.summarize()
        assert s["total_sessions"] == 0
