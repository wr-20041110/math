"""
GUI 事件系统单元测试。

测试观察者模式 + 事件驱动系统的正确性。
由于 tkinter 需要图形环境，这里测试事件系统和观察者模式的逻辑层。
"""

import pytest
from src.gui.events import AppEvent, EventType
from src.gui.observers import Observer


class FakeObserver(Observer):
    """测试用观察者：记录收到的事件。"""
    def __init__(self):
        self.received: list[AppEvent] = []

    def update(self, event: AppEvent) -> None:
        self.received.append(event)


class TestEventSystem:
    """测试事件系统。"""

    def test_event_creation(self):
        event = AppEvent(type=EventType.EXERCISE_GENERATED, data="test")
        assert event.type == EventType.EXERCISE_GENERATED
        assert event.data == "test"
        assert event.timestamp is not None

    def test_event_types_distinct(self):
        """所有事件类型应互不相同。"""
        types = list(EventType)
        values = [t.value for t in types]
        assert len(values) == len(set(values))

    def test_event_str_representation(self):
        event = AppEvent(type=EventType.GRADING_COMPLETE, data=95)
        assert "GRADING_COMPLETE" in str(event)
        assert "int" in str(event)


class TestObserverPattern:
    """测试观察者模式。"""

    def test_register_and_notify(self):
        obs1 = FakeObserver()
        obs2 = FakeObserver()

        # 模拟 Subject
        observers = [obs1, obs2]
        event = AppEvent(type=EventType.EXERCISE_GENERATED, data="hello")

        for obs in observers:
            obs.update(event)

        assert len(obs1.received) == 1
        assert obs1.received[0].data == "hello"
        assert len(obs2.received) == 1

    def test_multiple_events(self):
        obs = FakeObserver()

        for t in EventType:
            obs.update(AppEvent(type=t, data=None))

        assert len(obs.received) == len(EventType)

    def test_observer_sees_event_data(self):
        obs = FakeObserver()
        test_data = {"score": 95, "correct": 19, "wrong": 1}
        obs.update(AppEvent(type=EventType.GRADING_COMPLETE, data=test_data))

        received = obs.received[0]
        assert received.data["score"] == 95
        assert received.data["correct"] == 19

    def test_observer_abstract(self):
        """不能实例化未实现 update() 的 Observer 子类。"""
        class BadObserver(Observer):
            pass

        with pytest.raises(TypeError):
            BadObserver()  # type: ignore
