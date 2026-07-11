"""
ProblemGenerator 类 —— 按约束条件随机生成口算题。

故事1：随机生成两个 0-100 以内的数和运算符。
故事2：新增约束 —— 加法结果 ≤ 100，减法结果 ≥ 0。
故事3：不在此模块中处理去重，去重由 ExerciseSheet 层负责。
"""

import random
from typing import Optional

from .problem import Problem


class ProblemGenerator:
    """口算题生成器。

    支持三种生成模式：
      - generate_addition()：仅生成加法题
      - generate_subtraction()：仅生成减法题
      - generate_random()：随机选择运算符

    所有生成均满足：
      - 两个操作数 ∈ [0, 100]
      - 加法：num1 + num2 ≤ 100
      - 减法：num1 - num2 ≥ 0
    """

    def __init__(self, seed: Optional[int] = None):
        """初始化生成器。

        Args:
            seed: 随机种子，用于重现测试。为 None 时使用系统熵源。
        """
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # 公有 API
    # ------------------------------------------------------------------

    def generate_addition(self) -> Problem:
        """生成一道加法口算题，满足 num1 + num2 ≤ 100。"""
        # num1 ∈ [0, 100]，num2 ∈ [0, 100 - num1]
        num1 = self._rng.randint(0, 100)
        max_num2 = 100 - num1
        num2 = self._rng.randint(0, max_num2) if max_num2 >= 0 else 0
        return Problem(num1=num1, num2=num2, operator="+")

    def generate_subtraction(self) -> Problem:
        """生成一道减法口算题，满足 num1 - num2 ≥ 0。"""
        # num1 ∈ [0, 100]，num2 ∈ [0, num1]
        num1 = self._rng.randint(0, 100)
        num2 = self._rng.randint(0, num1)
        return Problem(num1=num1, num2=num2, operator="-")

    def generate_random(self) -> Problem:
        """随机选择运算符，生成一道加法或减法题。"""
        if self._rng.choice([True, False]):
            return self.generate_addition()
        else:
            return self.generate_subtraction()
