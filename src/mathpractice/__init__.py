"""
mathpractice —— 口算练习系统（重构版）。

重构要点：
  - 子包分层: core / models / services / io
  - 配置对象: Config 类集中管理参数
  - 日志系统: 标准化 logging 替代 print
  - 常量提取: 消除魔法数字
  - 方法提取: 长方法拆分为小方法
  - 类提取: 按单一职责拆分大类

详见 REFACTORING.md
"""

__version__ = "2.0.0"
