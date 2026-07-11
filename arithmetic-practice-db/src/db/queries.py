"""
SQL 查询常量 —— 集中管理所有 SQL 语句。

设计原则：
  - 查询与代码分离：SQL 集中定义，便于审查和优化
  - 参数化查询：所有 ? 占位符防止 SQL 注入
"""

# =========================================================================
# 学生管理
# =========================================================================

INSERT_STUDENT = """
INSERT OR IGNORE INTO students (name, grade) VALUES (?, ?)
"""

FIND_STUDENT_BY_NAME = """
SELECT * FROM students WHERE name = ?
"""

LIST_ALL_STUDENTS = """
SELECT * FROM students ORDER BY name
"""

DELETE_STUDENT = """
DELETE FROM students WHERE id = ?
"""

# =========================================================================
# 习题管理
# =========================================================================

INSERT_EXERCISE = """
INSERT INTO exercises (id, type, total_count) VALUES (?, ?, ?)
"""

INSERT_PROBLEM = """
INSERT INTO problems (exercise_id, problem_index, left_operand, operator, right_operand, correct_answer)
VALUES (?, ?, ?, ?, ?, ?)
"""

FIND_EXERCISE_BY_ID = """
SELECT * FROM exercises WHERE id = ?
"""

FIND_PROBLEMS_BY_EXERCISE = """
SELECT * FROM problems WHERE exercise_id = ? ORDER BY problem_index
"""

LIST_EXERCISES = """
SELECT * FROM exercises ORDER BY created_at DESC LIMIT ?
"""

# =========================================================================
# 答案 + 判题
# =========================================================================

INSERT_ANSWER = """
INSERT OR REPLACE INTO answers
    (exercise_id, student_id, problem_index, student_answer, is_correct)
VALUES (?, ?, ?, ?, ?)
"""

FIND_ANSWERS_BY_EXERCISE_STUDENT = """
SELECT * FROM answers WHERE exercise_id = ? AND student_id = ? ORDER BY problem_index
"""

# =========================================================================
# 成绩
# =========================================================================

INSERT_SCORE = """
INSERT INTO scores (exercise_id, student_id, total, correct, wrong, percentage)
VALUES (?, ?, ?, ?, ?, ?)
"""

FIND_SCORES_BY_STUDENT = """
SELECT * FROM scores WHERE student_id = ? ORDER BY graded_at DESC
"""

# =========================================================================
# 分析查询
# =========================================================================

CLASS_OVERVIEW = """
SELECT s.name,
       COUNT(sc.id) as total_sessions,
       ROUND(AVG(sc.percentage), 1) as avg_score,
       MAX(sc.percentage) as best_score,
       MIN(sc.percentage) as worst_score
FROM students s
LEFT JOIN scores sc ON s.id = sc.student_id
GROUP BY s.id
ORDER BY avg_score DESC
"""

WEAK_PROBLEMS_ANALYSIS = """
SELECT p.left_operand,
       p.operator,
       p.right_operand,
       p.correct_answer,
       COUNT(*) as total_attempts,
       SUM(CASE WHEN a.is_correct = 0 THEN 1 ELSE 0 END) as wrong_count,
       ROUND(
           CAST(SUM(CASE WHEN a.is_correct = 0 THEN 1 ELSE 0 END) AS REAL)
           / COUNT(*) * 100, 1
       ) as error_rate
FROM answers a
JOIN problems p ON a.exercise_id = p.exercise_id
    AND a.problem_index = p.problem_index
GROUP BY p.left_operand, p.operator, p.right_operand
HAVING wrong_count > 0
ORDER BY error_rate DESC
LIMIT ?
"""

STUDENT_PROGRESS = """
SELECT sc.exercise_id,
       sc.total,
       sc.correct,
       sc.wrong,
       sc.percentage,
       sc.graded_at
FROM scores sc
WHERE sc.student_id = ?
ORDER BY sc.graded_at
"""

STUDENT_WEAK_PROBLEMS = """
SELECT p.left_operand,
       p.operator,
       p.right_operand,
       p.correct_answer,
       COUNT(*) as total_attempts,
       SUM(CASE WHEN a.is_correct = 0 THEN 1 ELSE 0 END) as wrong_count
FROM answers a
JOIN problems p ON a.exercise_id = p.exercise_id
    AND a.problem_index = p.problem_index
WHERE a.student_id = ?
GROUP BY p.left_operand, p.operator, p.right_operand
HAVING wrong_count > 0
ORDER BY wrong_count DESC
LIMIT ?
"""

DATABASE_STATS = """
SELECT
    (SELECT COUNT(*) FROM students) as student_count,
    (SELECT COUNT(*) FROM exercises) as exercise_count,
    (SELECT COUNT(*) FROM problems) as problem_count,
    (SELECT COUNT(*) FROM answers) as answer_count,
    (SELECT COUNT(*) FROM scores) as score_count
"""
