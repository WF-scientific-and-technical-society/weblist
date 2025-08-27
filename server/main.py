from flask import Flask, request, jsonify, session, render_template
from pan123 import Pan123
import api
import json
import os
import threading
import time  # 添加时间模块喵～
from task.task_start import main_background_task  # 导入后台任务函数喵～
import bcrypt  # 密码加密库喵～
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

@app.route("/api/config", methods=['GET'])
def get_config():
    return jsonify(config)

@app.route("/api/list", methods=['GET'])
def list_files():
    # 获取查询参数
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=20, type=int)
    keyword = request.args.get('keyword', default='', type=str)
    file_type = request.args.get('file_type', default='', type=str)
    
    # 调用API获取文件列表
    try:
        # 获取当前目录下的所有文件和文件夹
        result = api.list()
        if "error" in result:
            return jsonify({
                "code": 500,
                "message": result["error"],
                "data": {}
            }), 500
        
        # 合并文件和文件夹列表
        all_items = []
        
        # 处理文件夹
        for folder in result["folder"]:
            item = {
                "file_id": folder["id"],
                "name": folder["name"],
                "size": 0,  # 文件夹大小为0
                "type": "folder",
                "upload_time": folder.get("upload_time", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),  # 使用元数据或当前时间
                "download_url": f"/api/files/{folder['id']}/download"
            }
            all_items.append(item)
        
        # 处理文件
        for file in result["file"]:
            # 从文件名中提取文件类型
            file_parts = file["name"].split(".")
            file_extension = file_parts[-1].lower() if len(file_parts) > 1 else ""
            
            # 将size_str转换为字节数（简化处理）
            size_str = file["size"]
            size_bytes = 0
            if size_str.endswith("GB"):
                size_bytes = int(float(size_str[:-2]) * 1024 * 1024 * 1024)
            elif size_str.endswith("MB"):
                size_bytes = int(float(size_str[:-2]) * 1024 * 1024)
            elif size_str.endswith("KB"):
                size_bytes = int(float(size_str[:-2]) * 1024)
            else:
                size_bytes = int(size_str[:-1]) if size_str.endswith("B") else 0
            
            item = {
                "file_id": file["id"],
                "name": file["name"],
                "size": size_bytes,
                "type": file_extension,
                "upload_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),  # 当前时间
                "download_url": f"/api/files/{file['id']}/download"
            }
            all_items.append(item)
        
        # 根据keyword过滤
        if keyword:
            all_items = [item for item in all_items if keyword.lower() in item["name"].lower()]
        
        # 根据file_type过滤
        if file_type:
            if file_type.lower() == "folder":
                all_items = [item for item in all_items if item["type"] == "folder"]
            else:
                all_items = [item for item in all_items if item["type"] == file_type.lower()]
        
        # 计算总数
        total = len(all_items)
        
        # 分页处理
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_items = all_items[start_index:end_index]
        
        # 返回结果
        return jsonify({
            "code": 200,
            "message": "success",
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "files": paginated_items
            }
        }), 200
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e),
            "data": {}
        }), 500

@app.route("/api/auth/password", methods=['PUT'])
def change_password():
    # 检查用户是否已登录
    if 'username' not in session:
        return jsonify({"code": 401, "message": "未登录"}), 401
    
    # 获取JSON数据
    data = request.json
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({"code": 400, "message": "缺少必要参数"}), 400
    
    old_password = data['old_password']
    new_password = data['new_password']
    
    try:
        # 读取用户账户文件
        with open('User-account-password.json', 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        
        # 验证旧密码是否正确
        if user_data.get('password') != old_password:
            return jsonify({"code": 400, "message": "旧密码错误"}), 400
        
        # 使用bcrypt加密新密码
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 保存新密码到文件
        user_data['password'] = hashed_password
        with open('User-account-password.json', 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({"code": 200, "message": "密码修改成功"}), 200
    except FileNotFoundError:
        return jsonify({"code": 500, "message": "用户账户文件不存在"}), 500
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

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
