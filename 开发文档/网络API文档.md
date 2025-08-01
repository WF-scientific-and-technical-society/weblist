# BYD123网盘项目网络API文档

# 注册管理员账号
## URL /api/admin/register" 
## mode = post
用法
``` js
{
    "username" : "字符串",
    "password" : "字符串"
}
```
返回

**成功时**
```json
{"status": "注册成功"}
```
**确实用户名和密码时**
```json
{"error": "缺少用户名或密码"}
```
**已有用户时**
``` json
{"error": "The.Setting.Is.Not.NULL"}
```
**更多情况**
```json
{"error": "保存"}
```

# 登录管理员账号
## URL /api/admin/login
## mode = post
用法
``` js
{
    "username" : "字符串",
    "password" : "字符串"
}
```
返回

**成功时**
```json
{"expires_in": "3600"}
```
**缺少用户名和密码时**
```json
{"error": "缺少用户名或密码"}
```
**更多情况**
```json
{"error": "保存"}
```

# 检查管理员登录
## URL /api/admin/check
## mode = null
用法
``` js
{}
```
返回
**登录成功**
```json
{"logged_in": "True","username":"username"}
```
**登录失败**
```json
{"logged_in": "Flase"}
```

# 列出文件目录
## URL /api/files
## mode = get
用法
```
&path=字符串
```
返回
**成功**
```json
{
            "folder": [{"id": "1", "name": "镜像文件夹"}, ...],
            "file": [{"id": "4", "name": "win11镜像.iso", "size": "3.5GB"}, ...]
        }
```
**失败**
```json
{"error": "主目录不合法"}
```

# 网盘登录
## URL /api/admin/123pan-login
## mode = post
用法
``` js
{
    "username" : "字符串",
    "password" : "字符串"
}
```
返回

**成功时**
```json
{"outcome": "Ture"}
```
**失败**
```json
{"outcome": "False"}
```

# 上传文件
## URL /api/upload
## mode = get
用法
``` 
&path=字符串（云
&file=字符串（本地
```
返回

**成功时**
```json
{"outcome": "Ture"}
```
**失败**
```json
{"outcome": "False"}
```

# 下载文件
## URL /api/download
## mode = get
用法
``` 
&path=字符串（云
```
返回

**成功时**
```json
{"outcome": "Ture"}
```
**失败**
```json
{"outcome": "False"}
```

# 删除文件
## URL /api/delete
## mode = get
用法
``` 
&path=字符串（云
```
返回

**成功时**
```json
{"outcome": "Ture"}
```
**失败**
```json
{"outcome": "False"}
```

# 创建文件夹
## /api/folder/create
## mode = get
用法
``` 
&path=字符串（云
&folder_name=字符串（文件夹名称
```
返回

**成功时**
```json
{"outcome": "Ture"}
```
**失败**
```json
{"outcome": "False"}
```

# 删除文件夹
## URL /api/folder/delete
## mode = get
用法
``` 
&path=字符串（云
```
返回

**成功时**
```json
{"outcome": "Ture"}
```
**失败**
```json
{"outcome": "False"}
```