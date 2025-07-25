# 123Pan API 文档

## 概述

这是一个123网盘的Python API封装，提供了文件管理、上传下载、分享等功能。所有功能都以Python函数的形式实现。

## 配置文件

程序使用 `settings.json` 文件存储配置信息，包括登录凭据和默认路径。

## 配置文件
### settings.json 配置说明
配置文件`settings.json`用于存储登录凭据和默认路径设置。

#### 创建配置文件
1. 复制`settings.json.example`为`settings.json`
2. 替换为你的真实用户名和密码

#### settings.json 示例
```json
{
  "username": "你的123Pan用户名",
  "password": "你的123Pan密码",
  "default-path": "镜像文件夹"
}
```

#### 重要说明
- **自动保存机制**：只有当调用`api.login(username, password)`并提供新的用户名密码时，才会更新此文件
- **现有配置保护**：如果settings.json已包含有效凭据，运行程序不会覆盖它们
- **模板值保护**：如果检测到用户名是"your_username"，程序会提示输入真实凭据
- **首次使用**：首次运行时需要将用户名密码改为真实值

## API函数

### 1. login(username=None, password=None)

用户登录123网盘。

**参数：**
- `username` (str, 可选): 用户名，如果为None则从settings.json读取
- `password` (str, 可选): 密码，如果为None则从settings.json读取

**返回值：**
```json
{"status": "success"}
```
或
```json
{"error": "错误信息"}
```

**示例：**
```python
import api
result = api.login("username", "password")
```

### 2. list()

列出当前目录下的文件和文件夹。

**参数：** 无

**返回值：**
```json
{
  "folder": [
    {"id": "1", "name": "镜像文件夹"},
    {"id": "2", "name": "小猪佩奇全集"},
    {"id": "3", "name": "学习资料"}
  ],
  "file": [
    {"id": "4", "name": "win11镜像.iso", "size": "3.5GB"},
    {"id": "5", "name": "PCL2.exe", "size": "3.52MB"},
    {"id": "6", "name": "requirements.txt", "size": "1.5KB"}
  ]
}
```

如果settings.json中设置了"default-path"但对应文件夹不存在：
```json
{"error": "主目录不合法"}
```

**示例：**
```python
result = api.list()
```

### 3. list_folder(path)

进入指定子目录并列出内容。

**参数：**
- `path` (str): 文件夹路径，如"/学习资料/小猪佩奇全集"

**返回值：**
```json
{
  "folder": [
    {"id": "1", "name": "第三季"},
    {"id": "2", "name": "第二季"},
    {"id": "3", "name": "第一季"}
  ],
  "file": [
    {"id": "4", "name": "1.mp4", "size": "3.5GB"}
  ]
}
```

如果路径不存在：
```json
{"error": "没有找到对应文件夹或文件"}
```

**示例：**
```python
result = api.list_folder("/学习资料/小猪佩奇全集")
```

### 4. parsing(path)

获取文件的下载链接。

**参数：**
- `path` (str): 文件路径，如"/学习资料/小猪佩奇全集/1.mp4"

**返回值：**
```json
{"url": "https://url.com/学习资料/小猪佩奇全集/1.mp4"}
```

如果文件不存在：
```json
{"error": "没有找到对应文件夹或文件"}
```

**示例：**
```python
result = api.parsing("/学习资料/小猪佩奇全集/1.mp4")
```

### 5. share(path)

分享指定文件。

**参数：**
- `path` (str): 文件路径，如"/学习资料/小猪佩奇全集/1.mp4"

**返回值：**
```json
{
  "share_url": "https://www.123pan.com/s/xxx",
  "share_key": "xxx",
  "share_pwd": ""
}
```

**示例：**
```python
result = api.share("/学习资料/小猪佩奇全集/1.mp4")
```

### 6. upload(local_path, remote_path="/")

上传本地文件到远程目录。

**参数：**
- `local_path` (str): 本地文件路径
- `remote_path` (str, 可选): 远程路径，默认为根目录"/"

**返回值：**
```json
{"status": "success"}
```
或
```json
{"error": "错误信息"}
```

**示例：**
```python
result = api.upload("C:/Users/user/Desktop/file.txt", "/文档")
```

### 7. delete(path)

删除文件或文件夹。

**参数：**
- `path` (str): 文件或文件夹路径

**返回值：**
```json
{"status": "success"}
```
或
```json
{"error": "错误信息"}
```

**示例：**
```python
result = api.delete("/学习资料/小猪佩奇全集/1.mp4")
```

### 8. create_folder(path, folder_name)

在指定路径创建新文件夹。

**参数：**
- `path` (str): 父目录路径
- `folder_name` (str): 新文件夹名称

**返回值：**
```json
{"status": "success", "folder_id": "新文件夹ID"}
```
或
```json
{"error": "错误信息"}
```

