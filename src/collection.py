"""
ProblemCollection 与 ProblemIterator —— 迭代器模式。

设计原则：
  - SRP（单一职责）：Collection 负责存储，Iterator 负责遍历逻辑。
  - OCP（开放-封闭）：可新增迭代器子类（如 FilteredIterator）而不修改 Collection。

模式：
  迭代器模式 —— 将遍历行为从集合中分离，
  允许以统一方式遍历不同类型的集合。

UML 关系：
  ┌──────────────────┐         ┌──────────────────────┐
  │  <<Iterable>>    │         │   <<Iterator>>       │
  │ ProblemCollection│ ──creates──▶  ProblemIterator    │
  ├──────────────────┤         ├──────────────────────┤
  │ - _problems: list│         │ - _problems: list     │
  │ + add(p)         │         │ - _index: int         │
  │ + __iter__()     │         │ + __next__(): Problem │
  │ + __len__()      │         │ + __iter__(): self    │
  └──────────────────┘         └──────────────────────┘
"""

from __future__ import annotations

from typing import Iterator, List, Optional, Callable
from .problem import Problem


# ---------------------------------------------------------------------------
# ProblemIterator —— 迭代器
# ---------------------------------------------------------------------------

class ProblemIterator(Iterator[Problem]):
    """Problem 集合的具体迭代器。

    实现 Python 迭代器协议：__iter__ + __next__。
    支持可选过滤谓词，遍历时只返回满足条件的题目。

    Attributes:
        _problems: 被遍历的 Problem 列表。
        _index: 当前遍历位置。
        _predicate: 可选过滤函数 f(Problem) -> bool。
    """

    def __init__(
        self,
        problems: List[Problem],
        predicate: Optional[Callable[[Problem], bool]] = None,
    ) -> None:
        self._problems = problems
        self._index = 0
        self._predicate = predicate

    def __iter__(self) -> "ProblemIterator":
        """返回自身，满足迭代器协议。"""
        return self

    def __next__(self) -> Problem:
        """返回下一个 Problem。

        若有过滤谓词，则跳过不满足条件的题目。

        Raises:
            StopIteration: 遍历结束时。
        """
        while self._index < len(self._problems):
            problem = self._problems[self._index]
            self._index += 1
            if self._predicate is None or self._predicate(problem):
                return problem
        raise StopIteration


# ---------------------------------------------------------------------------
# ProblemCollection —— 可迭代集合
# ---------------------------------------------------------------------------

class ProblemCollection:
    """口算题集合（可迭代）。

    存储 Problem 列表并支持多种迭代方式：
      - 默认迭代：遍历所有题目
      - 过滤迭代：只遍历满足条件的题目（如只遍历加法题）

    使用示例:
        >>> coll = ProblemCollection()
        >>> coll.add(Problem(num1=5, num2=3, operator=Addition()))
        >>> for p in coll:
        ...     print(p)
        5+3=

        >>> # 只遍历加法题
        >>> for p in coll.iter_filtered(lambda p: p.operator.symbol == '+'):
        ...     print(p)
    """

    def __init__(self, problems: Optional[List[Problem]] = None) -> None:
        self._problems: List[Problem] = list(problems) if problems else []

    # ------------------------------------------------------------------
    # 集合操作
    # ------------------------------------------------------------------

    def add(self, problem: Problem) -> None:
        """向集合中添加一道题。"""
        self._problems.append(problem)

    def extend(self, problems: List[Problem]) -> None:
        """批量添加题目。"""
        self._problems.extend(problems)

    def __len__(self) -> int:
        return len(self._problems)

    def __contains__(self, problem: Problem) -> bool:
        """支持 'in' 操作符。"""
        return problem in self._problems

    def __getitem__(self, index: int) -> Problem:
        """支持下标访问。"""
        return self._problems[index]

    # ------------------------------------------------------------------
    # 迭代器协议
    # ------------------------------------------------------------------

    def __iter__(self) -> ProblemIterator:
        """返回默认迭代器（遍历全部题目）。

        这是迭代器模式的核心：集合不自己实现遍历逻辑，
        而是委托给专门的迭代器对象。
        """
        return ProblemIterator(self._problems)

    def iter_filtered(
        self, predicate: Callable[[Problem], bool]
    ) -> ProblemIterator:
        """返回过滤迭代器。

        只遍历满足 predicate 的题目。
        体现 OCP：可新增过滤逻辑而无须修改 Collection 和默认 Iterator。

        Args:
            predicate: 过滤函数，接受 Problem 返回 bool。

        Returns:
            带过滤的 ProblemIterator。
        """
        return ProblemIterator(self._problems, predicate=predicate)
