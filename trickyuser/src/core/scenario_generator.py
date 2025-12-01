#!/usr/bin/env python3
"""场景生成器 - 生成刁钻测试场景"""

class ScenarioGenerator:
    """生成刁钻测试场景的组件"""
    
    def __init__(self):
        # 初始测试场景列表
        self.scenarios = [
            {
                "desc": "写一个可运行的Python Hello World代码",
                "difficulty": "easy"
            },
            {
                "desc": "写一个Python函数，接收一个列表，返回列表中所有偶数的平方和",
                "difficulty": "medium"
            },
            {
                "desc": "写一个Python程序，读取本地文件test.txt，统计其中每个单词出现的频率",
                "difficulty": "medium"
            },
            {
                "desc": "写一个Python类，实现一个简单的栈数据结构，包含push、pop、peek方法",
                "difficulty": "medium"
            },
            {
                "desc": "写一个Python程序，计算斐波那契数列的第100个数",
                "difficulty": "hard"
            }
        ]
    
    def generate_task(self, state):
        """生成任务描述
        
        Args:
            state: 当前状态字典
            
        Returns:
            str: 任务描述
        """
        # 简单实现：根据当前轮数选择不同难度的场景
        round_num = state.get("round", 1)
        scenario_index = (round_num - 1) % len(self.scenarios)
        
        return self.scenarios[scenario_index]["desc"]
