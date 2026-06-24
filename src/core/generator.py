"""
ProblemGenerator —— 策略驱动的题目生成器（重构：Extract Method + 配置对象）。"""
import random
from typing import List, Optional
from .operators import Operator
from .constraints import Constraint
from .problem import Problem
DEFAULT_GENERATE_MAX_ATTEMPTS = 200


class ProblemGenerator:
    """题目生成器。

    重构变更:
      - 构造参数简化（接受 Config 驱动）
      - generate_many → generate_unique / generate_batch（语义拆分）
      - 常量 DEFAULT_GENERATE_MAX_ATTEMPTS 提取
    """

    def __init__(
        self,
        operators: List[Operator],
        constraints: List[Constraint],
        seed: Optional[int] = None,
    ):
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

    def generate_one(self) -> Problem:
        """生成一道满足所有约束的题目。

        采用"生成-验证-重试"策略，适配任意约束组合。
        """
        for _ in range(DEFAULT_GENERATE_MAX_ATTEMPTS):
            operator = self._rng.choice(self._operators)
            left, right = self._pick_operands(operator)
            problem = Problem(left=left, right=right, operator=operator)
            try:
                problem.validate_against(self._constraints)
                return problem
            except ValueError:
                continue
        raise RuntimeError(
            f"在 {DEFAULT_GENERATE_MAX_ATTEMPTS} 次尝试中无法生成合法题目。"
        )

    def generate_unique(self, count: int) -> List[Problem]:
        """生成 count 道不重复题目。

        重构前: generate_many(count, unique=True)
        语义拆分: generate_unique / generate_batch
        """
        max_attempts = count * DEFAULT_GENERATE_MAX_ATTEMPTS
        seen: set[Problem] = set()
        attempts = 0

        while len(seen) < count:
            if attempts >= max_attempts:
                raise RuntimeError(
                    f"在 {max_attempts} 次尝试中无法生成 {count} 道不重复题目。"
                )
            seen.add(self.generate_one())
            attempts += 1

        return list(seen)

    def generate_batch(self, count: int) -> List[Problem]:
        """生成 count 道题（允许重复）。"""
        return [self.generate_one() for _ in range(count)]

    # ------------------------------------------------------------------
    # 内部方法 —— Extract Method
    # ------------------------------------------------------------------

    def _pick_operands(self, operator: Operator) -> tuple[int, int]:
        """根据运算符类型在合法范围内选择操作数对。

        重构后提取为独立方法，便于单独测试和覆写。
        """
        if operator.symbol == "+":
            left = self._rng.randint(0, 100)
            right = self._rng.randint(0, 100 - left)
        else:
            left = self._rng.randint(0, 100)
            right = self._rng.randint(0, left)
        return left, right
