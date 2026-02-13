import os
import sys
import json
from typing import Optional, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '123pan'))
from pan123 import Pan123

class Pan123Client:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, username: str = None, password: str = None, auto_login: bool = True):
        self.client = None
        self._username = username
        self._password = password
        if auto_login:
            self._initialize()
    
    def _initialize(self):
        settings_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '123pan', 'settings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            if not self._username:
                self._username = settings.get('username')
            if not self._password:
                self._password = settings.get('password')
        
        if self._username and self._password:
            self.client = Pan123(
                readfile=False,
                user_name=self._username,
                pass_word=self._password,
                input_pwd=False
            )
    
    def login(self, username: str = None, password: str = None) -> Dict[str, Any]:
        if username:
            self._username = username
        if password:
            self._password = password
        
        if not self._username or not self._password:
            return {"error": "用户名或密码未提供"}
        
        try:
            self.client = Pan123(
                readfile=False,
                user_name=self._username,
                pass_word=self._password,
                input_pwd=False
            )
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_quota(self) -> Dict[str, Any]:
        if not self.client:
            return {"error": "未登录"}
        try:
            url = "https://www.123pan.com/b/api/user/info"
            import requests
            res = requests.get(url, headers=self.client.header_logined, timeout=10)
            data = res.json()
            if data.get("code") == 0:
                return {
                    "success": True,
                    "data": {
                        "total": data["data"].get("spacePermanent", 0),
                        "used": data["data"].get("spaceUsed", 0)
                    }
                }
            return {"error": data.get("message", "获取配额失败")}
        except Exception as e:
            return {"error": str(e)}
    
    def search_files(self, keyword: str, path: str = "/") -> Dict[str, Any]:
        if not self.client:
            return {"error": "未登录"}
        try:
            if path != "/":
                folder_id = self._get_file_id_by_path(path)
                if folder_id is None:
                    return {"error": "路径不存在"}
                self.client.parent_file_id = folder_id
            else:
                self.client.parent_file_id = 0
            
            self.client.get_dir()
            results = {"folder": [], "file": []}
            
            for item in self.client.list:
                name = item.get("FileName", "")
                if keyword.lower() in name.lower():
                    if item["Type"] == 1:
                        results["folder"].append({
                            "id": str(item["FileId"]),
                            "name": name
                        })
                    else:
                        size = item["Size"]
                        size_str = self._format_size(size)
                        results["file"].append({
                            "id": str(item["FileId"]),
                            "name": name,
                            "size": size_str
                        })
            
            return results
        except Exception as e:
            return {"error": str(e)}
    
    def _get_file_id_by_path(self, path: str) -> Optional[int]:
        if not path.startswith("/"):
            path = "/" + path
        parts = path.strip("/").split("/")
        current_id = 0
        
        for part in parts:
            if not part:
                continue
            self.client.parent_file_id = current_id
            self.client.get_dir()
            found = False
            for item in self.client.list:
                if item["FileName"] == part:
                    current_id = item["FileId"]
                    found = True
                    break
            if not found:
                return None
        return current_id
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
