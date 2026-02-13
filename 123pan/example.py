#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
123Pan API 使用示例

这个示例文件展示了如何使用api.py中的各种功能

使用方法：
1. 直接运行：python example.py
2. 交互模式：运行后选择'y'进入交互式演示
3. 函数调用：导入api模块后直接使用各函数

前置要求：
- 确保已配置settings.json文件
- 确保已安装所有依赖
"""

import api
import json
import os
import sys

def print_result(title, result):
    """打印带有标题的结果"""
    print(f"\n=== {title} ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def main():
    """主示例函数"""
    
    print("123Pan API 使用示例")
    print("=" * 50)
    
    # 1. 用户登录
    print("\n1. 用户登录...")
    
    # 检查settings.json中的配置
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
            existing_user = settings.get("username", "")
            existing_pass = settings.get("password", "")
    except:
        settings = {}
        existing_user = ""
        existing_pass = ""
    
    # 根据现有配置决定是否提示输入
    if existing_user and existing_user != "your_username" and existing_pass and existing_pass != "your_password":
        print(f"使用现有配置中的用户名: {existing_user}")
        login_result = api.login()  # 使用现有配置
    else:
        # 提示用户输入真实凭据
        username = input("请输入123Pan用户名: ").strip()
        password = input("请输入123Pan密码: ").strip()
        if username and password:
            login_result = api.login(username, password)
        else:
            print("用户名或密码不能为空")
            return
    
    print_result("登录结果", login_result)
    
    if "error" in login_result:
        print("登录失败，请检查用户名密码")
        return
    
    # 2. 查看根目录内容
    print("\n2. 查看根目录内容...")
    root_content = api.list()
    print_result("根目录内容", root_content)
    
    # 3. 创建新文件夹
    print("\n3. 创建新文件夹...")
    create_result = api.create_folder("/", "测试文件夹")
    print_result("创建文件夹结果", create_result)
    
    # 4. 进入新创建的文件夹
    if "status" in create_result:
        print("\n4. 查看新文件夹内容...")
        folder_content = api.list_folder("/测试文件夹")
        print_result("测试文件夹内容", folder_content)
    
    # 5. 上传文件示例
    print("\n5. 上传文件...")
    # 创建一个临时测试文件用于演示
    test_file_path = "test_upload.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("这是一个测试文件，用于演示123Pan API的上传功能。\n")
        f.write("文件创建时间：测试时间\n")
    
    upload_result = api.upload(test_file_path, "/测试文件夹")
    print_result("上传文件结果", upload_result)
    
    # 6. 获取文件下载链接示例
    print("\n6. 获取文件下载链接...")
    if "status" in upload_result and upload_result["status"] == "success":
        download_url = api.parsing("/测试文件夹/test_upload.txt")
        print_result("下载链接", download_url)
    else:
        print("(上传失败，跳过下载链接获取)")
    
    # 7. 分享文件示例
    print("\n7. 分享文件...")
    if "status" in upload_result and upload_result["status"] == "success":
        share_result = api.share("/测试文件夹/test_upload.txt")
        print_result("分享结果", share_result)
    else:
        print("(上传失败，跳过分享操作)")
    
    # 8. 删除文件示例
    print("\n8. 删除文件...")
    if "status" in upload_result and upload_result["status"] == "success":
        delete_file_result = api.delete("/测试文件夹/test_upload.txt")
        print_result("删除文件结果", delete_file_result)
    else:
        print("(跳过删除文件操作)")
    
    # 9. 删除文件夹示例
    print("\n9. 删除文件夹...")
    delete_result = api.delete_folder("/测试文件夹")
    print_result("删除文件夹结果", delete_result)
    
    # 10. 重新加载会话
    print("\n10. 重新加载会话...")
    reload_result = api.reload_session()
    print_result("重新加载会话结果", reload_result)
    
    # 清理测试文件
    import os
    try:
        if os.path.exists("test_upload.txt"):
            os.remove("test_upload.txt")
            print("\n清理完成：已删除测试文件 test_upload.txt")
    except:
        pass
    
    print("\n" + "=" * 50)
    print("示例执行完成！")
    print("请根据实际需求修改文件路径和参数")

def interactive_demo():
    """交互式演示"""
    print("\n" + "=" * 50)
    print("交互式演示模式")
    print("=" * 50)
    
    # 完整的交互式菜单
    while True:
        print("\n" + "=" * 30)
        print("123Pan API 交互式演示")
        print("=" * 30)
        print("1. 登录")
        print("2. 查看根目录")
        print("3. 查看指定目录")
        print("4. 创建文件夹")
        print("5. 上传文件")
        print("6. 获取下载链接")
        print("7. 分享文件")
        print("8. 删除文件")
        print("9. 删除文件夹")
        print("10. 重新加载会话")
        print("11. 退出")
        
        choice = input("请输入选择 (1-11): ").strip()
        
        if choice == "1":
            # 检查现有配置
            try:
                with open("settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    existing_user = settings.get("username", "")
                    existing_pass = settings.get("password", "")
            except:
                existing_user = ""
                existing_pass = ""
            
            if existing_user and existing_user != "your_username":
                use_existing = input(f"是否使用现有配置的用户名 '{existing_user}'？(y/N): ").strip().lower()
                if use_existing == "y":
                    result = api.login()
                else:
                    username = input("请输入用户名: ").strip()
                    password = input("请输入密码: ").strip()
                    if username and password:
                        result = api.login(username, password)
                    else:
                        print("用户名或密码不能为空")
                        continue
            else:
                username = input("请输入用户名: ").strip()
                password = input("请输入密码: ").strip()
                if username and password:
                    result = api.login(username, password)
                else:
                    print("用户名或密码不能为空")
                    continue
            print_result("登录结果", result)
            
        elif choice == "2":
            result = api.list()
            print_result("根目录内容", result)
            
        elif choice == "3":
            path = input("请输入目录路径: ").strip()
            result = api.list_folder(path)
            print_result("目录内容", result)
            
        elif choice == "4":
            path = input("请输入父目录路径(留空为根目录): ").strip()
            if not path:
                path = "/"
            folder_name = input("请输入文件夹名称: ").strip()
            result = api.create_folder(path, folder_name)
            print_result("创建文件夹结果", result)
            
        elif choice == "5":
            file_path = input("请输入本地文件路径: ").strip()
            remote_path = input("请输入远程目录路径: ").strip()
            result = api.upload(file_path, remote_path)
            print_result("上传文件结果", result)
            
        elif choice == "6":
            file_path = input("请输入文件路径: ").strip()
            result = api.parsing(file_path)
            print_result("下载链接", result)
            
        elif choice == "7":
            file_path = input("请输入要分享的文件路径: ").strip()
            result = api.share(file_path)
            print_result("分享结果", result)
            
        elif choice == "8":
            file_path = input("请输入要删除的文件路径: ").strip()
            confirm = input(f"确定要删除文件 {file_path} 吗？(y/N): ").strip().lower()
            if confirm == "y":
                result = api.delete(file_path)
                print_result("删除文件结果", result)
            else:
                print("取消删除操作")
                
        elif choice == "9":
            folder_path = input("请输入要删除的文件夹路径: ").strip()
            confirm = input(f"确定要删除文件夹 {folder_path} 吗？(y/N): ").strip().lower()
            if confirm == "y":
                result = api.delete_folder(folder_path)
                print_result("删除文件夹结果", result)
            else:
                print("取消删除操作")
                
        elif choice == "10":
            result = api.reload_session()
            print_result("重新加载会话结果", result)
            
        elif choice == "11":
            print("感谢使用！")
            break
            
        else:
            print("无效选择，请重新输入")

def show_usage_examples():
    """显示使用示例"""
    print("\n" + "=" * 50)
    print("123Pan API 使用示例")
    print("=" * 50)
    print("""
基本使用示例：

1. 登录：
   result = api.login("username", "password")

2. 查看目录：
   files = api.list()  # 根目录
   files = api.list_folder("/文件夹路径")  # 指定目录

3. 上传文件：
   result = api.upload("本地文件路径", "/远程目录")

4. 获取下载链接：
   url = api.parsing("/远程文件路径")

5. 分享文件：
   share = api.share("/远程文件路径")

6. 删除文件：
   result = api.delete("/文件路径")

7. 删除文件夹：
   result = api.delete_folder("/文件夹路径")

8. 创建文件夹：
   result = api.create_folder("/父目录", "文件夹名称")

返回值格式：
- 成功：{"status": "success", ...}
- 失败：{"error": "错误信息"}
""")

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            show_usage_examples()
            sys.exit(0)
        elif sys.argv[1] == "--demo":
            main()
            sys.exit(0)
    
    # 直接进入交互式演示
    print("123Pan API 交互式演示")
    print("=" * 30)
    interactive_demo()