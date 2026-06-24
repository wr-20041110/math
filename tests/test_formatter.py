"""
Formatter 类的单元测试。

覆盖：
  - 默认 5 列输出
  - 自定义列数
  - 显示 / 不显示答案
  - 边界：空列表、单行
  - 输入校验
"""

import pytest
from src.formatter import Formatter
from src.problem import Problem


def make_problems(*pairs):
    """快捷构造 Problem 列表。

    pairs 中每个元素为 (num1, num2, operator)。
    """
    return [Problem(num1=a, num2=b, operator=op) for a, b, op in pairs]


class TestFormatterBase:
    """测试基础格式化。"""

    def test_default_5_cols(self):
        """默认每行 5 列。"""
        problems = make_problems(
            (1, 2, "+"), (8, 4, "-"), (5, 6, "+"),
            (9, 2, "-"), (9, 10, "+"), (22, 11, "-"),
        )
        fmt = Formatter()
        result = fmt.format(problems)
        lines = result.split("\n")
        assert len(lines) == 2  # 6 题 → 第 1 行 5 题，第 2 行 1 题
        assert "1+2=" in lines[0]
        assert "22-11=" in lines[1]

    def test_custom_cols(self):
        problems = make_problems((1, 2, "+"), (8, 4, "-"), (5, 6, "+"))
        fmt = Formatter(cols=2)
        result = fmt.format(problems)
        lines = result.split("\n")
        assert len(lines) == 2  # 3 题 → 2 + 1

    def test_empty_list(self):
        fmt = Formatter()
        result = fmt.format([])
        assert result == ""

    def test_single_problem(self):
        problems = make_problems((48, 7, "+"))
        fmt = Formatter(cols=5)
        result = fmt.format(problems)
        assert result == "48+7="
        assert "\n" not in result


class TestFormatterWithAnswers:
    """测试显示答案模式（故事2）。"""

    def test_show_answers(self):
        problems = make_problems((48, 7, "+"), (32, 22, "+"))
        fmt = Formatter(cols=2, show_answer=True)
        result = fmt.format(problems)
        assert "48+7=55" in result
        assert "32+22=54" in result

    def test_no_answers(self):
        problems = make_problems((48, 7, "+"),)
        fmt = Formatter(cols=1, show_answer=False)
        result = fmt.format(problems)
        assert "48+7=" in result
        assert "55" not in result


class TestFormatterValidation:
    """测试输入校验。"""

    def test_zero_cols_raises(self):
        with pytest.raises(ValueError):
            Formatter(cols=0)

    def test_negative_cols_raises(self):
        with pytest.raises(ValueError):
            Formatter(cols=-1)
