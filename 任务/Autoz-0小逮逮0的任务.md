Autoz-0小逮逮0 - 配置文件管理与主题系统开发任务清单

职责范围：负责JSON配置文件管理、主题系统、实时配置更新、配置验证与错误处理

**项目核心：**
- 统一的JSON配置中心（config.json）
- 支持实时热更新，无需重启服务
- 主题系统支持动态切换和自定义
- 配置文件版本管理和备份

**第一阶段：配置管理系统架构（第1-2周）**

**1.1 配置文件结构设计**
- **核心配置文件（config.json）：**
```json
{
  "site": {
    "title": "个人网盘",
    "description": "基于123网盘的个人文件管理系统",
    "keywords": ["网盘", "文件管理", "云存储"],
    "logo": "/assets/logo.png",
    "favicon": "/assets/favicon.ico",
    "default_avatar": "/assets/default-avatar.png"
  },
  "theme": {
    "primary_color": "#1890ff",
    "secondary_color": "#52c41a",
    "background_color": "#f5f5f5",
    "text_color": "#333333",
    "border_color": "#d9d9d9",
    "hover_color": "#40a9ff",
    "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI'",
    "font_size": "14px"
  },
  "layout": {
    "header_html": "<header class='site-header'><h1>个人网盘</h1></header>",
    "footer_html": "<footer class='site-footer'><p>&copy; 2024 个人网盘</p></footer>",
    "custom_css": "/* 自定义样式 */",
    "show_footer": true,
    "show_breadcrumb": true,
    "max_width": "1200px"
  },
  "upload": {
    "max_file_size": 2147483648,
    "allowed_types": ["jpg", "jpeg", "png", "gif", "pdf", "zip", "rar"],
    "chunk_size": 1048576,
    "max_concurrent": 3,
    "auto_start": true
  },
  "features": {
    "enable_search": true,
    "enable_share": true,
    "enable_preview": true,
    "enable_drag_drop": true,
    "enable_context_menu": true
  }
}
```

**1.2 配置管理API**
- **读取配置：**
  - GET /api/config - 获取完整配置
    请求示例：
    ```
    GET /api/config
    Authorization: Bearer <access_token>
    ```
    返回示例：
    ```json
    {
      "site": {"title": "个人网盘", ...},
      "theme": {"primary_color": "#1890ff", ...},
      "layout": {"header_html": "<header...", ...},
      ...
    }
    ```
  - GET /api/config/:section - 获取特定配置段
    请求示例：
    ```
    GET /api/config/theme
    Authorization: Bearer <access_token>
    ```
    返回示例：
    ```json
    {
      "primary_color": "#1890ff",
      "secondary_color": "#52c41a",
      "background_color": "#f5f5f5",
      ...
    }
    ```
  - GET /api/config/schema - 获取配置schema
    请求示例：
    ```
    GET /api/config/schema
    Authorization: Bearer <access_token>
    ```
    返回示例：
    ```json
    {
      "type": "object",
      "properties": {
        "site": {"type": "object", ...},
        "theme": {"type": "object", ...},
        ...
      },
      "required": ["site", "theme"]
    }
    ```

- **更新配置：**
  - PUT /api/config - 全量更新配置
    请求示例：
    ```json
    {
      "site": {"title": "我的网盘", ...},
      "theme": {"primary_color": "#333333", ...},
      ...
    }
    ```
    返回示例：
    ```json
    {
      "status": "success",
      "message": "配置已更新",
      "version": "v2"
    }
    ```
  - PATCH /api/config/:section - 增量更新配置段
    请求示例：
    ```json
    {
      "primary_color": "#40a9ff",
      "secondary_color": "#73d13d"
    }
    ```
    返回示例：
    ```json
    {
      "status": "success",
      "message": "主题配置已更新",
      "updated_fields": ["primary_color", "secondary_color"]
    }
    ```
  - POST /api/config/validate - 验证配置格式
    请求示例：
    ```json
    {
      "theme": {
        "primary_color": "#invalid-color",
        "secondary_color": "#52c41a"
      }
    }
    ```
    返回示例：
    ```json
    {
      "valid": false,
      "errors": [{
        "field": "theme.primary_color",
        "message": "无效的颜色代码"
      }]
    }
    ```

