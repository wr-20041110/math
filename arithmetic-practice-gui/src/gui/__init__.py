"""gui —— 图形用户界面层（MVP + 观察者模式 + 事件驱动）。"""
from .app import MathPracticeApp
from .events import AppEvent, EventType
from .observers import Observer
