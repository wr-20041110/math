"""
显示策略体系 —— 抽象基类 + 具体显示策略（策略模式）。

设计原则：
  - OCP（开放-封闭）：新增显示格式只需添加子类，无需修改已有代码。
  - SRP（单一职责）：每个 DisplayStrategy 子类只负责一种显示格式。
  - ISP（接口隔离）：抽象接口仅包含 display() 一个方法，实现类无冗余依赖。
  - DIP（依赖倒转）：高层模块依赖 DisplayStrategy 抽象，不依赖具体显示实现。

模式：
  策略模式 —— 将显示算法封装为可互换的策略对象，
  客户端通过 DisplayStrategy 接口操作，运行时可替换显示行为。
"""

from abc import ABC, abstractmethod
from typing import List
from .problem import Problem


# ---------------------------------------------------------------------------
# 抽象策略
# ---------------------------------------------------------------------------

class DisplayStrategy(ABC):
    """显示策略抽象基类。

    定义问题集格式化输出的统一接口。
    子类实现具体的排版和答案显示规则。
    """

    @abstractmethod
    def display(self, problems: List[Problem]) -> str:
        """将题目列表格式化为可打印的字符串。

        Args:
            problems: Problem 列表。

        Returns:
            格式化后的多行文本。
        """
        ...


# ---------------------------------------------------------------------------
# 具体策略：网格显示（无答案）
# ---------------------------------------------------------------------------

class GridDisplay(DisplayStrategy):
    """网格显示策略：每行 cols 列，不显示答案。

    故事2 需求：每行整齐显示多个算式。
    """

    def __init__(self, cols: int = 5) -> None:
        if cols < 1:
            raise ValueError(f"cols 必须 ≥ 1, 实际为 {cols}")
        self._cols = cols

    @property
    def cols(self) -> int:
        return self._cols

    def display(self, problems: List[Problem]) -> str:
        lines: List[str] = []
        for i in range(0, len(problems), self._cols):
            row = problems[i : i + self._cols]
            lines.append("\t".join(str(p) for p in row))
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"GridDisplay(cols={self._cols})"


# ---------------------------------------------------------------------------
# 具体策略：带答案显示
# ---------------------------------------------------------------------------

class AnswerDisplay(DisplayStrategy):
    """带答案显示策略：每行 cols 列，算式后紧跟答案。

    故事2 需求：爷爷需要答案来检查小明的练习。
    通过多态的 Problem.answer 属性获取结果。
    """

    def __init__(self, cols: int = 5) -> None:
        if cols < 1:
            raise ValueError(f"cols 必须 ≥ 1, 实际为 {cols}")
        self._cols = cols

    @property
    def cols(self) -> int:
        return self._cols

    def display(self, problems: List[Problem]) -> str:
        lines: List[str] = []
        for i in range(0, len(problems), self._cols):
            row = problems[i : i + self._cols]
            formatted = []
            for p in row:
                # 多态调用：p.answer 内部通过 Operator.apply() 计算
                formatted.append(f"{p}{p.answer}")
            lines.append("\t".join(formatted))
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"AnswerDisplay(cols={self._cols})"
