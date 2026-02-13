from typing import Dict, List, Any, Optional

class UploadValidator:
    def __init__(self, config: Dict[str, Any]):
        upload_config = config.get('upload', {})
        self.max_file_size = upload_config.get('max_file_size', 2 * 1024 * 1024 * 1024)
        self.allowed_types = upload_config.get('allowed_types', ['*'])
    
    def validate_upload(self, file_name: str, file_size: int, file_type: str = None) -> Dict[str, Any]:
        errors = []
        if file_size > self.max_file_size:
            errors.append(f"文件大小超过限制：{file_size} > {self.max_file_size}")
        
        if self.allowed_types and '*' not in self.allowed_types:
            extension = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
            if extension not in [t.lower() for t in self.allowed_types]:
                errors.append(f"不支持的文件类型：{extension}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def validate_batch_upload(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        total_size = 0
        all_valid = True
        
        for file_info in files:
            validation = self.validate_upload(
                file_info.get('name', ''),
                file_info.get('size', 0),
                file_info.get('type', '')
            )
            results.append({
                "name": file_info.get('name'),
                "valid": validation['valid'],
                "errors": validation['errors']
            })
            total_size += file_info.get('size', 0)
            if not validation['valid']:
                all_valid = False
        
        return {
            "valid": all_valid,
            "results": results,
            "total_size": total_size
        }

class PathValidator:
    @staticmethod
    def validate_path(path: str) -> Dict[str, Any]:
        errors = []
        if not path:
            errors.append("路径不能为空")
        if not path.startswith('/'):
            errors.append("路径必须以 / 开头")
        if '//' in path:
            errors.append("路径不能包含连续的斜杠")
        if '..' in path:
            errors.append("路径不能包含 .. ")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def sanitize_path(path: str) -> str:
        while '//' in path:
            path = path.replace('//', '/')
        path = path.replace('..', '')
        if not path.startswith('/'):
            path = '/' + path
        return path.rstrip('/') or '/'
