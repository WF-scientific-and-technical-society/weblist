"""
config 包初始化文件
包含所有安全配置和项目设置的导出
"""

from .security import SecureVault, ConfigEncryptor
from .settings import AppConfig, DevelopmentConfig, ProductionConfig

# 版本信息
__version__ = "1.0.0"

# 包级别的初始化操作
def _init():
    """包初始化时的安全检查"""
    import os
    if not os.path.exists('.vault.key'):
        from .security import SecureVault
        SecureVault()  # 自动生成密钥文件

_init()  # 导入包时自动执行

__all__ = [
    'SecureVault',
    'ConfigEncryptor',
    'AppConfig',
    'DevelopmentConfig',
    'ProductionConfig'
]
