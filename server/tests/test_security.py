import unittest
import tempfile
from config.security import SecureVault, ConfigEncryptor

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.test_key = tempfile.NamedTemporaryFile(delete=False)
        self.test_data = "sensitive_data_123"
    
    def test_encryption_cycle(self):
        """测试加密解密循环"""
        vault = SecureVault(self.test_key.name)
        encrypted = vault.encrypt_value(self.test_data)
        decrypted = vault.decrypt_value(encrypted)
        self.assertEqual(decrypted, self.test_data)
    
    def test_key_rotation(self):
        """测试密钥轮换"""
        old_vault = SecureVault(self.test_key.name)
        old_encrypted = old_vault.encrypt_value(self.test_data)
        
        # 模拟密钥轮换
        new_key = tempfile.NamedTemporaryFile(delete=False)
        new_vault = SecureVault(new_key.name)
        
        # 旧数据应能使用旧密钥解密
        decrypted = old_vault.decrypt_value(old_encrypted)
        self.assertEqual(decrypted, self.test_data)
        
        # 新加密的数据
        new_encrypted = new_vault.encrypt_value(self.test_data)
        self.assertNotEqual(old_encrypted, new_encrypted)
    
    def tearDown(self):
        self.test_key.close()
        os.unlink(self.test_key.name)

if __name__ == '__main__':
    unittest.main()
