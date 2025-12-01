#!/usr/bin/env python3
"""提醒注入器 - 注入行为约束提醒块"""

class ReminderInjector:
    """将行为约束提醒块与任务内容拼接的组件"""
    
    def __init__(self, reminder_text):
        """初始化提醒注入器
        
        Args:
            reminder_text: 行为约束提醒文本
        """
        self.reminder_text = reminder_text
    
    def inject_reminder(self, task_description):
        """拼接提醒块与任务内容
        
        Args:
            task_description: 任务描述
            
        Returns:
            str: 完整的提示文本
        """
        # 简单实现：直接拼接提醒文本和任务描述
        return f"{self.reminder_text}\n\n{task_description}"
