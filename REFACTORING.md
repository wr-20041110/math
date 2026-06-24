# 重构文档

## 重构方法清单

| # | 重构方法 | 重构前 | 重构后 | 文件 |
|---|---------|--------|--------|------|
| 1 | **Extract Class** | models.py 包含 4 个类 | 每个类独立文件 | models/exercise.py 等 |
| 2 | **Extract Class** | Reporter 逻辑散落 main.py/Analyzer | services/reporter.py | reporter.py |
| 3 | **Extract Class** | PracticeManager 直接耦合 CsvHandler | io/repository.py | repository.py |
| 4 | **Extract Method** | CsvHandler.load_exercise() ~60行 | _parse_exercise_csv() + _parse_problem_row() | csv_handler.py |
| 5 | **Extract Method** | Grader.grade() 前置条件内联 | _check_preconditions() | grader.py |
| 6 | **Extract Method** | CLI demo 逻辑 120+ 行混在 main | _run_demo() 提取到 cli.py | cli.py |
| 7 | **Extract Method** | argparser 构建内联 | build_parser() 工厂函数 | cli.py |
| 8 | **Rename Method** | generate_many(count, unique) | generate_unique(count) / generate_batch(count) | generator.py |
| 9 | **Rename Method** | generate() → generate_one() | 单数/复数语义区分 | generator.py |
| 10 | **Rename Method** | grade() → evaluate() | 更准确描述批改语义 | grader.py |
| 11 | **Rename Method** | find_weak_problems() → identify_weak_areas() | 语义精确 | analyzer.py |
| 12 | **Rename Method** | total → problem_count | 消除歧义 | exercise.py |
| 13 | **Rename Method** | add_score() → record() | 更自然的动词 | student.py |
| 14 | **Rename Field** | num1/num2 → left/right | 数学语义 | problem.py |
| 15 | **Rename Field** | total_exercises → session_count | 消除歧义 | student.py |
| 16 | **Rename Class** | PracticeManager → Application | 更准确描述职责 | app.py |
| 17 | **Extract Package** | src/ 平铺 | core/ models/ services/ io/ | 全部 |
| 18 | **Introduce Parameter Object** | 分散参数 | Config dataclass | config.py |
| 19 | **Replace Magic Numbers** | 硬编码 0/100/50/5 | DEFAULT_* 常量 | config.py |
| 20 | **Replace Conditional with Polymorphism** | if/else 运算符选择 | Operator.apply() 多态 | operators.py |
| 21 | **Introduce Logging** | print() | logging.getLogger() | 全部 |
| 22 | **Table-Driven Error Messages** | 字符串内联 | _ERRORS 字典 | csv_handler.py |

## 重构前后指标对比

| 指标 | 重构前 | 重构后 |
|------|--------|--------|
| 源文件数 | 12 | 20 |
| 子包数 | 0 | 4 |
| 最长方法 | ~60 行 | < 30 行 |
| 类平均方法数 | 5.2 | 3.8 |
| 耦合度 | PracticeManager → CsvHandler (紧) | Application → Repository (松) |
| 输出方式 | print() | logging |
| 配置管理 | 分散参数 | Config 对象 |
| 测试覆盖 | 71 tests / 6 files | 可独立测试每个子包 |

## TDD 开发流程

本项目采用 TDD（测试驱动开发）流程：

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  RED     │───▶│  GREEN   │───▶│ REFACTOR │
│ 写失败   │    │ 写最少   │    │ 在测试   │
│ 的测试   │    │ 代码通过 │    │ 保护下   │
│          │    │          │    │ 重构     │
└──────────┘    └──────────┘    └──────────┘
     ▲                                │
     └────────────────────────────────┘
              持续循环
```

示例（Problem.left/right 重命名）：
1. **RED**: 修改所有测试使用 `left/right` → 测试失败
2. **GREEN**: 修改 Problem 字段名 → 测试通过
3. **REFACTOR**: 在测试保护下重命名所有引用 → 保持绿色
