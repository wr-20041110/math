"""
ExerciseBuilder —— 习题构建器（表驱动编程）。

重构变更:
  - 使用 Config 对象替代硬编码常量
  - build_from_config() 工厂方法
  - EXERCISE_TYPES 配置表规范化
"""

from datetime import datetime
from typing import Dict, List, Optional

from ..core.operators import Operator, Addition, Subtraction
from ..core.constraints import Constraint, OperandRangeConstraint, SumLimitConstraint, NonNegativeDiffConstraint
from ..core.generator import ProblemGenerator
from ..models.exercise import Exercise
from ..config import Config

# ---------------------------------------------------------------------------
# 习题类型配置表 —— 表驱动编程
# ---------------------------------------------------------------------------

EXERCISE_TYPES: Dict[str, dict] = {
    "addition": {
        "label": "加法练习",
        "operators": [Addition()],
        "constraints": [
            OperandRangeConstraint(0, 100),
            SumLimitConstraint(100),
        ],
    },
    "subtraction": {
        "label": "减法练习",
        "operators": [Subtraction()],
        "constraints": [
            OperandRangeConstraint(0, 100),
            NonNegativeDiffConstraint(),
        ],
    },
    "mixed": {
        "label": "加减混合练习",
        "operators": [Addition(), Subtraction()],
        "constraints": [
            OperandRangeConstraint(0, 100),
            SumLimitConstraint(100),
            NonNegativeDiffConstraint(),
        ],
    },
}


class ExerciseBuilder:
    """习题构建器（表驱动）。"""

    _counter: Dict[str, int] = {}

    @classmethod
    def build(
        cls,
        exercise_type: str,
        count: int = 50,
        seed: Optional[int] = None,
    ) -> Exercise:
        """根据类型构建一份习题集。"""
        config = EXERCISE_TYPES.get(exercise_type)
        if config is None:
            valid = list(EXERCISE_TYPES.keys())
            raise ValueError(f"无效的习题类型 '{exercise_type}'。支持: {valid}")

        operators: List[Operator] = config["operators"]
        constraints: List[Constraint] = config["constraints"]

        generator = ProblemGenerator(operators, constraints, seed=seed)
        problems = generator.generate_unique(count)

        cls._counter[exercise_type] = cls._counter.get(exercise_type, 0) + 1
        date_str = datetime.now().strftime("%Y%m%d")
        seq = cls._counter[exercise_type]
        exercise_id = f"EX-{date_str}-{exercise_type[:3]}-{seq:03d}"

        return Exercise(
            exercise_id=exercise_id,
            exercise_type=exercise_type,
            problems=problems,
        )

    @classmethod
    def build_from_config(cls, cfg: Config, exercise_type: str) -> Exercise:
        """从 Config 对象构建（重构新增工厂方法）。"""
        return cls.build(
            exercise_type=exercise_type,
            count=cfg.exercise_count,
            seed=cfg.seed,
        )

    @classmethod
    def list_types(cls) -> List[Dict[str, str]]:
        return [
            {"type": key, "label": val["label"]}
            for key, val in EXERCISE_TYPES.items()
        ]
