"""
DisplayStrategy 抽象基类及其子类的单元测试。

覆盖：
  - 策略模式：运行时替换显示策略
  - OCP：新增显示格式只需添加子类
  - SRP：每个策略只负责一种显示格式
  - 多态：通过 DisplayStrategy 接口操作不同显示策略
"""

import pytest
from src.display import DisplayStrategy, GridDisplay, AnswerDisplay
from src.problem import Problem
from src.operators import Addition, Subtraction


def make_add(a: int, b: int) -> Problem:
    return Problem(num1=a, num2=b, operator=Addition())


def make_sub(a: int, b: int) -> Problem:
    return Problem(num1=a, num2=b, operator=Subtraction())


def test_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        DisplayStrategy()  # type: ignore[abstract]


class TestGridDisplay:
    """无答案网格显示。"""

    def test_single_row(self):
        problems = [make_add(1, 2), make_sub(5, 3)]
        d = GridDisplay(cols=2)
        output = d.display(problems)
        assert "1+2=" in output
        assert "5-3=" in output

    def test_multi_row(self):
        problems = [make_add(1, 2)] * 6
        d = GridDisplay(cols=3)
        output = d.display(problems)
        assert len(output.split("\n")) == 2

    def test_empty_list(self):
        d = GridDisplay()
        assert d.display([]) == ""

    def test_default_cols(self):
        d = GridDisplay()
        assert d.cols == 5

    def test_invalid_cols(self):
        with pytest.raises(ValueError):
            GridDisplay(cols=0)

    def test_repr(self):
        d = GridDisplay(cols=3)
        assert "3" in repr(d)


class TestAnswerDisplay:
    """带答案显示。"""

    def test_shows_answers(self):
        problems = [make_add(48, 7), make_add(32, 22)]
        d = AnswerDisplay(cols=2)
        output = d.display(problems)
        assert "48+7=55" in output
        assert "32+22=54" in output

    def test_does_not_show_answer_in_grid(self):
        """对比：GridDisplay 不含答案。"""
        problems = [make_add(48, 7)]
        g = GridDisplay()
        a = AnswerDisplay()
        assert "55" not in g.display(problems)
        assert "55" in a.display(problems)

    def test_multi_row_with_answers(self):
        problems = [make_add(i, i) for i in range(6)]
        d = AnswerDisplay(cols=3)
        output = d.display(problems)
        assert len(output.split("\n")) == 2

    def test_default_cols(self):
        d = AnswerDisplay()
        assert d.cols == 5

    def test_invalid_cols(self):
        with pytest.raises(ValueError):
            AnswerDisplay(cols=-1)

    def test_repr(self):
        d = AnswerDisplay(cols=4)
        assert "4" in repr(d)


class TestStrategyPattern:
    """策略模式验证：运行时替换显示策略。"""

    def test_runtime_swap(self):
        problems = [make_add(10, 5)]

        strategy: DisplayStrategy = GridDisplay()
        out1 = strategy.display(problems)
        assert "15" not in out1  # 无答案

        strategy = AnswerDisplay()
        out2 = strategy.display(problems)
        assert "15" in out2  # 有答案

    def test_polymorphic_interface(self):
        """通过 DisplayStrategy 抽象接口操作不同显示策略。"""

        def render(ds: DisplayStrategy, problems: list[Problem]) -> str:
            return ds.display(problems)

        problems = [make_add(1, 2)]
        assert render(GridDisplay(), problems) == "1+2="
        assert "3" in render(AnswerDisplay(), problems)
