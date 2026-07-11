"""
事件系统 —— 自定义事件类型 + 事件数据载体。

观察者模式的核心：Subject 产生 AppEvent，通知所有 Observer。
事件驱动编程：所有 GUI 状态变更都通过事件传播。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class EventType(Enum):
    """应用事件类型枚举。

    每个枚举值对应一种 GUI 状态变更事件。
    """
    EXERCISE_GENERATED = auto()   # 习题已生成
    ANSWERS_SUBMITTED = auto()    # 答案已提交
    GRADING_COMPLETE = auto()     # 批改已完成
    ANALYSIS_COMPLETE = auto()    # 分析已完成
    ERROR_OCCURRED = auto()       # 发生错误


@dataclass
class AppEvent:
    """应用事件数据载体。

    Attributes:
        type: 事件类型。
        data: 事件携带的数据（Exercise / Score / dict / str）。
        timestamp: 事件产生时间。
    """
    type: EventType
    data: Any = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"AppEvent({self.type.name}, data={type(self.data).__name__})"
