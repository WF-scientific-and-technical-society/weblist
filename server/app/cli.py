import click
from flask.cli import with_appcontext
from config.security import SecureVault
from config.settings import AppConfig
from business_logic.services.audit_service import SecureAuditLogger
import json
from pathlib import Path

@click.group()
def cli():
    """WebList 命令行工具"""
    pass

@cli.command()
@with_appcontext
def init():
    """初始化系统"""
    # 创建必要目录
    for dir in ['uploads', 'logs', 'data']:
        Path(dir).mkdir(exist_ok=True)
    
    # 初始化密钥
    vault = SecureVault()
    print(f"[✓] 系统初始化完成")
    print(f"密钥文件位置: {vault.master_key_path}")

@cli.command()
@click.option('--user', prompt=True, help='管理员用户名')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='管理员密码')
def create_admin(user, password):
    """创建管理员账户"""
    # 加密存储凭证
    encryptor = AppConfig.ENCRYPTOR
    secure_data = {
        "user": user,
        "enc_password": encryptor.encrypt(password),
        "role": "admin"
    }
    
    # 保存到安全配置
    config_path = Path("secure_settings.json")
    with open(config_path, 'w') as f:
        json.dump(secure_data, f, indent=2)
    
    # 设置文件权限
    config_path.chmod(0o600)
    print(f"[✓] 管理员 {user} 创建成功")

@cli.command()
@click.argument('log_type', default='all')
def show_logs(log_type):
    """查看审计日志"""
    logger = SecureAuditLogger(AppConfig.AUDIT_LOG)
    
    filters = {
        'all': None,
        'upload': lambda e: e['data']['action'] == 'upload',
        'delete': lambda e: e['data']['action'] == 'delete'
    }.get(log_type.lower())
    
    logs = logger.get_logs(filters)
    for log in logs[-10:]:  # 显示最后10条
        print(f"{log['timestamp']} {log['data']['action']} {log['data']['path']}")

@cli.command()
def rotate_keys():
    """轮换加密密钥"""
    from scripts.rotate_keys import rotate_keys
    rotate_keys()

if __name__ == '__main__':
    cli()