- **配置管理：**
  - POST /api/config/backup - 创建配置备份
    请求示例：
    ```
    POST /api/config/backup
    Authorization: Bearer <access_token>
    ```
    返回示例：
    ```json
    {
      "status": "success",
      "backup_id": "b12345",
      "timestamp": "2024-03-20T10:30:00Z"
    }
    ```
  - GET /api/config/backups - 获取备份列表
    请求示例：
    ```
    GET /api/config/backups
    Authorization: Bearer <access_token>
    ```
    返回示例：
    ```json
    {
      "backups": [
        {"id": "b12345", "timestamp": "2024-03-20T10:30:00Z", "size": "2KB"},
        {"id": "b12344", "timestamp": "2024-03-19T10:30:00Z", "size": "2KB"}
      ]
    }
    ```
  - POST /api/config/restore/:backup_id - 恢复备份
    请求示例：
    ```
    POST /api/config/restore/b12345
    Authorization: Bearer <access_token>
    ```
    返回示例：
    ```json
    {
      "status": "success",
      "message": "配置已恢复到备份b12345",
      "version": "v1"
    }
    ```

**第二阶段：主题系统开发（第3-4周）**

**2.1 主题引擎**
- **CSS变量生成：**
  ```javascript
  function generateCSSVariables(theme) {
    return `
      :root {
        --primary-color: ${theme.primary_color};
        --secondary-color: ${theme.secondary_color};
        --background-color: ${theme.background_color};
        --text-color: ${theme.text_color};
        --border-color: ${theme.border_color};
        --hover-color: ${theme.hover_color};
        --font-family: ${theme.font_family};
        --font-size: ${theme.font_size};
      }
    `;
  }
  ```

- **主题切换机制：**
  - 实时主题切换（无需刷新页面）
  - 主题预设方案（浅色/深色/自定义）
  - 主题导入/导出功能
  - 主题色盲友好模式

**2.2 配置验证系统**
- **数据验证规则：**
  - 颜色值验证：支持hex、rgb、hsl格式
  - 文件路径验证：确保路径存在且可访问
  - HTML验证：防止XSS攻击的HTML清理
  - CSS验证：确保CSS语法正确

- **错误处理：**
  - 详细的错误信息和修复建议
  - 配置回滚机制（出错时自动恢复）
  - 配置备份自动创建
  - 用户友好的错误提示

**第三阶段：实时配置更新系统（第5-6周）**

**3.1 热更新机制**
- **文件监听：**
  - 监听config.json文件变化
  - 自动重新加载配置
  - 变更差异对比
  - 变更通知推送

- **WebSocket实时同步：**
  - 配置变更实时推送到前端
  - 多客户端配置同步
  - 冲突检测和解决
  - 版本控制标记

**3.2 配置编辑器**
- **可视化编辑器：**
  - 颜色选择器（支持取色板）
  - 字体选择器（系统字体列表）
  - 图片上传器（自动压缩和优化）
  - HTML/CSS代码编辑器（带语法高亮）

- **预览功能：**
  - 实时预览配置效果
  - 移动端预览模式
  - 不同屏幕尺寸预览
  - 配置变更历史对比

**第四阶段：高级配置功能（第7-8周）**

**4.1 条件配置**
- **环境特定配置：**
  - 开发环境配置
  - 生产环境配置
  - 测试环境配置
  - 环境变量覆盖

- **用户偏好配置：**
  - 个人主题偏好
  - 布局偏好存储
  - 最近使用颜色
  - 自定义快捷键

**4.2 配置模板系统**
- **预设模板：**
  - 商务风格模板
  - 极简风格模板
  - 深色模式模板
  - 节日主题模板

- **模板市场：**
  - 模板分享功能
  - 模板评分系统
  - 模板导入/导出
  - 模板更新通知

**技术实现规范：**

**后端技术栈：**
- **python + Express**（配置管理服务）
- **文件监听：** chokidar库
- **WebSocket：** socket.io
- **数据验证：** joi或zod
- **配置存储：** lowdb（轻量级JSON数据库）

**前端技术栈：**
- **Monaco Editor**（代码编辑器）
- **Color Picker**（颜色选择组件）
- **File Upload**（拖拽上传支持）
- **Diff Viewer**（配置变更对比）

**API接口规范：**

**配置管理API：**
- **基础操作：**
  - GET /api/config - 获取配置
    请求示例：
    ```
    GET /api/config
    Authorization: Bearer <access_token>
    ```
  - PUT /api/config - 更新配置
    请求示例：
    ```json
    {
      "site": {"title": "我的网盘", ...},
      "theme": {"primary_color": "#333333", ...},
      ...
    }
    ```
  - PATCH /api/config/:section - 更新配置段
    请求示例：
    ```json
    {
      "primary_color": "#40a9ff",
      "secondary_color": "#73d13d"
    }
    ```
  - POST /api/config/validate - 验证配置
    请求示例：
    ```json
    {
      "theme": {
        "primary_color": "#1890ff",
        "secondary_color": "#52c41a"
      }
    }
    ```

