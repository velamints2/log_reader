#!/usr/bin/env python3
"""状态管理器 - 维护 state.json 的读写"""

import os
import json

class StateManager:
    """管理状态的组件"""
    
    def __init__(self):
        self.state_file = "trickyuser/src/store/state.json"
        self.default_state = {
            "round": 1,
            "difficulty": "easy",
            "feedback": "初始状态",
            "last_result_tags": [],
            "last_error_info": {}
        }
    
    def load_state(self):
        """加载状态
        
        Returns:
            dict: 当前状态
        """
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return self.default_state
        except Exception as e:
            print(f"加载状态失败: {e}")
            return self.default_state
    
    def save_state(self, state):
        """保存状态
        
        Args:
            state: 要保存的状态字典
        """
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}")
