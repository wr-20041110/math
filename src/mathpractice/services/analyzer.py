"""Analyzer —— 成绩分析器（重构：Extract Class —— Reporter 拆分）。"""
import logging
from collections import Counter
from typing import Dict, List, Optional
from ..models.score import Score
from ..models.exercise import Exercise
from ..core.problem import Problem
from ..core.operators import get_operator
from ..core.generator import ProblemGenerator
from ..core.constraints import default_constraints

logger = logging.getLogger(__name__)


class Analyzer:
    """成绩分析器。

    重构变更:
      - 报告生成功能提取到 Reporter 类（SRP）
      - 方法重命名: find_weak_problems → identify_weak_areas
    """

    def __init__(self, scores: Optional[List[Score]] = None):
        self._scores: List[Score] = list(scores) if scores else []

    def add_scores(self, scores: List[Score]) -> None:
        self._scores.extend(scores)

    # ------------------------------------------------------------------
    # 弱项分析
    # ------------------------------------------------------------------

    def identify_weak_areas(
        self,
        exercise_map: Dict[str, Exercise],
        min_error_rate: float = 0.0,
        top_n: int = 10,
    ) -> List[dict]:
        """识别弱项题目。

        Returns:
            按错误次数降序的弱项列表。
        """
        wrong_counter: Counter = Counter()
        attempt_counter: Counter = Counter()

        for score in self._scores:
            ex = exercise_map.get(score.exercise_id)
            if ex is None:
                continue

            for idx in score.wrong_indices:
                try:
                    p = ex.get_problem(idx)
                    key = (p.left, p.operator.symbol, p.right)
                    wrong_counter[key] += 1
                except IndexError:
                    continue

            for p in ex.problems:
                key = (p.left, p.operator.symbol, p.right)
                attempt_counter[key] += 1

        results = []
        for key, wrong in wrong_counter.items():
            attempts = attempt_counter.get(key, wrong)
            rate = wrong / attempts if attempts > 0 else 0.0
            if rate >= min_error_rate:
                left, op_sym, right = key
                op = get_operator(op_sym)
                results.append({
                    "left": left,
                    "operator": op_sym,
                    "right": right,
                    "correct_answer": op.apply(left, right),
                    "wrong_count": wrong,
                    "total_attempts": attempts,
                    "error_rate": round(rate, 2),
                })

        results.sort(key=lambda x: (-x["wrong_count"], -x["error_rate"]))
        return results[:top_n]

    # ------------------------------------------------------------------
    # 针对性练习
    # ------------------------------------------------------------------

    def build_targeted_practice(
        self,
        exercise_map: Dict[str, Exercise],
        count: int = 20,
        seed: Optional[int] = None,
    ) -> List[Problem]:
        """根据弱项生成针对性练习题。"""
        weak = self.identify_weak_areas(exercise_map, top_n=20)

        if not weak:
            from ..core.operators import Addition, Subtraction
            ops = [Addition(), Subtraction()]
        else:
            symbols = set(w["operator"] for w in weak)
            ops = [get_operator(s) for s in symbols if s in {"+", "-"}]
            if not ops:
                from ..core.operators import Addition, Subtraction
                ops = [Addition(), Subtraction()]

        gen = ProblemGenerator(ops, default_constraints(), seed=seed)
        return gen.generate_unique(count)

    # ------------------------------------------------------------------
    # 统计摘要
    # ------------------------------------------------------------------

    def summarize(self) -> dict:
        """生成成绩摘要统计。"""
        if not self._scores:
            return {"total_sessions": 0, "avg_percentage": 0.0}

        percentages = [s.percentage for s in self._scores]
        totals = [s.total for s in self._scores]
        corrects = [s.correct for s in self._scores]

        return {
            "total_sessions": len(self._scores),
            "total_problems_done": sum(totals),
            "total_correct": sum(corrects),
            "avg_percentage": round(sum(percentages) / len(percentages), 1),
            "best": max(percentages),
            "worst": min(percentages),
        }
