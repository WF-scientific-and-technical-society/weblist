from flask import Flask, request, jsonify
from pan123 import Pan123
import json
import os

app = Flask(__name__)

@app.route("/api/admin/register", methods=['POST'])
def register():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "缺少用户名或密码"}), 400
    # 配置文件存在性校验
    if os.path.exists('settings.json') and os.path.getsize('settings.json') > 0:
        try:
            with open('settings.json', 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
                if existing_settings.get('username') or existing_settings.get('password'):
                    return jsonify({"error": "The.Setting.Is.Not.NULL"}), 409
        except json.JSONDecodeError:
            return app.jsonify({"error": "配置文件格式错误"}), 409
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    try:
        # 调用Pan123的认证功能
        pan = Pan123(readfile=False, 
                    user_name=data['username'],
                    pass_word=data['password'],
                    input_pwd=False)
        # 保存凭证到配置文件
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump({'username': data['username'], 'password': data['password']}, f)
        return jsonify({"status": "注册成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/admin/login", methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "缺少用户名或密码"}), 400
    try:
        # 调用Pan123的认证功能
        pan = Pan123(readfile=False, 
                    user_name=data['username'],
                    pass_word=data['password'],
                    input_pwd=False)
        return jsonify({
            "expires_in": "3600"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)