"""
ExerciseSheet 类 —— 管理一套口算练习题集。

故事3 的核心模块：
  - 使用 set 跟踪已生成的题目，确保 50 道题无重复
  - 随机混合加法和减法（不指定各占几道）
  - 最多尝试 max_attempts 次以避免组合爆炸时的死循环
"""

from typing import List, Optional, Set

from .problem import Problem
from .generator import ProblemGenerator


class ExerciseSheet:
    """一套口算练习题。

    负责按指定数量生成不重复的口算题集。
    """

    def __init__(
        self,
        total: int = 50,
        seed: Optional[int] = None,
        max_attempts: int = 10000,
    ):
        """初始化习题集。

        Args:
            total: 题目总数，默认 50。
            seed: 随机种子，用于重现测试。
            max_attempts: 最大生成尝试次数，防止因可行空间不足而死循环。
        """
        if total < 0:
            raise ValueError(f"total 不能为负数: {total}")
        self.total = total
        self._generator = ProblemGenerator(seed=seed)
        self._max_attempts = max_attempts
        self._problems: List[Problem] = []

    # ------------------------------------------------------------------
    # 公有 API
    # ------------------------------------------------------------------

    @property
    def problems(self) -> List[Problem]:
        """返回已生成的题目列表（只读副本）。"""
        return list(self._problems)

    def generate(self) -> List[Problem]:
        """生成 total 道不重复的口算题。

        Returns:
            生成的 Problem 列表。

        Raises:
            RuntimeError: 如果在 max_attempts 次尝试内未能生成足够的唯一题目。
        """
        seen: Set[Problem] = set()
        attempts = 0

        while len(seen) < self.total:
            if attempts >= self._max_attempts:
                raise RuntimeError(
                    f"在 {self._max_attempts} 次尝试内无法生成 {self.total} 道不重复的口算题。"
                    f"已生成 {len(seen)} 道。"
                )
            problem = self._generator.generate_random()
            seen.add(problem)
            attempts += 1

        self._problems = list(seen)
        return self._problems
