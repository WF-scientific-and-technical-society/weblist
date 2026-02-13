import os
import sys
import json
import mimetypes
from pathlib import Path
from typing import Optional, Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '123pan'))
import api as original_api

class Pan123API:
    def __init__(self):
        self._initialized = False
    
    def _ensure_initialized(self):
        if not self._initialized:
            original_api._get_pan_instance()
            self._initialized = True
    
    def login(self, username: str = None, password: str = None) -> Dict[str, Any]:
        result = original_api.login(username, password)
        if "status" in result and result["status"] == "success":
            self._initialized = True
        return result
    
    def list_files(self, path: str = "/") -> Dict[str, Any]:
        self._ensure_initialized()
        if path == "/" or path == "":
            return original_api.list()
        return original_api.list_folder(path)
    
    def get_file_info(self, file_id: str, path: str) -> Dict[str, Any]:
        self._ensure_initialized()
        result = original_api.list_folder(path)
        if "error" in result:
            return result
        for item in result.get("file", []):
            if item.get("id") == file_id:
                return {"success": True, "data": item}
        for item in result.get("folder", []):
            if item.get("id") == file_id:
                return {"success": True, "data": {**item, "type": "folder"}}
        return {"error": "文件不存在"}
    
    def upload_file(self, local_path: str, remote_path: str = "/") -> Dict[str, Any]:
        self._ensure_initialized()
        if not os.path.exists(local_path):
            return {"error": "本地文件不存在"}
        return original_api.upload(local_path, remote_path)
    
    def download_file(self, remote_path: str) -> Dict[str, Any]:
        self._ensure_initialized()
        return original_api.parsing(remote_path)
    
    def delete_file(self, path: str) -> Dict[str, Any]:
        self._ensure_initialized()
        return original_api.delete(path)
    
    def delete_folder(self, path: str) -> Dict[str, Any]:
        self._ensure_initialized()
        return original_api.delete_folder(path)
    
    def create_folder(self, parent_path: str, folder_name: str) -> Dict[str, Any]:
        self._ensure_initialized()
        return original_api.create_folder(parent_path, folder_name)
    
    def share_file(self, path: str) -> Dict[str, Any]:
        self._ensure_initialized()
        return original_api.share(path)
    
    def reload_session(self) -> Dict[str, Any]:
        self._initialized = False
        return original_api.reload_session()
    
    @staticmethod
    def get_local_file_info(file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"error": "文件不存在"}
        stat = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        return {
            "name": os.path.basename(file_path),
            "path": file_path,
            "size": stat.st_size,
            "type": mime_type or "application/octet-stream",
            "modified": stat.st_mtime,
            "extension": Path(file_path).suffix.lower().lstrip('.')
        }
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
