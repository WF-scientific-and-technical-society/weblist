import json
import os
from pan123 import Pan123

# 全局实例
_pan_instance = None

def _get_pan_instance():
    """获取Pan123实例，如果未初始化则初始化"""
    global _pan_instance
    if _pan_instance is None:
        # 读取The-password-of-the-user-account-of-the-network-disk.json配置文件
        settings_path = "The-password-of-the-user-account-of-the-network-disk.json"
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except FileExistsError:
                raise "NO.USER"
        else:
            settings = {}
        
        # 创建Pan123实例
        _pan_instance = Pan123()
    return _pan_instance

def _find_folder_by_name(name, parent_id=0):
    """根据文件夹名称查找文件夹ID"""
    pan = _get_pan_instance()
    pan.parent_file_id = parent_id
    pan.get_dir()
    
    for item in pan.list:
        if item["Type"] == 1 and item["FileName"] == name:
            return item["FileId"]
    return None

def _get_file_by_path(path):
    """根据路径获取文件或文件夹信息"""
    if not path.startswith("/"):
        path = "/" + path
    
    parts = path.strip("/").split("/")
    current_id = 0
    
    for part in parts:
        found = False
        pan = _get_pan_instance()
        pan.parent_file_id = current_id
        pan.get_dir()
        
        for item in pan.list:
            if item["FileName"] == part:
                current_id = item["FileId"]
                found = True
                break
        
        if not found:
            return None
    
    return current_id

def login(username=None, password=None):
    """
    登录123pan
    
    参数:
        username: 用户名，如果为None则从The-password-of-the-user-account-of-the-network-disk.json读取
        password: 密码，如果为None则从The-password-of-the-user-account-of-the-network-disk.json读取
    
    返回:
        {"status": "success"} 或 {"error": "错误信息"}
    """
    try:
        settings_path = "The-password-of-the-user-account-of-the-network-disk.json"
        settings = {}
        
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        
        # 确定使用的用户名和密码
        use_username = username or settings.get("username")
        use_password = password or settings.get("password")
        
        if not use_username or not use_password:
            return {"error": "用户名或密码未提供"}
        
        # 只有在提供了新凭据时才更新The-password-of-the-user-account-of-the-network-disk.json
        if username and password:
            settings["username"] = username
            settings["password"] = password
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        
        # 创建新的Pan123实例并登录
        global _pan_instance
        try:
            _pan_instance = Pan123(readfile=False, user_name=use_username, pass_word=use_password)
        except "NO.123.DISK.USER":
            return {"error": "未注册"}
        except Exception as e:
            return {"error": str(e)}
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

def list():
    """
    列出当前目录下的文件和文件夹
    
    返回:
        {
            "folder": [{"id": "1", "name": "镜像文件夹"}, ...],
            "file": [{"id": "4", "name": "win11镜像.iso", "size": "3.5GB"}, ...]
        }
        或 {"error": "主目录不合法"}
    """
    try:
        pan = _get_pan_instance()
        
        # 检查The-password-of-the-user-account-of-the-network-disk.json.json.json.json中的default-path
        settings_path = "The-password-of-the-user-account-of-the-network-disk.json"
        default_path = None
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                default_path = settings.get("default-path")
        
        if default_path:
            # 查找默认路径对应的文件夹ID
            folder_id = _find_folder_by_name(default_path)
            if folder_id is None:
                return {"error": "主目录不合法"}
            pan.parent_file_id = folder_id
        else:
            pan.parent_file_id = 0
        
        pan.get_dir()
        
        folders = []
        files = []
        
        for item in pan.list:
            if item["Type"] == 1:  # 文件夹
                folders.append({
                    "id": str(item["FileId"]),
                    "name": item["FileName"]
                })
            else:  # 文件
                size = item["Size"]
                if size > 1024 * 1024 * 1024:
                    size_str = f"{size / (1024 * 1024 * 1024):.1f}GB"
                elif size > 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.1f}MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.1f}KB"
                else:
                    size_str = f"{size}B"
                
                files.append({
                    "id": str(item["FileId"]),
                    "name": item["FileName"],
                    "size": size_str
                })
        
        return {
            "folder": folders,
            "file": files
        }
    except Exception as e:
        return {"error": str(e)}

