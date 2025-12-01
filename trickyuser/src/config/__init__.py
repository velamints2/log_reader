#!/usr/bin/env python3
"""配置模块 - 加载配置文件"""

import os

# 读取提示提醒块
with open("trickyuser/src/config/prompt_reminder.txt", "r", encoding="utf-8") as f:
    prompt_reminder = f.read()

# 直接定义场景配置，避免使用YAML
scenarios = [
    {
        "desc": "写一个可运行的Python Hello World代码",
        "difficulty": "easy",
        "tags": ["basic", "python"],
        "expected": "输出Hello, World!"
    },
    {
        "desc": "写一个Python函数，接收一个列表，返回列表中所有偶数的平方和",
        "difficulty": "medium",
        "tags": ["function", "list", "math"],
        "expected": "正确计算偶数平方和"
    },
    {
        "desc": "写一个Python程序，读取本地文件test.txt，统计其中每个单词出现的频率",
        "difficulty": "medium",
        "tags": ["file", "io", "dictionary"],
        "expected": "正确统计单词频率"
    },
    {
        "desc": "写一个Python类，实现一个简单的栈数据结构，包含push、pop、peek方法",
        "difficulty": "medium",
        "tags": ["class", "data_structure", "stack"],
        "expected": "正确实现栈的基本操作"
    },
    {
        "desc": "写一个Python程序，计算斐波那契数列的第100个数",
        "difficulty": "hard",
        "tags": ["algorithm", "recursion", "math"],
        "expected": "正确计算第100个斐波那契数"
    }
]
