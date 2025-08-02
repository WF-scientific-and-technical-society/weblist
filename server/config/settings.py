import os
from pathlib import Path
from .security import ConfigEncryptor

BASE_DIR = Path(__file__).parent.parent

class AppConfig:
    # 安全配置
    ENCRYPTOR = ConfigEncryptor()
    SECRET_KEY = os.getenv('APP_SECRET', 'fallback-secret-key')
    
    # 数据库配置
    DB_PATH = BASE_DIR / 'data' / 'app.db'
    
    # 文件存储
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 2GB
    
    # 审计日志
    AUDIT_LOG = BASE_DIR / 'logs' / 'audit.log'
    
    @classmethod
    def get_safe_config(cls):
        """获取脱敏后的配置"""
        config = cls.__dict__.copy()
        for key in ['ENCRYPTOR', 'SECRET_KEY']:
            if key in config:
                config[key] = '******'
        return config

class DevelopmentConfig(AppConfig):
    DEBUG = True
    ALLOWED_EXTENSIONS = {'*'}

class ProductionConfig(AppConfig):
    DEBUG = False
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'jpg', 'png'}
