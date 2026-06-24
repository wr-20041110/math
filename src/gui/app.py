"""
MathPracticeApp —— GUI 主应用（Presenter + Subject）。

职责：
  - Presenter: 协调 Model（核心服务）和 View（GUI 组件）
  - Subject（观察者模式）: 管理 Observer 列表，广播 AppEvent
  - 事件驱动: 所有用户操作通过 tkinter 事件→回调→Observer 通知

设计原则：
  - MVP 模式: Model（services）← Presenter（app）→ View（widgets）
  - 观察者模式: App.notify_observers() → Observer.update()
  - 单一职责: App 只做协调，不直接操作 UI 细节
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Dict

from .events import AppEvent, EventType
from .observers import Observer
from .widgets import (
    ControlPanel,
    ExercisePanel,
    AnswerPanel,
    ResultPanel,
    AnalysisPanel,
    StatusBar,
)

from core.operators import Addition, Subtraction
from core.constraints import OperandRangeConstraint, SumLimitConstraint, NonNegativeDiffConstraint
from core.generator import ProblemGenerator
from core.problem import Problem
from models.exercise import Exercise
from models.answer import AnswerSheet
from services.grader import Grader
from services.analyzer import Analyzer


class MathPracticeApp:
    """口算练习 GUI 应用。

    实现：
      - Subject（观察者模式）：register_observer / notify_observers
      - Presenter（MVP）：接收 View 回调，调用 Model，更新 View
      - 事件驱动：tkinter 事件 → 回调 → Observer 更新
    """

    def __init__(self, root: tk.Tk):
        self._root = root
        self._root.title("口算练习系统 v3.0")
        self._root.geometry("1000x700")
        self._root.minsize(800, 600)

        # ---- Model ----
        self._operators = [Addition(), Subtraction()]
        self._constraints = [
            OperandRangeConstraint(0, 100),
            SumLimitConstraint(100),
            NonNegativeDiffConstraint(),
        ]
        self._generator = ProblemGenerator(self._operators, self._constraints)
        self._grader = Grader()
        self._analyzer = Analyzer()

        # ---- 状态 ----
        self._current_exercise: Optional[Exercise] = None
        self._observers: List[Observer] = []
        self._exercise_cache: Dict[str, Exercise] = {}

        # ---- View ----
        self._build_ui()

    # ==================================================================
    # 观察者模式 —— Subject
    # ==================================================================

    def register_observer(self, observer: Observer) -> None:
        """注册观察者。"""
        self._observers.append(observer)

    def notify_observers(self, event: AppEvent) -> None:
        """通知所有观察者。

        这是观察者模式的核心：遍历所有 Observer，调用 update()。
        """
        for obs in self._observers:
            try:
                obs.update(event)
            except Exception as e:
                messagebox.showwarning("通知错误", f"更新组件时出错: {e}")

    # ==================================================================
    # UI 构建
    # ==================================================================

    def _build_ui(self) -> None:
        """构建 GUI 布局。"""
        # -- 控制面板（顶部）--
        self._control = ControlPanel(self._root, callbacks={
            "generate": self._on_generate,
            "grade": self._on_grade,
            "analyze": self._on_analyze,
        })
        self._control.pack(fill=tk.X)
        self.register_observer(self._control)

        # -- 主内容区（左右分栏）--
        main = ttk.PanedWindow(self._root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧：习题显示 + 答案输入
        left = ttk.Frame(main)
        self._exercise_panel = ExercisePanel(left)
        self._exercise_panel.pack(fill=tk.BOTH, expand=True)
        self.register_observer(self._exercise_panel)

        self._answer_panel = AnswerPanel(left)
        self._answer_panel.pack(fill=tk.BOTH, expand=True)
        self.register_observer(self._answer_panel)

        main.add(left, weight=1)

        # 右侧：结果 + 分析
        right = ttk.Frame(main)
        self._result_panel = ResultPanel(right)
        self._result_panel.pack(fill=tk.BOTH, expand=True)
        self.register_observer(self._result_panel)

        self._analysis_panel = AnalysisPanel(right)
        self._analysis_panel.pack(fill=tk.BOTH, expand=True)
        self.register_observer(self._analysis_panel)

        main.add(right, weight=1)

        # -- 状态栏（底部）--
        self._status = StatusBar(self._root)
        self._status.pack(fill=tk.X, side=tk.BOTTOM)
        self.register_observer(self._status)

        # -- 快捷键绑定 --
        self._root.bind("<Control-g>", lambda e: self._on_generate())
        self._root.bind("<Control-Return>", lambda e: self._on_grade())

    # ==================================================================
    # 事件处理器 —— 事件驱动编程
    # ==================================================================

    def _on_generate(self) -> None:
        """「生成习题」按钮事件处理。

        事件链:
          <Button-1>  →  _on_generate()  →  notify_observers(EXERCISE_GENERATED)
        """
        try:
            ex_type = self._control.exercise_type
            count = self._control.count

            gen = ProblemGenerator(
                self._operators, self._constraints,
                seed=None,  # 每次随机
            )
            problems = gen.generate_unique(count)

            self._current_exercise = Exercise(
                exercise_id=f"EX-GUI-{len(self._exercise_cache) + 1:03d}",
                exercise_type=ex_type,
                problems=problems,
            )
            self._exercise_cache[self._current_exercise.exercise_id] = self._current_exercise

            self.notify_observers(AppEvent(
                type=EventType.EXERCISE_GENERATED,
                data=self._current_exercise,
            ))
        except Exception as e:
            self.notify_observers(AppEvent(
                type=EventType.ERROR_OCCURRED, data=str(e),
            ))

    def _on_grade(self) -> None:
        """「提交批改」按钮事件处理。

        事件链:
          <Button-1>  →  _on_grade()  →  notify_observers(GRADING_COMPLETE)
        """
        if self._current_exercise is None:
            messagebox.showwarning("提示", "请先生成习题！")
            return

        try:
            answers = self._answer_panel.get_answers()
            if not answers:
                messagebox.showwarning("提示", "请至少填写一道题的答案！")
                return

            answer_sheet = AnswerSheet(
                exercise_id=self._current_exercise.exercise_id,
                student="Student",
                answers=answers,
            )

            self.notify_observers(AppEvent(
                type=EventType.ANSWERS_SUBMITTED,
                data=answer_sheet,
            ))

            score = self._grader.evaluate(self._current_exercise, answer_sheet)
            self._analyzer.add_scores([score])

            self.notify_observers(AppEvent(
                type=EventType.GRADING_COMPLETE,
                data=score,
            ))
        except Exception as e:
            self.notify_observers(AppEvent(
                type=EventType.ERROR_OCCURRED, data=str(e),
            ))

    def _on_analyze(self) -> None:
        """「成绩分析」按钮事件处理。

        事件链:
          <Button-1>  →  _on_analyze()  →  notify_observers(ANALYSIS_COMPLETE)
        """
        try:
            summary = self._analyzer.summarize()
            weak = self._analyzer.identify_weak_areas(self._exercise_cache)

            data = {"summary": summary, "weak_problems": weak}
            self.notify_observers(AppEvent(
                type=EventType.ANALYSIS_COMPLETE,
                data=data,
            ))
        except Exception as e:
            self.notify_observers(AppEvent(
                type=EventType.ERROR_OCCURRED, data=str(e),
            ))
