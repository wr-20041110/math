"""
ExerciseBuilder 单元测试 —— 表驱动编程。

覆盖：
  - 三种习题类型构建
  - 表驱动查表逻辑
  - 唯一 ID 生成
  - 无效类型拒绝
"""

import pytest
from src.exercise_builder import ExerciseBuilder, EXERCISE_TYPES
from src.problem import Problem


class TestExerciseBuilder:
    """表驱动习题构建测试。"""

    def test_build_addition(self):
        ex = ExerciseBuilder.build("addition", count=10, seed=42)
        assert ex.exercise_type == "addition"
        assert ex.total == 10
        for p in ex.problems:
            assert p.operator.symbol == "+"
            assert p.answer <= 100

    def test_build_subtraction(self):
        ex = ExerciseBuilder.build("subtraction", count=10, seed=42)
        assert ex.exercise_type == "subtraction"
        assert ex.total == 10
        for p in ex.problems:
            assert p.operator.symbol == "-"
            assert p.answer >= 0

    def test_build_mixed(self):
        ex = ExerciseBuilder.build("mixed", count=20, seed=42)
        assert ex.exercise_type == "mixed"
        assert ex.total == 20
        ops = {p.operator.symbol for p in ex.problems}
        assert "+" in ops
        assert "-" in ops

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="无效的习题类型"):
            ExerciseBuilder.build("multiplication", count=10)

    def test_unique_ids(self):
        """每次构建应生成不同的 ID。"""
        ex1 = ExerciseBuilder.build("mixed", count=5, seed=1)
        ex2 = ExerciseBuilder.build("mixed", count=5, seed=2)
        assert ex1.exercise_id != ex2.exercise_id

    def test_id_format(self):
        ex = ExerciseBuilder.build("addition", count=5, seed=42)
        # ID 格式：EX-YYYYMMDD-add-NNN
        assert ex.exercise_id.startswith("EX-")
        assert "-add-" in ex.exercise_id

    def test_all_problems_unique(self):
        ex = ExerciseBuilder.build("mixed", count=30, seed=42)
        ids = {(p.num1, p.num2, p.operator.symbol) for p in ex.problems}
        assert len(ids) == 30

    def test_list_types(self):
        types = ExerciseBuilder.list_types()
        assert len(types) == 3
        type_names = {t["type"] for t in types}
        assert type_names == {"addition", "subtraction", "mixed"}

    def test_table_driven_config(self):
        """验证配置表完整性：每个类型都有 label, operators, constraints。"""
        for ex_type, config in EXERCISE_TYPES.items():
            assert "label" in config, f"{ex_type} 缺少 label"
            assert "operators" in config, f"{ex_type} 缺少 operators"
            assert "constraints" in config, f"{ex_type} 缺少 constraints"
            assert len(config["operators"]) > 0
            assert len(config["constraints"]) > 0
