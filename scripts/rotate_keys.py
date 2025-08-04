import os
import json
from datetime import datetime
from config.security import SecureVault
from config.settings import AppConfig


def rotate_keys():
    """执行密钥轮换全流程"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f".vault.key.backup_{timestamp}"

    if os.path.exists('.vault.key'):
        os.rename('.vault.key', backup_file)
        print("[✅] 旧密钥已备份至:", backup_file)
    else:
        print("[⚠️] 未找到现有密钥文件，将创建全新密钥")

    try:
        new_vault = SecureVault()
        print("[🆕] 新密钥已安全生成")

        config_files = [
            'secure_settings.json',
            'database_credentials.json'
        ]

        reencrypted_count = 0
        for config_file in config_files:
            if not os.path.exists(config_file):
                continue

            with open(config_file, 'r+', encoding='utf-8') as f:
                config_data = json.load(f)

                if 'enc_password' in config_data:
                    original = AppConfig.ENCRYPTOR.decrypt(
                        config_data['enc_password']
                    )
                    config_data['enc_password'] = new_vault.encrypt_value(
                        original
                    )

                if 'enc_token' in config_data:
                    original = AppConfig.ENCRYPTOR.decrypt(
                        config_data['enc_token']
                    )
                    config_data['enc_token'] = new_vault.encrypt_value(
                        original
                    )

                f.seek(0)
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                f.truncate()

            reencrypted_count += 1
            print(f"[🔐] 已更新: {config_file}")

        print(f"\n[🎉] 轮换完成！状态总结:")
        print(f"• 新密钥文件: {new_vault.master_key_path}")
        print(f"• 处理的配置文件: {reencrypted_count}个")
        print(f"• 旧密钥备份: {backup_file if os.path.exists(backup_file) else '无'}")

    except Exception as e:
        print(f"[❌] 关键错误: {str(e)}")
        if os.path.exists(backup_file):
            print("[⚡] 正在恢复备份...")
            os.rename(backup_file, '.vault.key')
        exit(1)

if __name__ == '__main__':
    print("=" * 50)
    print("安全密钥轮换系统".center(40))
    print("=" * 50)
    rotate_keys()
    print("\n[🔒] 重要安全提示:")
    print("1. 立即将新密钥文件(.vault.key)备份到安全位置")
    print("2. 删除所有临时备份文件")
    print("3. 在日志系统中记录本次轮换操作")
