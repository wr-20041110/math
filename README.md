# 口算练习生成器（OOP 版）

## 概述

基于 **面向对象设计原则** 和 **设计模式** 重构的口算练习题生成工具。

通过 **策略模式**、**迭代器模式** 和 **外观模式**，实现了高度可扩展、可维护的架构。新增运算符（如乘法）、新增约束（如结果必须为奇数）、新增显示格式（如 HTML 输出）只需添加新类，无需修改已有代码。

## 故事演化

| 阶段 | 需求 | OOP 实现 |
|------|------|----------|
| **故事1** | 随机生成 50 道 100 以内加减法 | `Operator` ABC → `Addition` / `Subtraction`（多态） |
| **故事2** | 答案 + 和≤100 + 差≥0 + 5列 | `Constraint` 策略 + `DisplayStrategy` 策略 |
| **故事3** | 无重复 + 混合加减 | `Problem.__hash__` + `generate_many(unique=True)` |
| **故事4** | OOP 重构 | SOLID 原则 + 策略/迭代器/外观模式 |

## 项目结构

```
arithmetic-practice-oop/
├── README.md
├── UML.md                    # UML 类图设计（PlantUML）
├── main.py                   # 主入口
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── operators.py          # Operator ABC + Addition/Subtraction（策略+多态）
│   ├── constraints.py        # Constraint ABC + 3 个具体约束（策略+OCP）
│   ├── problem.py            # Problem 类（封装+ADT）
│   ├── generator.py          # ProblemGenerator（DIP+策略组合）
│   ├── collection.py         # ProblemCollection + Iterator（迭代器模式）
│   ├── display.py            # DisplayStrategy ABC + Grid/Answer（策略模式）
│   └── sheet.py              # ExerciseSheet（外观模式）
└── tests/
    ├── __init__.py
    ├── test_operators.py     # 多态+LSP 测试
    ├── test_constraints.py   # OCP+策略组合 测试
    ├── test_problem.py       # 封装+ADT 测试
    ├── test_generator.py     # DIP+策略 测试
    ├── test_collection.py    # 迭代器模式 测试
    ├── test_display.py       # 策略模式 测试
    └── test_sheet.py         # 外观+集成 测试
```

## 架构一览

```
┌─────────────────────────────────────────────────┐
│                  ExerciseSheet                   │  ← 外观模式
│   (统一入口：生成 + 存储 + 显示)                    │
├─────────────────────────────────────────────────┤
│         │                │              │        │
│    ┌────▼────┐   ┌───────▼──────┐  ┌───▼───────┐│
│    │Generator │   │  Collection   │  │ Display   ││
│    │(DIP)    │   │  (Iterator)  │  │ (Strategy)││
│    └────┬────┘   └──────────────┘  └───────────┘│
│         │                                       │
│    ┌────▼────┐   ┌───────────────┐              │
│    │Operator  │   │  Constraint   │              │
│    │(Strategy)│   │  (Strategy)   │              │
│    └────┬────┘   └───────┬───────┘              │
│    ┌────┴────┐      ┌────┴────┐                 │
│    │Add│Sub  │      │3 种约束  │                 │
│    └─────────┘      └─────────┘                 │
│         │                                       │
│    ┌────▼────┐                                  │
│    │ Problem │  ← 数据模型（封装 + ADT）          │
│    └─────────┘                                  │
└─────────────────────────────────────────────────┘
```

## 设计模式

| 模式 | 应用 | 效果 |
|------|------|------|
| **策略模式** | `Operator`、`Constraint`、`DisplayStrategy` | 算法可互换，运行时替换行为 |
| **迭代器模式** | `ProblemCollection` + `ProblemIterator` | 分离遍历与存储，支持过滤迭代 |
| **外观模式** | `ExerciseSheet` | 隐藏子系统复杂性，提供简洁 API |

## SOLID 原则

- **SRP**：每个类只有一种职责（`Addition` 只管加法，`SumLimitConstraint` 只管和上限）
- **OCP**：新增运算符/约束/显示格式只需添加子类，不修改已有代码
- **DIP**：`ProblemGenerator` 依赖 `Operator` 和 `Constraint` 抽象，不依赖具体实现
- **LSP**：`Addition` / `Subtraction` 可透明替换 `Operator`，程序行为正确
- **ISP**：每个抽象接口最小化，`Constraint` 只有 `check()` 和 `description`

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python main.py                    # 50 题，无答案
python main.py --answers          # 50 题 + 答案
python main.py -n 20 -a -c 4      # 20 题 + 答案 + 4 列
python main.py --seed 42 -a       # 可重现
python main.py --stats            # 显示统计

# 测试
python -m pytest tests/ -v        # 118 个测试
```

## 扩展示例

新增「乘法」运算符（不修改已有代码）：

```python
from src.operators import Operator

class Multiplication(Operator):
    @property
    def symbol(self) -> str:
        return "×"

    def apply(self, a: int, b: int) -> int:
        return a * b

# 使用
sheet = ExerciseSheet(
    operators=[Addition(), Subtraction(), Multiplication()],
    constraints=[...],
)
```

新增「结果必须为偶数」约束：

```python
class EvenResultConstraint:
    description = "结果必须为偶数"

    def check(self, problem):
        return problem.answer % 2 == 0

# 使用
sheet = ExerciseSheet(constraints=[..., EvenResultConstraint()])
```

## License

MIT
