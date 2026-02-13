import os
import sys
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '123pan'))
import api as original_api

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.permission import UserRole, validate_path_access
from validators.upload_validator import PathValidator

class FileSearchService:
    def __init__(self):
        self.path_validator = PathValidator()
    
    def search_files(
        self,
        user_role: UserRole,
        path: str,
        keyword: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            path = self.path_validator.sanitize_path(path)
            if not validate_path_access(user_role, path):
                return {"success": False, "error": "无权限访问此路径"}
            
            if path == "/":
                file_list = original_api.list()
            else:
                file_list = original_api.list_folder(path)
            
            if "error" in file_list:
                return {"success": False, "error": file_list["error"]}
            
            results = self._apply_search_filters(file_list, keyword, filters)
            
            return {
                "success": True,
                "data": results,
                "total": len(results.get("files", [])) + len(results.get("folders", [])),
                "path": path,
                "keyword": keyword
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _apply_search_filters(
        self,
        file_list: Dict[str, Any],
        keyword: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        results = {"folders": [], "files": []}
        keyword_lower = keyword.lower() if keyword else ""
        filters = filters or {}
        
        file_type_filter = filters.get("file_type", "").lower()
        min_size = filters.get("min_size", 0)
        max_size = filters.get("max_size", float('inf'))
        
        for folder in file_list.get("folder", []):
            name = folder.get("name", "")
            if keyword_lower in name.lower():
                results["folders"].append(folder)
        
        for file_item in file_list.get("file", []):
            name = file_item.get("name", "")
            
            if keyword_lower and keyword_lower not in name.lower():
                continue
            
            if file_type_filter:
                ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
                if ext != file_type_filter:
                    continue
            
            size_str = file_item.get("size", "0B")
            size_bytes = self._parse_size(size_str)
            
            if min_size > 0 and size_bytes < min_size:
                continue
            if max_size < float('inf') and size_bytes > max_size:
                continue
            
            results["files"].append(file_item)
        
        return results
    
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
    
    def search_by_type(
        self,
        user_role: UserRole,
        path: str,
        file_type: str
    ) -> Dict[str, Any]:
        return self.search_files(user_role, path, "", {"file_type": file_type})
    
    def search_by_size(
        self,
        user_role: UserRole,
        path: str,
        min_size: int = 0,
        max_size: int = None
    ) -> Dict[str, Any]:
        filters = {"min_size": min_size}
        if max_size:
            filters["max_size"] = max_size
        return self.search_files(user_role, path, "", filters)
