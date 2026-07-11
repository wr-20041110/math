# 口算练习系统 v4.0 —— 基于复用的软件构造

## 项目简介

小学生口算（加减法）在线练习系统，支持：
- 🔢 **自动生成** 100以内加减法口算题
- 📝 **在线练习** 浏览器中答题，即时批改
- 📊 **成绩分析** 弱项识别、趋势图、饼图
- 📄 **Word导出** 习题和成绩报告导出为Word文档
- 📱 **手机适配** 响应式设计，手机浏览器可直接使用
- 🏗️ **设计模式** 策略模式、工厂方法、适配器、仓库、外观等

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 命令行使用

```bash
# 运行完整演示
python main.py demo

# 生成习题
python main.py generate --type mixed --count 20

# 全班概览
python main.py overview

# 弱项分析
python main.py weak --top 10

# 导出Word文档
python main.py export-word <exercise_id>

# 导出成绩图表
python main.py export-chart <学生姓名>
```

### 启动Web服务

```bash
python run_web.py
# 访问 http://127.0.0.1:5000
```

### 运行测试

```bash
pytest tests/ -v
# 带覆盖率
pytest tests/ -v --cov=src --cov-report=term
```

## 项目架构

```
arithmetic-practice-web/
├── src/
│   ├── core/         # 核心领域：运算符、约束、题目、生成器
│   ├── models/       # 数据模型：习题、答卷、成绩、学生
│   ├── services/     # 业务服务：评分、分析、报告
│   ├── db/           # 数据库层：SQLite仓库模式
│   ├── export/       # Word文档导出
│   ├── chart/        # 图表可视化（matplotlib）
│   ├── patterns/     # 设计模式（工厂方法 + 适配器）
│   └── web/          # Flask Web应用
├── tests/            # 单元测试和集成测试
├── docs/             # 设计文档和UML类图
└── data/             # 运行时数据
```

## 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.9+ | 开发语言 |
| SQLite3 | 数据库 |
| Flask | Web框架 |
| python-docx | Word文档生成 |
| matplotlib | 图表可视化 |
| Bootstrap 5 | 响应式UI |
| pytest | 测试框架 |

## 设计模式

| 模式 | 应用 |
|------|------|
| **策略模式** | Operator 运算符体系, Constraint 约束体系 |
| **工厂方法** | GeneratorFactory 习题生成器工厂体系 |
| **适配器** | ExportTarget 统一导出接口 |
| **外观模式** | Application 统一业务API |
| **仓库模式** | DatabaseRepository 数据访问封装 |
| **单例模式** | ConnectionManager 数据库连接管理 |

## 数据库设计

5张表：`students` → `exercises` → `problems` → `answers` → `scores`

支持多学生管理、自动判题、弱项分析（SQL聚合查询）、全班概览。

## 文档

- [UML类图](docs/UML.md) — 完整系统类图、设计模式类图、用例图
- [编码规范](docs/CODING_STANDARD.md) — Git工作流和Python编码规范
- [数据库设计](arithmetic-practice-db/DESIGN_DB.md) — ER图、数据字典、SQL语句

## 项目演进

本系统是6阶段渐进的第7阶段（全功能整合版）：

1. `arithmetic-practice/` — 基础过程式版本
2. `arithmetic-practice-oop/` — OOP+设计模式版本
3. `arithmetic-practice-dataproc/` — 数据处理版本
4. `arithmetic-practice-refactored/` — 分层架构重构版
5. `arithmetic-practice-gui/` — GUI图形界面版
6. `arithmetic-practice-db/` — 数据库持久化版
7. **`arithmetic-practice-web/`** — **全功能整合版（本项目）**

## 许可证

教育用途，自由使用。
