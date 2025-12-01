#!/usr/bin/env python3
"""TrickyUser - 世界上最刁钻的用户系统主入口"""

import os
import json
from datetime import datetime

# 导入核心组件
from core.scenario_generator import ScenarioGenerator
from core.reminder_injector import ReminderInjector
from core.cursor_adapter import CursorAdapter
from core.response_checker import ResponseChecker
from core.next_prompt_generator import NextPromptGenerator
from store.state_manager import StateManager

# 导入配置
from config import scenarios, prompt_reminder

class TrickyUser:
    """TrickyUser 主控制器"""
    
    def __init__(self):
        self.scenario_generator = ScenarioGenerator()
        self.reminder_injector = ReminderInjector(prompt_reminder)
        self.cursor_adapter = CursorAdapter()
        self.response_checker = ResponseChecker()
        self.next_prompt_generator = NextPromptGenerator()
        self.state_manager = StateManager()
        
        # 初始化状态
        self.state = self.state_manager.load_state()
        
    def run_round(self):
        """运行一轮测试"""
        print(f"\n=== 开始第 {self.state.get('round', 1)} 轮测试 ===")
        
        # 1. 生成刁钻场景
        task_description = self.scenario_generator.generate_task(self.state)
        print(f"生成的任务: {task_description}")
        
        # 2. 注入行为约束提醒
        prompt = self.reminder_injector.inject_reminder(task_description)
        print(f"完整提示: {prompt[:100]}...")
        
        # 3. 调用 Cursor AI
        reply = self.cursor_adapter.call_cursor(prompt)
        print(f"AI 回复: {reply[:100]}...")
        
        # 4. 检查回复
        result_tags, error_info = self.response_checker.check_response(reply)
        print(f"检查结果: {result_tags}, 错误信息: {error_info}")
        
        # 5. 生成下一轮任务
        self.state = self.next_prompt_generator.generate_next_prompt(
            self.state, result_tags, error_info
        )
        
        # 6. 保存状态
        self.state_manager.save_state(self.state)
        
        # 7. 记录日志
        self._log_round(prompt, reply, result_tags, error_info)
        
        print(f"=== 第 {self.state.get('round', 1) - 1} 轮测试结束 ===")
    
    def _log_round(self, prompt, reply, result_tags, error_info):
        """记录一轮对话到日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "round": self.state.get('round', 1) - 1,
            "prompt": prompt,
            "reply": reply,
            "result_tags": result_tags,
            "error_info": error_info,
            "state": self.state
        }
        
        # 写入历史日志
        with open("trickyuser/logs/history.jsonl", "a", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write("\n")
    
    def run(self, rounds=10):
        """运行多轮测试"""
        print("🚀 TrickyUser MVP 启动")
        
        for _ in range(rounds):
            self.run_round()
            
            # 更新轮数
            self.state["round"] = self.state.get("round", 1) + 1
        
        print("🎉 测试完成")

if __name__ == "__main__":
    tricky_user = TrickyUser()
    tricky_user.run()
