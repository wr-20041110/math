"""
ProblemGenerator 类 —— 基于策略的题目生成器。

设计原则：
  - DIP（依赖倒转）：依赖 Operator 和 Constraint 抽象，而非具体实现。
  - OCP（开放-封闭）：新增运算符或约束无需修改 Generator 代码。
  - SRP（单一职责）：只负责"按约束生成一道合法题目"。

与故事1-3 的区别：
  - 不再用 if/else 分派运算符 —— 通过随机选择 Operator 策略子类。
  - 约束不再硬编码 —— 通过 constraint.validate() 委托。
"""

import random
from typing import List, Optional

from .operators import Operator
from .constraints import Constraint
from .problem import Problem


class ProblemGenerator:
    """题目生成器。

    组合运算符策略列表和约束策略列表，
    随机选择运算符并生成满足所有约束的题目。
    """

    def __init__(
        self,
        operators: List[Operator],
        constraints: List[Constraint],
        seed: Optional[int] = None,
    ):
        """初始化生成器。

        Args:
            operators: 可用的运算符策略列表（如 [Addition(), Subtraction()]）。
            constraints: 约束策略列表。
            seed: 随机种子，用于重现。

        Raises:
            ValueError: operators 或 constraints 为空时。
        """
        if not operators:
            raise ValueError("至少需要一个运算符")
        if not constraints:
            raise ValueError("至少需要一个约束")
        self._operators = list(operators)
        self._constraints = list(constraints)
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # 公有 API
    # ------------------------------------------------------------------

    def generate(self, max_attempts: int = 200) -> Problem:
        """随机生成一道满足所有约束的口算题。

        采用"生成-验证-重试"策略，以适配任意约束组合：
        1. 随机选择运算符策略
        2. 在宽松范围内随机生成操作数
        3. 用约束列表校验，不通过则重试

        这种设计遵循 OCP：新增约束子类无需修改 Generator，
        只要约束实现了 check() 方法即可。

        Args:
            max_attempts: 最大重试次数。

        Returns:
            合法的 Problem 实例。

        Raises:
            RuntimeError: 在 max_attempts 次尝试后仍无法生成合法题目。
        """
        for _ in range(max_attempts):
            # 1. 随机选择运算符策略
            operator = self._rng.choice(self._operators)

            # 2. 在宽松范围内生成操作数（具体约束由 validate 把关）
            num1, num2 = self._generate_operands(operator)

            # 3. 构造
            problem = Problem(num1=num1, num2=num2, operator=operator)

            # 4. 校验 —— 不通过则重试
            try:
                problem.validate(self._constraints)
                return problem
            except ValueError:
                continue

        raise RuntimeError(
            f"在 {max_attempts} 次尝试中无法生成满足所有约束的题目。"
            f"运算符: {[op.symbol for op in self._operators]}"
        )

    def generate_many(self, count: int, unique: bool = True) -> List[Problem]:
        """批量生成题目。

        Args:
            count: 需要的题目数量。
            unique: 是否去重（默认 True）。

        Returns:
            Problem 列表。

        Raises:
            RuntimeError: 无法在 max_attempts 内生成足够唯一题目。
        """
        if not unique:
            return [self.generate() for _ in range(count)]

        max_attempts = count * 200  # 动态上限
        seen = set()
        attempts = 0

        while len(seen) < count:
            if attempts >= max_attempts:
                raise RuntimeError(
                    f"在 {max_attempts} 次尝试中无法生成 {count} 道不重复题目。"
                    f"已生成 {len(seen)} 道。"
                )
            problem = self.generate()
            seen.add(problem)
            attempts += 1

        return list(seen)

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _generate_operands(self, operator: Operator) -> tuple:
        """根据运算符类型生成合法的操作数对。

        通过分析约束条件推导合法范围，直接生成合规数值，
        避免暴力试错。

        这体现了"约束驱动"的生成策略：
        - 加法：a ∈ [0,100], b ≤ 100-a
        - 减法：a ∈ [0,100], b ≤ a
        """
        if operator.symbol == "+":
            a = self._rng.randint(0, 100)
            b = self._rng.randint(0, 100 - a)
        else:  # "-"
            a = self._rng.randint(0, 100)
            b = self._rng.randint(0, a)
        return a, b
