# 口算练习系统 —— 数据库设计文档

## 1. 系统用例图

```
                    ┌─────────────────────────────┐
                    │     口算练习系统 (DB版)       │
                    ├─────────────────────────────┤
                    │                             │
    ┌──────┐  生成习题  ┌──────────────────────┐   │
    │ 老师  │ ────────▶ │  选择类型+数量        │   │
    │      │ ◀──────── │  保存到数据库          │   │
    └──────┘  返回习题  └──────────────────────┘   │
                    │                             │
    ┌──────┐  录入答案  ┌──────────────────────┐   │
    │ 学生  │ ────────▶ │  提交答题卡           │   │
    │      │ ◀──────── │  保存答案到数据库       │   │
    └──────┘  返回成绩  └──────────────────────┘   │
                    │                             │
    ┌──────┐  查看分析  ┌──────────────────────┐   │
    │ 老师  │ ────────▶ │  全班成绩概览         │   │
    │      │ ◀──────── │  弱项题目统计          │   │
    └──────┘  返回报告  │  个人成绩追踪          │   │
                    └──────────────────────┘   │
                    │                             │
    ┌──────┐  管理学生  ┌──────────────────────┐   │
    │ 管理员│ ────────▶ │  注册/删除学生         │   │
    │      │ ◀──────── │  查看学生列表          │   │
    └──────┘  确认结果  └──────────────────────┘   │
                    └─────────────────────────────┘
```

## 2. 数据字典

| 表名 | 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|------|
| **students** | id | INTEGER | PK, AUTOINCREMENT | 学生唯一ID |
| | name | TEXT | NOT NULL, UNIQUE | 学生姓名 |
| | grade | TEXT | | 年级/班级 |
| | created_at | TEXT | DEFAULT now | 注册时间 |
| **exercises** | id | TEXT | PK | 习题ID (EX-20260624-add-001) |
| | type | TEXT | NOT NULL, CHECK | addition/subtraction/mixed/targeted |
| | total_count | INTEGER | NOT NULL | 题目总数 |
| | created_at | TEXT | DEFAULT now | 创建时间 |
| **problems** | id | INTEGER | PK, AUTOINCREMENT | 题目唯一ID |
| | exercise_id | TEXT | NOT NULL, FK→exercises | 所属习题集 |
| | problem_index | INTEGER | NOT NULL | 题号 (1-based) |
| | left_operand | INTEGER | NOT NULL | 左操作数 |
| | operator | TEXT | NOT NULL, CHECK | + 或 - |
| | right_operand | INTEGER | NOT NULL | 右操作数 |
| | correct_answer | INTEGER | NOT NULL | 正确答案 |
| | | | UNIQUE(exercise_id, idx) | |
| **answers** | id | INTEGER | PK, AUTOINCREMENT | 答案唯一ID |
| | exercise_id | TEXT | NOT NULL, FK→exercises | 所属习题集 |
| | student_id | INTEGER | NOT NULL, FK→students | 答题学生 |
| | problem_index | INTEGER | NOT NULL | 题号 |
| | student_answer | INTEGER | NOT NULL | 学生答案 |
| | is_correct | INTEGER | NOT NULL, CHECK 0/1 | 是否正确 |
| | submitted_at | TEXT | DEFAULT now | 提交时间 |
| | | | UNIQUE(ex_id, st_id, idx) | |
| **scores** | id | INTEGER | PK, AUTOINCREMENT | 成绩唯一ID |
| | exercise_id | TEXT | NOT NULL, FK→exercises | 所属习题集 |
| | student_id | INTEGER | NOT NULL, FK→students | 学生 |
| | total | INTEGER | NOT NULL | 总题数 |
| | correct | INTEGER | NOT NULL | 正确数 |
| | wrong | INTEGER | NOT NULL | 错误数 |
| | percentage | REAL | NOT NULL | 得分百分比 |
| | graded_at | TEXT | DEFAULT now | 批改时间 |

## 3. 概念设计 (ER 图)

