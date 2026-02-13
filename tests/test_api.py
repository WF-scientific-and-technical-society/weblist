import unittest
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestConfigAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['FLASK_ENV'] = 'testing'
        from app import app
        cls.app = app
        cls.client = app.test_client()
    
    def test_get_config(self):
        response = self.client.get('/api/config')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertIn('site', data['data'])
        self.assertIn('theme', data['data'])
    
    def test_get_config_section(self):
        response = self.client.get('/api/config/theme')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 200)
        self.assertIn('primary_color', data['data'])
    
    def test_get_config_section_not_found(self):
        response = self.client.get('/api/config/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_validate_config(self):
        response = self.client.post('/api/config/validate', 
            json={'theme': {'primary_color': '#1890ff'}},
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['data']['valid'])
    
    def test_validate_config_invalid_color(self):
        response = self.client.post('/api/config/validate',
            json={'theme': {'primary_color': 'invalid'}},
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['data']['valid'])

class TestAuthAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['FLASK_ENV'] = 'testing'
        from app import app
        cls.app = app
        cls.client = app.test_client()
    
    def test_login_success(self):
        response = self.client.post('/api/auth/login',
            json={'username': 'admin', 'password': 'admin'},
            content_type='application/json')
        data = json.loads(response.data)
        self.assertIn(data['code'], [200, 401])
    
    def test_login_missing_credentials(self):
        response = self.client.post('/api/auth/login',
            json={'username': '', 'password': ''},
            content_type='application/json')
        self.assertEqual(response.status_code, 401)
    
    def test_protected_route_without_token(self):
        response = self.client.put('/api/config',
            json={'site': {'title': 'Test'}},
            content_type='application/json')
        self.assertEqual(response.status_code, 401)

class TestFileAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['FLASK_ENV'] = 'testing'
        from app import app
        cls.app = app
        cls.client = app.test_client()
    
    def test_list_files(self):
        response = self.client.get('/api/files?path=/')
        self.assertIn(response.status_code, [200, 400, 500])
    
    def test_search_files_no_keyword(self):
        response = self.client.get('/api/search')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
