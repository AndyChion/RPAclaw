# Telegram 渠道配置指南

## 前提条件
- 一台公网可访问的服务器（用于接收 Webhook）
- Telegram 账号

## 配置步骤

### 第一步：创建 Telegram Bot
1. 在 Telegram 中搜索 `@BotFather`，发送 `/newbot`
2. 输入机器人名称（如 `RPAclaw Assistant`）
3. 输入机器人用户名（如 `rpaclaw_bot`，必须以 `_bot` 结尾）
4. 保存返回的 **Bot Token**（格式如 `123456789:ABCdefGhIJKlmnOPQRsTUVwxyz`）

### 第二步：配置 Nanobot
编辑 `~/.nanobot/config.json`，在 `channels` 中添加:

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "bot_token": "你的Bot Token",
      "allowed_users": ["你的Telegram用户ID"],
      "webhook_url": "https://你的域名/webhook/telegram"
    }
  }
}
```

### 第三步：获取你的用户 ID
1. 在 Telegram 搜索 `@userinfobot`
2. 发送任意消息，它会返回你的用户 ID（纯数字）
3. 填入 `allowed_users`

### 第四步：启动网关
```bash
rpaclaw start  # 或 nanobot gateway
```
网关启动后会自动设置 Webhook。

### 常见问题
- **Bot 没反应**: 检查 `allowed_users` 是否包含你的 ID
- **Webhook 失败**: 确保服务器 443 端口可访问，且 HTTPS 证书有效
- **不需要公网服务器**: 可使用 Polling 模式（去掉 `webhook_url` 配置）
