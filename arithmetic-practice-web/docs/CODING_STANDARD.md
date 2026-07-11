# 口算练习系统 —— Git代码管理和编程规范

## 一、Git工作流

### 1.1 分支策略

```
main (master)           —— 稳定发布版
  └── develop           —— 开发集成分支
        ├── feature/*   —— 功能分支
        ├── fix/*       —— 修复分支
        └── docs/*      —— 文档分支
```

### 1.2 分支命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 功能 | `feature/<简短描述>` | `feature/word-export` |
| 修复 | `fix/<问题描述>` | `fix/grader-zero-division` |
| 文档 | `docs/<文档类型>` | `docs/uml-diagrams` |
| 重构 | `refactor/<模块名>` | `refactor/extract-reporter` |
| 测试 | `test/<测试范围>` | `test/add-web-tests` |

### 1.3 提交信息格式

遵循 Conventional Commits 规范：

```
<type>(<scope>): <简短描述>

[可选的详细描述]

[可选的脚注]
```

**type 类型**:
- `feat`: 新功能
- `fix`: 缺陷修复
- `docs`: 文档变更
- `test`: 测试代码
- `refactor`: 重构（不改变功能）
- `style`: 代码格式（空格、分号等）
- `chore`: 构建/工具变更

**示例**:
```
feat(export): 实现Word文档导出功能
feat(web): 添加在线练习页面和AJAX提交
fix(grader): 修复空答案时的除零错误
test(db): 添加数据库仓库CRUD集成测试
docs(uml): 添加完整系统UML类图
refactor(services): 提取ChartService独立模块
chore: 更新requirements.txt依赖
```

### 1.4 工作流程

1. 从 `develop` 创建功能分支
2. 在分支上开发和测试
3. 运行 `pytest` 确保所有测试通过
4. 提交代码并推送到远程
5. 创建 Pull Request（或合并请求）
6. 代码审查
7. 合并到 `develop`（推荐 squash merge）

### 1.5 .gitignore

已配置忽略以下内容：
- `__pycache__/`, `*.pyc`, `*.pyo`
- `.pytest_cache/`, `.coverage`, `htmlcov/`
- `data/mathpractice.db`（数据库文件不纳入版本控制）
- `data/exports/*`, `data/charts/*.png`
- `.venv/`, `venv/`
- IDE文件（`.vscode/`, `.idea/`）

## 二、Python编码规范

### 2.1 风格指南（PEP 8增强）

**缩进**: 4空格，禁止Tab
**行长度**: 最大100字符
**空行**: 类之间2行，方法之间1行
**引号**: 字符串用双引号 `"`，文档字符串用三双引号 `"""`
**编码**: UTF-8

### 2.2 命名约定

| 类型 | 规则 | 示例 |
|------|------|------|
| 模块名 | `snake_case` | `word_exporter.py` |
| 类名 | `PascalCase` | `ProblemGenerator` |
| 函数/方法 | `snake_case` | `generate_unique()` |
| 变量 | `snake_case` | `exercise_count` |
| 常量 | `UPPER_CASE` | `DEFAULT_OPERAND_MAX` |
| 私有成员 | `_leading_underscore` | `_rng`, `_constraints` |
| 属性 | 名词或名词短语 | `problem_count`, `exercise_type` |
| 布尔方法 | `is_`, `has_` 前缀 | `is_satisfied()`, `has_errors()` |

### 2.3 类型注解

所有公开方法必须包含类型注解：

```python
def generate_unique(self, count: int) -> List[Problem]:
    """生成指定数量的不重复题目。"""
    ...

def evaluate(self, exercise: Exercise, answer_sheet: AnswerSheet) -> Score:
    """评分并返回Score对象。"""
    ...
```

### 2.4 文档字符串（Docstring）

使用 Google 风格：

```python
def export_exercise(self, exercise: Exercise, output_path: str,
                    include_answers: bool = False) -> str:
    """导出单套习题为Word文档。

    Args:
        exercise: Exercise 对象。
        output_path: 输出文件路径。
        include_answers: 是否包含答案页，默认 False。

    Returns:
        输出文件的绝对路径。

    Raises:
        OSError: 无法创建输出目录时。
    """
```

### 2.5 Import顺序

```python
# 1. 标准库
import os
import sys
from typing import List, Optional

# 2. 第三方库
from flask import Flask, render_template
import matplotlib.pyplot as plt

# 3. 本地模块
from core.operators import Operator, Addition
from models.exercise import Exercise
```

### 2.6 代码风格要点

**使用 f-string 进行字符串格式化**:
```python
# 推荐
logger.info(f"习题已生成: {exercise.exercise_id} ({count}题)")

# 不推荐
logger.info("习题已生成: %s (%d题)" % (exercise.exercise_id, count))
```

**使用 `pathlib.Path` 替代 `os.path`**:
```python
# 推荐
from pathlib import Path
output_dir = Path("data/exports")
output_dir.mkdir(parents=True, exist_ok=True)

# 不推荐
import os
os.makedirs("data/exports", exist_ok=True)
```

**使用数据类（dataclass）表示数据结构**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Problem:
    left: int
    right: int
    operator: Operator
```

**优先使用列表推导式**:
```python
# 推荐
add_count = sum(1 for p in problems if p.operator.symbol == "+")

# 不推荐
add_count = 0
for p in problems:
    if p.operator.symbol == "+":
        add_count += 1
```

### 2.7 错误处理

```python
# 明确的异常类型
raise ValueError(f"未知的习题类型: '{exercise_type}'")

# 提供有用的错误消息
raise RuntimeError(
    f"在 {max_attempts} 次尝试中无法生成 {count} 道不重复题目。"
    f"已生成 {len(seen)} 道。"
)
```

## 三、代码审查清单

- [ ] 类型注解完整
- [ ] 文档字符串清晰
- [ ] 变量命名有意义
- [ ] 函数短小（<30行）
- [ ] 没有重复代码
- [ ] 错误处理充分
- [ ] 测试覆盖新功能
- [ ] 遵循SOLID原则
- [ ] 没有硬编码的魔法数字
- [ ] Import按规范排序
