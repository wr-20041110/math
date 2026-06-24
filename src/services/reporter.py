"""
Reporter —— 报告生成器（Extract Class 重构）。

重构前: 报告格式化逻辑混在 Analyzer 和 main.py 中。
重构后: 独立的 Reporter 类，负责所有面向用户的文本输出（SRP）。
"""

from typing import List


class Reporter:
    """报告生成器 —— 将分析数据格式化为人类可读文本。"""

    @staticmethod
    def format_summary(summary: dict) -> str:
        """格式化成绩摘要。"""
        lines = [
            "=" * 40,
            "  成绩摘要",
            "=" * 40,
            f"  练习次数: {summary.get('total_sessions', 0)}",
            f"  总做题数: {summary.get('total_problems_done', 0)}",
            f"  总正确数: {summary.get('total_correct', 0)}",
            f"  平均得分: {summary.get('avg_percentage', 0.0)}%",
            f"  最佳: {summary.get('best', 0)}%  最差: {summary.get('worst', 0)}%",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_weak_problems(weak: List[dict]) -> str:
        """格式化弱项列表。"""
        if not weak:
            return "  [OK] 没有发现弱项题目！"

        lines = [
            f"  [!!] 弱项题目 (Top {len(weak)}):",
            f"  {'题目':<12} {'正确答案':<8} {'错误次数':<8} {'错误率':<8}",
            f"  {'-' * 40}",
        ]
        for w in weak:
            prob = f"{w['left']}{w['operator']}{w['right']}"
            lines.append(
                f"  {prob:<12} {w['correct_answer']:<8} "
                f"{w['wrong_count']:<8} {w['error_rate']:.0%}"
            )
        return "\n".join(lines)

    @staticmethod
    def format_problem_grid(problems, cols: int = 5) -> str:
        """将题目列表格式化为网格文本。"""
        lines = []
        for i in range(0, len(problems), cols):
            row = problems[i:i + cols]
            lines.append("\t".join(str(p) for p in row))
        return "\n".join(lines)

    @staticmethod
    def format_score_detail(score) -> str:
        """格式化单次成绩详情。"""
        lines = [
            f"  [OK] 批改完成: {score.exercise_id}",
            f"    学生: {score.student}",
            f"    总题数: {score.total}  正确: {score.correct}  错误: {score.wrong}",
            f"    得分: {score.percentage}%",
        ]
        if score.wrong_indices:
            lines.append(f"    错题索引: {score.wrong_indices}")
        return "\n".join(lines)
