# UML 类图设计

## 1. 完整类图（PlantUML）

```plantuml
@startuml
' ============================================================
' 口算练习生成器 —— 面向对象架构类图
' 故事4：基于 SOLID 原则和设计模式重构
' ============================================================

' --- 策略模式：运算符体系 ---
abstract class Operator <<abstract>> {
  + {abstract} symbol: str
  + {abstract} apply(a: int, b: int): int
}

class Addition {
  + symbol: str = "+"
  + apply(a, b): int
}

class Subtraction {
  + symbol: str = "-"
  + apply(a, b): int
}

Operator <|-- Addition
Operator <|-- Subtraction

' --- 策略模式：约束体系 ---
abstract class Constraint <<abstract>> {
  + {abstract} check(p: Problem): bool
  + {abstract} description: str
}

class OperandRangeConstraint {
  - _min: int
  - _max: int
  + check(p: Problem): bool
  + description: str
}

class SumLimitConstraint {
  - _limit: int
  + check(p: Problem): bool
  + description: str
}

class NonNegativeDiffConstraint {
  + check(p: Problem): bool
  + description: str
}

Constraint <|-- OperandRangeConstraint
Constraint <|-- SumLimitConstraint
Constraint <|-- NonNegativeDiffConstraint

' --- 数据模型 ---
class Problem <<frozen dataclass>> {
  - num1: int
  - num2: int
  - operator: Operator
  + answer: int
  + validate(constraints: List[Constraint]): void
  + __eq__(other): bool
  + __hash__(): int
  + __str__(): str
}

Problem --> Operator : uses ▶
Problem ..> Constraint : validates with ▶

' --- 生成器 ---
class ProblemGenerator {
  - _operators: List[Operator]
  - _constraints: List[Constraint]
  - _rng: Random
  + generate(max_attempts: int): Problem
  + generate_many(count: int, unique: bool): List[Problem]
  - _generate_operands(op: Operator): tuple
}

ProblemGenerator --> Operator : selects from ▶
ProblemGenerator ..> Constraint : checks with ▶
ProblemGenerator ..> Problem : creates ▶

' --- 迭代器模式 ---
class ProblemCollection <<Iterable>> {
  - _problems: List[Problem]
  + add(p: Problem): void
  + extend(problems: List[Problem]): void
  + __iter__(): ProblemIterator
  + iter_filtered(predicate): ProblemIterator
  + __len__(): int
  + __contains__(p: Problem): bool
  + __getitem__(index: int): Problem
}

class ProblemIterator <<Iterator>> {
  - _problems: List[Problem]
  - _index: int
  - _predicate: Callable | None
  + __iter__(): self
  + __next__(): Problem
}

ProblemCollection --> Problem : stores ▶
ProblemCollection ..> ProblemIterator : creates ▶
ProblemIterator --> Problem : traverses ▶

' --- 策略模式：显示体系 ---
abstract class DisplayStrategy <<abstract>> {
  + {abstract} display(problems: List[Problem]): str
}

class GridDisplay {
  - _cols: int
  + display(problems): str
}

class AnswerDisplay {
  - _cols: int
  + display(problems): str
}

DisplayStrategy <|-- GridDisplay
DisplayStrategy <|-- AnswerDisplay
DisplayStrategy ..> Problem : formats ▶

' --- 外观模式 ---
class ExerciseSheet <<Facade>> {
  - _total: int
  - _generator: ProblemGenerator
  - _collection: ProblemCollection
  - _display_strategy: DisplayStrategy
  + generate(): ProblemCollection
  + render(): str
  + get_problems(): List[Problem]
  + stats: dict
}

ExerciseSheet --> ProblemGenerator : delegates ▶
ExerciseSheet --> ProblemCollection : manages ▶
ExerciseSheet --> DisplayStrategy : delegates ▶

@enduml
```

## 2. 设计模式应用总结

| 模式 | 参与者 | 角色 |
|------|--------|------|
| **策略模式** | `Operator` / `Addition` / `Subtraction` | 封装可互换的运算算法 |
| **策略模式** | `Constraint` / `SumLimitConstraint` / ... | 封装可组合的校验规则 |
| **策略模式** | `DisplayStrategy` / `GridDisplay` / `AnswerDisplay` | 封装可互换的显示算法 |
| **迭代器模式** | `ProblemCollection` / `ProblemIterator` | 分离集合与遍历逻辑 |
| **外观模式** | `ExerciseSheet` | 为子系统提供统一入口 |

## 3. SOLID 原则落地

| 原则 | 实现位置 | 说明 |
|------|----------|------|
| **SRP** 单一职责 | `operators.py`, `constraints.py`, `display.py` | 每个类只有一种职责（运算/校验/显示） |
| **OCP** 开放-封闭 | 所有 ABC 子类体系 | 新增运算符/约束/显示格式只需添加子类 |
| **DIP** 依赖倒转 | `ProblemGenerator`, `Problem` | 依赖 Operator/Constraint 抽象，不依赖具体类 |
| **LSP** 里氏代换 | `Addition` / `Subtraction` | 子类可透明替换 Operator 基类 |
| **ISP** 接口隔离 | `Operator`, `Constraint`, `DisplayStrategy` | 每个接口只定义最小必要方法集 |

## 4. 核心交互序列

```
Client → ExerciseSheet.render()
           │
           ├─→ ProblemGenerator.generate_many(50)
           │     └─→ generate() × N 次
           │           ├─→ 随机选择 Operator 策略
           │           ├─→ _generate_operands()
           │           ├─→ Problem(…)
           │           └─→ problem.validate(constraints)  ← 策略模式校验
           │
           ├─→ ProblemCollection(problems)                ← 存储
           │
           └─→ DisplayStrategy.display(problems)          ← 策略模式渲染
                 └─→ GridDisplay / AnswerDisplay
```
