#!/usr/bin/env python3
"""代码运行器 - 提取代码并本地执行（沙盒/安全模式）"""

import re
import subprocess
import sys
import tempfile
import os

def extract_code(text):
    """提取文本中的Python代码块
    
    Args:
        text: 包含代码块的文本
        
    Returns:
        list: 提取的Python代码块列表
    """
    # 匹配 ```python ... ``` 格式的代码块
    pattern = r'```python\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

def run_code(code):
    """在安全模式下执行Python代码
    
    Args:
        code: 要执行的Python代码
        
    Returns:
        dict: 执行结果，包含success、output和error字段
    """
    result = {
        "success": False,
        "output": "",
        "error": ""
    }
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file_name = f.name
        
        # 执行代码
        completed_process = subprocess.run(
            [sys.executable, temp_file_name],
            capture_output=True,
            text=True,
            timeout=5  # 设置5秒超时
        )
        
        # 收集结果
        if completed_process.returncode == 0:
            result["success"] = True
            result["output"] = completed_process.stdout
        else:
            result["error"] = completed_process.stderr
        
    except subprocess.TimeoutExpired:
        result["error"] = "代码执行超时（5秒）"
    except Exception as e:
        result["error"] = str(e)
    finally:
        # 清理临时文件
        if 'temp_file_name' in locals() and os.path.exists(temp_file_name):
            os.unlink(temp_file_name)
    
    return result
