#!/usr/bin/env python3
"""响应检查器 - 检查违反规则、提取代码并测试"""

from utils.text_rules import check_forbidden_words
from utils.code_runner import extract_code, run_code

class ResponseChecker:
    """检查AI回复的组件"""
    
    def __init__(self):
        pass
    
    def check_response(self, reply):
        """检查回复是否违规、执行代码、生成标记
        
        Args:
            reply: AI的回复文本
            
        Returns:
            tuple: (result_tags, error_info)
                result_tags: 结果标记列表
                error_info: 错误信息字典
        """
        result_tags = []
        error_info = {}
        
        # 1. 检查禁语
        forbidden_words = check_forbidden_words(reply)
        if forbidden_words:
            result_tags.append("ASYNC_PROMISE")
            error_info["forbidden_words"] = forbidden_words
        
        # 2. 提取代码
        code_blocks = extract_code(reply)
        if code_blocks:
            code = code_blocks[0]  # 只处理第一个代码块
            
            # 3. 执行代码
            execution_result = run_code(code)
            
            if execution_result["success"]:
                result_tags.append("CODE_EXECUTED_SUCCESS")
                error_info["execution_output"] = execution_result["output"]
            else:
                result_tags.append("CODE_EXECUTED_FAILED")
                error_info["execution_error"] = execution_result["error"]
        else:
            result_tags.append("NO_CODE_BLOCK")
            error_info["no_code"] = "未找到代码块"
        
        return result_tags, error_info
