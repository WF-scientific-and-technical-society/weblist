import os
import json
from lxml import etree

def validate_config_files(root_dir):
    errors = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.json'):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        json.load(f)
                except Exception as e:
                    errors.append(f"配置文件错误 {filepath}: {str(e)}")
                    
            elif filename.endswith('.html'):
                filepath = os.path.join(dirpath, filename)
                try:
                    parser = etree.HTMLParser(recover=False)
                    tree = etree.parse(filepath, parser)
                except Exception as e:
                    errors.append(f"HTML验证失败 {filepath}: {str(e)}")
    
    return errors

if __name__ == "__main__":
    web_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'web')
    errors = validate_config_files(web_dir)
    
    if errors:
        print("验证发现错误:")
        for error in errors:
            print(error)
        print(f"\n验证目录: {os.path.abspath(web_dir)}")
        exit(1)
    else:
        print(f"所有配置文件格式正确，HTML文件符合标准 (验证目录: {os.path.abspath(web_dir)})")
