"""
Config —— 集中配置管理（引入参数对象重构）。

重构前: 参数散落在各模块的构造函数中（seed, total, cols, data_dir...）
重构后: 统一 Config 对象，一处定义、全局使用。

重构方法: Introduce Parameter Object
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


# ---------------------------------------------------------------------------
# 常量提取 —— Replace Magic Numbers with Named Constants
# ---------------------------------------------------------------------------

DEFAULT_OPERAND_MIN = 0
DEFAULT_OPERAND_MAX = 100
DEFAULT_SUM_LIMIT = 100
DEFAULT_DIFF_MIN = 0
DEFAULT_EXERCISE_COUNT = 50
DEFAULT_DISPLAY_COLS = 5
DEFAULT_GENERATE_MAX_ATTEMPTS = 200


@dataclass
class Config:
    """应用配置对象。

    集中管理所有可配置参数，替代分散的构造函数参数。
    支持从字典构造，便于从配置文件/命令行加载。
    """

    # ---- 习题生成 ----
    exercise_count: int = DEFAULT_EXERCISE_COUNT
    exercise_types: List[str] = field(default_factory=lambda: ["addition", "subtraction", "mixed"])
    seed: Optional[int] = None
    max_generate_attempts: int = DEFAULT_GENERATE_MAX_ATTEMPTS

    # ---- 操作数/约束 ----
    operand_min: int = DEFAULT_OPERAND_MIN
    operand_max: int = DEFAULT_OPERAND_MAX
    sum_limit: int = DEFAULT_SUM_LIMIT

    # ---- 显示 ----
    display_cols: int = DEFAULT_DISPLAY_COLS
    show_answers: bool = False

    # ---- 数据存储 ----
    data_dir: str = "data"

    # ---- 日志 ----
    log_level: str = "INFO"

    # ------------------------------------------------------------------
    # 工厂方法
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: dict) -> "Config":
        """从字典构造（用于 CLI 参数解析）。"""
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in d.items() if k in valid_keys}
        return cls(**filtered)

    @property
    def data_path(self) -> Path:
        return Path(self.data_dir)

    @property
    def exercise_dir(self) -> Path:
        return self.data_path / "exercises"

    @property
    def answer_dir(self) -> Path:
        return self.data_path / "answers"

    @property
    def score_dir(self) -> Path:
        return self.data_path / "scores"

    @property
    def analysis_dir(self) -> Path:
        return self.data_path / "analysis"
