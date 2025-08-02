from ..utils.data_formatter import DataFormatter

class FileSearchService:
    def __init__(self, api_client):
        self.api = api_client
    
    def search_files(self, user_role, path, keyword=None, filters=None):
        """搜索文件"""
        try:
            # 获取文件列表
            if path == "/":
                result = self.api.list()
            else:
                result = self.api.list_folder(path)
            
            # 格式化数据
            formatted_data = DataFormatter.format_file_list(result)
            all_items = formatted_data["folder"] + formatted_data["file"]
            
            # 应用搜索条件
            results = self._apply_search_filters(all_items, keyword, filters)
            
            return {
                "success": True,
                "data": results,
                "total": len(results),
                "path": path,
                "keyword": keyword
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _apply_search_filters(self, items, keyword, filters):
        """应用搜索筛选条件"""
        results = []
        
        for item in items:
            # 关键词匹配
            if keyword and keyword.lower() not in item.get('name', '').lower():
                continue
            
            # 文件类型筛选
            if filters and filters.get('type'):
                if filters['type'] == 'folder' and item.get('type') != 'folder':
                    continue
                if filters['type'] == 'file' and item.get('type') != 'file':
                    continue
            
            # 文件大小筛选
            if filters and filters.get('size_min') and item.get('size', 0) < filters['size_min']:
                continue
            
            if filters and filters.get('size_max') and item.get('size', 0) > filters['size_max']:
                continue
            
            # 修改时间筛选
            if filters and filters.get('modified_after') and item.get('modified') < filters['modified_after']:
                continue
            
            results.append(item)
        
        return results
