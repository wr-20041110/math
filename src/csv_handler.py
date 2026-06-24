"""
CsvHandler —— CSV 文件读写处理器。

技术应用：
  - 防御性编程：文件不存在、格式错误、类型不匹配均有明确错误处理
  - 正则表达式：解析 # 注释元数据行、校验 CSV 行格式
  - 字符串处理：行级分割、strip、类型转换

CSV 格式规范见 DESIGN.md。
"""

import csv
import os
import re
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple

from .problem import Problem
from .operators import Operator, Addition, Subtraction
from .models import Exercise, AnswerSheet, Score

# ---------------------------------------------------------------------------
# 正则模式（编译一次，重复使用 —— 性能优化）
# ---------------------------------------------------------------------------

_META_RE = re.compile(r"^#\s*(\w+)\s*:\s*(.+)$")
# 匹配: # key: value
# 用于解析 CSV 注释元数据行

_ANSWER_ROW_RE = re.compile(r"^\d+\s*,\s*-?\d+$")
# 匹配: <整数>,<整数> （允许负号，虽然实践中不会出现）
# 用于预检答案行格式

# ---------------------------------------------------------------------------
# 常量表 —— 表驱动编程
# ---------------------------------------------------------------------------

# 操作符符号 → Operator 实例映射表
_OPERATOR_MAP: Dict[str, Operator] = {
    "+": Addition(),
    "-": Subtraction(),
}

# 错误消息表
_ERROR_MESSAGES = {
    "file_not_found": "文件不存在: {path}。请检查路径是否正确。",
    "empty_file": "文件为空: {path}。",
    "bad_metadata": "元数据行格式错误 (行 {line}): '{raw}'。期望格式: # key: value",
    "bad_header": "CSV 表头格式错误: 期望 {expected}，实际为 {actual}",
    "bad_problem_row": "习题行格式错误 (行 {line}, 习题索引 {idx}): '{raw}'",
    "bad_answer_row": "答案行格式错误 (行 {line}): '{raw}'。期望: <index>,<answer>",
    "answer_not_integer": "答案不是有效整数 (行 {line}): '{raw}'",
    "missing_metadata": "缺少必需的元数据: {key}",
    "invalid_operator": "无效的运算符 '{op}'。支持: +, -",
}


# ---------------------------------------------------------------------------
# CsvHandler
# ---------------------------------------------------------------------------

