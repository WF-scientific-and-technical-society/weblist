import json
import logging
from datetime import datetime
from config.security import ConfigEncryptor

class SecureAuditLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.encryptor = ConfigEncryptor()
        self._setup_logger()

    def _setup_logger(self):
        """配置安全日志"""
        self.logger = logging.getLogger('secure_audit')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def log(self, action, user, path, details):
        """记录脱敏日志"""
        safe_details = {
            'action': action,
            'user': self.encryptor.encrypt(user),
            'path': path,
            **self._sanitize(details)
        }
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'data': safe_details
        }
        
        self.logger.info(json.dumps(log_entry))

    def _sanitize(self, data):
        """数据脱敏"""
        if isinstance(data, dict):
            return {k: self.encryptor.encrypt(v) if k in ['ip', 'device'] else v 
                   for k, v in data.items()}
        return data

    def get_logs(self, filter_func=None):
        """安全读取日志"""
        logs = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.split('|')[-1])
                        if not filter_func or filter_func(entry):
                            logs.append(self._decrypt_entry(entry))
                    except (json.JSONDecodeError, IndexError):
                        continue
        except FileNotFoundError:
            pass
        return logs

    def _decrypt_entry(self, entry):
        """解密日志条目"""
        decrypted = entry.copy()
        if 'user' in decrypted['data']:
            decrypted['data']['user'] = self.encryptor.decrypt(
                decrypted['data']['user'])
        return decrypted
