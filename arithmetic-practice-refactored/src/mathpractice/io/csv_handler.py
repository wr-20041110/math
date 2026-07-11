"""
CsvHandler —— CSV 文件读写（重构：Extract Method + 表驱动错误消息）。

重构变更:
  - 长方法拆分为 _parse_metadata / _parse_problem_row 等小方法
  - 错误消息统一使用 _ERROR_MESSAGES 表（表驱动）
  - 正则模式使用 re.compile 缓存（性能优化）
"""

import csv
import os
import re
import logging
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple

from ..core.problem import Problem
from ..core.operators import get_operator
from ..models.exercise import Exercise
from ..models.answer import AnswerSheet
from ..models.score import Score

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 正则模式（编译缓存）
# ---------------------------------------------------------------------------

_META_PATTERN = re.compile(r"^#\s*(\w+)\s*:\s*(.+)$")
_ANSWER_ROW_PATTERN = re.compile(r"^\d+\s*,\s*-?\d+$")

# ---------------------------------------------------------------------------
# 错误消息表 —— 表驱动
# ---------------------------------------------------------------------------

_ERRORS = {
    "file_not_found": "文件不存在: {path}",
    "empty_file": "文件为空: {path}",
    "bad_metadata": "元数据行格式错误 (行 {line}): '{raw}'",
    "bad_header": "CSV 表头错误: 期望 {expected}，实际 {actual}",
    "bad_problem": "习题行格式错误 (行 {line}): '{raw}'",
    "bad_answer": "答案行格式错误 (行 {line}): '{raw}'",
    "missing_meta": "缺少必需的元数据: {key}",
    "invalid_op": "无效的运算符 '{op}'。支持: +, -",
    "meta_after_header": "元数据行出现在表头之后 (行 {line})",
}


class CsvHandler:
    """CSV 文件读写器。

    所有方法包含完善的错误处理（防御性编程）。
    """

    # ==================================================================
    # 习题
    # ==================================================================

    @staticmethod
    def save_exercise(exercise: Exercise, directory: str) -> str:
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"{exercise.exercise_id}.csv")
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write(f"# exercise_id: {exercise.exercise_id}\n")
            f.write(f"# type: {exercise.exercise_type}\n")
            f.write(f"# created_at: {exercise.created_at.isoformat()}\n")
            f.write(f"# total: {exercise.problem_count}\n")
            writer = csv.writer(f)
            writer.writerow(["index", "left", "operator", "right", "correct_answer"])
            for i, p in enumerate(exercise.problems, start=1):
                writer.writerow([i, p.left, p.operator.symbol, p.right, p.answer])
        logger.info("习题已保存: %s", filepath)
        return filepath

    @staticmethod
    def load_exercise(filepath: str) -> Exercise:
        if not os.path.isfile(filepath):
            raise FileNotFoundError(_ERRORS["file_not_found"].format(path=filepath))

        metadata, problems = CsvHandler._parse_exercise_csv(filepath)

        exercise_id = metadata.get("exercise_id", "")
        ex_type = metadata.get("type", "")

        if not exercise_id:
            raise ValueError(_ERRORS["missing_meta"].format(key="exercise_id"))
        if not ex_type:
            raise ValueError(_ERRORS["missing_meta"].format(key="type"))
        if not problems:
            raise ValueError(_ERRORS["empty_file"].format(path=filepath))

        created_str = metadata.get("created_at")
        created_at = datetime.fromisoformat(created_str) if created_str else datetime.now()

        return Exercise(
            exercise_id=exercise_id, exercise_type=ex_type,
            problems=problems, created_at=created_at,
        )

    @staticmethod
    def _parse_exercise_csv(filepath: str) -> Tuple[Dict[str, str], List[Problem]]:
        """解析习题 CSV（Extract Method 重构）。"""
        metadata: Dict[str, str] = {}
        problems: List[Problem] = []
        header_found = False

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                raw = line.rstrip("\n").rstrip("\r")
                if not raw.strip():
                    continue

                m = _META_PATTERN.match(raw)
                if m:
                    if header_found:
                        raise ValueError(_ERRORS["meta_after_header"].format(line=line_num))
                    key, value = m.group(1).strip(), m.group(2).strip()
                    metadata[key] = value
                    continue

                if not header_found and raw.startswith("index"):
                    header_found = True
                    continue

                if header_found:
                    problems.append(CsvHandler._parse_problem_row(raw, line_num))

        return metadata, problems

    @staticmethod
    def _parse_problem_row(raw: str, line_num: int) -> Problem:
        """解析单行题目数据（Extract Method 重构）。"""
        try:
            reader = csv.reader(StringIO(raw))
            row = next(reader)
            if len(row) < 4:
                raise ValueError("列数不足")
            left = int(row[1].strip())
            op_symbol = row[2].strip()
            right = int(row[3].strip())
            op = get_operator(op_symbol)
            return Problem(left=left, right=right, operator=op)
        except (ValueError, KeyError, IndexError) as e:
            raise ValueError(
                _ERRORS["bad_problem"].format(line=line_num, raw=raw)
            ) from e

    # ==================================================================
    # 答案
    # ==================================================================

    @staticmethod
    def save_answers(answer_sheet: AnswerSheet, directory: str) -> str:
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"{answer_sheet.exercise_id}_answers.csv")
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
        if not os.path.isfile(filepath):
            raise FileNotFoundError(_ERRORS["file_not_found"].format(path=filepath))

        metadata: Dict[str, str] = {}
        answers: Dict[int, int] = {}
        header_found = False

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                raw = line.rstrip("\n").rstrip("\r")
                if not raw.strip():
                    continue

                m = _META_PATTERN.match(raw)
                if m:
                    if header_found:
                        raise ValueError(_ERRORS["meta_after_header"].format(line=line_num))
                    key, value = m.group(1).strip(), m.group(2).strip()
                    metadata[key] = value
                    continue

                if not header_found and raw.startswith("problem_index"):
                    header_found = True
                    continue

                if header_found:
                    if not _ANSWER_ROW_PATTERN.match(raw.strip()):
                        raise ValueError(_ERRORS["bad_answer"].format(line=line_num, raw=raw))
                    parts = raw.split(",")
                    answers[int(parts[0].strip())] = int(parts[1].strip())

        if not answers:
            raise ValueError(_ERRORS["empty_file"].format(path=filepath))

        submitted_str = metadata.get("submitted_at")
        return AnswerSheet(
            exercise_id=metadata.get("exercise_id", ""),
            student=metadata.get("student", "unknown"),
            answers=answers,
            submitted_at=datetime.fromisoformat(submitted_str) if submitted_str else datetime.now(),
        )

    # ==================================================================
    # 成绩
    # ==================================================================

    @staticmethod
    def save_scores(scores: List[Score], filepath: str) -> str:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file_exists = os.path.isfile(filepath)
        with open(filepath, "a" if file_exists else "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "exercise_id", "student", "graded_at", "total",
                    "correct", "wrong", "percentage", "wrong_indices",
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
        if not os.path.isfile(filepath):
            raise FileNotFoundError(_ERRORS["file_not_found"].format(path=filepath))
        scores = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                raise ValueError(_ERRORS["empty_file"].format(path=filepath))
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
