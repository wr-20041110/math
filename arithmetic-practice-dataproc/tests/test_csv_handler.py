"""
CsvHandler 单元测试 —— CSV 文件读写 + 防御性编程。

覆盖：
  - 习题/答案/成绩的读写往返
  - 文件不存在异常
  - 格式错误检测
  - 正则解析元数据行
  - 数据类型校验
"""

import os
import pytest
from datetime import datetime
from src.csv_handler import CsvHandler
from src.models import Exercise, AnswerSheet, Score
from src.operators import Addition as Add, Subtraction as Sub
from src.problem import Problem


handler = CsvHandler()


# =====================================================================
# 习题 CSV 读写
# =====================================================================

class TestExerciseCsv:
    def test_save_and_load_roundtrip(self, sample_exercise, temp_dir):
        """保存再加载应得到等价的 Exercise。"""
        path = handler.save_exercise(sample_exercise, temp_dir)
        loaded = handler.load_exercise(path)

        assert loaded.exercise_id == sample_exercise.exercise_id
        assert loaded.exercise_type == sample_exercise.exercise_type
        assert loaded.total == sample_exercise.total
        for i, (orig, reloaded) in enumerate(zip(sample_exercise.problems, loaded.problems)):
            assert orig == reloaded, f"题目 {i+1} 不匹配"

    def test_load_nonexistent_file(self, temp_dir):
        """防御性：文件不存在应抛出 FileNotFoundError。"""
        path = os.path.join(temp_dir, "nonexistent.csv")
        with pytest.raises(FileNotFoundError, match="文件不存在"):
            handler.load_exercise(path)

    def test_saved_file_contains_metadata(self, sample_exercise, temp_dir):
        """保存的 CSV 应包含 # 元数据注释行。"""
        path = handler.save_exercise(sample_exercise, temp_dir)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert f"# exercise_id: {sample_exercise.exercise_id}" in content
        assert f"# type: {sample_exercise.exercise_type}" in content
        assert "# total:" in content
        assert "index,num1,operator,num2,correct_answer" in content

    def test_load_bad_metadata(self, temp_dir):
        """防御性：损坏的元数据应报告错误。"""
        path = os.path.join(temp_dir, "bad.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# bad line without colon\n")
            f.write("index,num1,operator,num2,correct_answer\n")
            f.write("1,15,+,7,22\n")
        # 缺少 # key: value 格式的元数据 → 加载时报缺少 exercise_id
        with pytest.raises(ValueError, match="缺少必需的元数据"):
            handler.load_exercise(path)

    def test_load_bad_problem_row(self, temp_dir):
        """防御性：损坏的题目行应报告错误。"""
        path = os.path.join(temp_dir, "bad_problem.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# exercise_id: EX-BAD-001\n")
            f.write("# type: mixed\n")
            f.write("# total: 2\n")
            f.write("index,num1,operator,num2,correct_answer\n")
            f.write("1,15,+,7,22\n")
            f.write("2,not_a_number,+,33,55\n")  # 损坏行
        with pytest.raises(ValueError, match="习题行格式错误"):
            handler.load_exercise(path)

    def test_load_invalid_operator(self, temp_dir):
        """防御性：无效运算符应报告错误（被外层捕获为行格式错误）。"""
        path = os.path.join(temp_dir, "bad_op.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# exercise_id: EX-BAD-OP\n")
            f.write("# type: mixed\n")
            f.write("# total: 1\n")
            f.write("index,num1,operator,num2,correct_answer\n")
            f.write("1,15,*,7,105\n")  # * 不是支持的运算符
        # 错误消息：外层捕获后报告为 "习题行格式错误"
        with pytest.raises(ValueError, match="习题行格式错误"):
            handler.load_exercise(path)


# =====================================================================
# 答案 CSV 读写
# =====================================================================

class TestAnswerCsv:
    def test_save_and_load_roundtrip(self, sample_answer_sheet, temp_dir):
        """保存再加载应得到等价的 AnswerSheet。"""
        path = handler.save_answers(sample_answer_sheet, temp_dir)
        loaded = handler.load_answers(path)

        assert loaded.exercise_id == sample_answer_sheet.exercise_id
        assert loaded.student == sample_answer_sheet.student
        assert loaded.answers == sample_answer_sheet.answers

    def test_load_nonexistent_file(self, temp_dir):
        with pytest.raises(FileNotFoundError, match="文件不存在"):
            handler.load_answers(os.path.join(temp_dir, "nonexistent.csv"))

    def test_load_bad_answer_row(self, temp_dir):
        """防御性：正则预检应捕获格式错误的答案行。"""
        path = os.path.join(temp_dir, "bad_answer.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# exercise_id: EX-TEST-001\n")
            f.write("# student: XiaoMing\n")
            f.write("problem_index,student_answer\n")
            f.write("1,22\n")
            f.write("not_a_number\n")  # 损坏行
        with pytest.raises(ValueError, match="答案行格式错误"):
            handler.load_answers(path)

    def test_load_answer_not_integer(self, temp_dir):
        """防御性：非整数答案被正则预检捕获为格式错误。"""
        path = os.path.join(temp_dir, "bad_int.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# exercise_id: EX-TEST-001\n")
            f.write("# student: XiaoMing\n")
            f.write("problem_index,student_answer\n")
            f.write("1,abc\n")  # abc 不是整数，被正则 _ANSWER_ROW_RE 先捕获
        with pytest.raises(ValueError, match="答案行格式错误"):
            handler.load_answers(path)

    def test_saved_file_contains_metadata(self, sample_answer_sheet, temp_dir):
        path = handler.save_answers(sample_answer_sheet, temp_dir)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert f"# exercise_id: {sample_answer_sheet.exercise_id}" in content
        assert f"# student: {sample_answer_sheet.student}" in content


# =====================================================================
# 成绩 CSV 读写
# =====================================================================

class TestScoreCsv:
    def test_save_and_load_roundtrip(self, sample_score, temp_dir):
        path = os.path.join(temp_dir, "scores.csv")
        handler.save_scores([sample_score], path)
        loaded = handler.load_scores(path)

        assert len(loaded) == 1
        assert loaded[0].exercise_id == sample_score.exercise_id
        assert loaded[0].student == sample_score.student
        assert loaded[0].total == sample_score.total
        assert loaded[0].correct == sample_score.correct
        assert loaded[0].wrong == sample_score.wrong
        assert loaded[0].percentage == sample_score.percentage

    def test_append_scores(self, sample_score, temp_dir):
        path = os.path.join(temp_dir, "scores.csv")
        handler.save_scores([sample_score], path)
        s2 = Score(exercise_id="EX-002", student="XiaoMing",
                   total=10, correct=10, wrong=0, percentage=100.0, wrong_indices=[])
        handler.save_scores([s2], path)  # 追加
        loaded = handler.load_scores(path)
        assert len(loaded) == 2

    def test_load_nonexistent(self, temp_dir):
        with pytest.raises(FileNotFoundError, match="文件不存在"):
            handler.load_scores(os.path.join(temp_dir, "nonexistent.csv"))
