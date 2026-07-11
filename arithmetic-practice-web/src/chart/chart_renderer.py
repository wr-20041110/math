"""
ChartRenderer —— 成绩图表渲染器。

功能：
  - 成绩趋势折线图
  - 正确率饼图
  - 弱项柱状图
  - 多套习题对比图
  - 支持保存为PNG文件

依赖：matplotlib
"""

import os
import io
import base64
from pathlib import Path
from typing import List, Dict, Optional

import matplotlib
matplotlib.use('Agg')  # 非交互式后端，适配Web服务器
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class ChartRenderer:
    """成绩图表渲染器。

    使用 matplotlib 生成成绩分析相关的图表，
    支持文件保存和 Base64 编码输出（用于Web嵌入）。

    使用示例:
        >>> renderer = ChartRenderer("data/charts")
        >>> path = renderer.plot_score_trend(scores, "小明")
        >>> base64_str = renderer.plot_correct_pie(score, as_base64=True)
    """

    # 颜色方案
    COLOR_CORRECT = '#4CAF50'    # 绿色 - 正确
    COLOR_WRONG = '#F44336'      # 红色 - 错误
    COLOR_PRIMARY = '#2196F3'    # 蓝色 - 主色
    COLOR_SECONDARY = '#FF9800'  # 橙色 - 辅色
    COLORS_PALETTE = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0',
                      '#00BCD4', '#E91E63', '#3F51B5']

    def __init__(self, output_dir: str = "data/charts"):
        """初始化渲染器。

        Args:
            output_dir: 图表输出目录。
        """
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 公开API - 图表生成
    # ------------------------------------------------------------------

    def plot_score_trend(self, progress_data: List[dict],
                         student_name: str = "",
                         as_base64: bool = False) -> Optional[str]:
        """绘制成绩趋势折线图。

        横轴: 练习次序（1, 2, 3, ...）
        纵轴: 得分百分比（0-100）
        水平虚线: 60分及格线和80分优秀线

        Args:
            progress_data: 成绩记录列表，每项含 {'percentage': float, ...}
            student_name: 学生姓名（用于标题）。
            as_base64: 是否返回Base64编码字符串。

        Returns:
            文件路径 或 Base64字符串。
        """
        if not progress_data:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))

        sessions = list(range(1, len(progress_data) + 1))
        percentages = [r['percentage'] for r in progress_data]

        # 折线图
        ax.plot(sessions, percentages, marker='o', linewidth=2,
                markersize=8, color=self.COLOR_PRIMARY,
                markerfacecolor=self.COLOR_PRIMARY)

        # 填充区域
        ax.fill_between(sessions, percentages, alpha=0.15,
                        color=self.COLOR_PRIMARY)

        # 参考线
        ax.axhline(y=60, color=self.COLOR_SECONDARY, linestyle='--',
                   linewidth=1, alpha=0.7, label='及格线 (60%)')
        ax.axhline(y=80, color=self.COLOR_CORRECT, linestyle='--',
                   linewidth=1, alpha=0.7, label='优秀线 (80%)')

        # 在数据点上标注数值
        for i, pct in enumerate(percentages, 1):
            ax.annotate(f'{pct}%', (i, pct),
                        textcoords="offset points",
                        xytext=(0, 12), ha='center', fontsize=9)

        # 坐标轴设置
        ax.set_xlabel('练习次序', fontsize=12)
        ax.set_ylabel('得分 (%)', fontsize=12)
        title = f'{student_name} 成绩趋势' if student_name else '成绩趋势'
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylim(0, 105)
        ax.set_xticks(sessions)
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d%%'))
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return self._save_or_encode(fig, f"trend_{student_name}", as_base64)

    def plot_correct_pie(self, score, as_base64: bool = False) -> Optional[str]:
        """绘制单次练习正确率饼图。

        Args:
            score: Score 对象或含 correct/wrong 的 dict。
            as_base64: 是否返回Base64编码字符串。

        Returns:
            文件路径 或 Base64字符串。
        """
        if hasattr(score, 'correct'):
            correct, wrong = score.correct, score.wrong
        else:
            correct = score.get('correct', 0)
            wrong = score.get('wrong', 0)

        if correct + wrong == 0:
            return None

        fig, ax = plt.subplots(figsize=(6, 6))

        sizes = [correct, wrong]
        labels = [f'正确 ({correct}题)', f'错误 ({wrong}题)']
        colors = [self.COLOR_CORRECT, self.COLOR_WRONG]
        explode = (0.05, 0)  # 正确部分稍微突出

        wedges, texts, autotexts = ax.pie(
            sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', startangle=90,
            textprops={'fontsize': 12},
        )

        # 中心文字
        pct = score.percentage if hasattr(score, 'percentage') \
            else round(correct / (correct + wrong) * 100, 1)
        ax.text(0, 0, f'{pct}%', ha='center', va='center',
                fontsize=28, fontweight='bold',
                color=self.COLOR_CORRECT if pct >= 60 else self.COLOR_WRONG)

        ax.set_title('答题正确率', fontsize=14, fontweight='bold')

        plt.tight_layout()
        return self._save_or_encode(fig, "pie_chart", as_base64)

    def plot_weak_bar(self, weak_problems: List[dict],
                      top_n: int = 10,
                      as_base64: bool = False) -> Optional[str]:
        """绘制弱项题目柱状图（横向）。

        Args:
            weak_problems: 弱项列表，每项含 operator/left_operand/right_operand/
                          wrong_count/error_rate。
            top_n: 显示前N个。
            as_base64: 是否返回Base64编码字符串。

        Returns:
            文件路径 或 Base64字符串。
        """
        if not weak_problems:
            return None

        data = weak_problems[:top_n]
        # 反转顺序（横向柱状图从下到上）
        data = list(reversed(data))

        fig, ax = plt.subplots(figsize=(10, max(6, len(data) * 0.5)))

        labels = []
        for w in data:
            op = w.get('operator', '+')
            left = w.get('left_operand', w.get('left', 0))
            right = w.get('right_operand', w.get('right', 0))
            labels.append(f"{left} {op} {right}")

        values = [w.get('wrong_count', 0) for w in data]
        colors = [self.COLOR_WRONG if w.get('error_rate', 0) > 0.5
                  else self.COLOR_SECONDARY for w in data]

        bars = ax.barh(labels, values, color=colors, edgecolor='white')

        # 在柱上标注
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                    str(val), va='center', fontsize=11)

        ax.set_xlabel('错误次数', fontsize=12)
        ax.set_title(f'弱项题目 Top {top_n}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        return self._save_or_encode(fig, "weak_problems", as_base64)

    def plot_multi_session_bars(self, records: List[dict],
                                student_name: str = "",
                                as_base64: bool = False) -> Optional[str]:
        """绘制多套习题成绩对比分组柱状图。

        Args:
            records: 成绩记录列表，每项含 exercise_id/total/correct/wrong。
            student_name: 学生姓名。
            as_base64: 是否返回Base64编码字符串。

        Returns:
            文件路径 或 Base64字符串。
        """
        if not records:
            return None

        fig, ax = plt.subplots(figsize=(12, 6))

        n = len(records)
        x = range(n)
        width = 0.35

        corrects = [r.get('correct', 0) for r in records]
        wrongs = [r.get('wrong', 0) for r in records]
        labels = [r.get('exercise_id', f'#{i + 1}')[-8:] for i, r in enumerate(records)]

        ax.bar(x, corrects, width, label='正确', color=self.COLOR_CORRECT)
        ax.bar(x, wrongs, width, bottom=corrects, label='错误',
               color=self.COLOR_WRONG, alpha=0.8)

        # 标注正确率
        for i, (corr, wron) in enumerate(zip(corrects, wrongs)):
            total = corr + wron
            pct = round(corr / total * 100, 1) if total > 0 else 0
            ax.text(i, total + 0.3, f'{pct}%', ha='center', fontsize=10)

        ax.set_xlabel('习题集', fontsize=12)
        ax.set_ylabel('题目数', fontsize=12)
        title = f'{student_name} 多套习题对比' if student_name else '多套习题成绩对比'
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha='right')
        ax.legend()

        plt.tight_layout()
        return self._save_or_encode(fig, f"multi_bar_{student_name}", as_base64)

    def plot_student_comparison(self, overview_data: List[dict],
                                as_base64: bool = False) -> Optional[str]:
        """绘制全班学生成绩对比图。

        Args:
            overview_data: class_overview() 返回的列表。
            as_base64: 是否返回Base64编码字符串。

        Returns:
            文件路径 或 Base64字符串。
        """
        if not overview_data:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        names = [r.get('name', '?') for r in overview_data]
        x = range(len(names))

        avg_scores = [r.get('avg_score', 0) or 0 for r in overview_data]
        best_scores = [r.get('best_score', 0) or 0 for r in overview_data]
        worst_scores = [r.get('worst_score', 0) or 0 for r in overview_data]

        width = 0.25
        ax.bar([i - width for i in x], best_scores, width,
               label='最佳', color=self.COLOR_CORRECT, alpha=0.8)
        ax.bar(x, avg_scores, width,
               label='平均', color=self.COLOR_PRIMARY, alpha=0.8)
        ax.bar([i + width for i in x], worst_scores, width,
               label='最差', color=self.COLOR_WRONG, alpha=0.6)

        ax.set_xlabel('学生', fontsize=12)
        ax.set_ylabel('得分 (%)', fontsize=12)
        ax.set_title('全班成绩对比', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(names)
        ax.legend()
        ax.axhline(y=60, color='gray', linestyle='--', alpha=0.5)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        return self._save_or_encode(fig, "class_comparison", as_base64)

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _save_or_encode(self, fig, name: str,
                        as_base64: bool) -> Optional[str]:
        """保存图表或编码为Base64。

        Args:
            fig: matplotlib Figure 对象。
            name: 文件名（不含扩展名）。
            as_base64: True 返回 Base64 字符串，False 保存文件。

        Returns:
            文件路径 或 Base64 编码字符串。
        """
        if as_base64:
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            return encoded
        else:
            filepath = self._output_dir / f"{name}.png"
            fig.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close(fig)
            return str(filepath)
