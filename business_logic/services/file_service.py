import os
import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '123pan'))
import api as original_api

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.permission import UserRole, Permission, check_permission, validate_path_access
from validators.upload_validator import UploadValidator, PathValidator
from models.file_model import FileInfo, FolderInfo, UploadResult

class FileOperationService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validator = UploadValidator(config)
        self.path_validator = PathValidator()
    
    def list_files(self, user_role: UserRole, path: str = "/") -> Dict[str, Any]:
        try:
            path = self.path_validator.sanitize_path(path)
            if not validate_path_access(user_role, path):
                return {"success": False, "error": "无权限访问此路径"}
            
            if path == "/":
                result = original_api.list()
            else:
                result = original_api.list_folder(path)
            
            if "error" in result:
                return {"success": False, "error": result["error"]}
            
            return {
                "success": True,
                "data": self._format_file_list(result, path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_file_list(self, raw_data: Dict, path: str) -> Dict[str, Any]:
        formatted = {
            "folders": [],
            "files": [],
            "total_count": 0,
            "total_size": 0,
            "path": path
        }
        
        for item in raw_data.get('folder', []):
            formatted["folders"].append({
                "id": item.get("id"),
                "name": item.get("name"),
                "type": "folder",
                "path": f"{path.rstrip('/')}/{item.get('name')}"
            })
        
        for item in raw_data.get('file', []):
            size_str = item.get("size", "0B")
            size_bytes = self._parse_size(size_str)
            formatted["files"].append({
                "id": item.get("id"),
                "name": item.get("name"),
                "type": "file",
                "size": size_bytes,
                "size_formatted": size_str,
                "extension": self._get_extension(item.get("name", "")),
                "path": f"{path.rstrip('/')}/{item.get('name')}"
            })
            formatted["total_size"] += size_bytes
        
        formatted["total_count"] = len(formatted["files"]) + len(formatted["folders"])
        return formatted
    
    def _parse_size(self, size_str: str) -> int:
        try:
            size_str = str(size_str).upper().strip()
            units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
            for unit, multiplier in units.items():
                if size_str.endswith(unit):
                    value = float(size_str[:-len(unit)].strip())
                    return int(value * multiplier)
            return int(float(size_str))
        except:
            return 0
    
    def _get_extension(self, filename: str) -> str:
        if '.' in filename:
            return filename.rsplit('.', 1)[-1].lower()
        return ""
    
    def upload_file(self, user_role: UserRole, local_path: str, remote_path: str) -> Dict[str, Any]:
        try:
            if not check_permission(user_role, Permission.WRITE):
                return {"success": False, "error": "没有上传权限"}
            
            if not validate_path_access(user_role, remote_path):
                return {"success": False, "error": "无权限访问此路径"}
            
            if not os.path.exists(local_path):
                return {"success": False, "error": "本地文件不存在"}
            
            file_size = os.path.getsize(local_path)
            file_name = os.path.basename(local_path)
            
            validation = self.validator.validate_upload(file_name, file_size)
            if not validation['valid']:
                return {"success": False, "errors": validation['errors']}
            
            result = original_api.upload(local_path, remote_path)
            
            if "error" in result:
                return {"success": False, "error": result["error"]}
            
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def download_file(self, user_role: UserRole, remote_path: str) -> Dict[str, Any]:
        try:
            if not check_permission(user_role, Permission.READ):
                return {"success": False, "error": "没有下载权限"}
            
            remote_path = self.path_validator.sanitize_path(remote_path)
            if not validate_path_access(user_role, remote_path):
                return {"success": False, "error": "无权限访问此路径"}
            
            result = original_api.parsing(remote_path)
            
            if "error" in result:
                return {"success": False, "error": result["error"]}
            
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_file(self, user_role: UserRole, path: str) -> Dict[str, Any]:
        try:
            if not check_permission(user_role, Permission.DELETE):
                return {"success": False, "error": "没有删除权限"}
            
            path = self.path_validator.sanitize_path(path)
            if not validate_path_access(user_role, path):
                return {"success": False, "error": "无权限访问此路径"}
            
            result = original_api.delete(path)
            
            if "error" in result:
                return {"success": False, "error": result["error"]}
            
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_folder(self, user_role: UserRole, parent_path: str, folder_name: str) -> Dict[str, Any]:
        try:
            if not check_permission(user_role, Permission.WRITE):
                return {"success": False, "error": "没有创建权限"}
            
            parent_path = self.path_validator.sanitize_path(parent_path)
            if not validate_path_access(user_role, parent_path):
                return {"success": False, "error": "无权限访问此路径"}
            
            result = original_api.create_folder(parent_path, folder_name)
            
            if "error" in result:
                return {"success": False, "error": result["error"]}
            
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def share_file(self, user_role: UserRole, path: str) -> Dict[str, Any]:
        try:
            if not check_permission(user_role, Permission.SHARE):
                return {"success": False, "error": "没有分享权限"}
            
            path = self.path_validator.sanitize_path(path)
            if not validate_path_access(user_role, path):
                return {"success": False, "error": "无权限访问此路径"}
            
            result = original_api.share(path)
            
            if "error" in result:
                return {"success": False, "error": result["error"]}
            
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
