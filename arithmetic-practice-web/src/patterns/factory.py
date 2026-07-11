"""
工厂方法模式 —— 习题生成器工厂体系。

设计意图：
  - 将习题生成器的创建逻辑从客户端代码中分离
  - 每个具体工厂封装一种习题类型的创建策略
  - 遵循 OCP：新增习题类型只需添加新工厂子类

模式结构：
  GeneratorFactory (抽象工厂)
      ├── AdditionGeneratorFactory     —— 加法专用
      ├── SubtractionGeneratorFactory  —— 减法专用
      ├── MixedGeneratorFactory        —— 混合加减
      └── TargetedGeneratorFactory     —— 针对性练习

与现有 ExerciseBuilder（表驱动简单工厂）比较：
  - ExerciseBuilder：通过 EXERCISE_TYPES 字典配置驱动（适合固定类型）
  - GeneratorFactory 体系：通过继承多态（适合需要扩展行为的类型）
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from core.operators import Operator, Addition, Subtraction
from core.constraints import (
    Constraint,
    OperandRangeConstraint,
    SumLimitConstraint,
    NonNegativeDiffConstraint,
)
from core.generator import ProblemGenerator


class GeneratorFactory(ABC):
    """抽象工厂 —— 定义创建 ProblemGenerator 的接口。

    工厂方法模式的核心：将对象的创建延迟到子类。
    """

    @abstractmethod
    def create_generator(self, seed: Optional[int] = None) -> ProblemGenerator:
        """工厂方法：创建 ProblemGenerator 实例。

        Args:
            seed: 随机种子（可选，用于重现）。

        Returns:
            配置好的 ProblemGenerator 实例。
        """
        ...

    @property
    @abstractmethod
    def factory_name(self) -> str:
        """工厂名称（用于显示和日志）。"""
        ...

    @property
    @abstractmethod
    def exercise_type(self) -> str:
        """对应的习题类型标识。"""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class AdditionGeneratorFactory(GeneratorFactory):
    """加法习题生成器工厂。

    创建仅含加法运算符、适配加法约束的生成器。
    """

    def __init__(self, operand_max: int = 100, sum_limit: int = 100):
        self._operand_max = operand_max
        self._sum_limit = sum_limit

    def create_generator(self, seed: Optional[int] = None) -> ProblemGenerator:
        return ProblemGenerator(
            operators=[Addition()],
            constraints=[
                OperandRangeConstraint(0, self._operand_max),
                SumLimitConstraint(self._sum_limit),
            ],
            seed=seed,
        )

    @property
    def factory_name(self) -> str:
        return "加法练习"

    @property
    def exercise_type(self) -> str:
        return "addition"


class SubtractionGeneratorFactory(GeneratorFactory):
    """减法习题生成器工厂。

    创建仅含减法运算符、适配减法约束的生成器。
    """

    def __init__(self, operand_max: int = 100):
        self._operand_max = operand_max

    def create_generator(self, seed: Optional[int] = None) -> ProblemGenerator:
        return ProblemGenerator(
            operators=[Subtraction()],
            constraints=[
                OperandRangeConstraint(0, self._operand_max),
                NonNegativeDiffConstraint(),
            ],
            seed=seed,
        )

    @property
    def factory_name(self) -> str:
        return "减法练习"

    @property
    def exercise_type(self) -> str:
        return "subtraction"


class MixedGeneratorFactory(GeneratorFactory):
    """混合加减习题生成器工厂。

    包含加法和减法运算符及各自的约束。
    """

    def __init__(self, operand_max: int = 100, sum_limit: int = 100):
        self._operand_max = operand_max
        self._sum_limit = sum_limit

    def create_generator(self, seed: Optional[int] = None) -> ProblemGenerator:
        return ProblemGenerator(
            operators=[Addition(), Subtraction()],
            constraints=[
                OperandRangeConstraint(0, self._operand_max),
                SumLimitConstraint(self._sum_limit),
                NonNegativeDiffConstraint(),
            ],
            seed=seed,
        )

    @property
    def factory_name(self) -> str:
        return "混合加减"

    @property
    def exercise_type(self) -> str:
        return "mixed"


class TargetedGeneratorFactory(GeneratorFactory):
    """针对性练习生成器工厂。

    根据弱项分析结果，动态指定目标运算符和约束。
    用于为特定学生生成"补弱"练习。
    """

    def __init__(self, operators: List[Operator],
                 constraints: Optional[List[Constraint]] = None):
        """初始化针对性工厂。

        Args:
            operators: 弱项中涉及的运算符列表。
            constraints: 自定义约束（默认使用标准约束）。
        """
        if not operators:
            raise ValueError("至少需要一个运算符")
        self._operators = list(operators)
        self._constraints = list(constraints) if constraints else [
            OperandRangeConstraint(0, 100),
            SumLimitConstraint(100),
            NonNegativeDiffConstraint(),
        ]

    def create_generator(self, seed: Optional[int] = None) -> ProblemGenerator:
        return ProblemGenerator(
            operators=self._operators,
            constraints=self._constraints,
            seed=seed,
        )

    @property
    def factory_name(self) -> str:
        ops = ",".join(op.symbol for op in self._operators)
        return f"针对性练习({ops})"

    @property
    def exercise_type(self) -> str:
        return "targeted"


# ------------------------------------------------------------------
# 工厂注册表 —— 表驱动 + 工厂方法模式结合
# ------------------------------------------------------------------

# 将工厂实例注册为查表可用（融合表驱动和工厂模式）
FACTORY_REGISTRY: dict = {
    "addition": AdditionGeneratorFactory(),
    "subtraction": SubtractionGeneratorFactory(),
    "mixed": MixedGeneratorFactory(),
}


def get_factory(exercise_type: str) -> GeneratorFactory:
    """根据类型名称获取工厂实例（表驱动查找）。

    Args:
        exercise_type: 习题类型字符串。

    Returns:
        GeneratorFactory 实例。

    Raises:
        ValueError: 未知的习题类型。
    """
    factory = FACTORY_REGISTRY.get(exercise_type)
    if factory is None:
        raise ValueError(
            f"未知的习题类型: '{exercise_type}'。"
            f"支持: {list(FACTORY_REGISTRY.keys())}"
        )
    return factory


def registered_types() -> list:
    """返回已注册的习题类型列表。"""
    return list(FACTORY_REGISTRY.keys())
