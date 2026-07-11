# 口算练习系统（数据处理版）

## 概述

在 OOP 架构基础上引入 **数据处理层**，实现完整的：
- **习题生成 → CSV 存储 → 自动判题 → 成绩分析 → 针对性练习** 闭环。

## 交互流程

```
华经理(生成习题) → CSV保存 → 小明(做题) → 妈妈(录入CSV) → 华经理(导入判题) → 自动打分 → 成绩分析 → 弱项识别 → 针对性练习
```

## 项目结构

```
arithmetic-practice-dataproc/
├── README.md
├── DESIGN.md                   # 设计文档 + 交互流程图
├── main.py                     # CLI 入口（generate/grade/analyze/target/demo）
├── requirements.txt
├── .gitignore
├── data/                       # CSV 数据存储
│   ├── exercises/              # 习题 CSV
│   ├── answers/                # 答卷 CSV
│   ├── scores/                 # 成绩 CSV
│   └── analysis/               # 分析输出
├── src/
│   ├── operators.py            # Operator 策略（复用 OOP 版）
│   ├── constraints.py          # Constraint 策略（复用 OOP 版）
│   ├── problem.py              # Problem 数据模型
│   ├── generator.py            # ProblemGenerator
│   ├── models.py               # Exercise/AnswerSheet/Score/StudentRecord
│   ├── csv_handler.py          # CSV 读写（防御性编程 + 正则）
│   ├── grader.py               # 自动判题器（契约式编程）
│   ├── analyzer.py             # 成绩分析器（弱项识别）
│   ├── exercise_builder.py     # 习题构建器（表驱动编程）
│   └── practice_manager.py     # 练习管理外观（Facade）
└── tests/
    ├── conftest.py              # fixtures
    ├── test_models.py           # 数据模型测试
    ├── test_csv_handler.py      # CSV 读写 + 防御性测试
    ├── test_grader.py           # 判题 + 契约测试
    ├── test_analyzer.py         # 分析器测试
    ├── test_exercise_builder.py # 表驱动测试
    └── test_practice_manager.py # 集成测试
```

## 快速开始

```bash
# 安装
pip install -r requirements.txt

# 生成习题
python main.py generate --type mixed --count 50

# 批改答案
python main.py grade --answers data/answers/EX-xxx_answers.csv

# 分析成绩
python main.py analyze

# 针对性练习
python main.py target --count 20

# 完整演示
python main.py demo

# 测试
python -m pytest tests/ -v    # 71 个测试
```

## 关键技术应用

| 技术 | 文件 | 说明 |
|------|------|------|
| **CSV 存储** | `csv_handler.py` | 习题/答案/成绩持久化 |
| **防御性编程** | `csv_handler.py` | 文件不存在、格式错误、类型校验 |
| **正则表达式** | `csv_handler.py` | 元数据解析 `# key: value`、答案格式预检 |
| **契约式编程** | `grader.py`, `models.py` | 前置条件/后置条件/不变量 |
| **表驱动编程** | `exercise_builder.py` | EXERCISE_TYPES 配置表 |
| **策略模式** | `operators.py`, `constraints.py` | 运算符/约束可互换 |
| **外观模式** | `practice_manager.py` | 统一入口 |

## CSV 数据格式

参见 [DESIGN.md](DESIGN.md) 中的详细规范。

## License

MIT
