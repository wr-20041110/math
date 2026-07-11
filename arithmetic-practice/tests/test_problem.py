"""
Problem 类的单元测试。

覆盖：
  - 创建合法题目
  - 非法运算符拒绝
  - 非法操作数拒绝
  - 加法结果 > 100 拒绝（故事2）
  - 减法结果 < 0 拒绝（故事2）
  - 相等性与哈希（故事3 去重基础）
  - answer 属性正确性
  - __str__ 输出格式
"""

import pytest
from src.problem import Problem


class TestProblemCreation:
    """测试 Problem 创建。"""

    def test_valid_addition(self):
        p = Problem(num1=30, num2=50, operator="+")
        assert p.num1 == 30
        assert p.num2 == 50
        assert p.operator == "+"

    def test_valid_subtraction(self):
        p = Problem(num1=80, num2=20, operator="-")
        assert p.num1 == 80
        assert p.num2 == 20
        assert p.operator == "-"

    def test_boundary_addition_sum_exactly_100(self):
        """加法结果刚好 100 是合法的。"""
        p = Problem(num1=60, num2=40, operator="+")
        assert p.answer == 100

    def test_boundary_subtraction_diff_exactly_0(self):
        """减法结果刚好 0 是合法的。"""
        p = Problem(num1=50, num2=50, operator="-")
        assert p.answer == 0

    def test_boundary_zero_operands(self):
        """操作数为 0 是合法的。"""
        p = Problem(num1=0, num2=0, operator="+")
        assert p.answer == 0

    def test_boundary_100_operands(self):
        p = Problem(num1=100, num2=0, operator="-")
        assert p.answer == 100


class TestProblemValidation:
    """测试 Problem 校验逻辑（故事2 约束）。"""

    def test_invalid_operator_raises(self):
        with pytest.raises(ValueError, match="运算符"):
            Problem(num1=10, num2=5, operator="*")

    def test_num1_out_of_range_raises(self):
        with pytest.raises(ValueError, match="num1"):
            Problem(num1=150, num2=10, operator="+")

    def test_num2_out_of_range_raises(self):
        with pytest.raises(ValueError, match="num2"):
            Problem(num1=10, num2=150, operator="+")

    def test_addition_exceeds_100_raises(self):
        """故事2：加法结果不能超过 100。"""
        with pytest.raises(ValueError, match="加法结果不能超过 100"):
            Problem(num1=80, num2=30, operator="+")

    def test_subtraction_negative_raises(self):
        """故事2：减法结果不能为负数。"""
        with pytest.raises(ValueError, match="减法结果不能为负数"):
            Problem(num1=5, num2=10, operator="-")


class TestProblemAnswer:
    """测试 answer 属性。"""

    def test_addition_answer(self):
        p = Problem(num1=23, num2=44, operator="+")
        assert p.answer == 67

    def test_subtraction_answer(self):
        p = Problem(num1=88, num2=21, operator="-")
        assert p.answer == 67


class TestProblemEquality:
    """测试相等性与哈希（故事3 去重基础）。"""

    def test_same_problems_equal(self):
        p1 = Problem(num1=44, num2=23, operator="+")
        p2 = Problem(num1=44, num2=23, operator="+")
        assert p1 == p2
        assert hash(p1) == hash(p2)

    def test_different_num1_not_equal(self):
        p1 = Problem(num1=44, num2=23, operator="+")
        p2 = Problem(num1=45, num2=23, operator="+")
        assert p1 != p2

    def test_different_operator_not_equal(self):
        p1 = Problem(num1=44, num2=23, operator="+")
        p2 = Problem(num1=44, num2=23, operator="-")
        assert p1 != p2

    def test_commutative_not_equal(self):
        """故事3 明确：32+22 和 22+32 应被视为不同题目，不能出现在同一套题中。"""
        p1 = Problem(num1=32, num2=22, operator="+")
        p2 = Problem(num1=22, num2=32, operator="+")
        # 它们不相等，所以都会被加入 set → 去重不会漏掉
        assert p1 != p2

    def test_set_deduplication(self):
        """相同题目加入 set 只保留一个。"""
        p1 = Problem(num1=44, num2=23, operator="+")
        p2 = Problem(num1=44, num2=23, operator="+")
        s = {p1, p2}
        assert len(s) == 1

    def test_set_commutative_both_kept(self):
        """故事3 场景：32+22 和 22+32 都在 set 中（不同题目）。"""
        p1 = Problem(num1=32, num2=22, operator="+")
        p2 = Problem(num1=22, num2=32, operator="+")
        s = {p1, p2}
        assert len(s) == 2


class TestProblemStr:
    """测试字符串输出格式。"""

    def test_addition_str(self):
        p = Problem(num1=48, num2=7, operator="+")
        assert str(p) == "48+7="

    def test_subtraction_str(self):
        p = Problem(num1=88, num2=21, operator="-")
        assert str(p) == "88-21="
