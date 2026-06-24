"""
Formatter 类 —— 将习题集格式化输出。

故事2 的要求：
  - 每行显示多个算式（默认 5 列）
  - 支持显示 / 不显示答案
  - 50 题 = 5 列 × 10 行，整洁对齐
"""

from typing import List

from .problem import Problem


class Formatter:
    """习题格式化器。

    负责将 Problem 列表渲染为适合屏幕显示的文本。
    """

    def __init__(self, cols: int = 5, show_answer: bool = False):
        """初始化格式化器。

        Args:
            cols: 每行显示的算式数量，默认 5。
            show_answer: 是否在算式后显示答案，默认 False。
        """
        if cols < 1:
            raise ValueError(f"cols 必须 ≥ 1，实际为 {cols}")
        self.cols = cols
        self.show_answer = show_answer

    # ------------------------------------------------------------------
    # 公有 API
    # ------------------------------------------------------------------

    def format(self, problems: List[Problem]) -> str:
        """将题目列表格式化为多行文本。

        Args:
            problems: Problem 列表。

        Returns:
            格式化后的字符串，每行 col 个算式。
        """
        lines: List[str] = []
        for i in range(0, len(problems), self.cols):
            row = problems[i : i + self.cols]
            line = self._format_row(row)
            lines.append(line)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _format_row(self, row: List[Problem]) -> str:
        """格式化一行算式，列间用制表符对齐。"""
        parts: List[str] = []
        for p in row:
            if self.show_answer:
                parts.append(f"{p}{p.answer}")
            else:
                parts.append(str(p))
        return "\t".join(parts)