```
┌──────────┐         ┌──────────────┐         ┌──────────┐
│ students │ 1 ──── * │   answers    │ * ──── 1 │ problems │
│          │          │              │          │          │
│ id (PK)  │          │ id (PK)      │          │ id (PK)  │
│ name     │          │ student_id   │          │ exercise │
│ grade    │          │ problem_idx  │          │ _id (FK) │
└──────────┘          │ is_correct   │          │ ...      │
       │              └──────────────┘          └────┬─────┘
       │                                             │
       │              ┌──────────────┐               │
       │              │   scores     │               │
       └──── 1 ─── * │ id (PK)      │               │
                      │ student_id   │               │
                      │ exercise_id  │ * ────────────┘
                      │ percentage   │        │
                      └──────────────┘        │
                                              │
                               ┌──────────────┴┐
                               │  exercises    │
                               │ id (PK)       │
                               │ type          │
                               │ total_count   │
                               └───────────────┘

关系:
  students 1 ── * answers        (一个学生有多条答案)
  problems * ── 1 exercises      (多道题属于一个习题集)
  answers  * ── 1 problems       (一条答案对应一道题)
  scores   * ── 1 students       (一个学生有多条成绩)
  scores   * ── 1 exercises      (一个习题集有多条成绩)
```

## 4. 逻辑设计 (关系模式)

```
students(id, name, grade, created_at)
  PK: id
  AK: name

exercises(id, type, total_count, created_at)
  PK: id

problems(id, exercise_id, problem_index, left_operand, operator, right_operand, correct_answer)
  PK: id
  FK: exercise_id → exercises(id)
  AK: (exercise_id, problem_index)

answers(id, exercise_id, student_id, problem_index, student_answer, is_correct, submitted_at)
  PK: id
  FK: exercise_id → exercises(id)
  FK: student_id → students(id)
  AK: (exercise_id, student_id, problem_index)

scores(id, exercise_id, student_id, total, correct, wrong, percentage, graded_at)
  PK: id
  FK: exercise_id → exercises(id)
  FK: student_id → students(id)
```

## 5. 物理设计 (SQLite DDL)

参见 `src/db/schema.py` 中的完整 DDL 语句。

关键设计决策:
- SQLite 数据库文件: `data/mathpractice.db`
- WAL 模式：支持并发读写
- 外键约束：显式启用 `PRAGMA foreign_keys = ON`
- 索引策略：
  - `idx_problems_exercise` on problems(exercise_id)
  - `idx_answers_exercise_student` on answers(exercise_id, student_id)
  - `idx_scores_student` on scores(student_id)

## 6. 关键 SQL 语句

### 插入习题
```sql
INSERT INTO exercises (id, type, total_count) VALUES (?, ?, ?);
INSERT INTO problems (exercise_id, problem_index, left_operand, operator, right_operand, correct_answer)
VALUES (?, ?, ?, ?, ?, ?);
```

### 提交答案 + 自动判题
```sql
INSERT INTO answers (exercise_id, student_id, problem_index, student_answer, is_correct)
VALUES (?, ?, ?, ?, ?);
```

### 全班成绩概览
```sql
SELECT s.name, sc.total, sc.correct, sc.wrong, sc.percentage, sc.graded_at
FROM scores sc JOIN students s ON sc.student_id = s.id
ORDER BY sc.graded_at DESC;
```

### 弱项分析（错误率最高的题目）
```sql
SELECT p.left_operand, p.operator, p.right_operand,
       COUNT(*) as total_attempts,
       SUM(CASE WHEN a.is_correct = 0 THEN 1 ELSE 0 END) as wrong_count,
       ROUND(CAST(SUM(CASE WHEN a.is_correct = 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 1) as error_rate
FROM answers a JOIN problems p ON a.exercise_id = p.exercise_id AND a.problem_index = p.problem_index
GROUP BY p.left_operand, p.operator, p.right_operand
HAVING wrong_count > 0
ORDER BY error_rate DESC
LIMIT 20;
```

### 个人进步趋势
```sql
SELECT sc.total, sc.correct, sc.percentage, sc.graded_at
FROM scores sc
WHERE sc.student_id = ?
ORDER BY sc.graded_at;
```