**示例：**
```python
result = api.create_folder("/学习资料", "新文件夹")
```

### 9. delete_folder(path)

删除文件夹（包括空文件夹和非空文件夹），会删除文件夹内的所有内容。

**参数：**
- `path` (str): 文件夹路径

**返回值：**
```json
{"status": "success", "deleted_files": 删除的文件数量}
```
或
```json
{"error": "错误信息"}
```

**示例：**
```python
result = api.delete_folder("/学习资料/旧文件夹")
```

**注意：**
- 删除操作不可恢复，请谨慎使用
- 会删除文件夹内的所有文件和子文件夹
- 返回的deleted_files包含被删除的文件和文件夹总数

### 10. reload_session()

重新加载会话，用于刷新登录状态。

**参数：** 无

**返回值：**
```json
{"status": "success"}
```
或
```json
{"error": "错误信息"}
```

**示例：**
```python
result = api.reload_session()
```

## 使用示例

### 完整使用流程

```python
import api

# 1. 登录
api.login("your_username", "your_password")

# 2. 查看根目录内容
content = api.list()
print(content)

# 3. 进入子目录
sub_content = api.list_folder("/学习资料")
print(sub_content)

# 4. 获取文件下载链接
download_url = api.parsing("/学习资料/文档.pdf")
print(download_url)

# 5. 分享文件
share_info = api.share("/学习资料/文档.pdf")
print(share_info)

# 6. 上传文件
api.upload("C:/Users/user/Desktop/newfile.txt", "/学习资料")

# 7. 创建文件夹
api.create_folder("/学习资料", "新文件夹")

# 8. 删除文件
api.delete("/学习资料/旧文件.txt")
```

## 注意事项

1. 所有路径都以"/"开头，表示从根目录开始的绝对路径
2. 文件夹路径不要包含最后的"/"
3. 文件路径需要包含完整的文件名和扩展名
4. 登录信息会自动保存在123pan.txt文件中，用于维持会话
5. 如果长时间未使用，可能需要重新登录

## 错误处理

所有API函数在出错时都会返回包含"error"字段的JSON对象，建议在使用时检查返回值：

```python
result = api.some_function()
if "error" in result:
    print(f"发生错误: {result['error']}")
else:
    # 正常处理结果
```

## 交互式演示程序 (example.py)

`example.py` 是一个功能完整的交互式演示程序，提供了图形化的菜单界面来测试所有API功能。

### 启动方式

```bash
# 直接启动交互式演示
python example.py

# 查看使用帮助
python example.py --help

# 运行完整示例程序
python example.py --demo
```

### 功能菜单

启动后会显示以下菜单：

```
123Pan API 交互式演示
==============================
1. 登录
2. 查看根目录
3. 查看指定目录
4. 创建文件夹
5. 上传文件
6. 获取下载链接
7. 分享文件
8. 删除文件
9. 删除文件夹
10. 重新加载会话
11. 退出
```

### 使用流程

1. **首次使用**：程序会自动检测`settings.json`中的凭据
   - 如果未配置，会提示输入用户名和密码
   - 配置完成后会自动保存，后续无需重复输入

2. **功能测试**：通过数字选择对应功能
   - 每个功能都有清晰的提示信息
   - 危险操作（如删除）会有确认提示
   - 操作完成后自动返回主菜单

3. **示例操作**：
   - **上传测试**：自动创建`test_upload.txt`测试文件，完成后自动清理
   - **目录浏览**：支持逐级进入子目录查看内容
   - **文件分享**：获取分享链接和提取码
   - **批量操作**：支持文件夹的创建和删除

### 特色功能

- **智能凭据管理**：自动读取settings.json，避免重复输入
- **安全确认机制**：删除操作需要二次确认
- **自动测试文件**：上传功能自动生成和清理测试文件
- **错误处理**：友好的错误提示和重试机制
- **会话管理**：支持重新登录和会话刷新

### 使用场景

- **API功能测试**：快速验证所有API接口
- **新手入门**：通过交互方式熟悉API使用
- **功能演示**：向他人展示123Pan的功能特性
- **故障排查**：测试网络连接和API响应

### 注意事项

1. **配置文件**：确保`settings.json`中有正确的用户名和密码
2. **网络要求**：需要稳定的网络连接
3. **文件安全**：删除操作不可恢复，请谨慎使用
4. **测试文件**：程序会自动创建和删除`test_upload.txt`，请勿手动干预
5. **兼容性**：支持Python 3.6+版本运行

### 开发建议

`example.py`的代码结构清晰，可以作为：
- 学习API使用的最佳实践
- 开发自定义功能的基础模板
- 集成测试的参考实现
- 用户界面的设计参考

通过`example.py`，您可以：
- 快速了解所有API功能
- 测试网络环境和API响应
- 验证用户凭据是否正确
- 熟悉文件操作流程