"""
适配器模式 —— 统一导出接口。

设计意图：
  - 将不同类型的导出目标（Word、HTML、文本、图表）统一为一致的接口
  - 客户端只需依赖 ExportTarget 抽象，无需了解具体导出格式
  - 遵循 OCP：新增导出格式只需添加新的适配器类

模式结构：
  ExportTarget (目标接口/ABC)
      ├── TextExportAdapter     —— 适配为纯文本（复用现有 formatter）
      ├── WordExportAdapter     —— 适配为Word文档
      ├── HTMLExportAdapter     —— 适配为HTML字符串
      └── ChartExportAdapter    —— 适配为图表PNG

适配器模式的"被适配者"：
  - WordExporter（Word导出）
  - ChartRenderer（图表渲染）
  - Reporter（文本格式化）
  - Exercise 数据模型（HTML转换）
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ExportTarget(ABC):
    """导出目标接口 —— 所有适配器的抽象基类。

    定义统一的 export() 方法，所有具体适配器必须实现。
    """

    @abstractmethod
    def export(self, data: Any, filepath: str,
               **kwargs) -> str:
        """将数据导出到指定文件。

        Args:
            data: 要导出的数据（类型取决于具体适配器）。
            filepath: 输出文件路径。
            **kwargs: 额外参数。

        Returns:
            输出文件的绝对路径 或 内容字符串。
        """
        ...

    @property
    @abstractmethod
    def format_name(self) -> str:
        """导出格式名称。"""
        ...

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """文件扩展名（含点号）。"""
        ...


class TextExportAdapter(ExportTarget):
    """纯文本导出适配器。

    将习题数据适配为格式化的纯文本字符串。
    适配现有的 Reporter 文本格式化功能。
    """

    def export(self, data: Any, filepath: str,
               **kwargs) -> str:
        """导出为文本文件。

        Args:
            data: Exercise 对象 或 Problem 列表。
            filepath: 输出 .txt 文件路径。

        Returns:
            输出文件路径。
        """
        from services.reporter import Reporter

        if hasattr(data, 'problems'):
            problems = data.problems
        else:
            problems = data

        cols = kwargs.get('cols', 5)
        content = Reporter.format_problem_grid(problems, cols=cols)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    @property
    def format_name(self) -> str:
        return "纯文本"

    @property
    def file_extension(self) -> str:
        return ".txt"


class WordExportAdapter(ExportTarget):
    """Word文档导出适配器。

    将习题/成绩数据适配为 .docx 格式。
    适配 WordExporter 的导出功能。
    """

    def __init__(self):
        from export.word_exporter import WordExporter
        self._exporter = WordExporter()

    def export(self, data: Any, filepath: str,
               **kwargs) -> str:
        """导出为Word文档。

        Args:
            data: Exercise 对象。
            filepath: 输出 .docx 文件路径。
            **kwargs:
                - include_answers (bool): 是否包含答案。
                - answer_sheet: AnswerSheet 对象（带批改结果时）。
                - score: Score 对象（带批改结果时）。

        Returns:
            输出文件路径。
        """
        include_answers = kwargs.get('include_answers', False)
        answer_sheet = kwargs.get('answer_sheet')
        score = kwargs.get('score')

        if answer_sheet and score:
            return self._exporter.export_with_answers(
                data, answer_sheet, score, filepath,
            )
        else:
            return self._exporter.export_exercise(
                data, filepath, include_answers=include_answers,
            )

    @property
    def format_name(self) -> str:
        return "Word文档"

    @property
    def file_extension(self) -> str:
        return ".docx"


class HTMLExportAdapter(ExportTarget):
    """HTML导出适配器。

    将习题数据适配为HTML格式字符串。
    用于Web页面的内容渲染。
    """

    def export(self, data: Any, filepath: str = "",
               **kwargs) -> str:
        """导出为HTML内容。

        Args:
            data: Exercise 对象 或 Problem 列表。
            filepath: 可选输出文件路径（为空时仅返回字符串）。

        Returns:
            HTML字符串。
        """
        if hasattr(data, 'problems'):
            problems = data.problems
        else:
            problems = data

        show_answers = kwargs.get('show_answers', False)

        rows = []
        for i, p in enumerate(problems, 1):
            expr = f"{p.left} {p.operator.symbol} {p.right}"
            if show_answers:
                expr += f" = {p.answer}"
            else:
                expr += " = ______"
            rows.append(f"<tr><td class='idx'>{i}</td>"
                        f"<td class='problem'>{expr}</td></tr>")

        html = (
            "<table class='problem-table'>\n"
            + "\n".join(rows)
            + "\n</table>"
        )

        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

        return html

    @property
    def format_name(self) -> str:
        return "HTML"

    @property
    def file_extension(self) -> str:
        return ".html"


class ChartExportAdapter(ExportTarget):
    """图表导出适配器。

    将成绩分析数据适配为PNG图表。
    适配 ChartRenderer 的图表渲染功能。
    """

    def __init__(self, output_dir: str = "data/charts"):
        from chart.chart_renderer import ChartRenderer
        self._renderer = ChartRenderer(output_dir)

    def export(self, data: Any, filepath: str = "",
               **kwargs) -> str:
        """导出为图表PNG文件。

        Args:
            data: 成绩数据（Score列表 或 弱项列表）。
            filepath: 输出 .png 文件路径。
            **kwargs:
                - chart_type (str): 'trend' | 'pie' | 'bar' | 'multi_bar'
                - student_name (str): 学生姓名。

        Returns:
            图表文件路径。
        """
        chart_type = kwargs.get('chart_type', 'bar')
        student_name = kwargs.get('student_name', '')

        if chart_type == 'trend':
            result = self._renderer.plot_score_trend(
                data, student_name,
            )
        elif chart_type == 'pie':
            result = self._renderer.plot_correct_pie(data)
        elif chart_type == 'bar':
            result = self._renderer.plot_weak_bar(data)
        elif chart_type == 'multi_bar':
            result = self._renderer.plot_multi_session_bars(
                data, student_name,
            )
        else:
            raise ValueError(f"未知图表类型: {chart_type}")

        return result or ""

    @property
    def format_name(self) -> str:
        return "PNG图表"

    @property
    def file_extension(self) -> str:
        return ".png"


# ------------------------------------------------------------------
# 适配器注册表
# ------------------------------------------------------------------

ADAPTER_REGISTRY: dict = {
    "text": TextExportAdapter(),
    "word": WordExportAdapter(),
    "html": HTMLExportAdapter(),
    "chart": ChartExportAdapter(),
}


def get_adapter(format_type: str) -> ExportTarget:
    """获取指定格式的适配器实例。

    Args:
        format_type: 格式类型 ('text' | 'word' | 'html' | 'chart')。

    Returns:
        ExportTarget 实例。

    Raises:
        ValueError: 不支持的格式。
    """
    adapter = ADAPTER_REGISTRY.get(format_type)
    if adapter is None:
        raise ValueError(
            f"不支持的导出格式: '{format_type}'。"
            f"支持: {list(ADAPTER_REGISTRY.keys())}"
        )
    return adapter
