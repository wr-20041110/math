"""
观察者模式 —— Observer 抽象基类。

所有 GUI 面板都实现 Observer 接口，
通过 update() 方法接收 AppEvent 通知。

这是观察者模式的 Python 实现：
  Subject (App) ──notify──▶ Observer (Panels)
"""

from abc import ABC, abstractmethod
from .events import AppEvent


class Observer(ABC):
    """观察者抽象基类。

    所有需要响应应用状态变更的 GUI 组件都应实现此接口。
    """

    @abstractmethod
    def update(self, event: AppEvent) -> None:
        """接收主题通知。

        Args:
            event: 携带状态变更信息的应用事件。
        """
        ...
