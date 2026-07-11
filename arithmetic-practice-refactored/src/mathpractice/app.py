"""
Application —— 应用外观（重构：Rename Class + 使用 Config + Repository）。

重构前: PracticeManager
重构后: Application（语义更清晰）+ 依赖注入 Repository 和 Config
"""

import logging
from typing import Dict, List, Optional, Tuple

from .config import Config
from .core.problem import Problem
from .models.exercise import Exercise
from .models.answer import AnswerSheet
from .models.score import Score
from .services.grader import Grader
from .services.analyzer import Analyzer
from .services.reporter import Reporter
from .services.exercise_builder import ExerciseBuilder
from .io.repository import ExerciseRepository

logger = logging.getLogger(__name__)


class Application:
    """口算练习系统应用外观。

    重构变更:
      - 类名 PracticeManager → Application
      - 接收 Config 对象（依赖注入）
      - 使用 Repository 管理数据持久化
      - 引入 Reporter 处理输出格式化
    """

    def __init__(self, config: Optional[Config] = None):
        self.cfg = config or Config()
        self._repo = ExerciseRepository(data_dir=self.cfg.data_dir)
        self._grader = Grader()
        self._analyzer = Analyzer()
        self._reporter = Reporter()

        # 配置日志
        logging.basicConfig(
            level=getattr(logging, self.cfg.log_level.upper(), logging.INFO),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

    # ------------------------------------------------------------------
    # 习题生成
    # ------------------------------------------------------------------

    def generate_exercise(
        self, exercise_type: str = "mixed", count: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> Tuple[Exercise, str]:
        """生成习题并保存。"""
        count = count or self.cfg.exercise_count
        seed = seed if seed is not None else self.cfg.seed

        exercise = ExerciseBuilder.build(
            exercise_type=exercise_type, count=count, seed=seed,
        )
        path = self._repo.save_exercise(exercise)
        return exercise, path

    # ------------------------------------------------------------------
    # 判题打分
    # ------------------------------------------------------------------

    def grade_from_file(self, answer_csv_path: str) -> Score:
        """从 CSV 文件加载答案并判题。"""
        answer_sheet = self._repo.load_answers(answer_csv_path)
        exercise = self._repo.find_exercise(answer_sheet.exercise_id)
        score = self._grader.evaluate(exercise, answer_sheet)
        self._repo.save_scores([score])
        self._analyzer.add_scores([score])
        return score

    def grade_from_dict(
        self, exercise_id: str, student: str, answers: Dict[int, int]
    ) -> Score:
        """从 dict 直接判题（无需 CSV）。"""
        exercise = self._repo.find_exercise(exercise_id)
        answer_sheet = AnswerSheet(
            exercise_id=exercise_id, student=student, answers=answers,
        )
        score = self._grader.evaluate(exercise, answer_sheet)
        self._repo.save_scores([score])
        self._analyzer.add_scores([score])
        return score

    # ------------------------------------------------------------------
    # 分析
    # ------------------------------------------------------------------

    def analyze(self) -> dict:
        """分析成绩，返回摘要和弱项。"""
        return {
            "summary": self._analyzer.summarize(),
            "weak_problems": self._analyzer.identify_weak_areas(
                self._repo.cached_exercises()
            ),
        }

    def generate_targeted_practice(
        self, count: Optional[int] = None, seed: Optional[int] = None,
    ) -> Exercise:
        """生成针对性练习。"""
        count = count or self.cfg.exercise_count
        seed = seed if seed is not None else self.cfg.seed

        problems = self._analyzer.build_targeted_practice(
            self._repo.cached_exercises(), count=count, seed=seed,
        )
        exercise = Exercise(
            exercise_id=f"EX-TARGETED-{len(self._repo.cached_exercises()) + 1:03d}",
            exercise_type="targeted",
            problems=problems,
        )
        self._repo.save_exercise(exercise)
        return exercise

    def load_history(self) -> List[Score]:
        """加载历史成绩。"""
        scores = self._repo.load_scores()
        self._analyzer.add_scores(scores)
        return scores

    # ------------------------------------------------------------------
    # 输出
    # ------------------------------------------------------------------

    @property
    def reporter(self) -> Reporter:
        return self._reporter
