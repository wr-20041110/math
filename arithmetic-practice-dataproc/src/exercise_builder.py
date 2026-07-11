"""
ExerciseBuilder —— 习题构建器（表驱动编程）。

核心设计：
  使用配置表 EXERCISE_TYPES 定义习题类型 → 运算符/约束的映射。
  新增习题类型只需在表中添加一行，无需修改代码逻辑。

这是表驱动编程（Table-Driven Programming）的典型应用：
  用数据表替代条件分支，提高可扩展性和可读性。
"""

from datetime import datetime
from typing import Dict, List, Optional

from .operators import Operator, Addition, Subtraction
from .constraints import Constraint, OperandRangeConstraint, SumLimitConstraint, NonNegativeDiffConstraint
from .generator import ProblemGenerator
from .models import Exercise

# =========================================================================
# 习题类型配置表 —— 表驱动编程核心
# =========================================================================
# 新增习题类型只需在此表中添加一行，无需修改任何其他代码。

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
    """习题构建器。

    使用表驱动方式，根据类型名查表获取配置，构建习题。
    """

    # 计数器 —— 生成唯一 ID
    _counter: Dict[str, int] = {}

    @classmethod
    def build(
        cls,
        exercise_type: str,
        count: int = 50,
        seed: Optional[int] = None,
    ) -> Exercise:
        """构建一份习题集。

        表驱动：查 EXERCISE_TYPES 获取运算符和约束配置。

        Args:
            exercise_type: 习题类型 ('addition' | 'subtraction' | 'mixed')。
            count: 题目数量。
            seed: 随机种子。

        Returns:
            Exercise 实例。

        Raises:
            ValueError: 无效的习题类型。
        """
        config = EXERCISE_TYPES.get(exercise_type)
        if config is None:
            valid = list(EXERCISE_TYPES.keys())
            raise ValueError(
                f"无效的习题类型 '{exercise_type}'。支持: {valid}"
            )

        # 从配置表取参数
        operators: List[Operator] = config["operators"]
        constraints: List[Constraint] = config["constraints"]

        # 生成题目
        generator = ProblemGenerator(
            operators=operators,
            constraints=constraints,
            seed=seed,
        )
        problems = generator.generate_many(count, unique=True)

        # 生成唯一 ID
        cls._counter[exercise_type] = cls._counter.get(exercise_type, 0) + 1
        date_str = datetime.now().strftime("%Y%m%d")
        seq = cls._counter[exercise_type]
        exercise_id = f"EX-{date_str}-{exercise_type[:3]}-{seq:03d}"

        return Exercise(
            exercise_id=exercise_id,
            exercise_type=exercise_type,
            problems=problems,
            created_at=datetime.now(),
        )

    @classmethod
    def list_types(cls) -> List[Dict[str, str]]:
        """列出所有习题类型及其说明。"""
        return [
            {"type": key, "label": val["label"]}
            for key, val in EXERCISE_TYPES.items()
        ]
