# 口算练习系统（数据库版）

## 概述

基于 **SQLite** 数据库的口算练习系统，支持多学生管理、自动判题、全班成绩分析和弱项识别。

## 启动

```bash
# 初始化数据库
python main.py setup

# 注册学生
python main.py student add 小明 三年级1班

# 生成习题
python main.py generate --type mixed --count 20

# 提交判题
python main.py grade EX-20260624-mix-001 小明

# 全班概览
python main.py overview

# 弱项分析
python main.py weak

# 个人进步
python main.py progress 小明

# 数据库统计
python main.py stats

# 完整演示
python main.py demo
```

## 项目结构

```
arithmetic-practice-db/
├── README.md
├── DESIGN_DB.md               # 完整数据库设计文档
├── main.py
├── requirements.txt
├── data/
│   └── mathpractice.db        # SQLite 数据库文件
├── src/
│   ├── core/                  # 核心领域（复用）
│   ├── models/                # 数据模型（复用）
│   ├── services/              # 业务服务（复用）
│   ├── db/                    # 数据库层（新增）
│   │   ├── connection.py      # 连接管理器（单例+WAL+事务）
│   │   ├── schema.py          # DDL 建表语句
│   │   ├── queries.py         # SQL 查询常量（参数化）
│   │   └── repository.py      # CRUD + 分析查询
│   └── app.py                 # 应用外观
└── tests/
    ├── test_db_connection.py  # 连接/事务/DDL 测试
    └── test_db_repository.py  # CRUD/分析查询测试
```

## 数据库设计

详见 [DESIGN_DB.md](DESIGN_DB.md)

| 表 | 说明 | 关键字段 |
|----|------|----------|
| `students` | 学生信息 | id(PK), name(UNIQUE), grade |
| `exercises` | 习题集 | id(PK), type, total_count |
| `problems` | 题目 | id(PK), exercise_id(FK), left_operand, operator, right_operand, correct_answer |
| `answers` | 答题记录 | id(PK), exercise_id(FK), student_id(FK), student_answer, is_correct |
| `scores` | 成绩 | id(PK), exercise_id(FK), student_id(FK), total, correct, wrong, percentage |

### ER 关系

```
students 1 ── * answers * ── 1 problems * ── 1 exercises
students 1 ── * scores  * ── 1 exercises
```

### 关键 SQL

- **弱项分析**: JOIN answers + problems, GROUP BY 题目, 统计错误率
- **全班概览**: LEFT JOIN students + scores, AVG(percentage) 聚合
- **个人进步**: WHERE student_id = ? ORDER BY graded_at

## 测试

```bash
python -m pytest tests/ -v    # 18 个测试
```

| 测试文件 | 覆盖 |
|----------|------|
| `test_db_connection.py` | 单例、连接验证、事务提交/回滚、DDL |
| `test_db_repository.py` | 学生CRUD、习题CRUD、自动判题、弱项分析、全班概览 |

## License

MIT
