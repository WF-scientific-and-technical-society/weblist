import os
from ..utils.permission_middleware import is_safe_filename

class UploadValidator:
    def __init__(self, config):
        self.max_file_size = config.get('MAX_FILE_SIZE', 2 * 1024 * 1024 * 1024)  # 默认2GB
        self.allowed_types = config.get('ALLOWED_TYPES', ['*'])
    
    def validate(self, file_path):
        """验证上传文件"""
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        errors = []
        
        # 文件大小检查
        if file_size > self.max_file_size:
            errors.append(f"文件大小超过限制: {self._format_size(file_size)} > {self._format_size(self.max_file_size)}")
        
        # 文件类型检查
        if self.allowed_types != ['*']:
            file_extension = os.path.splitext(file_name)[1][1:].lower()
            if file_extension not in self.allowed_types:
                errors.append(f"不支持的文件类型: {file_extension}")
        
        # 文件名安全检查
        if not is_safe_filename(file_name):
            errors.append("文件名包含非法字符")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _format_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
