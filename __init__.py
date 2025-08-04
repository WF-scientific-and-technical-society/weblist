from .api import create_app
from .cli import main

__version__ = "0.1.0"

app = create_app()

def _initialize():
    """确保必要的目录存在"""
    import os
    for dir in ['uploads', 'logs', 'data']:
        os.makedirs(dir, exist_ok=True)

_initialize()

__all__ = ['app', 'main', '__version__']
