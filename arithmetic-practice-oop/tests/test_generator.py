"""
ProblemGenerator 类的单元测试。

覆盖 OOP 原则：
  - DIP（依赖倒转）：Generator 依赖 Operator/Constraint 抽象
  - 策略模式：运行时通过组合不同的 Operator 和 Constraint 策略改变行为
  - OCP：新增运算符/约束不需修改 Generator
"""

import pytest
from src.generator import ProblemGenerator
from src.operators import Addition, Subtraction
from src.constraints import (
    OperandRangeConstraint,
    SumLimitConstraint,
    NonNegativeDiffConstraint,
)
from src.problem import Problem


DEFAULT_OPS = [Addition(), Subtraction()]
DEFAULT_CONS = [
    OperandRangeConstraint(0, 100),
    SumLimitConstraint(100),
    NonNegativeDiffConstraint(),
]


class TestGeneratorCreation:
    """测试 Generator 构造。"""

    def test_valid_creation(self):
        gen = ProblemGenerator(DEFAULT_OPS, DEFAULT_CONS)
        assert gen is not None

    def test_empty_operators_raises(self):
        with pytest.raises(ValueError, match="运算符"):
            ProblemGenerator([], DEFAULT_CONS)

    def test_empty_constraints_raises(self):
        with pytest.raises(ValueError, match="约束"):
            ProblemGenerator(DEFAULT_OPS, [])

    def test_seed_reproducibility(self):
        gen1 = ProblemGenerator(DEFAULT_OPS, DEFAULT_CONS, seed=42)
        gen2 = ProblemGenerator(DEFAULT_OPS, DEFAULT_CONS, seed=42)
        for _ in range(20):
            assert gen1.generate() == gen2.generate()


class TestGenerate:
    """测试单题生成。"""

    def test_generates_valid_problem(self):
        gen = ProblemGenerator(DEFAULT_OPS, DEFAULT_CONS, seed=42)
        p = gen.generate()
        assert isinstance(p, Problem)
        assert p.operator is not None

    def test_all_satisfy_constraints(self):
        gen = ProblemGenerator(DEFAULT_OPS, DEFAULT_CONS, seed=42)
        for _ in range(100):
            p = gen.generate()
            # 操作数范围
            assert 0 <= p.num1 <= 100
            assert 0 <= p.num2 <= 100
            # 加法约束
            if p.operator.symbol == "+":
                assert p.answer <= 100
            # 减法约束
            if p.operator.symbol == "-":
                assert p.answer >= 0

    def test_produces_both_operators(self):
        """随机生成应同时包含加法和减法。"""
        gen = ProblemGenerator(DEFAULT_OPS, DEFAULT_CONS, seed=42)
        ops = set()
        for _ in range(100):
            ops.add(gen.generate().operator.symbol)
        assert "+" in ops
        assert "-" in ops


class TestGenerateMany:
    """测试批量生成。"""

    def test_generates_correct_count(self):
        gen = ProblemGenerator(DEFAULT_OPS, DEFAULT_CONS, seed=42)
        problems = gen.generate_many(50)
        assert len(problems) == 50

    def test_all_unique(self):
        """故事3：去重。"""
        gen = ProblemGenerator(DEFAULT_OPS, DEFAULT_CONS, seed=42)
        problems = gen.generate_many(50, unique=True)
        ids = {(p.num1, p.num2, p.operator.symbol) for p in problems}
        assert len(ids) == 50

    def test_no_dedup_when_unique_false(self):
        gen = ProblemGenerator(DEFAULT_OPS, DEFAULT_CONS, seed=42)
        problems = gen.generate_many(50, unique=False)
        assert len(problems) == 50

    def test_generate_zero(self):
        gen = ProblemGenerator(DEFAULT_OPS, DEFAULT_CONS, seed=42)
        problems = gen.generate_many(0)
        assert problems == []

    def test_raises_on_impossible_count(self):
        gen = ProblemGenerator(DEFAULT_OPS, DEFAULT_CONS, seed=42)
        with pytest.raises(RuntimeError, match="无法生成"):
            gen.generate_many(100000, unique=True)


class TestDIP:
    """依赖倒转原则验证。"""

    def test_addition_only_strategy(self):
        """只使用 Addition 运算符策略。"""
        gen = ProblemGenerator(
            operators=[Addition()],
            constraints=[SumLimitConstraint(100), OperandRangeConstraint(0, 100)],
        )
        for _ in range(50):
            p = gen.generate()
            assert p.operator.symbol == "+"

    def test_subtraction_only_strategy(self):
        """只使用 Subtraction 运算符策略。"""
        gen = ProblemGenerator(
            operators=[Subtraction()],
            constraints=[NonNegativeDiffConstraint(), OperandRangeConstraint(0, 100)],
        )
        for _ in range(50):
            p = gen.generate()
            assert p.operator.symbol == "-"

    def test_custom_constraint_composition(self):
        """可组合自定义约束 —— OCP 体现。"""

        class EvenResultConstraint:
            """自定义约束：结果必须为偶数（扩展，不修改已有代码）。"""
            description = "结果必须为偶数"

            def check(self, p: Problem) -> bool:
                return p.answer % 2 == 0

        gen = ProblemGenerator(
            operators=[Addition()],
            constraints=[
                OperandRangeConstraint(0, 100),
                SumLimitConstraint(100),
                EvenResultConstraint(),
            ],
            seed=42,
        )
        for _ in range(20):
            p = gen.generate()
            assert p.answer % 2 == 0
