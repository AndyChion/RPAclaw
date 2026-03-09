# 微信渠道配置指南 (WeChat via 企业微信)

## 前提条件
- 企业微信管理员账号（个人可免费注册企业）
- 一台公网可访问的服务器

## 配置步骤

### 第一步：注册企业微信
1. 访问 https://work.weixin.qq.com/ 注册企业
2. 登录企业微信管理后台

### 第二步：创建自建应用
1. 进入「应用管理」→「自建」→「创建应用」
2. 填写应用名称（如 RPAclaw）、上传 Logo
3. 记录 **AgentId**
4. 在「企业信息」页记录 **CorpID**
5. 在应用详情页记录 **Secret**

### 第三步：配置接收消息
1. 在应用详情页 →「接收消息」→「设置API接收」
2. 填入：
   - URL: `https://你的域名/webhook/wechat`
   - Token: 自定义一个随机字符串
   - EncodingAESKey: 点击「随机获取」
3. 保存（需要你的服务已启动并能响应验证请求）

### 第四步：配置 Nanobot
编辑 `~/.nanobot/config.json`:

```json
{
  "channels": {
    "wechat": {
      "enabled": true,
      "corp_id": "你的CorpID",
      "agent_id": "你的AgentId",
      "secret": "你的Secret",
      "token": "你设置的Token",
      "encoding_aes_key": "你的EncodingAESKey"
    }
  }
}
```

### 第五步：设置可信域名
1. 在应用详情 →「网页授权及JS-SDK」→ 设置可信域名
2. 填入你的服务器域名

### 常见问题
- **回调验证失败**: 确保服务已启动，Token 和 AESKey 与后台一致
- **收不到消息**: 检查「接收消息」的 URL 是否正确配置
- **想用个人微信**: 需要第三方桥接工具如 wechaty，配置更复杂
