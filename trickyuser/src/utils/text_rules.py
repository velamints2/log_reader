#!/usr/bin/env python3
"""文本规则 - 违规内容检测规则库"""

# 禁语列表
FORBIDDEN_WORDS = [
    "稍后",
    "等会儿再说",
    "稍后再说",
    "稍后再聊",
    "等一下",
    "等一会儿",
    "暂时不",
    "现在不"
]

def check_forbidden_words(text):
    """检查文本中是否包含禁语
    
    Args:
        text: 要检查的文本
        
    Returns:
        list: 包含的禁语列表，如果没有则返回空列表
    """
    found_words = []
    for word in FORBIDDEN_WORDS:
        if word in text:
            found_words.append(word)
    return found_words
