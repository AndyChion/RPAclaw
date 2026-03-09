# 钉钉渠道配置指南 (DingTalk)

## 前提条件
- 钉钉开发者账号
- 一台公网可访问的服务器

## 配置步骤

### 第一步：创建钉钉机器人
1. 访问 https://open-dev.dingtalk.com/ 登录开发者后台
2. 「应用开发」→「企业内部开发」→「创建应用」
3. 填写应用名称、描述
4. 在应用凭证页记录 **AppKey** 和 **AppSecret**

### 第二步：添加机器人能力
1. 在应用详情 →「添加能力」→ 选择「机器人」
2. 配置消息接收地址: `https://你的域名/webhook/dingtalk`
3. 发布应用

### 第三步：配置 Nanobot
编辑 `~/.nanobot/config.json`:

```json
{
  "channels": {
    "dingtalk": {
      "enabled": true,
      "app_key": "你的AppKey",
      "app_secret": "你的AppSecret",
      "webhook_url": "https://你的域名/webhook/dingtalk"
    }
  }
}
```

### 第四步：测试
1. 在钉钉中搜索你的机器人应用
2. 发送一条消息测试

### 常见问题
- **机器人无响应**: 确认应用已发布，且消息接收地址正确
- **权限不足**: 在应用权限管理中添加「企业内机器人」相关权限
- **只想群聊使用**: 创建群聊机器人（Webhook 方式），但功能较有限
