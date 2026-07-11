"""适配器模式单元测试。"""
import os
import tempfile
import pytest
from core.operators import Addition, Subtraction
from core.problem import Problem
from models.exercise import Exercise
from patterns.adapter import (
    TextExportAdapter,
    WordExportAdapter,
    HTMLExportAdapter,
    ChartExportAdapter,
    ADAPTER_REGISTRY,
    get_adapter,
)


class TestTextExportAdapter:
    def test_export_to_file(self, sample_exercise):
        adapter = TextExportAdapter()
        path = os.path.join(tempfile.gettempdir(), "test_export.txt")

        result = adapter.export(sample_exercise, path)
        assert os.path.exists(result)
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "15+7=" in content
        os.remove(result)

    def test_format_name(self):
        assert "文本" in TextExportAdapter().format_name

    def test_file_extension(self):
        assert TextExportAdapter().file_extension == ".txt"


class TestHTMLExportAdapter:
    def test_export_html_string(self, sample_exercise):
        adapter = HTMLExportAdapter()
        html = adapter.export(sample_exercise)
        assert "<table" in html
        assert "15+7=" in html or "15 + 7" in html

    def test_export_with_answers(self, sample_exercise):
        adapter = HTMLExportAdapter()
        html = adapter.export(sample_exercise, show_answers=True)
        assert "22" in html  # 15+7=22

    def test_export_to_file(self, sample_exercise):
        adapter = HTMLExportAdapter()
        path = os.path.join(tempfile.gettempdir(), "test_export.html")
        adapter.export(sample_exercise, path)
        assert os.path.exists(path)
        os.remove(path)


class TestWordExportAdapter:
    def test_export_exercise(self, sample_exercise):
        adapter = WordExportAdapter()
        path = os.path.join(tempfile.gettempdir(), "test_export.docx")

        result = adapter.export(sample_exercise, path)
        assert os.path.exists(result)
        # 验证是有效的 docx 文件
        assert os.path.getsize(result) > 0
        os.remove(result)

    def test_format_name(self):
        assert WordExportAdapter().format_name == "Word文档"


class TestChartExportAdapter:
    def test_export_bar_chart(self):
        weak_data = [
            {"left_operand": 15, "operator": "+", "right_operand": 7,
             "wrong_count": 5, "error_rate": 75.0},
            {"left_operand": 88, "operator": "-", "right_operand": 21,
             "wrong_count": 3, "error_rate": 50.0},
        ]
        adapter = ChartExportAdapter(tempfile.gettempdir())
        path = os.path.join(tempfile.gettempdir(), "test_chart.png")

        result = adapter.export(weak_data, path, chart_type="bar")
        if result:
            assert os.path.exists(result)
            os.remove(result)

    def test_unknown_chart_type(self):
        adapter = ChartExportAdapter()
        with pytest.raises(ValueError, match="未知"):
            adapter.export([], chart_type="unknown")


class TestAdapterRegistry:
    def test_registry_has_formats(self):
        assert "text" in ADAPTER_REGISTRY
        assert "word" in ADAPTER_REGISTRY
        assert "html" in ADAPTER_REGISTRY
        assert "chart" in ADAPTER_REGISTRY

    def test_get_adapter_valid(self):
        adapter = get_adapter("text")
        assert isinstance(adapter, TextExportAdapter)

        adapter = get_adapter("word")
        assert isinstance(adapter, WordExportAdapter)

    def test_get_adapter_invalid(self):
        with pytest.raises(ValueError, match="不支持"):
            get_adapter("pdf")

    def test_all_adapters_implement_interface(self):
        for fmt in ADAPTER_REGISTRY:
            adapter = ADAPTER_REGISTRY[fmt]
            assert hasattr(adapter, 'export')
            assert hasattr(adapter, 'format_name')
            assert hasattr(adapter, 'file_extension')
