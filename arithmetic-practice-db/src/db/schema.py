"""
Schema —— 数据库 DDL 语句（物理设计）。

包含建表、删表、索引创建。
"""

# ---------------------------------------------------------------------------
# 建表 DDL
# ---------------------------------------------------------------------------

CREATE_STUDENTS = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    grade TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
)
"""

CREATE_EXERCISES = """
CREATE TABLE IF NOT EXISTS exercises (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('addition', 'subtraction', 'mixed', 'targeted')),
    total_count INTEGER NOT NULL,
    created_by TEXT DEFAULT 'system',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
)
"""

CREATE_PROBLEMS = """
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id TEXT NOT NULL,
    problem_index INTEGER NOT NULL,
    left_operand INTEGER NOT NULL,
    operator TEXT NOT NULL CHECK(operator IN ('+', '-')),
    right_operand INTEGER NOT NULL,
    correct_answer INTEGER NOT NULL,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE,
    UNIQUE(exercise_id, problem_index)
)
"""

CREATE_ANSWERS = """
CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id TEXT NOT NULL,
    student_id INTEGER NOT NULL,
    problem_index INTEGER NOT NULL,
    student_answer INTEGER NOT NULL,
    is_correct INTEGER NOT NULL CHECK(is_correct IN (0, 1)),
    submitted_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(exercise_id, student_id, problem_index)
)
"""

CREATE_SCORES = """
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id TEXT NOT NULL,
    student_id INTEGER NOT NULL,
    total INTEGER NOT NULL,
    correct INTEGER NOT NULL,
    wrong INTEGER NOT NULL,
    percentage REAL NOT NULL,
    graded_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
)
"""

# ---------------------------------------------------------------------------
# 索引 DDL
# ---------------------------------------------------------------------------

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_problems_exercise ON problems(exercise_id)",
    "CREATE INDEX IF NOT EXISTS idx_answers_exercise_student ON answers(exercise_id, student_id)",
    "CREATE INDEX IF NOT EXISTS idx_answers_student ON answers(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_scores_student ON scores(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_scores_exercise ON scores(exercise_id)",
]

# ---------------------------------------------------------------------------
# 删表 DDL（CASCADE 顺序）
# ---------------------------------------------------------------------------

DROP_TABLES = [
    "DROP TABLE IF EXISTS answers",
    "DROP TABLE IF EXISTS scores",
    "DROP TABLE IF EXISTS problems",
    "DROP TABLE IF EXISTS exercises",
    "DROP TABLE IF EXISTS students",
]

# ---------------------------------------------------------------------------
# 执行函数
# ---------------------------------------------------------------------------

ALL_DDL = [
    CREATE_STUDENTS,
    CREATE_EXERCISES,
    CREATE_PROBLEMS,
    CREATE_ANSWERS,
    CREATE_SCORES,
]


def create_schema(conn) -> None:
    """创建所有表 + 索引。"""
    for ddl in ALL_DDL:
        conn.execute(ddl)
    for idx in CREATE_INDEXES:
        conn.execute(idx)
    conn.commit()


def drop_schema(conn) -> None:
    """删除所有表。"""
    for ddl in DROP_TABLES:
        conn.execute(ddl)
    conn.commit()
