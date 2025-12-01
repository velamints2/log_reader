#!/usr/bin/env python3
"""Cursor适配器 - 与Cursor AI交互（API层）"""

class CursorAdapter:
    """与Cursor AI交互的组件"""
    
    def __init__(self):
        # MVP阶段使用mock实现
        self.mock_responses = {
            "easy": "```python\nprint('Hello, World!')\n```",
            "medium": "```python\ndef sum_of_squares(numbers):\n    return sum(x**2 for x in numbers if x % 2 == 0)\n\n# 测试\nprint(sum_of_squares([1, 2, 3, 4, 5]))\n```",
            "hard": "```python\ndef fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n-1):\n        a, b = b, a + b\n    return a\n\n# 计算第100个斐波那契数\nprint(fibonacci(100))\n```"
        }
    
    def call_cursor(self, prompt):
        """调用Cursor LLM接口
        
        Args:
            prompt: 完整的提示文本
            
        Returns:
            str: AI的回复
        """
        # MVP阶段使用mock实现，根据提示难度返回不同的mock回复
        if "Hello World" in prompt:
            return self.mock_responses["easy"]
        elif "平方和" in prompt or "栈数据结构" in prompt or "单词频率" in prompt:
            return self.mock_responses["medium"]
        else:
            return self.mock_responses["hard"]
