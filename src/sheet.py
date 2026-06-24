"""
ExerciseSheet 类 —— 外观模式（Facade）。

设计原则：
  - 外观模式：为 Generator、Collection、DisplayStrategy 子系统提供统一入口。
  - SRP：只负责协调，不自己生成/存储/显示。

客户端只需与 ExerciseSheet 交互，无需了解内部子系统。
"""

from typing import List, Optional

from .operators import Operator, Addition, Subtraction
from .constraints import Constraint, OperandRangeConstraint, SumLimitConstraint, NonNegativeDiffConstraint
from .generator import ProblemGenerator
from .collection import ProblemCollection
from .display import DisplayStrategy, GridDisplay, AnswerDisplay
from .problem import Problem


class ExerciseSheet:
    """习题集外观。

    封装了口算题生成、存储、显示的完整流程，
    对外提供简洁的 API。

    使用示例:
        >>> sheet = ExerciseSheet(total=50, seed=42, show_answers=True)
        >>> print(sheet.render())
    """

    def __init__(
        self,
        total: int = 50,
        cols: int = 5,
        show_answers: bool = False,
        seed: Optional[int] = None,
        operators: Optional[List[Operator]] = None,
        constraints: Optional[List[Constraint]] = None,
    ):
        """初始化习题集。

        Args:
            total: 题目总数（默认 50）。
            cols: 每行列数（默认 5）。
            show_answers: 是否显示答案（默认 False）。
            seed: 随机种子。
            operators: 自定义运算符列表（默认 +、-）。
            constraints: 自定义约束列表（默认：范围 [0,100]、和 ≤ 100、差 ≥ 0）。
        """
        if total < 0:
            raise ValueError(f"total 不能为负数: {total}")

        self._total = total

        # 组装子系统（依赖注入）
        self._operators = operators or [Addition(), Subtraction()]
        self._constraints = constraints or [
            OperandRangeConstraint(0, 100),
            SumLimitConstraint(100),
            NonNegativeDiffConstraint(),
        ]

        self._generator = ProblemGenerator(
            operators=self._operators,
            constraints=self._constraints,
            seed=seed,
        )

        self._collection = ProblemCollection()

        # 选择显示策略
        if show_answers:
            self._display_strategy: DisplayStrategy = AnswerDisplay(cols=cols)
        else:
            self._display_strategy = GridDisplay(cols=cols)

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def generate(self) -> ProblemCollection:
        """生成习题集。

        Returns:
            包含所有题目的 ProblemCollection（可迭代）。
        """
        problems = self._generator.generate_many(self._total, unique=True)
        self._collection = ProblemCollection(problems)
        return self._collection

    def render(self) -> str:
        """生成并渲染习题集为字符串。

        Returns:
            格式化后的习题文本。
        """
        if len(self._collection) == 0:
            self.generate()
        return self._display_strategy.display(list(self._collection))

    def get_problems(self) -> List[Problem]:
        """获取题目列表（用于程序化访问）。"""
        if len(self._collection) == 0:
            self.generate()
        return list(self._collection)

    # ------------------------------------------------------------------
    # 统计信息
    # ------------------------------------------------------------------

    @property
    def stats(self) -> dict:
        """返回习题集统计信息。"""
        if len(self._collection) == 0:
            self.generate()
        problems = list(self._collection)
        add_count = sum(1 for p in problems if p.operator.symbol == "+")
        sub_count = len(problems) - add_count
        return {
            "total": len(problems),
            "addition": add_count,
            "subtraction": sub_count,
            "max_answer": max(p.answer for p in problems) if problems else 0,
            "min_answer": min(p.answer for p in problems) if problems else 0,
        }