class CsvHandler:
    """CSV 文件读写器。

    所有方法均有完善的错误处理（防御性编程）。
    """

    # ==================================================================
    # 习题读写
    # ==================================================================

    @staticmethod
    def save_exercise(exercise: Exercise, directory: str) -> str:
        """将习题保存为 CSV 文件。

        Args:
            exercise: Exercise 实例。
            directory: 保存目录。

        Returns:
            生成的文件路径。

        Raises:
            OSError: 目录创建或文件写入失败。
        """
        os.makedirs(directory, exist_ok=True)
        filename = f"{exercise.exercise_id}.csv"
        filepath = os.path.join(directory, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            # 元数据（# 注释行）
            f.write(f"# exercise_id: {exercise.exercise_id}\n")
            f.write(f"# type: {exercise.exercise_type}\n")
            f.write(f"# created_at: {exercise.created_at.isoformat()}\n")
            f.write(f"# total: {exercise.total}\n")
            # 表头 + 数据
            writer = csv.writer(f)
            writer.writerow(["index", "num1", "operator", "num2", "correct_answer"])
            for i, p in enumerate(exercise.problems, start=1):
                writer.writerow([i, p.num1, p.operator.symbol, p.num2, p.answer])

        return filepath

    @staticmethod
    def load_exercise(filepath: str) -> Exercise:
        """从 CSV 文件加载习题。

        防御性编程：
          - 文件不存在 → 明确提示
          - 元数据缺失 → 指出缺哪个 key
          - 数据行格式错误 → 报告行号和内容

        Args:
            filepath: CSV 文件路径。

        Returns:
            Exercise 实例。

        Raises:
            FileNotFoundError: 文件不存在。
            ValueError: 格式错误或数据无效。
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(
                _ERROR_MESSAGES["file_not_found"].format(path=filepath)
            )

        metadata: Dict[str, str] = {}
        problems: List[Problem] = []
        header_found = False

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                raw = line.rstrip("\n").rstrip("\r")

                # --- 空行跳过 ---
                if not raw.strip():
                    continue

                # --- 元数据行 (# key: value) ---
                m = _META_RE.match(raw)
                if m:
                    if header_found:
                        raise ValueError(
                            f"元数据行出现在表头之后 (行 {line_num})"
                        )
                    key, value = m.group(1).strip(), m.group(2).strip()
                    metadata[key] = value
                    continue

                # --- 表头行 ---
                if not header_found and raw.startswith("index"):
                    header_found = True
                    expected = ["index", "num1", "operator", "num2", "correct_answer"]
                    actual = [h.strip() for h in raw.split(",")]
                    if actual != expected:
                        raise ValueError(
                            _ERROR_MESSAGES["bad_header"].format(
                                expected=expected, actual=actual
                            )
                        )
                    continue

                # --- 数据行 ---
                if header_found:
                    try:
                        reader = csv.reader(StringIO(raw))
                        row = next(reader)
                        if len(row) < 5:
                            raise ValueError("列数不足")
                        idx = int(row[0].strip())
                        num1 = int(row[1].strip())
                        op_symbol = row[2].strip()
                        num2 = int(row[3].strip())
                        # 忽略 row[4] (correct_answer)，由 Problem 计算

                        op = _OPERATOR_MAP.get(op_symbol)
                        if op is None:
                            raise ValueError(
                                _ERROR_MESSAGES["invalid_operator"].format(op=op_symbol)
                            )

                        problem = Problem(num1=num1, num2=num2, operator=op)
                        problems.append(problem)
                    except (ValueError, IndexError) as e:
                        raise ValueError(
                            _ERROR_MESSAGES["bad_problem_row"].format(
                                line=line_num, idx=len(problems) + 1, raw=raw
                            )
                        ) from e

        # --- 验证元数据 ---
        exercise_id = metadata.get("exercise_id")
        if not exercise_id:
            raise ValueError(
                _ERROR_MESSAGES["missing_metadata"].format(key="exercise_id")
            )

        ex_type = metadata.get("type")
        if not ex_type:
            raise ValueError(_ERROR_MESSAGES["missing_metadata"].format(key="type"))

        if not problems:
            raise ValueError(_ERROR_MESSAGES["empty_file"].format(path=filepath))

        created_str = metadata.get("created_at")
        created_at = datetime.fromisoformat(created_str) if created_str else datetime.now()

        return Exercise(
            exercise_id=exercise_id,
            exercise_type=ex_type,
            problems=problems,
            created_at=created_at,
        )

    # ==================================================================
    # 答案读写
    # ==================================================================

    @staticmethod
    def save_answers(
        answer_sheet: AnswerSheet, directory: str
    ) -> str:
        """将答卷保存为 CSV 文件。"""
        os.makedirs(directory, exist_ok=True)
        filename = f"{answer_sheet.exercise_id}_answers.csv"
        filepath = os.path.join(directory, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write(f"# exercise_id: {answer_sheet.exercise_id}\n")
            f.write(f"# student: {answer_sheet.student}\n")
            f.write(f"# submitted_at: {answer_sheet.submitted_at.isoformat()}\n")
            writer = csv.writer(f)
            writer.writerow(["problem_index", "student_answer"])
            for idx in sorted(answer_sheet.answers.keys()):
                writer.writerow([idx, answer_sheet.answers[idx]])

        return filepath

    @staticmethod
    def load_answers(filepath: str) -> AnswerSheet:
        """从 CSV 文件加载答卷。

        防御性编程：
          - 正则预检每行格式
          - 类型转换错误处理
          - 元数据完整性检查
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(
                _ERROR_MESSAGES["file_not_found"].format(path=filepath)
            )

        metadata: Dict[str, str] = {}
        answers: Dict[int, int] = {}
        header_found = False

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                raw = line.rstrip("\n").rstrip("\r")

                if not raw.strip():
                    continue

                m = _META_RE.match(raw)
                if m:
                    if header_found:
                        raise ValueError(
                            f"元数据行出现在表头之后 (行 {line_num})"
                        )
                    key, value = m.group(1).strip(), m.group(2).strip()
                    metadata[key] = value
                    continue

                if not header_found and raw.startswith("problem_index"):
                    header_found = True
                    continue

                if header_found:
                    # 正则预检
                    if not _ANSWER_ROW_RE.match(raw.strip()):
                        raise ValueError(
                            _ERROR_MESSAGES["bad_answer_row"].format(
                                line=line_num, raw=raw
                            )
                        )
                    parts = raw.split(",")
                    try:
                        idx = int(parts[0].strip())
                        ans = int(parts[1].strip())
                    except ValueError:
                        raise ValueError(
                            _ERROR_MESSAGES["answer_not_integer"].format(
                                line=line_num, raw=raw
                            )
                        )
                    answers[idx] = ans

        exercise_id = metadata.get("exercise_id", "")
        student = metadata.get("student", "unknown")
        submitted_str = metadata.get("submitted_at")
        submitted_at = datetime.fromisoformat(submitted_str) if submitted_str else datetime.now()

        if not answers:
            raise ValueError(_ERROR_MESSAGES["empty_file"].format(path=filepath))

        return AnswerSheet(
            exercise_id=exercise_id,
            student=student,
            answers=answers,
            submitted_at=submitted_at,
        )

    # ==================================================================
    # 成绩读写
    # ==================================================================

    @staticmethod
    def save_scores(scores: List[Score], filepath: str) -> str:
        """将成绩列表追加/写入 CSV 文件。

        Args:
            scores: Score 列表。
            filepath: CSV 文件路径（如 data/scores/scores.csv）。
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file_exists = os.path.isfile(filepath)

        with open(filepath, "a" if file_exists else "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "exercise_id", "student", "graded_at", "total",
                    "correct", "wrong", "percentage", "wrong_indices"
                ])
            for s in scores:
                writer.writerow([
                    s.exercise_id, s.student, s.graded_at.isoformat(),
                    s.total, s.correct, s.wrong,
                    f"{s.percentage:.1f}",
                    ",".join(str(i) for i in s.wrong_indices),
                ])

        return filepath

    @staticmethod
    def load_scores(filepath: str) -> List[Score]:
        """从 CSV 文件加载成绩记录。"""
        if not os.path.isfile(filepath):
            raise FileNotFoundError(
                _ERROR_MESSAGES["file_not_found"].format(path=filepath)
            )

        scores: List[Score] = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                raise ValueError(_ERROR_MESSAGES["empty_file"].format(path=filepath))

            for row in reader:
                if len(row) < 8:
                    continue
                wrong_str = row[7].strip() if row[7].strip() else ""
                wrong_indices = (
                    [int(x) for x in wrong_str.split(",") if x.strip()]
                    if wrong_str else []
                )
                scores.append(Score(
                    exercise_id=row[0].strip(),
                    student=row[1].strip(),
                    graded_at=datetime.fromisoformat(row[2].strip()),
                    total=int(row[3].strip()),
                    correct=int(row[4].strip()),
                    wrong=int(row[5].strip()),
                    percentage=float(row[6].strip()),
                    wrong_indices=wrong_indices,
                ))

        return scores
