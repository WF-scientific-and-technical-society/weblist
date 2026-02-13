import os
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class FileUtils:
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"error": "文件不存在"}
        
        stat = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return {
            "name": os.path.basename(file_path),
            "path": file_path,
            "size": stat.st_size,
            "size_formatted": FileUtils.format_file_size(stat.st_size),
            "type": mime_type or "application/octet-stream",
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "extension": Path(file_path).suffix.lower().lstrip('.'),
            "is_directory": os.path.isdir(file_path)
        }
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    @staticmethod
    def parse_size_string(size_str: str) -> int:
        size_str = size_str.upper().strip()
        units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
        
        for unit, multiplier in sorted(units.items(), key=lambda x: len(x[0]), reverse=True):
            if size_str.endswith(unit):
                try:
                    value_str = size_str[:-len(unit)].strip()
                    if value_str:
                        value = float(value_str)
                        return int(value * multiplier)
                except ValueError:
                    pass
        try:
            return int(float(size_str))
        except ValueError:
            return 0
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        return Path(filename).suffix.lower().lstrip('.')
    
    @staticmethod
    def is_allowed_type(filename: str, allowed_types: list) -> bool:
        if not allowed_types or '*' in allowed_types:
            return True
        ext = FileUtils.get_file_extension(filename)
        return ext.lower() in [t.lower() for t in allowed_types]
    
    @staticmethod
    def get_file_icon(extension: str) -> str:
        icon_map = {
            'folder': '📁',
            'pdf': '📄',
            'doc': '📝', 'docx': '📝',
            'xls': '📊', 'xlsx': '📊',
            'ppt': '📽️', 'pptx': '📽️',
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️', 'webp': '🖼️',
            'mp4': '🎬', 'avi': '🎬', 'mkv': '🎬', 'mov': '🎬', 'wmv': '🎬',
            'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'aac': '🎵',
            'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦', 'gz': '📦',
            'txt': '📃', 'md': '📃',
            'py': '🐍', 'js': '📜', 'html': '🌐', 'css': '🎨', 'json': '📋',
            'exe': '⚙️', 'msi': '⚙️',
        }
        return icon_map.get(extension.lower(), '📄')
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()
