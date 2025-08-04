from ..utils.data_formatter import DataFormatter

class FileSearchService:
    def __init__(self, api_client):
        self.api = api_client

    def search_files(self, user_role, path, keyword=None, filters=None):
        """搜索文件"""
        try:
            if path == "/":
                result = self.api.list()
            else:
                result = self.api.list_folder(path)

            formatted_data = DataFormatter.format_file_list(result)
            all_items = formatted_data["folder"] + formatted_data["file"]

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
            if keyword and keyword.lower() not in item.get('name', '').lower():
                continue

            if filters and filters.get('type'):
                if filters['type'] == 'folder' and item.get('type') != 'folder':
                    continue
                if filters['type'] == 'file' and item.get('type') != 'file':
                    continue

            if filters and filters.get('size_min') and \
                    item.get('size', 0) < filters['size_min']:
                continue

            if filters and filters.get('size_max') and \
                    item.get('size', 0) > filters['size_max']:
                continue

            if filters and filters.get('modified_after') and \
                    item.get('modified') < filters['modified_after']:
                continue

            results.append(item)

        return results
