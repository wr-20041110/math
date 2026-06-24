# 口算练习生成器（Arithmetic Practice Generator）

一个 **模块化** 的口算练习题生成工具，用于生成 100 以内加减法口算题。

## 需求演化（故事1 → 故事2 → 故事3）

| 阶段 | 需求 | 实现 |
|------|------|------|
| **故事1** | 随机生成 50 道 100 以内加减法口算题 | `Problem` + `ProblemGenerator` |
| **故事2** | ① 每道题显示答案；② 加法结果 ≤ 100；③ 减法结果 ≥ 0；④ 每行 5 题 | `Problem.answer` + 校验 + `Formatter(cols=5)` |
| **故事3** | ① 无重复算式；② 混合加减法 | `ExerciseSheet`（set 去重 + 随机运算符） |

## 项目结构

```
arithmetic-practice/
├── README.md                 # 项目说明
├── main.py                   # 主入口
├── requirements.txt          # 依赖
├── .gitignore
├── src/                      # 源码包
│   ├── __init__.py
│   ├── problem.py            # Problem 类 —— 算式与答案的数据模型
│   ├── generator.py          # ProblemGenerator 类 —— 按约束生成题目
│   ├── exercise.py           # ExerciseSheet 类 —— 管理习题集、去重
│   └── formatter.py          # Formatter 类 —— 格式化输出
└── tests/                    # 单元测试
    ├── __init__.py
    ├── test_problem.py       # Problem 测试（创建、校验、相等性）
    ├── test_generator.py     # ProblemGenerator 测试（约束、种子）
    ├── test_exercise.py      # ExerciseSheet 测试（去重、混合）
    └── test_formatter.py     # Formatter 测试（列数、答案显示）
```

## 模块设计（模块化编程思想）

```
┌─────────────────┐
│    main.py      │  ← 入口：解析参数 → 调度各模块
└───────┬─────────┘
        │
┌───────▼─────────┐
│  ExerciseSheet  │  ← 故事3：管理 50 道不重复题集
└───────┬─────────┘
        │ 使用 ProblemGenerator
┌───────▼─────────┐
│ ProblemGenerator│  ← 故事2：按约束随机生成单道题
└───────┬─────────┘
        │ 生成 Problem 实例
┌───────▼─────────┐
│    Problem      │  ← 故事1-3：数据模型 + 答案计算 + 相等性
└───────┬─────────┘
        │ 传给 Formatter
┌───────▼─────────┐
│   Formatter     │  ← 故事2：每行 5 列格式化输出
└─────────────────┘
```

## 快速开始

### 环境要求

- Python 3.8+
- pytest（仅测试需要）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行

```bash
# 生成 50 道题（默认）
python main.py

# 生成 50 道题 + 答案
python main.py --answers

# 生成 20 道题 + 答案，每行 4 列
python main.py -n 20 -a -c 4

# 使用固定种子（可重现结果）
python main.py --seed 42 -a
```

### 输出示例

```
48+7=	32+22=	88-21=	15+34=	67-23=
3+45=	91-56=	12+78=	44-19=	55+22=
...
```

### 运行测试

```bash
pytest tests/ -v
```

## 关键设计决策

1. **`Problem` 是 frozen dataclass**
   - 不可变对象，可安全放入 `set` 去重
   - `__eq__` 和 `__hash__` 基于 `(num1, num2, operator)` 实现

2. **去重在 ExerciseSheet 层**
   - `ProblemGenerator` 只负责按约束随机生成（可能重复）
   - `ExerciseSheet` 使用 `set` 确保 50 道题全部唯一

3. **种子可重现**
   - `ProblemGenerator` 和 `ExerciseSheet` 都接受可选 `seed` 参数
   - 方便测试和复现特定题目组合

4. **格式化与数据分离**
   - `Formatter` 独立于 `Problem`，遵循单一职责原则
   - 可灵活切换显示模式（是否显示答案、调整列数）

## 测试覆盖

| 测试文件 | 覆盖内容 |
|----------|----------|
| `test_problem.py` | 创建、校验（非法运算符/操作数/范围）、answer 计算、相等性、哈希、去重、字符串输出 |
| `test_generator.py` | 加法约束（≤100）、减法约束（≥0）、操作数范围、混合生成、种子可重现性 |
| `test_exercise.py` | 生成数量、全部唯一、混合加减、约束满足、边界（0题）、max_attempts 保护 |
| `test_formatter.py` | 默认列数、自定义列数、显示答案、空列表、输入校验 |

## License

MIT
