# 口算练习系统 GUI v3.0

## 概述

基于 **tkinter** 的图形用户界面版本，运用 **MVP 架构**、**观察者模式** 和 **事件驱动编程**。

告别黑底白字的命令行，全部操作可用鼠标完成。

## 启动

```bash
python main.py
```

## GUI 布局

```
┌──────────────────────────────────────────────────┐
│  [类型: ▼] [数量: 20] [生成习题] [提交批改] [成绩分析] │ ← ControlPanel
├────────────────────┬─────────────────────────────┤
│                    │                             │
│  📝 口算练习题      │  📊 批改结果                  │
│  ┌──────────────┐  │  得分: 95.0%                │ ← ResultPanel
│  │ 1. 15+7 = _  │  │  错题: 3, 7                │
│  │ 2. 88-21 = _ │  │                             │
│  │ ...          │  │  📈 成绩分析                  │
│  └──────────────┘  │  练习次数: 5                │ ← AnalysisPanel
│                    │  弱项题目: ...               │
│  ✏️ 填写答案        │                             │
│  ┌──────────────┐  │                             │
│  │ 第1题: [   ] │  │                             │
│  │ 第2题: [   ] │  │                             │
│  └──────────────┘  │                             │
│                                              │
├──────────────────────────────────────────────┤
│  就绪 — 点击「生成习题」开始                       │ ← StatusBar
└──────────────────────────────────────────────┘
```

## 项目结构

```
arithmetic-practice-gui/
├── README.md
├── main.py                     # 启动入口
├── requirements.txt
├── .gitignore
├── docs/
│   └── GUI_CLASS_DIAGRAM.md    # UML 类图设计
├── src/
│   ├── core/                   # 核心领域（复用）
│   │   ├── operators.py        # Operator 策略
│   │   ├── constraints.py      # Constraint 策略
│   │   ├── problem.py          # Problem 数据模型
│   │   └── generator.py        # ProblemGenerator
│   ├── models/                 # 数据模型（复用）
│   │   ├── exercise.py
│   │   ├── answer.py
│   │   └── score.py
│   ├── services/               # 业务服务（复用）
│   │   ├── grader.py           # Grader 判题器
│   │   ├── analyzer.py         # Analyzer 分析器
│   │   └── exercise_builder.py # ExerciseBuilder
│   └── gui/                    # GUI 层（新增）
│       ├── __init__.py
│       ├── app.py              # 主应用（Presenter + Subject）
│       ├── events.py           # 事件系统（EventType + AppEvent）
│       ├── observers.py        # 观察者抽象基类
│       └── widgets.py          # 所有 GUI 面板组件
└── tests/
    ├── test_gui_events.py      # 事件系统 + 观察者模式测试
    └── test_gui_integration.py # 集成测试 + 服务测试
```

## 设计模式

| 模式 | 应用位置 | 说明 |
|------|----------|------|
| **MVP** | `app.py` (Presenter) ↔ `widgets.py` (View) ↔ `core/` (Model) | 分离关注点 |
| **观察者模式** | `observers.py` + `app.py.register_observer()` | 状态变更自动通知所有面板 |
| **事件驱动** | `events.py` + tkinter 事件绑定 | 用户操作→事件→回调→Observer 更新 |
| **策略模式** | `core/operators.py`, `core/constraints.py` | 运算符/约束可互换 |

## 事件清单

| 事件 | 类型 | 触发方式 | 监听者 |
|------|------|----------|--------|
| 生成习题 | `<Button-1>` | 鼠标点击按钮 | ExercisePanel, AnswerPanel, StatusBar |
| 提交批改 | `<Button-1>` | 鼠标点击按钮 | ResultPanel, StatusBar |
| 成绩分析 | `<Button-1>` | 鼠标点击按钮 | AnalysisPanel |
| 回车跳转 | `<Key-Return>` | 键盘回车 | AnswerPanel |
| 输入高亮 | `<FocusIn>` | 获得焦点 | AnswerPanel |
| 滚轮滚动 | `<MouseWheel>` | 鼠标滚轮 | ExercisePanel, AnswerPanel |
| 快捷键生成 | `<Control-g>` | Ctrl+G | App._on_generate |
| 快捷键提交 | `<Control-Return>` | Ctrl+Enter | App._on_grade |

## 测试

```bash
python -m pytest tests/ -v    # 13 个测试
```

## License

MIT
