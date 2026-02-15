import json
import os
import hashlib
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import jwt

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'config', 'config.json')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'config', 'backups')

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

def save_config(config):
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Save config error: {e}")
        return False

def validate_color(color):
    hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    rgb_pattern = r'^rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)$'
    hsl_pattern = r'^hsl\(\s*\d{1,3}\s*,\s*\d{1,3}%?\s*,\s*\d{1,3}%?\s*\)$'
    return bool(re.match(hex_pattern, color) or re.match(rgb_pattern, color) or re.match(hsl_pattern, color))

def sanitize_html(html_content):
    dangerous_tags = ['<script', '</script>', 'javascript:', 'onerror=', 'onclick=', 'onload=']
    sanitized = html_content
    for tag in dangerous_tags:
        sanitized = sanitized.replace(tag, '')
    return sanitized

def create_backup():
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        config = load_config()
        if "error" in config:
            return None
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(BACKUP_DIR, f'config_backup_{timestamp}.json')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return timestamp
    except Exception as e:
        print(f"Backup error: {e}")
        return None

def get_token_from_request():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None

def generate_token(username):
    config = load_config()
    secret = config.get('auth', {}).get('jwt_secret', 'default-secret')
    expire_hours = config.get('auth', {}).get('token_expire_hours', 24)
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=expire_hours),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, secret, algorithm='HS256')

def verify_token(token):
    try:
        config = load_config()
        secret = config.get('auth', {}).get('jwt_secret', 'default-secret')
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'code': 401, 'message': '未提供认证令牌', 'data': None}), 401
        payload = verify_token(token)
        if not payload:
            return jsonify({'code': 401, 'message': '令牌无效或已过期', 'data': None}), 401
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    config = load_config()
    if "error" in config:
        return jsonify({'code': 500, 'message': config['error'], 'data': None}), 500
    safe_config = config.copy()
    if 'auth' in safe_config:
        del safe_config['auth']
    return jsonify({'code': 200, 'message': 'success', 'data': safe_config})

@app.route('/api/config/<section>', methods=['GET'])
def get_config_section(section):
    config = load_config()
    if "error" in config:
        return jsonify({'code': 500, 'message': config['error'], 'data': None}), 500
    if section not in config:
        return jsonify({'code': 404, 'message': f'配置段 {section} 不存在', 'data': None}), 404
    return jsonify({'code': 200, 'message': 'success', 'data': config[section]})

@app.route('/api/config', methods=['PUT'])
@require_auth
def update_config():
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'code': 400, 'message': '请求体不能为空', 'data': None}), 400
        create_backup()
        current_config = load_config()
        if "error" in current_config:
            return jsonify({'code': 500, 'message': current_config['error'], 'data': None}), 500
        updated_fields = []
        for key, value in new_config.items():
            if key == 'auth':
                continue
            if key == 'theme' and isinstance(value, dict):
                for color_key in ['primary_color', 'secondary_color', 'background_color', 'text_color', 'border_color', 'hover_color']:
                    if color_key in value and not validate_color(value[color_key]):
                        return jsonify({'code': 400, 'message': f'颜色值 {color_key} 格式不正确', 'data': None}), 400
            if key == 'layout' and isinstance(value, dict):
                for html_key in ['header_html', 'footer_html']:
                    if html_key in value:
                        value[html_key] = sanitize_html(value[html_key])
            current_config[key] = value
            updated_fields.append(key)
        if save_config(current_config):
            return jsonify({'code': 200, 'message': '配置更新成功', 'data': {'updated_fields': updated_fields}})
        return jsonify({'code': 500, 'message': '保存配置失败', 'data': None}), 500
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/config/<section>', methods=['PATCH'])
@require_auth
def update_config_section(section):
    try:
        new_section = request.get_json()
        if not new_section:
            return jsonify({'code': 400, 'message': '请求体不能为空', 'data': None}), 400
        create_backup()
        current_config = load_config()
        if "error" in current_config:
            return jsonify({'code': 500, 'message': current_config['error'], 'data': None}), 500
        if section not in current_config:
            return jsonify({'code': 404, 'message': f'配置段 {section} 不存在', 'data': None}), 404
        if section == 'theme':
            for color_key in ['primary_color', 'secondary_color', 'background_color', 'text_color', 'border_color', 'hover_color']:
                if color_key in new_section and not validate_color(new_section[color_key]):
                    return jsonify({'code': 400, 'message': f'颜色值 {color_key} 格式不正确', 'data': None}), 400
        if section == 'layout':
            for html_key in ['header_html', 'footer_html']:
                if html_key in new_section:
                    new_section[html_key] = sanitize_html(new_section[html_key])
        current_config[section].update(new_section)
        if save_config(current_config):
            return jsonify({'code': 200, 'message': f'{section} 配置更新成功', 'data': current_config[section]})
        return jsonify({'code': 500, 'message': '保存配置失败', 'data': None}), 500
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/config/validate', methods=['POST'])
def validate_config():
    try:
        config_data = request.get_json()
        errors = []
        if 'theme' in config_data:
            for color_key in ['primary_color', 'secondary_color', 'background_color', 'text_color', 'border_color', 'hover_color']:
                if color_key in config_data['theme']:
                    if not validate_color(config_data['theme'][color_key]):
                        errors.append(f'颜色值 {color_key} 格式不正确')
        if 'upload' in config_data:
            if 'max_file_size' in config_data['upload']:
                if not isinstance(config_data['upload']['max_file_size'], int) or config_data['upload']['max_file_size'] <= 0:
                    errors.append('max_file_size 必须是正整数')
        return jsonify({'code': 200, 'message': '验证完成', 'data': {'valid': len(errors) == 0, 'errors': errors}})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/config/backup', methods=['POST'])
