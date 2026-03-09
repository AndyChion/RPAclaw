# 飞书渠道配置指南 (Feishu / Lark)

## 前提条件
- 飞书开发者账号
- 一台公网可访问的服务器

## 配置步骤

### 第一步：创建飞书应用
1. 访问 https://open.feishu.cn/app 登录开发者后台
2. 「创建企业自建应用」
3. 填写应用名称和描述
4. 在「凭证与基础信息」中记录 **App ID** 和 **App Secret**

### 第二步：添加机器人能力
1. 在应用详情 →「添加应用能力」→ 选择「机器人」
2. 配置消息卡片请求网址: `https://你的域名/webhook/feishu`
3. 添加 **事件订阅**:
   - 请求网址: `https://你的域名/webhook/feishu/event`
   - 订阅事件: `im.message.receive_v1`（接收消息）

### 第三步：配置权限
在「权限管理」中开通:
- `im:message` — 获取与发送消息
- `im:message:send_as_bot` — 以机器人身份发消息
- `im:chat` — 获取群信息

### 第四步：配置 Nanobot
编辑 `~/.nanobot/config.json`:

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "app_id": "你的App ID",
      "app_secret": "你的App Secret",
      "verification_token": "事件订阅的Verification Token",
      "encrypt_key": "事件订阅的Encrypt Key（可选）"
    }
  }
}
```

### 第五步：发布与测试
1. 创建版本并提交审核（企业内部应用通常自动通过）
2. 在飞书中搜索机器人名称，发送消息测试

### 常见问题
- **事件回调失败**: 确保服务已启动，且能正确响应 challenge 验证
- **没有权限**: 检查是否已在权限管理中添加并发布了必要权限
- **消息发不出去**: 确认 `im:message:send_as_bot` 权限已开通
