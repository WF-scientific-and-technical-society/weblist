import unittest
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_wrapper.utils.file_utils import FileUtils
from api_wrapper.utils.cache_manager import CacheManager
from business_logic.validators.upload_validator import UploadValidator, PathValidator
from business_logic.models.permission import UserRole, Permission, check_permission, validate_path_access

class TestFileUtils(unittest.TestCase):
    def test_format_file_size(self):
        self.assertEqual(FileUtils.format_file_size(0), '0.0 B')
        self.assertEqual(FileUtils.format_file_size(1024), '1.0 KB')
        self.assertEqual(FileUtils.format_file_size(1048576), '1.0 MB')
        self.assertEqual(FileUtils.format_file_size(1073741824), '1.0 GB')
    
    def test_parse_size_string(self):
        self.assertEqual(FileUtils.parse_size_string('100 B'), 100)
        self.assertEqual(FileUtils.parse_size_string('1 KB'), 1024)
        self.assertEqual(FileUtils.parse_size_string('1 MB'), 1048576)
        self.assertEqual(FileUtils.parse_size_string('1 GB'), 1073741824)
    
    def test_get_file_extension(self):
        self.assertEqual(FileUtils.get_file_extension('test.txt'), 'txt')
        self.assertEqual(FileUtils.get_file_extension('document.pdf'), 'pdf')
        self.assertEqual(FileUtils.get_file_extension('noextension'), '')
    
    def test_is_allowed_type(self):
        self.assertTrue(FileUtils.is_allowed_type('test.jpg', ['jpg', 'png']))
        self.assertFalse(FileUtils.is_allowed_type('test.exe', ['jpg', 'png']))
        self.assertTrue(FileUtils.is_allowed_type('test.jpg', ['*']))
        self.assertTrue(FileUtils.is_allowed_type('test.jpg', []))
    
    def test_get_file_icon(self):
        self.assertEqual(FileUtils.get_file_icon('folder'), '📁')
        self.assertEqual(FileUtils.get_file_icon('pdf'), '📄')
        self.assertEqual(FileUtils.get_file_icon('jpg'), '🖼️')
        self.assertEqual(FileUtils.get_file_icon('mp4'), '🎬')
    
    def test_sanitize_filename(self):
        self.assertEqual(FileUtils.sanitize_filename('test<>file.txt'), 'test__file.txt')
        self.assertEqual(FileUtils.sanitize_filename('file:name.txt'), 'file_name.txt')

class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.cache = CacheManager(ttl=1, max_size=3)
        self.cache._cache.clear()
        self.cache._max_size = 3
    
    def test_set_and_get(self):
        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.get('key1'), 'value1')
    
    def test_get_nonexistent(self):
        self.assertIsNone(self.cache.get('nonexistent'))
    
    def test_max_size(self):
        self.cache.clear()
        self.cache.set('key1', 'value1')
        self.cache.set('key2', 'value2')
        self.cache.set('key3', 'value3')
        self.cache.set('key4', 'value4')
        self.assertIsNone(self.cache.get('key1'))
        self.assertEqual(self.cache.get('key4'), 'value4')
    
    def test_delete(self):
        self.cache.set('key1', 'value1')
        self.assertTrue(self.cache.delete('key1'))
        self.assertIsNone(self.cache.get('key1'))
    
    def test_clear(self):
        self.cache.set('key1', 'value1')
        self.cache.clear()
        self.assertIsNone(self.cache.get('key1'))

class TestUploadValidator(unittest.TestCase):
    def setUp(self):
        self.config = {
            'upload': {
                'max_file_size': 1024 * 1024,
                'allowed_types': ['jpg', 'png', 'pdf']
            }
        }
        self.validator = UploadValidator(self.config)
    
    def test_validate_upload_success(self):
        result = self.validator.validate_upload('test.jpg', 500000, 'image/jpeg')
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_upload_size_exceeded(self):
        result = self.validator.validate_upload('test.jpg', 2 * 1024 * 1024, 'image/jpeg')
        self.assertFalse(result['valid'])
        self.assertIn('文件大小超过限制', result['errors'][0])
    
    def test_validate_upload_invalid_type(self):
        result = self.validator.validate_upload('test.exe', 500000, 'application/exe')
        self.assertFalse(result['valid'])
        self.assertIn('不支持的文件类型', result['errors'][0])

class TestPathValidator(unittest.TestCase):
    def test_validate_path_valid(self):
        result = PathValidator.validate_path('/folder/subfolder')
        self.assertTrue(result['valid'])
    
    def test_validate_path_empty(self):
        result = PathValidator.validate_path('')
        self.assertFalse(result['valid'])
    
    def test_validate_path_no_leading_slash(self):
        result = PathValidator.validate_path('folder')
        self.assertFalse(result['valid'])
    
    def test_validate_path_double_dots(self):
        result = PathValidator.validate_path('/folder/../test')
        self.assertFalse(result['valid'])
    
    def test_sanitize_path(self):
        self.assertEqual(PathValidator.sanitize_path('folder'), '/folder')
        self.assertEqual(PathValidator.sanitize_path('//folder//file'), '/folder/file')

class TestPermission(unittest.TestCase):
    def test_check_permission_admin(self):
        self.assertTrue(check_permission(UserRole.ADMIN, Permission.READ))
        self.assertTrue(check_permission(UserRole.ADMIN, Permission.WRITE))
        self.assertTrue(check_permission(UserRole.ADMIN, Permission.DELETE))
        self.assertTrue(check_permission(UserRole.ADMIN, Permission.ADMIN))
    
    def test_check_permission_user(self):
        self.assertTrue(check_permission(UserRole.USER, Permission.READ))
        self.assertTrue(check_permission(UserRole.USER, Permission.SHARE))
        self.assertFalse(check_permission(UserRole.USER, Permission.WRITE))
        self.assertFalse(check_permission(UserRole.USER, Permission.DELETE))
    
    def test_validate_path_access_admin(self):
        self.assertTrue(validate_path_access(UserRole.ADMIN, '/config'))
        self.assertTrue(validate_path_access(UserRole.ADMIN, '/admin'))
    
    def test_validate_path_access_user(self):
        self.assertFalse(validate_path_access(UserRole.USER, '/config'))
        self.assertFalse(validate_path_access(UserRole.USER, '/admin'))
        self.assertTrue(validate_path_access(UserRole.USER, '/documents'))

if __name__ == '__main__':
    unittest.main()
