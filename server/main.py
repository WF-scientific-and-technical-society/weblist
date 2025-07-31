from flask import Flask, request, jsonify, session, render_template
from pan123 import Pan123
#from config import config
import api
import json
import os

app = Flask(__name__, template_folder='../web/templates')
app.secret_key = 'd6c8a7f3e409b42d2a5e7c1f8d9b0a3e'

@app.route("/")
def index():
    return render_template('index.html', config=config)
@app.route("/api/admin/register", methods=['POST'])
def register():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "缺少用户名或密码"}), 400
    # 配置文件存在性校验
    if os.path.exists('settings.json') and os.path.getsize(
        'settings.json'
        ) > 0:
        try:
            with open('settings.json', 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
                if existing_settings.get('username') or existing_settings.get(
                    'password'
                    ):
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
            json.dump({
                'username': data['username'],
                'password': data['password']},
                f
            )
        return jsonify({"status": "注册成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/admin/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "缺少用户名或密码"}), 400
    try:
        pan = Pan123(readfile=False, 
                    user_name=data['username'],
                    pass_word=data['password'],
                    input_pwd=False)
        session['username'] = data['username']  # 新增session存储
        return jsonify({"expires_in": "3600"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/admin/check")
def check():
    if 'username' in session:
        return jsonify({"logged_in": True,"username":session['username']}), 200
    return jsonify({"logged_in": False}), 401

@app.route("/api/files")
def files():
    Path = request.args.get('path')
    api.list_folder(Path)
    #进入文件目录
    files = api.list()
    return jsonify({files}),200

@app.route("/api/admin/123pan-login" , methods=['POST'])
def LogInToTheNetworkDisk():
    data = request.json
    username = data['username']
    password = data['password']
    back = api.login(username , password)
    if(back != ({"status": "success"})):
        return jsonify ({"outcome": "False"}),200
    else :
        return jsonify ({"outcome": "Ture"}),200

@app.route("/api/upload")
def upload():
    data = request.json
    path = data['path']
    file = data['file']
    back = api.upload(file , path)
    if(back != ({"status": "success"})):
        return jsonify ({"outcome": "False"}),200
    else :
        return jsonify ({"outcome": "True"}),200
    
@app.route("/api/download")
def download():
    Path = request.args.get('path')
    back = api.download(Path)
    if(back != ({"error": "没有找到对应文件夹或文件"})):
        return jsonify ({"outcome": "False"}),200
    else :
        return jsonify ({back}),200
    
@app.route("/api/delete")
def delete():
    Path = request.args.get('path')
    back = api.delete(Path)
    if(back != ({"error": "没有找到对应文件夹或文件"})):
        return jsonify ({"outcome": "False"}),200
    else :
        return jsonify ({"outcome": "True"}),200

@app.route("/api/folder/create")
def create_folder():
    data = request.json
    path = data['path']
    folder_name = data['folder_name']
    back = api.create_folder(folder_name, path)
    if(back != ({"status": "success"})):
        return jsonify ({"outcome": "False"}),200
    else :
        return jsonify ({"outcome": "True"}),200

@app.route("/api/folder/delete")
def delete_folder():
    data = request.json
    path = data['path']
    back = api.delete_folder(path)
    if(back != ({"status": "success"})):
        return jsonify ({"outcome": "False"}),200
    else :
        return jsonify ({"outcome": "True"}),200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)