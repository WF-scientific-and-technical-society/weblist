import unittest
import tempfile
from unittest.mock import MagicMock
from pathlib import Path
from config.settings import DevelopmentConfig
from business_logic.services.file_service import SecureFileService
from business_logic.models.permission import UserRole, Permission

class TestFileService(unittest.TestCase):
    def setUp(self):
        # 创建模拟API客户端
        self.mock_api = MagicMock()
        self.mock_api.upload.return_value = MagicMock(success=True, file_id="file123")
        
        # 初始化服务
        self.service = SecureFileService(self.mock_api, DevelopmentConfig)
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"test content")
        self.temp_file.close()
    
    def test_secure_upload_success(self):
        """测试文件上传成功场景"""
        # 模拟文件对象
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        mock_file.save = lambda path: Path(path).write_text("content")
        
        # 模拟用户
        mock_user = MagicMock()
        mock_user.role = UserRole.ADMIN
        mock_user.name = "admin"
        
        result = self.service.secure_upload(mock_user, mock_file, "/uploads")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["id"], "file123")
    
    def test_upload_invalid_path(self):
        """测试无权限路径上传"""
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        
        mock_user = MagicMock()
        mock_user.role = UserRole.USER  # 普通用户
        
        with self.assertRaises(PermissionError):
            self.service.secure_upload(mock_user, mock_file, "/system/config")
    
    def test_upload_invalid_filename(self):
        """测试危险文件名"""
        mock_file = MagicMock()
        mock_file.filename = "malicious<file>.exe"
        
        mock_user = MagicMock()
        mock_user.role = UserRole.ADMIN
        
        result = self.service.secure_upload(mock_user, mock_file, "/uploads")
        self.assertFalse(result["success"])
        self.assertIn("非法字符", result["errors"][0])
    
    def tearDown(self):
        if Path(self.temp_file.name).exists():
            Path(self.temp_file.name).unlink()

class TestSearchService(unittest.TestCase):
    def setUp(self):
        self.mock_api = MagicMock()
        self.mock_api.list.return_value = {
            "folder": [{"id": "1", "name": "文档"}],
            "file": [{"id": "2", "name": "报告.pdf", "size": "1MB"}]
        }
        from business_logic.services.search_service import FileSearchService
        self.service = FileSearchService(self.mock_api)
    
    def test_search_by_keyword(self):
        """测试关键词搜索"""
        result = self.service.search_files(UserRole.USER, "/", keyword="报告")
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["name"], "报告.pdf")
    
    def test_search_with_filters(self):
        """测试带过滤条件的搜索"""
        result = self.service.search_files(
            UserRole.USER, 
            "/", 
            filters={"type": "file", "size_max": 2*1024*1024}  # 2MB
        )
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["type"], "file")

if __name__ == '__main__':
    unittest.main(verbosity=2)
