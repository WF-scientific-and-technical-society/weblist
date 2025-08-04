"""
WebList 主包初始化文件
"""

# 导出核心功能
from .api import create_app
from .cli import main

# 版本控制
__version__ = "0.1.0"

# Flask应用实例
app = create_app()

# 包启动时的初始化操作
def _initialize():
    """确保必要的目录存在"""
    import os
    for dir in ['uploads', 'logs', 'data']:
        os.makedirs(dir, exist_ok=True)

_initialize()

__all__ = ['app', 'main', '__version__']
