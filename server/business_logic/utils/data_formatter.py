class DataFormatter:
    @staticmethod
    def format_file_list(raw_data):
        """格式化文件列表数据"""
        formatted = {
            "folder": [],
            "file": [],
            "total_count": 0,
            "total_size": 0
        }
        
        for item in raw_data.get('folder', []):
            formatted["folder"].append({
                "id": str(item.get("id", "")),
                "name": item.get("name", ""),
                "type": "folder",
                "size": 0,
                "size_formatted": "0B"
            })
        
        for item in raw_data.get('file', []):
            file_size = DataFormatter._parse_size(item.get("size", "0B"))
            formatted["file"].append({
                "id": str(item.get("id", "")),
                "name": item.get("name", ""),
                "type": "file",
                "size": file_size,
                "size_formatted": DataFormatter._format_size(file_size),
                "extension": DataFormatter._get_extension(item.get("name", ""))
            })
            formatted["total_size"] += file_size
        
        formatted["total_count"] = len(formatted["folder"]) + len(formatted["file"])
        formatted["total_size_formatted"] = DataFormatter._format_size(formatted["total_size"])
        return formatted
    
    @staticmethod
    def _parse_size(size_str):
        """解析文件大小字符串"""
        if isinstance(size_str, (int, float)):
            return size_str
        
        size_str = str(size_str).upper()
        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
        
        # 处理数字+单位格式
        if any(unit in size_str for unit in multipliers.keys()):
            for suffix, multiplier in multipliers.items():
                if size_str.endswith(suffix):
                    num_part = size_str.replace(suffix, "").strip()
                    try:
                        return float(num_part) * multiplier
                    except ValueError:
                        return 0
        # 处理纯数字格式
        try:
            return float(size_str)
        except ValueError:
            return 0
    
    @staticmethod
    def _format_size(size_bytes):
        """格式化文件大小"""
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        while size_bytes >= 1024 and unit_index < len(units)-1:
            size_bytes /= 1024.0
            unit_index += 1
        return f"{size_bytes:.2f} {units[unit_index]}"
    
    @staticmethod
    def _get_extension(filename):
        """获取文件扩展名"""
        if '.' not in filename:
            return ""
        return filename.split('.')[-1].lower()
