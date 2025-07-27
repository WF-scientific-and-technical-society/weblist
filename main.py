from flask import Flask
import json
from pan123 import Pan123

app = Flask(__name__)
@app.route("/api/admin/register", methods=['POST'])
def register():
    data = app.request.json
    if not data or 'username' not in data or 'password' not in data:
        return app.jsonify({"error": "缺少用户名或密码"}), 400
    
    try:
        # 调用Pan123的认证功能
        pan = Pan123(readfile=False, 
                    user_name=data['username'],
                    pass_word=data['password'],
                    input_pwd=False)
        # 保存凭证到配置文件
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump({'username': data['username'], 'password': data['password']}, f)
        return app.jsonify({"status": "注册成功"})
    except Exception as e:
        return app.jsonify({"error": str(e)}), 500