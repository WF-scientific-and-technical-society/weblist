from functools import wraps
from ..models.permission import check_permission, Permission, UserRole
import re

PROTECTED_PATHS = [
    "/config",
    "/system",
    "/logs",
    "/admin"
]

def require_permission(permission):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_role = kwargs.get('user_role', UserRole.USER)
            if not check_permission(user_role, permission):
                raise PermissionError(f"需要{permission}权限")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_path_access(user_role, path):
    """验证路径访问权限"""
    if user_role == UserRole.ADMIN:
        return True
    
    # 标准化路径
    normalized_path = path.strip('/')
    
    for protected_path in PROTECTED_PATHS:
        clean_path = protected_path.strip('/')
        if normalized_path.startswith(clean_path):
            return False
    
    return True

def is_safe_filename(filename):
    """检查文件名安全性"""
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    return not any(char in filename for char in dangerous_chars)
