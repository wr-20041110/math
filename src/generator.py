"""ProblemGenerator —— 基于策略的题目生成器（DIP）。"""
import random
from typing import List, Optional
from .operators import Operator
from .constraints import Constraint
from .problem import Problem


class ProblemGenerator:
    def __init__(self, operators: List[Operator], constraints: List[Constraint],
                 seed: Optional[int] = None):
        if not operators:
            raise ValueError("至少需要一个运算符")
        if not constraints:
            raise ValueError("至少需要一个约束")
        self._operators = list(operators)
        self._constraints = list(constraints)
        self._rng = random.Random(seed)

    def generate(self, max_attempts: int = 200) -> Problem:
        for _ in range(max_attempts):
            operator = self._rng.choice(self._operators)
            num1, num2 = self._generate_operands(operator)
            problem = Problem(num1=num1, num2=num2, operator=operator)
            try:
                problem.validate(self._constraints)
                return problem
            except ValueError:
                continue
        raise RuntimeError(f"在 {max_attempts} 次尝试中无法生成合法题目。")

    def generate_many(self, count: int, unique: bool = True) -> List[Problem]:
        if not unique:
            return [self.generate() for _ in range(count)]
        max_attempts = count * 200
        seen = set()
        attempts = 0
        while len(seen) < count:
            if attempts >= max_attempts:
                raise RuntimeError(
                    f"在 {max_attempts} 次尝试中无法生成 {count} 道不重复题目。"
                    f"已生成 {len(seen)} 道。")
            seen.add(self.generate())
            attempts += 1
        return list(seen)

    def _generate_operands(self, operator: Operator) -> tuple:
        if operator.symbol == "+":
            a = self._rng.randint(0, 100)
            b = self._rng.randint(0, 100 - a)
        else:
            a = self._rng.randint(0, 100)
            b = self._rng.randint(0, a)
        return a, b
