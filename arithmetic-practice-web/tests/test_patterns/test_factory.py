"""工厂方法模式单元测试。"""
import pytest
from core.operators import Addition, Subtraction
from patterns.factory import (
    GeneratorFactory,
    AdditionGeneratorFactory,
    SubtractionGeneratorFactory,
    MixedGeneratorFactory,
    TargetedGeneratorFactory,
    FACTORY_REGISTRY,
    get_factory,
    registered_types,
)


class TestAdditionGeneratorFactory:
    def test_creates_generator(self):
        factory = AdditionGeneratorFactory()
        gen = factory.create_generator(seed=42)
        assert gen is not None

    def test_generates_only_addition(self):
        factory = AdditionGeneratorFactory()
        gen = factory.create_generator(seed=42)
        problems = gen.generate_unique(20)
        for p in problems:
            assert p.operator.symbol == "+"

    def test_factory_name(self):
        factory = AdditionGeneratorFactory()
        assert "加法" in factory.factory_name

    def test_exercise_type(self):
        factory = AdditionGeneratorFactory()
        assert factory.exercise_type == "addition"


class TestSubtractionGeneratorFactory:
    def test_generates_only_subtraction(self):
        factory = SubtractionGeneratorFactory()
        gen = factory.create_generator(seed=42)
        problems = gen.generate_unique(20)
        for p in problems:
            assert p.operator.symbol == "-"

    def test_exercise_type(self):
        factory = SubtractionGeneratorFactory()
        assert factory.exercise_type == "subtraction"


class TestMixedGeneratorFactory:
    def test_generates_both_operators(self):
        factory = MixedGeneratorFactory()
        gen = factory.create_generator(seed=42)
        problems = gen.generate_unique(50)
        symbols = {p.operator.symbol for p in problems}
        assert "+" in symbols
        assert "-" in symbols

    def test_exercise_type(self):
        assert MixedGeneratorFactory().exercise_type == "mixed"


class TestTargetedGeneratorFactory:
    def test_creates_with_specific_operators(self):
        factory = TargetedGeneratorFactory([Addition()])
        gen = factory.create_generator(seed=42)
        problems = gen.generate_unique(10)
        for p in problems:
            assert p.operator.symbol == "+"

    def test_rejects_empty_operators(self):
        with pytest.raises(ValueError):
            TargetedGeneratorFactory([])


class TestFactoryRegistry:
    def test_registry_has_all_types(self):
        types = registered_types()
        assert "addition" in types
        assert "subtraction" in types
        assert "mixed" in types

    def test_get_factory_returns_correct_type(self):
        factory = get_factory("addition")
        assert isinstance(factory, AdditionGeneratorFactory)

        factory = get_factory("mixed")
        assert isinstance(factory, MixedGeneratorFactory)

    def test_get_factory_unknown_type(self):
        with pytest.raises(ValueError, match="未知"):
            get_factory("multiplication")

    def test_all_factories_create_valid_generators(self):
        for ex_type in registered_types():
            factory = get_factory(ex_type)
            gen = factory.create_generator(seed=42)
            problems = gen.generate_unique(10)
            assert len(problems) == 10
