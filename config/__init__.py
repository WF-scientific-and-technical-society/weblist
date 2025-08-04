from .security import SecureVault, ConfigEncryptor
from .settings import AppConfig, DevelopmentConfig, ProductionConfig

__version__ = "1.0.0"

def _init():
    """包初始化时的安全检查"""
    import os
    if not os.path.exists('.vault.key'):
        from .security import SecureVault
        SecureVault()  # 自动生成密钥文件

_init()

__all__ = [
    'SecureVault',
    'ConfigEncryptor',
    'AppConfig',
    'DevelopmentConfig',
    'ProductionConfig'
]