- **主题管理：**
  - GET /api/themes - 获取主题列表
    请求示例：
    ```
    GET /api/themes
    Authorization: Bearer <access_token>
    ```
    返回示例：
    ```json
    {
      "themes": [
        {"id": "1", "name": "默认主题", "preview": "/theme-preview/1"},
        {"id": "2", "name": "深色主题", "preview": "/theme-preview/2"}
      ]
    }
    ```
  - POST /api/themes - 创建新主题
    请求示例：
    ```json
    {
      "name": "自定义主题",
      "config": {
        "primary_color": "#ff4d4f",
        "secondary_color": "#faad14",
        "background_color": "#ffffff",
        ...
      }
    }
    ```
    返回示例：
    ```json
    {
      "status": "success",
      "theme_id": "3",
      "preview_url": "/theme-preview/3"
    }
    ```
  - PUT /api/themes/:id - 更新主题
    请求示例：
    ```json
    {
      "name": "更新的深色主题",
      "config": {
        "primary_color": "#1890ff",
        "secondary_color": "#52c41a",
        ...
      }
    }
    ```
    返回示例：
    ```json
    {
      "status": "success",
      "message": "主题已更新",
      "theme_id": "2"
    }
    ```
  - DELETE /api/themes/:id - 删除主题
    请求示例：
    ```
    DELETE /api/themes/3
    Authorization: Bearer <access_token>
    ```
    返回示例：
    ```json
    {
      "status": "success",
      "message": "主题已删除",
      "theme_id": "3"
    }
    ```

- **配置历史：**
  - GET /api/config/history - 配置变更历史
    请求示例：
    ```
    GET /api/config/history?limit=10&offset=0
    Authorization: Bearer <access_token>
    ```
    返回示例：
    ```json
    {
      "history": [
        {
          "version": "v2",
          "timestamp": "2024-03-20T10:30:00Z",
          "user": "admin",
          "changes": ["theme.primary_color", "site.title"]
        },
        {
          "version": "v1",
          "timestamp": "2024-03-19T10:30:00Z",
          "user": "admin",
          "changes": ["upload.max_file_size"]
        }
      ]
    }
    ```
  - POST /api/config/rollback/:version - 回滚到指定版本
    请求示例：
    ```
    POST /api/config/rollback/v1
    Authorization: Bearer <access_token>
    ```
    返回示例：
    ```json
    {
      "status": "success",
      "message": "配置已回滚到版本v1",
      "current_version": "v3"
    }
    ```
  - GET /api/config/diff/:from/:to - 配置差异对比
    请求示例：
    ```
    GET /api/config/diff/v1/v2
    Authorization: Bearer <access_token>
    ```
    返回示例：
    ```json
    {
      "diff": [
        {
          "path": "theme.primary_color",
          "from": "#1890ff",
          "to": "#333333"
        },
        {
          "path": "site.title",
          "from": "个人网盘",
          "to": "我的网盘"
        }
      ]
    }
    ```

**实时通信：**
- **WebSocket事件：**
  - config:updated - 配置更新事件
  - config:validated - 配置验证完成
  - config:error - 配置错误事件
  - theme:changed - 主题变更事件

**安全规范：**
- **输入验证：**
  - 所有配置项严格验证
  - HTML内容XSS过滤
  - 文件路径安全检查
  - 文件类型白名单

- **权限控制：**
  - 仅管理员可修改配置
  - 配置修改日志记录
  - 敏感配置加密存储
  - 配置备份权限管理

**测试要求：**
- **单元测试：**
  - 配置验证规则测试（100%覆盖）
  - 主题切换功能测试
  - 文件监听功能测试
  - 错误处理测试

- **集成测试：**
  - 配置更新端到端测试
  - 实时同步测试
  - 多客户端同步测试
  - 配置回滚测试

**性能优化：**
- **配置缓存：**
  - 内存缓存配置对象
  - 配置变更缓存失效
  - 缓存预热机制
  - 缓存命中率监控

- **文件优化：**
  - 配置文件压缩
  - 图片资源压缩
  - CDN资源缓存
  - 懒加载策略

**监控与日志：**
- **配置监控：**
  - 配置变更频率统计
  - 配置错误率监控
  - 主题使用情况分析
  - 用户偏好统计

- **日志系统：**
  - 配置修改操作日志
  - 错误日志详细记录
  - 性能日志监控
  - 用户行为分析

**交付物清单：**
1. 完整的配置管理系统
2. 主题引擎和预设主题
3. 实时配置编辑器
4. 配置验证和错误处理系统
5. 配置备份和恢复系统
6. WebSocket实时同步系统
7. 配置管理API文档
8. 主题开发指南
9. 性能优化报告
10. 用户使用手册

**成功标准：**
- 配置更新实时生效（<100ms延迟）
- 配置验证准确率100%
- 主题切换无闪烁
- 配置错误率<0.1%
- 用户满意度>4.5/5.0