def list_folder(path):
    """
    进入子目录
    
    参数:
        path: 文件夹路径，如"/学习资料/小猪佩奇全集"
    
    返回:
        {
            "folder": [{"id": "1", "name": "第三季"}, ...],
            "file": [{"id": "4", "name": "1.mp4", "size": "3.5GB"}, ...]
        }
        或 {"error": "没有找到对应文件夹或文件"}
    """
    try:
        folder_id = _get_file_by_path(path)
        if folder_id is None:
            return {"error": "没有找到对应文件夹或文件"}
        
        pan = _get_pan_instance()
        pan.parent_file_id = folder_id
        pan.get_dir()
        
        folders = []
        files = []
        
        for item in pan.list:
            if item["Type"] == 1:  # 文件夹
                folders.append({
                    "id": str(item["FileId"]),
                    "name": item["FileName"]
                })
            else:  # 文件
                size = item["Size"]
                if size > 1024 * 1024 * 1024:
                    size_str = f"{size / (1024 * 1024 * 1024):.1f}GB"
                elif size > 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.1f}MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.1f}KB"
                else:
                    size_str = f"{size}B"
                
                files.append({
                    "id": str(item["FileId"]),
                    "name": item["FileName"],
                    "size": size_str
                })
        
        return {
            "folder": folders,
            "file": files
        }
    except Exception as e:
        return {"error": str(e)}

def parsing(path):
    """
    解析文件获取下载链接
    
    参数:
        path: 文件路径，如"/学习资料/小猪佩奇全集/1.mp4"
    
    返回:
        {"url": "https://url.com/学习资料/小猪佩奇全集/1.mp4"}
        或 {"error": "没有找到对应文件夹或文件"}
    """
    try:
        file_id = _get_file_by_path(path)
        if file_id is None:
            return {"error": "没有找到对应文件夹或文件"}
        
        pan = _get_pan_instance()
        
        # 找到对应的文件索引
        file_index = None
        for i, item in enumerate(pan.list):
            if item["FileId"] == file_id and item["Type"] != 1:
                file_index = i
                break
        
        if file_index is None:
            return {"error": "没有找到对应文件夹或文件"}
        
        download_url = pan.link(file_index, showlink=False)
        return {"url": download_url}
    except Exception as e:
        return {"error": str(e)}

def share(path):
    """
    分享文件
    
    参数:
        path: 文件路径，如"/学习资料/小猪佩奇全集/1.mp4"
    
    返回:
        {"share_url": "https://www.123pan.com/s/xxx", "share_key": "xxx", "share_pwd": ""}
        或 {"error": "错误信息"}
    """
    try:
        file_id = _get_file_by_path(path)
        if file_id is None:
            return {"error": "没有找到对应文件夹或文件"}
        
        pan = _get_pan_instance()
        
        # 找到对应的文件
        file_info = None
        for item in pan.list:
            if item["FileId"] == file_id:
                file_info = item
                break
        
        if not file_info:
            return {"error": "没有找到对应文件夹或文件"}
        
        data = {
            "driveId": 0,
            "expiration": "2099-12-12T08:00:00+08:00",
            "fileIdList": str(file_id),
            "shareName": file_info["FileName"],
            "sharePwd": "",
            "event": "shareCreate"
        }
        
        import requests
        import json
        
        share_res = requests.post(
            "https://www.123pan.com/a/api/share/create",
            headers=pan.header_logined,
            data=json.dumps(data),
            timeout=10
        )
        
        share_res_json = share_res.json()
        if share_res_json["code"] != 0:
            return {"error": share_res_json["message"]}
        
        share_key = share_res_json["data"]["ShareKey"]
        share_url = f"https://www.123pan.com/s/{share_key}"
        
        return {
            "share_url": share_url,
            "share_key": share_key,
            "share_pwd": ""
        }
    except Exception as e:
        return {"error": str(e)}

def upload(local_path, remote_path="/"):
    """
    上传文件
    
    参数:
        local_path: 本地文件路径
        remote_path: 远程路径，默认为根目录
    
    返回:
        {"status": "success"}
        或 {"error": "错误信息"}
    """
    try:
        if remote_path != "/":
            folder_id = _get_file_by_path(remote_path)
            if folder_id is None:
                return {"error": "远程路径不存在"}
        else:
            folder_id = 0
        
        pan = _get_pan_instance()
        pan.parent_file_id = folder_id
        pan.up_load(local_path)
        
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