@require_auth
def backup_config():
    timestamp = create_backup()
    if timestamp:
        return jsonify({'code': 200, 'message': '备份创建成功', 'data': {'backup_id': timestamp}})
    return jsonify({'code': 500, 'message': '备份创建失败', 'data': None}), 500

@app.route('/api/config/backups', methods=['GET'])
@require_auth
def list_backups():
    try:
        if not os.path.exists(BACKUP_DIR):
            return jsonify({'code': 200, 'message': 'success', 'data': {'backups': []}})
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith('config_backup_') and filename.endswith('.json'):
                backup_id = filename.replace('config_backup_', '').replace('.json', '')
                filepath = os.path.join(BACKUP_DIR, filename)
                stat = os.stat(filepath)
                backups.append({
                    'backup_id': backup_id,
                    'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'size': stat.st_size
                })
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return jsonify({'code': 200, 'message': 'success', 'data': {'backups': backups}})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/config/restore/<backup_id>', methods=['POST'])
@require_auth
def restore_backup(backup_id):
    try:
        backup_path = os.path.join(BACKUP_DIR, f'config_backup_{backup_id}.json')
        if not os.path.exists(backup_path):
            return jsonify({'code': 404, 'message': '备份文件不存在', 'data': None}), 404
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_config = json.load(f)
        if save_config(backup_config):
            return jsonify({'code': 200, 'message': '配置恢复成功', 'data': None})
        return jsonify({'code': 500, 'message': '恢复配置失败', 'data': None}), 500
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/config/theme', methods=['GET'])
def get_theme():
    config = load_config()
    if "error" in config:
        return jsonify({'code': 500, 'message': config['error'], 'data': None}), 500
    return jsonify({'code': 200, 'message': 'success', 'data': config.get('theme', {})})

@app.route('/api/config/theme', methods=['PUT'])
@require_auth
def update_theme():
    return update_config_section('theme')

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        config = load_config()
        if "error" in config:
            return jsonify({'code': 500, 'message': config['error'], 'data': None}), 500
        
        admin_username = config.get('auth', {}).get('admin_username', 'admin')
        stored_password_hash = config.get('auth', {}).get('admin_password_hash', '')
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username == admin_username and (not stored_password_hash or password_hash == stored_password_hash):
            token = generate_token(username)
            return jsonify({
                'code': 200,
                'message': '登录成功',
                'data': {'token': token, 'username': username}
            })
        
        return jsonify({'code': 401, 'message': '用户名或密码错误', 'data': None}), 401
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/auth/password', methods=['PUT'])
@require_auth
def change_password():
    try:
        data = request.get_json()
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or not new_password:
            return jsonify({'code': 400, 'message': '密码不能为空', 'data': None}), 400
        
        config = load_config()
        if "error" in config:
            return jsonify({'code': 500, 'message': config['error'], 'data': None}), 500
        
        old_hash = hashlib.sha256(old_password.encode()).hexdigest()
        stored_hash = config.get('auth', {}).get('admin_password_hash', '')
        
        if stored_hash and old_hash != stored_hash:
            return jsonify({'code': 400, 'message': '原密码错误', 'data': None}), 400
        
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        config.setdefault('auth', {})['admin_password_hash'] = new_hash
        
        if save_config(config):
            return jsonify({'code': 200, 'message': '密码修改成功', 'data': None})
        return jsonify({'code': 500, 'message': '保存密码失败', 'data': None}), 500
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/auth/check', methods=['GET'])
@require_auth
def check_auth():
    return jsonify({'code': 200, 'message': '已认证', 'data': {'username': request.current_user.get('username')}})

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '123pan'))
import api as pan_api

