"""
Analyzer —— 成绩分析器。

功能：
  - 弱项识别：统计每道题的历史错误率
  - 弱项排序：按错误次数降序排列
  - 针对性出题：为弱项生成同类变体题
"""

from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional

from .models import Score, Exercise, Problem
from .operators import Operator, Addition, Subtraction
from .generator import ProblemGenerator
from .constraints import (
    Constraint,
    OperandRangeConstraint,
    SumLimitConstraint,
    NonNegativeDiffConstraint,
)

# 操作符符号 → Operator 实例映射表（表驱动）
_SYMBOL_TO_OP: Dict[str, Operator] = {"+": Addition(), "-": Subtraction()}

# 默认约束
_DEFAULT_CONSTRAINTS: List[Constraint] = [
    OperandRangeConstraint(0, 100),
    SumLimitConstraint(100),
    NonNegativeDiffConstraint(),
]


class Analyzer:
    """成绩分析器。

    分析学生成绩历史，识别弱项并生成针对性练习。
    """

    def __init__(self, scores: Optional[List[Score]] = None):
        self._scores: List[Score] = list(scores) if scores else []

    def add_scores(self, scores: List[Score]) -> None:
        self._scores.extend(scores)

    # ------------------------------------------------------------------
    # 弱项分析
    # ------------------------------------------------------------------

    def find_weak_problems(
        self,
        exercise_map: Dict[str, Exercise],
        min_error_rate: float = 0.0,
        top_n: int = 10,
    ) -> List[Dict]:
        """识别弱项题目。

        对每道出现过的题，统计：
          - wrong_count: 做错次数
          - total_attempts: 出现次数
          - error_rate: 错误率

        Args:
            exercise_map: {exercise_id: Exercise} 映射（用于回查题目内容）。
            min_error_rate: 最小错误率阈值（0.0-1.0）。
            top_n: 返回前 N 个弱项。

        Returns:
            弱项列表，每个元素为 dict:
              {num1, operator, num2, correct_answer, wrong_count, total_attempts, error_rate}
              按 wrong_count 降序排列。
        """
        # 统计每道题的做错次数和总出现次数
        wrong_counter: Counter = Counter()
        attempt_counter: Counter = Counter()

        for score in self._scores:
            ex = exercise_map.get(score.exercise_id)
            if ex is None:
                continue

            for idx in score.wrong_indices:
                try:
                    p = ex.get_problem(idx)
                    key = (p.num1, p.operator.symbol, p.num2)
                    wrong_counter[key] += 1
                except IndexError:
                    continue

            # 统计总尝试次数（该习题中所有题目）
            for p in ex.problems:
                key = (p.num1, p.operator.symbol, p.num2)
                attempt_counter[key] += 1

        # 构建结果
        results = []
        for key, wrong in wrong_counter.items():
            attempts = attempt_counter.get(key, wrong)
            rate = wrong / attempts if attempts > 0 else 0.0
            if rate >= min_error_rate:
                num1, op_sym, num2 = key
                op = _SYMBOL_TO_OP[op_sym]
                results.append({
                    "num1": num1,
                    "operator": op_sym,
                    "num2": num2,
                    "correct_answer": op.apply(num1, num2),
                    "wrong_count": wrong,
                    "total_attempts": attempts,
                    "error_rate": round(rate, 2),
                })

        # 按错误次数降序
        results.sort(key=lambda x: (-x["wrong_count"], -x["error_rate"]))
        return results[:top_n]

    # ------------------------------------------------------------------
    # 针对性练习生成
    # ------------------------------------------------------------------

    def generate_targeted_practice(
        self,
        exercise_map: Dict[str, Exercise],
        count: int = 20,
        seed: Optional[int] = None,
    ) -> List[Problem]:
        """根据弱项生成针对性练习。

        策略：分析弱项中涉及的运算符类型，
        生成包含这些运算符的题目（不重复）。

        Args:
            exercise_map: 习题映射。
            count: 目标题目数。
            seed: 随机种子。

        Returns:
            针对性 Problem 列表。
        """
        weak = self.find_weak_problems(exercise_map, top_n=20)

        if not weak:
            # 没有弱项 → 随机混合练习
            ops: List[Operator] = [Addition(), Subtraction()]
        else:
            # 从弱项中提取涉及的运算符类型
            op_symbols = set(w["operator"] for w in weak)
            ops = [_SYMBOL_TO_OP[s] for s in op_symbols if s in _SYMBOL_TO_OP]
            if not ops:
                ops = [Addition(), Subtraction()]

        gen = ProblemGenerator(
            operators=ops,
            constraints=_DEFAULT_CONSTRAINTS,
            seed=seed,
        )
        return gen.generate_many(count, unique=True)

    # ------------------------------------------------------------------
    # 统计摘要
    # ------------------------------------------------------------------

    def summary(self) -> Dict:
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
