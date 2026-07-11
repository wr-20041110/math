"""core —— 核心领域对象（运算符、约束、题目、生成器）。"""
from .operators import Operator, Addition, Subtraction
from .constraints import Constraint, OperandRangeConstraint, SumLimitConstraint, NonNegativeDiffConstraint
from .problem import Problem
from .generator import ProblemGenerator
