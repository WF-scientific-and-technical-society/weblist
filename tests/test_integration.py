import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestIntegration(unittest.TestCase):
    def test_import_modules(self):
        try:
            from api_wrapper import Pan123API, Pan123Client
            from api_wrapper.utils import FileUtils, CacheManager
            from api_wrapper.decorators import retry_on_error
            from business_logic import FileOperationService, FileSearchService, AuditLogger
            from business_logic.models import UserRole, Permission
            from business_logic.validators import UploadValidator, PathValidator
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_config_file_exists(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'config', 'config.json')
        self.assertTrue(os.path.exists(config_path), f"Config file not found at {config_path}")
    
    def test_config_file_valid_json(self):
        import json
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'config', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.assertIn('site', config)
        self.assertIn('theme', config)
        self.assertIn('upload', config)
    
    def test_templates_exist(self):
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.assertTrue(os.path.exists(os.path.join(templates_dir, 'index.html')))
        self.assertTrue(os.path.exists(os.path.join(templates_dir, 'settings.html')))
    
    def test_static_files_exist(self):
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        self.assertTrue(os.path.exists(os.path.join(static_dir, 'css', 'main.css')))
        self.assertTrue(os.path.exists(os.path.join(static_dir, 'js', 'app.js')))
        self.assertTrue(os.path.exists(os.path.join(static_dir, 'js', 'api.js')))

if __name__ == '__main__':
    unittest.main()
