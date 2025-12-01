#!/usr/bin/env python3
"""下一轮提示生成器 - 根据错误制造更刁钻的下一轮任务"""

class NextPromptGenerator:
    """生成下一轮任务的组件"""
    
    def __init__(self):
        pass
    
    def generate_next_prompt(self, state, result_tags, error_info):
        """根据违规情况生成下一任务
        
        Args:
            state: 当前状态字典
            result_tags: 结果标记列表
            error_info: 错误信息字典
            
        Returns:
            dict: 更新后的状态
        """
        # 更新状态
        state["last_result_tags"] = result_tags
        state["last_error_info"] = error_info
        
        # 根据错误类型生成更刁钻的任务
        if "ASYNC_PROMISE" in result_tags:
            # 如果有禁语，生成更严格的任务
            state["difficulty"] = "hard"
            state["feedback"] = "上一轮回复中包含禁语，请严格遵守规则"
        elif "CODE_EXECUTED_FAILED" in result_tags:
            # 如果代码执行失败，生成类似但更简单的任务
            state["difficulty"] = "medium"
            state["feedback"] = f"上一轮代码执行失败: {error_info.get('execution_error', '')}"
        elif "NO_CODE_BLOCK" in result_tags:
            # 如果没有代码块，生成明确要求代码的任务
            state["difficulty"] = "easy"
            state["feedback"] = "上一轮回复中没有代码块，请提供可运行的代码"
        else:
            # 如果成功，增加难度
            if state.get("difficulty") == "easy":
                state["difficulty"] = "medium"
            elif state.get("difficulty") == "medium":
                state["difficulty"] = "hard"
            state["feedback"] = "上一轮回复成功，增加难度"
        
        return state
