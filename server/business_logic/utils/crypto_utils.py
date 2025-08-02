import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
from config.settings import AppConfig

class CryptoUtils:
    @staticmethod
    def generate_fernet_key(password: str, salt: bytes = None) -> bytes:
        """加密密钥"""
        salt = salt or os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def hmac_sign(data: str, key: str) -> str:
        """生成HMAC签名"""
        return hmac.new(
            key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def encrypt_at_rest(data: str, key: bytes = None) -> str:
        """静态数据加密"""
        key = key or AppConfig.ENCRYPTOR.master_key
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_at_rest(ciphertext: str, key: bytes = None) -> str:
        """静态数据解密"""
        if not ciphertext:
            return ""
        key = key or AppConfig.ENCRYPTOR.master_key
        f = Fernet(key)
        return f.decrypt(ciphertext.encode()).decode()
