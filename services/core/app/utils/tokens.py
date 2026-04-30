"""Token 计算工具"""


def estimate_token_count(text: str) -> int:
    """估算 token 数量
    
    简单估算：中文约 1.5 字符/token，英文约 4 字符/token
    这里使用保守估计：4 字符 = 1 token
    """
    return len(text) // 4


def estimate_message_tokens(content: str, role: str = "user") -> int:
    """估算消息 token 数量"""
    # 加上角色和其他开销
    base_tokens = 4  # 角色开销
    content_tokens = estimate_token_count(content)
    return base_tokens + content_tokens