@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        path = request.args.get('path', '/')
        result = pan_api.list_folder(path) if path != '/' else pan_api.list()
        
        if 'error' in result:
            return jsonify({'code': 400, 'message': result['error'], 'data': None}), 400
        
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/list', methods=['GET'])
def list_files_paginated():
    try:
        path = request.args.get('path', '/')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        keyword = request.args.get('keyword', '')
        file_type = request.args.get('file_type', '')
        
        result = pan_api.list_folder(path) if path != '/' else pan_api.list()
        
        if 'error' in result:
            return jsonify({'code': 400, 'message': result['error'], 'data': None}), 400
        
        folders = result.get('folder', [])
        files = result.get('file', [])
        
        if keyword:
            folders = [f for f in folders if keyword.lower() in f.get('name', '').lower()]
            files = [f for f in files if keyword.lower() in f.get('name', '').lower()]
        
        if file_type:
            files = [f for f in files if f.get('name', '').lower().endswith(f'.{file_type.lower()}')]
        
        all_items = folders + files
        total = len(all_items)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = all_items[start:end]
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'folders': folders,
                'files': files
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/download', methods=['GET'])
def download_file():
    try:
        path = request.args.get('path', '')
        if not path:
            return jsonify({'code': 400, 'message': '路径不能为空', 'data': None}), 400
        
        result = pan_api.parsing(path)
        
        if 'error' in result:
            return jsonify({'code': 400, 'message': result['error'], 'data': None}), 400
        
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/upload', methods=['POST'])
@require_auth
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'code': 400, 'message': '没有上传文件', 'data': None}), 400
        
        file = request.files['file']
        remote_path = request.form.get('path', '/')
        
        if file.filename == '':
            return jsonify({'code': 400, 'message': '文件名为空', 'data': None}), 400
        
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            result = pan_api.upload(tmp_path, remote_path, file.filename)
        finally:
            os.unlink(tmp_path)
        
        if 'error' in result:
            return jsonify({'code': 400, 'message': result['error'], 'data': None}), 400
        
        return jsonify({'code': 200, 'message': '上传成功', 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/folder', methods=['POST'])
@require_auth
def create_folder():
    try:
        data = request.get_json()
        parent_path = data.get('parentPath', '/')
        folder_name = data.get('name', '')
        
        if not folder_name:
            return jsonify({'code': 400, 'message': '文件夹名称不能为空', 'data': None}), 400
        
        result = pan_api.create_folder(parent_path, folder_name)
        
        if 'error' in result:
            return jsonify({'code': 400, 'message': result['error'], 'data': None}), 400
        
        return jsonify({'code': 200, 'message': '创建成功', 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/files', methods=['DELETE'])
@require_auth
def delete_file():
    try:
        path = request.args.get('path', '')
        if not path:
            return jsonify({'code': 400, 'message': '路径不能为空', 'data': None}), 400
        
        result = pan_api.delete(path)
        
        if 'error' in result:
            return jsonify({'code': 400, 'message': result['error'], 'data': None}), 400
        
        return jsonify({'code': 200, 'message': '删除成功', 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/share', methods=['POST'])
@require_auth
def share_file():
    try:
        data = request.get_json()
        path = data.get('path', '')
        
        if not path:
            return jsonify({'code': 400, 'message': '路径不能为空', 'data': None}), 400
        
        result = pan_api.share(path)
        
        if 'error' in result:
            return jsonify({'code': 400, 'message': result['error'], 'data': None}), 400
        
        return jsonify({'code': 200, 'message': '分享成功', 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/search', methods=['GET'])
def search_files():
    try:
        keyword = request.args.get('keyword', '')
        path = request.args.get('path', '/')
        
        if not keyword:
            return jsonify({'code': 400, 'message': '搜索关键词不能为空', 'data': None}), 400
        
        result = pan_api.list_folder(path) if path != '/' else pan_api.list()
        
        if 'error' in result:
            return jsonify({'code': 400, 'message': result['error'], 'data': None}), 400
        
        folders = [f for f in result.get('folder', []) if keyword.lower() in f.get('name', '').lower()]
        files = [f for f in result.get('file', []) if keyword.lower() in f.get('name', '').lower()]
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'folders': folders,
                'files': files,
                'total': len(folders) + len(files)
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

LOG_FILE = 'audit.log'

@app.route('/api/logs', methods=['GET'])
@require_auth
def get_logs():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        start_time = request.args.get('start_time', '')
        end_time = request.args.get('end_time', '')
        
        if not os.path.exists(LOG_FILE):
            return jsonify({'code': 200, 'message': 'success', 'data': {'logs': [], 'total': 0}})
        
        logs = []
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    parts = line.split(' - ', 3)
                    if len(parts) >= 4:
                        log_data = json.loads(parts[3])
                        logs.append({
                            'timestamp': parts[0],
                            'level': parts[2],
                            **log_data
                        })
                except:
                    continue
        
        if start_time:
            logs = [l for l in logs if l.get('timestamp', '') >= start_time]
        if end_time:
            logs = [l for l in logs if l.get('timestamp', '') <= end_time]
        
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        total = len(logs)
        start = (page - 1) * page_size
        end = start + page_size
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'logs': logs[start:end],
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

@app.route('/api/business/stats', methods=['GET'])
@require_auth
def get_stats():
    try:
        result = pan_api.list()
        
        if 'error' in result:
            return jsonify({'code': 400, 'message': result['error'], 'data': None}), 400
        
        total_files = len(result.get('file', []))
        total_folders = len(result.get('folder', []))
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total_files': total_files,
                'total_folders': total_folders
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
