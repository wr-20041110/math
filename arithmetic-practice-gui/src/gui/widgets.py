"""
GUI 组件 —— 所有可视化面板（View 层）。

设计原则：
  - 每个面板是独立的 Frame 子类（单一职责）
  - 每个面板实现 Observer 接口（观察者模式）
  - 用户交互通过 tkinter 事件绑定处理（事件驱动）
  - 按钮回调通过 command= 委托给 Presenter（MVP）

事件绑定清单：
  - <Button-1>: 鼠标单击
  - <Key-Return>: 回车键提交
  - <FocusIn>: 输入框获得焦点
  - <<ComboboxSelected>>: 下拉框选择
  - <MouseWheel>: 滚轮滚动
  - <Control-g>: Ctrl+G 快捷键生成
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Callable

from .observers import Observer
from .events import AppEvent, EventType


# =========================================================================
# ControlPanel —— 控制面板（按钮区）
# =========================================================================

class ControlPanel(ttk.Frame, Observer):
    """顶部控制面板：习题类型选择 + 操作按钮。

    事件：<Button-1> 触发各命令按钮。
    """

    def __init__(self, parent, callbacks: Dict[str, Callable] = None):
        super().__init__(parent, padding="10")
        self._callbacks = callbacks or {}
        self._build()

    def _build(self) -> None:
        """构建控件布局。"""
        # 习题类型选择
        ttk.Label(self, text="类型:").pack(side=tk.LEFT, padx=(0, 5))
        self._type_var = tk.StringVar(value="mixed")
        type_combo = ttk.Combobox(
            self, textvariable=self._type_var,
            values=["addition", "subtraction", "mixed"],
            state="readonly", width=10,
        )
        type_combo.pack(side=tk.LEFT, padx=5)

        # 题目数量
        ttk.Label(self, text="数量:").pack(side=tk.LEFT, padx=(10, 5))
        self._count_var = tk.IntVar(value=20)
        count_spin = ttk.Spinbox(
            self, from_=5, to=100, textvariable=self._count_var, width=5,
        )
        count_spin.pack(side=tk.LEFT, padx=5)

        # 按钮
        ttk.Button(
            self, text="生成习题",
            command=lambda: self._fire("generate"),
        ).pack(side=tk.LEFT, padx=10)

        self._grade_btn = ttk.Button(
            self, text="提交批改",
            command=lambda: self._fire("grade"),
            state=tk.DISABLED,
        )
        self._grade_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self, text="成绩分析",
            command=lambda: self._fire("analyze"),
        ).pack(side=tk.LEFT, padx=5)

    def _fire(self, name: str) -> None:
        if name in self._callbacks:
            self._callbacks[name]()

    @property
    def exercise_type(self) -> str:
        return self._type_var.get()

    @property
    def count(self) -> int:
        return self._count_var.get()

    def set_grade_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        self._grade_btn.config(state=state)

    # -- Observer --
    def update(self, event: AppEvent) -> None:
        if event.type == EventType.EXERCISE_GENERATED:
            self.set_grade_enabled(True)
        elif event.type == EventType.GRADING_COMPLETE:
            self.set_grade_enabled(False)


# =========================================================================
# ExercisePanel —— 习题显示面板
# =========================================================================

class ExercisePanel(ttk.Frame, Observer):
    """习题显示区域：滚动列表中展示题目。

    事件：<MouseWheel> 滚轮滚动浏览题目。
    """

    def __init__(self, parent):
        super().__init__(parent, padding="5")
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="📝 口算练习题", font=("", 12, "bold")).pack(anchor=tk.W)

        # 滚动区域
        canvas = tk.Canvas(self, height=300)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        self._scroll_frame = ttk.Frame(canvas)

        self._scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._scroll_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        # 鼠标滚轮事件
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._canvas = canvas
        self._problem_labels: List[ttk.Label] = []

    def display_problems(self, problems) -> None:
        """刷新题目显示。"""
        self.clear()
        for i, p in enumerate(problems, 1):
            text = f"  {i:>3}.   {p.left} {p.operator.symbol} {p.right} = ______"
            lbl = ttk.Label(self._scroll_frame, text=text, font=("Consolas", 11))
            lbl.pack(anchor=tk.W, pady=1)
            self._problem_labels.append(lbl)

    def clear(self) -> None:
        for lbl in self._problem_labels:
            lbl.destroy()
        self._problem_labels.clear()

    # -- Observer --
    def update(self, event: AppEvent) -> None:
        if event.type == EventType.EXERCISE_GENERATED:
            ex = event.data
            self.display_problems(ex.problems)
        elif event.type == EventType.GRADING_COMPLETE:
            pass  # 保持显示


# =========================================================================
# AnswerPanel —— 答案输入面板
# =========================================================================

class AnswerPanel(ttk.Frame, Observer):
    """答案输入区域：为每道题提供输入框。

    事件：
      - <FocusIn>: 输入框获得焦点时高亮
      - <Key-Return>: 回车自动跳转到下一题
    """

    def __init__(self, parent):
        super().__init__(parent, padding="5")
        self._entries: List[ttk.Entry] = []
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="✏️  填写答案", font=("", 12, "bold")).pack(anchor=tk.W)

        canvas = tk.Canvas(self, height=200)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        self._scroll_frame = ttk.Frame(canvas)

        self._scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._scroll_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._canvas = canvas

    def build_inputs(self, count: int) -> None:
        """创建 count 个答案输入框。"""
        self.clear()
        for i in range(1, count + 1):
            row = ttk.Frame(self._scroll_frame)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=f" 第{i:>3}题:", width=8).pack(side=tk.LEFT)
            entry = ttk.Entry(row, width=8, font=("Consolas", 11))
            entry.pack(side=tk.LEFT)
            # <FocusIn> 高亮
            entry.bind("<FocusIn>", lambda e, ent=entry: ent.configure(style=""))
            # <Key-Return> 跳转
            entry.bind("<Key-Return>", lambda e, idx=i: self._focus_next(idx))
            self._entries.append(entry)

    def _focus_next(self, current_idx: int) -> None:
        """回车跳转到下一个输入框。"""
        if current_idx < len(self._entries):
            self._entries[current_idx].focus()

    def get_answers(self) -> Dict[int, int]:
        """收集所有答案。"""
        result = {}
        for i, entry in enumerate(self._entries, 1):
            val = entry.get().strip()
            if val.lstrip("-").isdigit():
                result[i] = int(val)
        return result

    def clear(self) -> None:
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        self._entries.clear()

    # -- Observer --
    def update(self, event: AppEvent) -> None:
        if event.type == EventType.EXERCISE_GENERATED:
            ex = event.data
            self.build_inputs(ex.problem_count)
        elif event.type == EventType.GRADING_COMPLETE:
            pass  # 保持输入以便查看


# =========================================================================
# ResultPanel —— 结果展示面板
# =========================================================================

class ResultPanel(ttk.Frame, Observer):
    """批改结果显示区域。"""

    def __init__(self, parent):
        super().__init__(parent, padding="5")
        self._result_text = tk.StringVar(value="等待批改...")
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="📊 批改结果", font=("", 12, "bold")).pack(anchor=tk.W)

        self._score_label = ttk.Label(
            self, textvariable=self._result_text,
            font=("Consolas", 14, "bold"), foreground="blue",
        )
        self._score_label.pack(pady=10)

        self._detail_frame = ttk.Frame(self)
        self._detail_frame.pack(fill=tk.X)

    def show_score(self, score) -> None:
        """显示评分结果。"""
        color = "green" if score.percentage >= 80 else "orange" if score.percentage >= 60 else "red"
        self._score_label.configure(foreground=color)

        text = (
            f"总题数: {score.total}  |  "
            f"正确: {score.correct}  |  "
            f"错误: {score.wrong}  |  "
            f"得分: {score.percentage}%"
        )
        self._result_text.set(text)

        # 显示错题
        for w in self._detail_frame.winfo_children():
            w.destroy()
        if score.wrong_indices:
            ttk.Label(
                self._detail_frame,
                text=f"错题: {', '.join(str(i) for i in score.wrong_indices)}",
                foreground="red",
            ).pack()

    def show_error(self, msg: str) -> None:
        self._result_text.set(msg)
        self._score_label.configure(foreground="red")

    def clear(self) -> None:
        self._result_text.set("等待批改...")
        self._score_label.configure(foreground="blue")
        for w in self._detail_frame.winfo_children():
            w.destroy()

    # -- Observer --
    def update(self, event: AppEvent) -> None:
        if event.type == EventType.GRADING_COMPLETE:
            self.show_score(event.data)
        elif event.type == EventType.ERROR_OCCURRED:
            self.show_error(str(event.data))


# =========================================================================
# AnalysisPanel —— 分析面板
# =========================================================================

class AnalysisPanel(ttk.Frame, Observer):
    """成绩分析结果展示区域。"""

    def __init__(self, parent):
        super().__init__(parent, padding="5")
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="📈 成绩分析", font=("", 12, "bold")).pack(anchor=tk.W)
        self._text = tk.Text(self, height=10, width=60, font=("Consolas", 10),
                             state=tk.DISABLED, wrap=tk.WORD)
        self._text.pack(fill=tk.BOTH, expand=True, pady=5)

    def show_analysis(self, summary: dict, weak: list) -> None:
        """显示分析结果。"""
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)

        lines = [
            "=== 成绩摘要 ===",
            f"练习次数: {summary.get('total_sessions', 0)}",
            f"总做题数: {summary.get('total_problems_done', 0)}",
            f"平均得分: {summary.get('avg_percentage', 0.0)}%",
            f"最佳: {summary.get('best', 0)}%  最差: {summary.get('worst', 0)}%",
            "",
        ]

        if weak:
            lines.append("=== 弱项题目 ===")
            lines.append(f"{'题目':<12} {'错误次数':<8} {'错误率':<8}")
            lines.append("-" * 30)
            for w in weak[:10]:
                prob = f"{w['left']}{w['operator']}{w['right']}"
                lines.append(f"{prob:<12} {w['wrong_count']:<8} {w['error_rate']:.0%}")
        else:
            lines.append("暂无弱项数据（需先批改多份练习）")

        self._text.insert("1.0", "\n".join(lines))
        self._text.configure(state=tk.DISABLED)

    def clear(self) -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.configure(state=tk.DISABLED)

    # -- Observer --
    def update(self, event: AppEvent) -> None:
        if event.type == EventType.ANALYSIS_COMPLETE:
            data = event.data
            self.show_analysis(data["summary"], data["weak_problems"])


# =========================================================================
# StatusBar —— 状态栏
# =========================================================================

class StatusBar(ttk.Frame, Observer):
    """底部状态栏。"""

    def __init__(self, parent):
        super().__init__(parent, padding="3")
        self._status_var = tk.StringVar(value="就绪 — 点击「生成习题」开始")
        self._build()

    def _build(self) -> None:
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, side=tk.TOP)
        ttk.Label(self, textvariable=self._status_var, font=("", 9)).pack(side=tk.LEFT)

    def set_status(self, text: str) -> None:
        self._status_var.set(text)

    # -- Observer --
    def update(self, event: AppEvent) -> None:
        messages = {
            EventType.EXERCISE_GENERATED: lambda e: f"已生成 {e.data.problem_count} 道习题，请在右侧输入答案",
            EventType.ANSWERS_SUBMITTED: lambda e: "答案已提交，正在批改...",
            EventType.GRADING_COMPLETE: lambda e: f"批改完成 — 得分 {e.data.percentage}%",
            EventType.ANALYSIS_COMPLETE: lambda e: f"分析完成 — 共 {e.data['summary']['total_sessions']} 次练习",
            EventType.ERROR_OCCURRED: lambda e: f"错误: {e.data}",
        }
        msg_fn = messages.get(event.type)
        if msg_fn:
            self.set_status(msg_fn(event))
