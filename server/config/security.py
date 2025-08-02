import os
import logging
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecureVault:
    def __init__(self, master_key_path: str = ".vault.key"):
        self.master_key_path = master_key_path
        self.logger = logging.getLogger('secure_vault')
        self._ensure_key_file()

    def _ensure_key_file(self):
        """安全初始化密钥文件"""
        if not os.path.exists(self.master_key_path):
            self.logger.warning("Generating new master key...")
            key = Fernet.generate_key()
            with open(self.master_key_path, 'wb') as f:
                f.write(key)
            os.chmod(self.master_key_path, 0o600)
            self.logger.info(f"New master key stored at {self.master_key_path}")

    def _derive_key(self, salt: bytes, password: str = None) -> bytes:
        """加密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode() if password else b''))

    def encrypt_value(self, plaintext: str, secret: str = None) -> str:
        """加密数据"""
        if not plaintext:
            return ""
        
        salt = os.urandom(16)
        key = self._derive_key(salt, secret)
        fernet = Fernet(key)
        
        try:
            ciphertext = fernet.encrypt(plaintext.encode())
            return f"{base64.b64encode(salt).decode()}:{ciphertext.decode()}"
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise ValueError("Failed to encrypt sensitive data")

    def decrypt_value(self, ciphertext: str, secret: str = None) -> str:
        """解密数据"""
        if not ciphertext:
            return ""
            
        try:
            salt_b64, encrypted = ciphertext.split(':')
            salt = base64.b64decode(salt_b64)
            key = self._derive_key(salt, secret)
            fernet = Fernet(key)
            return fernet.decrypt(encrypted.encode()).decode()
        except (InvalidToken, ValueError) as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise ValueError("Invalid ciphertext or secret")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise

class ConfigEncryptor:
    def __init__(self, vault: SecureVault = None):
        self.vault = vault or SecureVault()
        self.master_key = self._load_master_key()

    def _load_master_key(self) -> bytes:
        """加载主密钥"""
        with open(self.vault.master_key_path, 'rb') as f:
            key = f.read()
            # 验证密钥有效性
            Fernet(key)
            return key

    def encrypt(self, plaintext: str) -> str:
        """使用主密钥加密"""
        fernet = Fernet(self.master_key)
        return fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """使用主密钥解密"""
        if not ciphertext:
            return ""
        fernet = Fernet(self.master_key)
        return fernet.decrypt(ciphertext.encode()).decode()
