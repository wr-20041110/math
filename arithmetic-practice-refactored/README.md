# 口算练习系统（重构版）

## 概述

基于 SOLID 原则和设计模式的完整重构版本。

**从模块化 → OOP → 数据处理 → 重构交付** 的最终形态。

## 项目结构

```
arithmetic-practice-refactored/
├── README.md
├── REFACTORING.md              # 重构方法 & TDD 文档
├── UML_BEFORE_AFTER.md         # 重构前后 UML 类图对比
├── pyproject.toml              # 打包配置（pip install）
├── scripts/
│   └── build_exe.py            # PyInstaller 打包脚本
├── src/mathpractice/           # 主包
│   ├── __init__.py
│   ├── __main__.py             # python -m mathpractice
│   ├── config.py               # Config 配置对象（Introduce Parameter Object）
│   ├── app.py                  # Application 外观（Rename Class + Repository）
│   ├── cli.py                  # CLI 接口（Extract Class）
│   ├── core/                   # 核心领域
│   │   ├── operators.py        # Operator 策略 + 注册表
│   │   ├── constraints.py      # Constraint 策略 + 工厂方法
│   │   ├── problem.py          # Problem（left/right 重命名）
│   │   └── generator.py        # ProblemGenerator（方法重命名+拆分）
│   ├── models/                 # 数据模型（Extract Class 拆分）
│   │   ├── exercise.py
│   │   ├── answer.py
│   │   ├── score.py
│   │   └── student.py
│   ├── services/               # 业务服务
│   │   ├── grader.py           # Grader（evaluate + 提取前置检查）
│   │   ├── analyzer.py         # Analyzer（方法重命名）
│   │   ├── reporter.py         # Reporter（新提取类！SRP）
│   │   └── exercise_builder.py # ExerciseBuilder（表驱动）
│   └── io/                     # 数据访问（Repository 模式）
│       ├── csv_handler.py      # CsvHandler（提取解析方法）
│       └── repository.py       # ExerciseRepository（新提取类！）
└── tests/                      # TDD 测试
    ├── core/
    │   └── test_problem.py
    └── services/
        └── test_grader.py
```

## 重构方法（22 项）

详见 [REFACTORING.md](REFACTORING.md)

| 方法 | 数量 |
|------|------|
| Extract Class | 3 |
| Extract Method | 5 |
| Rename Method/Field/Class | 11 |
| Extract Package | 1 |
| Introduce Parameter Object | 1 |
| Replace Magic Numbers | 1 |

## 快速开始

### 安装

```bash
# 开发模式
pip install -e .

# 或直接运行
python -m mathpractice

# 打包为 exe
pip install pyinstaller
python scripts/build_exe.py
```

### 使用

```bash
# 子命令
python -m mathpractice generate --type mixed --count 50
python -m mathpractice grade --answers data/answers/EX-xxx_answers.csv
python -m mathpractice analyze
python -m mathpractice target --count 20
python -m mathpractice demo

# 作为已安装包
mathpractice demo
```

### 测试

```bash
python -m pytest tests/ -v
```

## TDD 流程

本项目采用测试驱动开发：

```
RED (写失败测试) → GREEN (最小代码通过) → REFACTOR (在测试保护下重构)
```

## License

MIT
