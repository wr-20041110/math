"""
ProblemCollection 与 ProblemIterator 的单元测试。

覆盖：
  - 迭代器模式：Collection 不自己遍历，委托给 Iterator
  - 过滤迭代：iter_filtered()
  - 集合操作：add、extend、__len__、__contains__、__getitem__
  - StopIteration：遍历结束正确抛出
"""

import pytest
from src.collection import ProblemCollection, ProblemIterator
from src.problem import Problem
from src.operators import Addition, Subtraction


def make_add(a: int, b: int) -> Problem:
    return Problem(num1=a, num2=b, operator=Addition())


def make_sub(a: int, b: int) -> Problem:
    return Problem(num1=a, num2=b, operator=Subtraction())


class TestProblemCollection:
    """测试集合操作。"""

    def test_empty_collection(self):
        c = ProblemCollection()
        assert len(c) == 0
        assert list(c) == []

    def test_add_and_len(self):
        c = ProblemCollection()
        c.add(make_add(1, 2))
        c.add(make_sub(5, 3))
        assert len(c) == 2

    def test_extend(self):
        c = ProblemCollection()
        c.extend([make_add(1, 2), make_sub(5, 3), make_add(10, 20)])
        assert len(c) == 3

    def test_contains(self):
        p = make_add(44, 23)
        c = ProblemCollection([p])
        assert p in c
        assert make_add(99, 99) not in c

    def test_getitem(self):
        p1, p2 = make_add(1, 2), make_sub(5, 3)
        c = ProblemCollection([p1, p2])
        assert c[0] == p1
        assert c[1] == p2

    def test_getitem_out_of_range(self):
        c = ProblemCollection([make_add(1, 2)])
        with pytest.raises(IndexError):
            _ = c[5]

    def test_constructor_with_list(self):
        problems = [make_add(1, 2), make_sub(5, 3)]
        c = ProblemCollection(problems)
        assert len(c) == 2


class TestIteratorBasic:
    """测试基本迭代器行为。"""

    def test_iteration_yields_all(self):
        p1, p2, p3 = make_add(1, 2), make_sub(5, 3), make_add(10, 20)
        c = ProblemCollection([p1, p2, p3])
        items = list(c)
        assert items == [p1, p2, p3]

    def test_empty_iterator(self):
        it = ProblemIterator([])
        with pytest.raises(StopIteration):
            next(it)

    def test_iterator_is_self_iterable(self):
        """迭代器满足 __iter__ → self 协议。"""
        p1 = make_add(1, 2)
        it = ProblemIterator([p1])
        assert iter(it) is it

    def test_stop_iteration(self):
        it = ProblemIterator([make_add(1, 2)])
        _ = next(it)
        with pytest.raises(StopIteration):
            next(it)


class TestFilteredIterator:
    """测试过滤迭代器（OCP：扩展遍历行为无需修改类）。"""

    def test_filter_addition_only(self):
        p1, p2, p3 = make_add(1, 2), make_sub(5, 3), make_add(10, 20)
        c = ProblemCollection([p1, p2, p3])

        results = list(c.iter_filtered(lambda p: p.operator.symbol == "+"))
        assert results == [p1, p3]
        assert len(results) == 2

    def test_filter_subtraction_only(self):
        p1, p2, p3 = make_add(1, 2), make_sub(5, 3), make_add(10, 20)
        c = ProblemCollection([p1, p2, p3])

        results = list(c.iter_filtered(lambda p: p.operator.symbol == "-"))
        assert results == [p2]

    def test_filter_none_match(self):
        c = ProblemCollection([make_add(1, 2), make_add(3, 4)])
        results = list(c.iter_filtered(lambda p: p.operator.symbol == "-"))
        assert results == []

    def test_filter_answer_range(self):
        p1, p2 = make_add(10, 20), make_add(50, 40)
        c = ProblemCollection([p1, p2])

        results = list(c.iter_filtered(lambda p: p.answer > 50))
        assert results == [p2]

    def test_for_loop_with_filter(self):
        """验证 for 循环与过滤迭代器配合。"""
        p1, p2 = make_add(1, 2), make_sub(10, 3)
        c = ProblemCollection([p1, p2])

        collected = []
        for p in c.iter_filtered(lambda p: p.answer >= 0):
            collected.append(p)
        assert len(collected) == 2
