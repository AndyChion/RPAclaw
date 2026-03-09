# 🤖 RPAclaw

**AI 驱动的 RPA 自动化平台 / AI-Powered RPA Automation Platform**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

RPAclaw 基于 [Nanobot](https://github.com/HKUDS/nanobot)，提供 CLI-first 的 AI Agent 交互体验，内置 RPA 自动化工具，支持 Telegram/微信/钉钉/飞书消息渠道。

Built on [Nanobot](https://github.com/HKUDS/nanobot), RPAclaw provides a CLI-first AI Agent experience with built-in RPA automation tools and multi-channel messaging support.

---

## ✨ 功能 / Features

| 功能 | 描述 |
|------|------|
| 🚀 **一键启动** | 双击 exe / app 即可运行，自动引导配置 |
| 🔑 **智能配置** | 首次启动自动引导选择 LLM + 输入 API Key |
| 📱 **渠道指导** | AI 指导配置 Telegram / 微信 / 钉钉 / 飞书 |
| 💬 **Rich 终端** | Markdown 渲染、彩色输出、进度动画 |
| 🤖 **完整 Agent** | Nanobot 全部机制：Skills、MCP、Heartbeat |

### 🔧 RPA 工具 / RPA Tools

- 🌐 **浏览器** — Playwright headless，14 个操作
- 📄 **PDF** — 文本提取、表格提取
- 📊 **Excel** — 读写、创建工作表
- 📧 **邮件** — IMAP/SMTP 收发搜索
- 🖥️ **桌面** — macOS/Windows 鼠标键盘控制、OCR

---

## 🚀 快速开始 / Quick Start

### 方式一：下载可执行文件（推荐）

从 [Releases](https://github.com/AndyChion/RPAclaw/releases) 下载：
- **Windows**: `rpaclaw-windows.exe` → 双击运行
- **macOS**: `rpaclaw-macos` → `chmod +x rpaclaw-macos && ./rpaclaw-macos start`

### 方式二：pip 安装

```bash
pip install -e .
rpaclaw start
```

### 方式三：Docker

```bash
docker load < rpaclaw-docker-image.tar.gz
docker run -d -p 18790:18790 rpaclaw:latest
```

---

## 📖 使用流程 / Usage Flow

```
启动 rpaclaw start
  ↓
选择 LLM (OpenAI / Anthropic / DeepSeek / OpenRouter / 自定义)
  ↓
输入 API Key → 自动验证连接
  ↓
选择配置渠道 (Telegram / 微信 / 钉钉 / 飞书 / 跳过)
  ↓
进入对话 → 直接用自然语言描述任务
  ↓
AI 自动选择 RPA 工具完成自动化
```

### 命令 / Commands

```bash
rpaclaw start          # 启动交互对话
rpaclaw setup          # 重新运行配置向导
rpaclaw version        # 显示版本
```

### 对话中 / In Chat

```
/exit    退出
/help    帮助
```

---

## 🏗 项目结构 / Structure

```
RPAclaw/
├── rpaclaw/
│   ├── main.py              # CLI 入口
│   ├── setup.py             # 配置向导
│   ├── chat.py              # 对话循环
│   ├── rpa_skill_creator.py # 工作流→Skill
│   └── channels/            # 渠道配置指南
│       ├── telegram.md
│       ├── wechat.md
│       ├── dingtalk.md
│       └── feishu.md
├── rpaclaw.spec             # PyInstaller 打包
├── .github/workflows/       # CI/CD
├── Dockerfile               # Docker 备选
└── pyproject.toml
```

---

## 📝 License

MIT — [Nanobot](https://github.com/HKUDS/nanobot) · [robocorp](https://github.com/robocorp/robocorp) · [rpaframework](https://github.com/robocorp/rpaframework)
