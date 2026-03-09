# 🤖 RPAclaw

**Nanobot + RPA 管理平台 / Nanobot + RPA Management Platform**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

RPAclaw 是基于 [Nanobot](https://github.com/HKUDS/nanobot) 框架的 RPA 自动化管理平台，提供 WebUI 界面来管理 AI Agent 的配置、工具、技能和 RPA 工作流。

RPAclaw is an RPA automation management platform built on the [Nanobot](https://github.com/HKUDS/nanobot) framework, providing a WebUI to manage AI Agent configuration, tools, skills, and RPA workflows.

---

## ✨ 功能 / Features

| 功能 Feature | 描述 Description |
|---|---|
| 💬 **流式对话 Streaming Chat** | WebSocket 实时对话 / Real-time WebSocket chat |
| ⚙️ **LLM 配置 LLM Config** | 多 Provider API Key 管理 / Multi-provider API key management |
| 📡 **渠道管理 Channels** | Telegram, WeChat, DingTalk, Slack, Discord 等 / Multiple channels |
| 🔧 **工具管理 Tools** | 查看工具、MCP 服务器配置 / View tools, MCP server config |
| 📚 **Skills 管理** | 浏览和查看 Agent 技能 / Browse and view agent skills |
| ⏰ **定时任务 Cron** | Heartbeat 心跳配置 / Heartbeat config |
| 🎭 **性格编辑 Persona** | 编辑 Agent 身份和规则 / Edit agent identity and rules |
| 🤖 **RPA 工作流 Workflow** | 对话式搭建 + 一键转为 Skill / Chat-driven + save as Skill |

### 🤖 RPA 功能 / RPA Capabilities

- **浏览器自动化 Browser** — Headless Playwright, 14 个操作（导航、点击、填表、截图...）
- **PDF 处理 PDF** — 文本提取、表格提取、元数据
- **Excel 操作 Excel** — 读写、创建、表格导出
- **邮件自动化 Email** — IMAP/SMTP 收发搜索
- **桌面控制 Desktop** — macOS/Windows 鼠标、键盘、窗口管理、OCR

---

## 🚀 快速开始 / Quick Start

### 前置要求 / Prerequisites

- Python 3.11+
- Node.js 18+ (用于前端构建 / for frontend build)

### 一键启动 / One-Click Start

**macOS / Linux:**
```bash
git clone https://github.com/AndyChion/RPAclaw.git
cd RPAclaw
chmod +x launchers/start_rpaclaw.sh
./launchers/start_rpaclaw.sh
```

**Windows (CMD):**
```batch
git clone https://github.com/AndyChion/RPAclaw.git
cd RPAclaw
launchers\start_rpaclaw.bat
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/AndyChion/RPAclaw.git
cd RPAclaw
.\launchers\start_rpaclaw.ps1
```

启动器会自动安装依赖、构建前端、打开浏览器。
Launchers auto-install dependencies, build frontend, and open browser.

### 手动安装 / Manual Install

```bash
# 安装 RPAclaw
pip install -e .

# 安装 RPA 依赖
pip install robocorp-browser robocorp-excel rpaframework rpaframework-pdf
python -m playwright install chromium

# 构建前端
cd frontend && npm install && npx vite build && cd ..

# 启动
rpaclaw start
```

打开 http://localhost:18790 访问 WebUI。
Open http://localhost:18790 in your browser.

---

## 📖 使用指南 / Usage Guide

### RPA 工作流搭建 / Creating RPA Workflows

1. 进入 **RPA 工作流** 页面
2. 用自然语言描述你要自动化的任务
3. Agent 会使用 RPA 工具逐步完成
4. 验证通过后，输入名称点击 **保存为 Skill**
5. 下次提到类似任务时，Agent 会自动使用该 Skill

### 配置 LLM / Configure LLM

1. 进入 **LLM 配置** 页面
2. 填入 Provider 的 API Key
3. 在 **Agent 设置** 中选择模型和参数

---

## 🏗 项目结构 / Project Structure

```
RPAclaw/
├── rpaclaw/                  # Python 后端
│   ├── main.py               # CLI 入口
│   ├── web/                  # FastAPI 服务
│   │   ├── server.py         # WebSocket + 静态文件
│   │   ├── api_config.py     # 配置 CRUD
│   │   ├── api_tools.py      # 工具/MCP/Skills
│   │   └── api_rpa.py        # RPA 工作流
│   └── rpa_skill_creator.py  # 工作流→Skill 转换器
├── frontend/                 # React 前端 (Vite)
├── launchers/                # 启动脚本
└── pyproject.toml
```

---

## 📝 License

MIT License

---

## 🙏 致谢 / Acknowledgments

- [Nanobot](https://github.com/HKUDS/nanobot) — AI Agent 框架
- [robocorp](https://github.com/robocorp/robocorp) — Browser & Excel 自动化
- [rpaframework](https://github.com/robocorp/rpaframework) — RPA 工具库
