"""
ProblemGenerator 类的单元测试。

覆盖：
  - 加法题满足 sum ≤ 100（故事2）
  - 减法题满足 diff ≥ 0（故事2）
  - 操作数在 [0, 100] 范围内
  - 随机生成混合加减
  - 种子可重现性
"""

import pytest
from src.generator import ProblemGenerator


class TestGenerateAddition:
    """测试加法题生成。"""

    def test_sum_within_100(self):
        """故事2：加法结果不能超过 100。"""
        gen = ProblemGenerator(seed=42)
        for _ in range(200):
            p = gen.generate_addition()
            assert p.answer <= 100, f"{p.num1} + {p.num2} = {p.answer} > 100"

    def test_operands_in_range(self):
        gen = ProblemGenerator(seed=42)
        for _ in range(200):
            p = gen.generate_addition()
            assert 0 <= p.num1 <= 100
            assert 0 <= p.num2 <= 100

    def test_operator_is_plus(self):
        gen = ProblemGenerator()
        for _ in range(50):
            p = gen.generate_addition()
            assert p.operator == "+"


class TestGenerateSubtraction:
    """测试减法题生成。"""

    def test_diff_not_negative(self):
        """故事2：减法结果不能小于 0。"""
        gen = ProblemGenerator(seed=42)
        for _ in range(200):
            p = gen.generate_subtraction()
            assert p.answer >= 0, f"{p.num1} - {p.num2} = {p.answer} < 0"

    def test_operands_in_range(self):
        gen = ProblemGenerator(seed=42)
        for _ in range(200):
            p = gen.generate_subtraction()
            assert 0 <= p.num1 <= 100
            assert 0 <= p.num2 <= 100

    def test_operator_is_minus(self):
        gen = ProblemGenerator()
        for _ in range(50):
            p = gen.generate_subtraction()
            assert p.operator == "-"


class TestGenerateRandom:
    """测试随机生成（故事3：混合加减法）。"""

    def test_produces_both_operators(self):
        """随机生成应该同时包含加法和减法。"""
        gen = ProblemGenerator(seed=42)
        ops = set()
        for _ in range(100):
            p = gen.generate_random()
            ops.add(p.operator)
        assert "+" in ops
        assert "-" in ops

    def test_all_valid(self):
        """所有随机生成的题目都应满足约束。"""
        gen = ProblemGenerator()
        for _ in range(200):
            p = gen.generate_random()
            assert 0 <= p.num1 <= 100
            assert 0 <= p.num2 <= 100
            assert p.operator in ("+", "-")
            assert p.answer <= 100
            assert p.answer >= 0


class TestSeedReproducibility:
    """测试随机种子可重现性。"""

    def test_same_seed_same_sequence(self):
        gen1 = ProblemGenerator(seed=123)
        gen2 = ProblemGenerator(seed=123)
        for _ in range(50):
            p1 = gen1.generate_random()
            p2 = gen2.generate_random()
            assert p1 == p2

    def test_different_seed_different_sequence(self):
        gen1 = ProblemGenerator(seed=1)
        gen2 = ProblemGenerator(seed=2)
        results1 = [gen1.generate_random() for _ in range(20)]
        results2 = [gen2.generate_random() for _ in range(20)]
        # 极大概率下不同种子产生不同序列
        assert results1 != results2
