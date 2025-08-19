from flask import Flask, request, jsonify, session, render_template
from pan123 import Pan123
import api
import json
import os
import threading
import time  # 添加时间模块喵～
from task.task_start import main_background_task  # 导入后台任务函数喵～
with open(os.path.join(os.path.dirname(__file__), '..', 'config.json'),
          'r', encoding='utf-8') as f:
    config = json.load(f)

app = Flask(__name__, template_folder='../web',
            static_folder='../web/static',
            static_url_path='')
app.secret_key = 'd6c8a7f3e409b42d2a5e7c1f8d9b0a3e'

@app.route("/")
def index():
    return render_template('index_example.html', config=config)

@app.route("/api/admin/register", methods=['POST'])
def register():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "缺少用户名或密码"}), 400
    # 配置文件存在性校验
    if os.path.exists('User-account-password.json') and os.path.getsize(
        'User-account-password.json'
        ) > 0:
        try:
            with open('User-account-password.json', 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
                if existing_settings.get('username') or existing_settings.get(
                    'password'
                    ):
                    return jsonify({"error": "The.User-account-password.json.Is.Not.NULL"}), 409
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
        with open('User-account-password.json', 'w', encoding='utf-8') as f:
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
        with open('User-account-password.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data.get('username') == request.json.get('username') and data.get('password') == request.json.get('password'):
                session['username'] = data['username']
                return jsonify({"expires_in": "3600"})
            else:
                return jsonify({"error": "用户名或密码错误"}), 401
    except FileExistsError:
        return jsonify({"error": "NO.USER"}), 500
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
    try:
        api.list_folder(Path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    #进入文件目录
    files = api.list()
    return jsonify(files),200

@app.route("/api/admin/123pan-login" , methods=['POST'])
def LogInToTheNetworkDisk():
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

@app.route("/api/config", methods=['PUT'])
def update_config():
    # 获取请求体中的JSON数据
    data = request.json
    if not data:
        return jsonify({"code": 400, "message": "请求体不能为空"}), 400
    
    # 读取当前配置
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 更新site配置
    if 'site' in data:
        site_data = data['site']
        if 'title' in site_data:
            config['site']['title'] = site_data['title']
        if 'description' in site_data:
            config['site']['description'] = site_data['description']
    
    # 更新theme配置
    if 'theme' in data:
        theme_data = data['theme']
        if 'primary_color' in theme_data:
            config['theme']['primary_color'] = theme_data['primary_color']
    
    # 保存更新后的配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # 返回成功响应，固定返回指定的字段列表
    return jsonify({
        "code": 200,
        "message": "配置更新成功",
        "data": {
            "updated_fields": ["site.title", "site.description", "theme.primary_color"]
        }
    }), 200

if __name__ == "__main__":
    # 启动后台线程喵～
    def periodic_task():
        while True:
            main_background_task()  
            time.sleep(20)  
    
    thread = threading.Thread(target=periodic_task)
    thread.daemon = True 
    
    app.run(host='0.0.0.0', port=5000, debug=True)