def delete(path):
    """
    删除文件或文件夹（包括空文件夹和非空文件夹）
    
    参数:
        path: 文件或文件夹路径
    
    返回:
        {"status": "success"}
        或 {"error": "错误信息"}
    """
    try:
        file_id = _get_file_by_path(path)
        if file_id is None:
            return {"error": "没有找到对应文件夹或文件"}
        
        pan = _get_pan_instance()
        
        # 找到对应的文件索引
        file_index = None
        for i, item in enumerate(pan.list):
            if item["FileId"] == file_id:
                file_index = i
                break
        
        if file_index is None:
            return {"error": "没有找到对应文件夹或文件"}
        
        pan.delete_file(file_index, by_num=True, operation=True)
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}

def delete_folder(path):
    """
    删除文件夹（包括空文件夹和非空文件夹）
    
    参数:
        path: 文件夹路径
    
    返回:
        {"status": "success", "deleted_files": 删除的文件数量}
        或 {"error": "错误信息"}
    """
    try:
        folder_id = _get_file_by_path(path)
        if folder_id is None:
            return {"error": "没有找到对应文件夹"}
        
        pan = _get_pan_instance()
        
        # 检查是否是文件夹
        is_folder = False
        for item in pan.list:
            if item["FileId"] == folder_id and item["Type"] == 1:
                is_folder = True
                break
        
        if not is_folder:
            return {"error": "指定路径不是文件夹"}
        
        # 删除文件夹及其内容
        import requests
        import json
        
        # 获取文件夹内容
        pan.parent_file_id = folder_id
        pan.get_dir()
        
        deleted_count = 0
        
        # 删除文件夹内的所有文件和子文件夹
        for item in pan.list:
            data_delete = {
                "driveId": 0,
                "fileTrashInfoList": [item],
                "operation": True,
            }
            
            delete_res = requests.post(
                "https://www.123pan.com/a/api/file/trash",
                data=json.dumps(data_delete),
                headers=pan.header_logined,
                timeout=10
            )
            
            if delete_res.json()["code"] == 0:
                deleted_count += 1
        
        # 最后删除文件夹本身
        # 找到文件夹在父目录中的索引
        parent_path = "/".join(path.strip("/").split("/")[:-1])
        if parent_path:
            parent_id = _get_file_by_path("/" + parent_path)
        else:
            parent_id = 0
        
        pan.parent_file_id = parent_id
        pan.get_dir()
        
        folder_index = None
        for i, item in enumerate(pan.list):
            if item["FileId"] == folder_id and item["Type"] == 1:
                folder_index = i
                break
        
        if folder_index is not None:
            pan.delete_file(folder_index, by_num=True, operation=True)
            deleted_count += 1
        
        return {"status": "success", "deleted_files": deleted_count}
    except Exception as e:
        return {"error": str(e)}

def create_folder(path, folder_name):
    """
    创建文件夹
    
    参数:
        path: 父目录路径
        folder_name: 新文件夹名称
    
    返回:
        {"status": "success", "folder_id": "新文件夹ID"}
        或 {"error": "错误信息"}
    """
    try:
        if path == "/":
            parent_id = 0
        else:
            parent_id = _get_file_by_path(path)
            if parent_id is None:
                return {"error": "父目录不存在"}
        
        pan = _get_pan_instance()
        
        import requests
        import json
        
        data = {
            "driveId": 0,
            "etag": "",
            "fileName": folder_name,
            "parentFileId": parent_id,
            "size": 0,
            "type": 1,
            "duplicate": 0
        }
        
        create_res = requests.post(
            "https://www.123pan.com/b/api/file/upload_request",
            headers=pan.header_logined,
            data=json.dumps(data),
            timeout=10
        )
        
        create_res_json = create_res.json()
        if create_res_json["code"] != 0:
            return {"error": create_res_json["message"]}
        
        return {"status": "success", "folder_id": str(create_res_json["data"]["FileId"])}
    except Exception as e:
        return {"error": str(e)}

def reload_session():
    """
    重新加载会话
    
    返回:
        {"status": "success"}
        或 {"error": "错误信息"}
    """
    try:
        global _pan_instance
        _pan_instance = None
        _get_pan_instance()
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
