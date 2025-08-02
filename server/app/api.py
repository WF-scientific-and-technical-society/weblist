import os
import json
import logging
from flask import Flask, request, jsonify, current_app
from werkzeug.utils import secure_filename
from pan123 import Pan123
from config.settings import DevelopmentConfig
from config.security import SecureVault
from threading import Lock
from pathlib import Path

# 初始化应用
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# 安全初始化
vault = SecureVault()
encryptor = vault.ENCRYPTOR

# 全局锁
api_lock = Lock()

class SecurePanAPI:
    def __init__(self, config_path="secure_settings.json"):
        self.config_path = Path(config_path)
        self._load_secure_config()
        self.pan = self._init_client()

    def _load_secure_config(self):
        """安全加载配置"""
        default_config = {
            "user": "",
            "enc_password": "",  # 加密存储
            "enc_auth_token": "",
            "default_path": "/"
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                try:
                    self.config = {**default_config, **json.load(f)}
                    # 实时解密
                    self.password = encryptor.decrypt(self.config['enc_password'])
                    self.auth_token = encryptor.decrypt(self.config['enc_auth_token'])
                except (json.JSONDecodeError, ValueError) as e:
                    current_app.logger.error(f"Config load error: {str(e)}")
                    raise

    def _init_client(self):
        """初始化安全客户端"""
        return Pan123(
            user_name=self.config['user'],
            pass_word=self.password,
            authorization=self.auth_token,
            input_pwd=False
        )

    def save_config(self):
        """安全保存配置"""
        secure_config = {
            **self.config,
            "enc_password": encryptor.encrypt(self.password),
            "enc_auth_token": encryptor.encrypt(self.auth_token)
        }
        
        with api_lock:
            with open(self.config_path, 'w') as f:
                json.dump(secure_config, f, indent=2)
            os.chmod(self.config_path, 0o600)

# API路由实现
@app.route('/api/login', methods=['POST'])
def login():
    """安全登录接口"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({"error": "Missing credentials"}), 400
            
        # 安全验证逻辑
        api = SecurePanAPI()
        api.config.update({
            "user": username,
            "password": password
        })
        
        # 模拟登录
        if api.pan.login() != 200:
            return jsonify({"error": "Authentication failed"}), 401
            
        # 安全保存
        api.save_config()
        
        return jsonify({
            "status": "success",
            "user": username,
            "auth_token": "******"  # 实际不返回token
        })
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# ... 其他API路由 ...

if __name__ == '__main__':
    # 安全启动检查
    if not Path('.vault.key').exists():
        vault = SecureVault()
        
    # 创建必要目录
    for dir in ['uploads', 'logs', 'data']:
        os.makedirs(dir, exist_ok=True)
    
    #启动
    app.run(ssl_context='adhoc', host='0.0.0.0', port=5000)
