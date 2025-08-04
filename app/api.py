import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from threading import Lock
from pathlib import Path
import jwt
from config.settings import DevelopmentConfig
from config.security import SecureVault
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
vault = SecureVault()
lock = Lock()
class SecureAPI:
    def __init__(self, config="secure_settings.json"):
        self.config_path = Path(config)
        self.config = self._load_config()
        self.client = self._init_client()
    def _load_config(self):
        defaults = {"user": "", "enc_password": "", "enc_token": ""}
        if self.config_path.exists():
            with open(self.config_path) as f:
                return {**defaults, **json.load(f)}
        return defaults
    def _init_client(self):
        from pan123 import Pan123  # 延迟导入减少启动依赖
        return Pan123(
            user_name=self.config["user"],
            pass_word=vault.decrypt(self.config["enc_password"]),
            authorization=vault.decrypt(self.config["enc_token"]),
            input_pwd=False
        )
    def _generate_token(self, username):
        """生成JWT令牌"""
        return jwt.encode(
            {
                'sub': username,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    def save(self):
        secure = {
            **self.config,
            "enc_password": vault.encrypt(self.config["password"]),
            "enc_token": vault.encrypt(self.config["token"])
        }
        with lock:
            with open(self.config_path, 'w') as f:
                json.dump(secure, f, indent=2)
            os.chmod(self.config_path, 0o600)
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not all(k in data for k in ('username', 'password')):
            return jsonify({"error": "Missing credentials"}), 400
        # 这里应替换为真实的用户验证逻辑
        if not (data["username"] == "admin" and data["password"] == "secret"):
            return jsonify({"error": "Invalid credentials"}), 401
        api = SecureAPI()
        token = api._generate_token(data["username"])
        api.config.update({
            "user": data["username"],
            "password": data["password"],
            "token": token
        })
        api.save()
        return jsonify({
            "status": "success",
            "user": data["username"],
            "token": token,
            "expires_in": 3600
        })
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Server error"}), 500
if __name__ == '__main__':
    if not Path('.vault.key').exists():
        SecureVault()
    app.run(host='0.0.0.0', port=5000)
