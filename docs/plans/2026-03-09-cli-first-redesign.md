# RPAclaw CLI-First Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign RPAclaw from WebUI to CLI-first: single executable with Rich terminal, Setup Wizard, AI-guided channel config, wrapping Nanobot's full mechanism + RPA tools.

**Architecture:** RPAclaw wraps Nanobot CLI (`agent`, `gateway`, `onboard`) with an enhanced first-run wizard and Rich terminal UX. Nanobot's AgentLoop drives all LLM interactions. Channel guidance docs are injected into system prompt so LLM can guide users.

**Tech Stack:** Python 3.12, Nanobot (AgentLoop/Config/Skills/MCP/Heartbeat), Rich + prompt_toolkit, PyInstaller, GitHub Actions CI

---

### Task 1: Clean Up WebUI Code

**Files:**
- Delete: `rpaclaw/web/` (entire directory)
- Delete: `frontend/` (entire directory)
- Modify: `rpaclaw/main.py`
- Modify: `pyproject.toml`

**Step 1:** Remove `rpaclaw/web/` directory and `frontend/` directory

```bash
rm -rf rpaclaw/web/ frontend/
```

**Step 2:** Rewrite `rpaclaw/main.py` as new CLI entry point

```python
"""RPAclaw — Nanobot + RPA automation platform."""

import sys
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(
    help="RPAclaw — AI-powered RPA automation platform",
    no_args_is_help=True,
)
console = Console()


@app.command()
def start(
    config: str = typer.Option(None, "--config", "-c", help="Path to config file"),
    workspace: str = typer.Option(None, "--workspace", "-w", help="Workspace dir"),
):
    """Launch RPAclaw interactive session."""
    from rpaclaw.setup import run_setup_if_needed
    from rpaclaw.chat import start_chat

    run_setup_if_needed(config_path=config)
    start_chat(config_path=config, workspace=workspace)


@app.command()
def setup():
    """Re-run the setup wizard."""
    from rpaclaw.setup import run_setup_wizard
    run_setup_wizard(force=True)


@app.command()
def version():
    """Show version."""
    from rpaclaw import __version__
    console.print(f"RPAclaw v{__version__}")


if __name__ == "__main__":
    app()
```

**Step 3:** Update `pyproject.toml` — remove FastAPI/uvicorn deps, add rich/prompt_toolkit

```toml
dependencies = [
    "nanobot-ai>=0.1.4",
    "typer>=0.20.0,<1.0.0",
    "rich>=14.0.0",
    "prompt-toolkit>=3.0.0",
    "pydantic>=2.12.0,<3.0.0",
    "loguru>=0.7.3,<1.0.0",
    "robocorp-browser>=2.3.0",
    "robocorp-excel>=0.4.0",
    "rpaframework>=28.0.0",
    "rpaframework-pdf>=7.0.0",
]
```

**Step 4:** Commit

```bash
git add -A && git commit -m "refactor: remove WebUI, restructure as CLI-first"
```

---

### Task 2: Setup Wizard

**Files:**
- Create: `rpaclaw/setup.py`

**Step 1:** Implement setup wizard

```python
"""RPAclaw first-run setup wizard."""

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

console = Console()

PROVIDERS = {
    "1": {"name": "OpenAI", "key_prefix": "sk-", "base_url": "https://api.openai.com/v1", "model": "gpt-4o"},
    "2": {"name": "Anthropic", "key_prefix": "sk-ant-", "base_url": "https://api.anthropic.com", "model": "claude-sonnet-4-20250514"},
    "3": {"name": "DeepSeek", "key_prefix": "sk-", "base_url": "https://api.deepseek.com", "model": "deepseek-chat"},
    "4": {"name": "OpenRouter", "key_prefix": "sk-or-", "base_url": "https://openrouter.ai/api/v1", "model": "openai/gpt-4o"},
    "5": {"name": "自定义 / Custom", "key_prefix": "", "base_url": "", "model": ""},
}

LOGO = r"""
[bold cyan]
  ██████╗ ██████╗  █████╗  ██████╗██╗      █████╗ ██╗    ██╗
  ██╔══██╗██╔══██╗██╔══██╗██╔════╝██║     ██╔══██╗██║    ██║
  ██████╔╝██████╔╝███████║██║     ██║     ███████║██║ █╗ ██║
  ██╔══██╗██╔═══╝ ██╔══██║██║     ██║     ██╔══██║██║███╗██║
  ██║  ██║██║     ██║  ██║╚██████╗███████╗██║  ██║╚███╔███╔╝
  ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝
[/bold cyan]
  [dim]AI-Powered RPA Automation Platform[/dim]
"""


def get_config_path() -> Path:
    return Path.home() / ".nanobot" / "config.json"


def load_config() -> dict:
    path = get_config_path()
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_config(config: dict):
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def run_setup_if_needed(config_path: str | None = None):
    """Run setup wizard if no valid config exists."""
    cfg = load_config()
    providers = cfg.get("providers", {})
    has_key = any(
        p.get("apiKey") for p in providers.values()
    ) if providers else False
    if not has_key:
        run_setup_wizard()


def run_setup_wizard(force: bool = False):
    """Interactive setup wizard."""
    console.print(LOGO)
    console.print(Panel("首次启动配置 / First-Time Setup", style="bold green"))

    # Step 1: LLM Provider
    console.print("\n[bold]📡 选择 LLM 供应商 / Select LLM Provider:[/bold]\n")
    table = Table(show_header=False, box=None, padding=(0, 2))
    for k, v in PROVIDERS.items():
        table.add_row(f"[cyan]{k}[/cyan]", v["name"])
    console.print(table)

    choice = Prompt.ask("\n选择 / Choose", choices=list(PROVIDERS.keys()), default="1")
    provider = PROVIDERS[choice]

    if choice == "5":
        provider["name"] = Prompt.ask("Provider 名称 / Name")
        provider["base_url"] = Prompt.ask("API Base URL")
        provider["model"] = Prompt.ask("模型名称 / Model name")

    api_key = Prompt.ask(f"\n🔑 输入 {provider['name']} API Key", password=True)

    # Verify connection
    console.print("\n[yellow]⏳ 验证连接中... / Verifying connection...[/yellow]")
    if _verify_api_key(provider, api_key):
        console.print("[green]✅ 连接成功 / Connection successful![/green]")
    else:
        console.print("[red]⚠️  验证失败，但仍保存配置 / Verification failed, config saved anyway[/red]")

    # Save to nanobot config
    cfg = load_config()
    cfg.setdefault("providers", {})
    cfg["providers"][provider["name"].lower()] = {
        "apiKey": api_key,
        "baseUrl": provider["base_url"],
    }
    cfg["agent"] = cfg.get("agent", {})
    cfg["agent"]["model"] = provider["model"]
    cfg["agent"]["provider"] = provider["name"].lower()
    save_config(cfg)
    console.print(f"\n[green]✅ 配置已保存 / Config saved to {get_config_path()}[/green]")

    # Step 2: Channel config
    _setup_channels(cfg)


def _verify_api_key(provider: dict, api_key: str) -> bool:
    """Quick LLM connectivity check."""
    try:
        import httpx
        resp = httpx.post(
            f"{provider['base_url']}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": provider["model"], "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
            timeout=15,
        )
        return resp.status_code == 200
    except Exception:
        return False


def _setup_channels(cfg: dict):
    """Prompt for channel configuration."""
    console.print("\n" + "─" * 50)
    console.print("\n[bold]📱 配置消息渠道 / Configure Channels[/bold]\n")
    console.print("  [cyan]1[/cyan]  Telegram")
    console.print("  [cyan]2[/cyan]  微信 / WeChat")
    console.print("  [cyan]3[/cyan]  钉钉 / DingTalk")
    console.print("  [cyan]4[/cyan]  飞书 / Feishu (Lark)")
    console.print("  [cyan]0[/cyan]  暂不配置，直接对话 / Skip, go to chat")

    choice = Prompt.ask("\n选择 / Choose", choices=["0", "1", "2", "3", "4"], default="0")

    if choice == "0":
        console.print("\n[dim]你可以随时让 AI 帮你配置渠道 / Ask AI to configure channels anytime[/dim]")
        return

    channel_map = {"1": "telegram", "2": "wechat", "3": "dingtalk", "4": "feishu"}
    channel = channel_map[choice]
    console.print(f"\n[yellow]💡 进入对话后，AI 将指导你完成 {channel} 的配置[/yellow]")
    console.print("[dim]Channel guidance will be provided by AI in the chat[/dim]")

    # Mark pending channel setup
    cfg["_rpaclaw_pending_channel"] = channel
    save_config(cfg)
```

**Step 2:** Commit

```bash
git add rpaclaw/setup.py && git commit -m "feat: add Rich setup wizard with LLM provider selection"
```

---

### Task 3: Chat Loop

**Files:**
- Create: `rpaclaw/chat.py`

**Step 1:** Implement chat loop wrapping Nanobot's AgentLoop

```python
"""RPAclaw Rich terminal chat loop."""

import asyncio
import signal
import sys
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

console = Console()


def start_chat(config_path: str | None = None, workspace: str | None = None):
    """Start the interactive chat loop."""
    console.print("\n[bold green]🤖 RPAclaw 已就绪 / Ready[/bold green]")
    console.print("[dim]输入消息开始对话，/exit 退出，/help 查看帮助[/dim]")
    console.print("[dim]Type a message to chat, /exit to quit, /help for help[/dim]\n")

    # Initialize Nanobot AgentLoop
    from nanobot.config.loader import load_config
    from nanobot.agent.loop import AgentLoop

    config = load_config()

    # Check for pending channel setup
    pending_channel = config.raw.get("_rpaclaw_pending_channel")
    if pending_channel:
        console.print(f"[yellow]📱 检测到待配置的渠道: {pending_channel}[/yellow]")
        console.print("[dim]AI 将在第一轮对话中指导你完成配置[/dim]\n")

    loop = AgentLoop(config=config)

    # Register RPA tools
    try:
        from nanobot.agent.tools.rpa import (
            RPABrowserTool, RPAExcelTool, RPAPDFTool,
            RPAEmailTool, RPADesktopTool,
        )
        loop.register_tool(RPABrowserTool())
        loop.register_tool(RPAExcelTool())
        loop.register_tool(RPAPDFTool())
        loop.register_tool(RPAEmailTool())
        loop.register_tool(RPADesktopTool())
    except ImportError:
        pass

    # Load channel guidance into system context
    _inject_channel_guidance(loop, pending_channel)

    # Prompt session with history
    history_path = Path.home() / ".nanobot" / ".rpaclaw_history"
    session = PromptSession(history=FileHistory(str(history_path)))

    EXIT_COMMANDS = {"exit", "quit", "/exit", "/quit", ":q"}

    # Interactive loop
    try:
        while True:
            try:
                user_input = session.prompt("\n🧑 You > ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not user_input:
                continue
            if user_input.lower() in EXIT_COMMANDS:
                break
            if user_input == "/help":
                _show_help()
                continue

            # Prepend channel setup instruction on first message
            if pending_channel:
                guidance_path = Path(__file__).parent / "channels" / f"{pending_channel}.md"
                if guidance_path.exists():
                    guidance = guidance_path.read_text(encoding="utf-8")
                    user_input = (
                        f"[System: 用户想配置 {pending_channel} 渠道，请根据以下指南指导用户操作]\n"
                        f"{guidance}\n\n"
                        f"用户消息: {user_input}"
                    )
                pending_channel = None
                # Clear pending flag from config
                cfg_raw = config.raw
                cfg_raw.pop("_rpaclaw_pending_channel", None)
                from nanobot.config.loader import save_config as _save
                _save(config)

            # Send to agent and display response
            _run_turn(loop, user_input)

    except KeyboardInterrupt:
        pass
    finally:
        console.print("\n[dim]👋 再见 / Goodbye![/dim]")


def _run_turn(loop: "AgentLoop", message: str):
    """Run one conversation turn with Rich output."""
    chunks = []

    def on_progress(content: str, *, tool_hint: bool = False):
        if tool_hint:
            console.print(f"  [dim]🔧 {content}[/dim]")
        else:
            console.print(f"  [dim]⏳ {content}[/dim]")

    with console.status("[bold cyan]思考中 / Thinking...", spinner="dots"):
        response = asyncio.run(
            loop.chat(message, session_id="cli:rpaclaw", progress_callback=on_progress)
        )

    if response:
        console.print()
        console.print(Panel(Markdown(response), title="🤖 RPAclaw", border_style="cyan"))


def _inject_channel_guidance(loop, pending_channel: str | None):
    """Load channel docs into agent context."""
    channels_dir = Path(__file__).parent / "channels"
    if not channels_dir.exists():
        return

    guidance_parts = []
    for md_file in channels_dir.glob("*.md"):
        guidance_parts.append(f"## {md_file.stem} 渠道配置指南\n{md_file.read_text(encoding='utf-8')}")

    if guidance_parts:
        combined = "\n\n---\n\n".join(guidance_parts)
        loop.add_system_context(
            "channel_guidance",
            f"以下是各消息渠道的配置指南，当用户询问渠道配置时请据此指导:\n\n{combined}"
        )


def _show_help():
    """Display help information."""
    console.print(Panel(
        "[bold]命令 / Commands:[/bold]\n"
        "  /exit    退出 / Exit\n"
        "  /help    显示帮助 / Show help\n\n"
        "[bold]RPA 工具 / RPA Tools:[/bold]\n"
        "  浏览器自动化、PDF、Excel、邮件、桌面控制\n"
        "  直接用自然语言描述任务，AI 会自动调用\n\n"
        "[bold]渠道配置 / Channel Config:[/bold]\n"
        "  告诉 AI 你想配置哪个渠道即可",
        title="帮助 / Help",
        border_style="blue",
    ))
```

**Step 2:** Commit

```bash
git add rpaclaw/chat.py && git commit -m "feat: add Rich terminal chat loop wrapping Nanobot AgentLoop"
```

---

### Task 4: Channel Guidance Docs

**Files:**
- Create: `rpaclaw/channels/telegram.md`
- Create: `rpaclaw/channels/wechat.md`
- Create: `rpaclaw/channels/dingtalk.md`
- Create: `rpaclaw/channels/feishu.md`
- Create: `rpaclaw/channels/__init__.py` (empty marker)

**Step 1:** Create 4 channel guidance documents (Chinese + English, step-by-step with Nanobot config examples)

**Step 2:** Commit

```bash
git add rpaclaw/channels/ && git commit -m "feat: add channel guidance docs for Telegram/WeChat/DingTalk/Feishu"
```

---

### Task 5: PyInstaller Packaging

**Files:**
- Create: `rpaclaw.spec` (PyInstaller spec file)
- Create: `.github/workflows/release.yml`

**Step 1:** Create PyInstaller spec

```python
# rpaclaw.spec
a = Analysis(
    ['rpaclaw/main.py'],
    pathex=['.'],
    datas=[
        ('rpaclaw/channels', 'rpaclaw/channels'),
    ],
    hiddenimports=[
        'nanobot', 'nanobot.agent', 'nanobot.cli',
        'nanobot.config', 'nanobot.agent.tools.rpa',
        'tiktoken_ext.openai_public', 'tiktoken_ext',
    ],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, name='rpaclaw', console=True)
```

**Step 2:** Create GitHub Actions workflow

```yaml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -e . && pip install pyinstaller
      - run: pyinstaller rpaclaw.spec
      - uses: actions/upload-artifact@v4
        with: { name: rpaclaw-windows, path: dist/rpaclaw.exe }
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -e . && pip install pyinstaller
      - run: pyinstaller rpaclaw.spec
      - uses: actions/upload-artifact@v4
        with: { name: rpaclaw-macos, path: dist/rpaclaw }
  release:
    needs: [build-windows, build-macos]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
      - uses: softprops/action-gh-release@v2
        with:
          files: |
            rpaclaw-windows/rpaclaw.exe
            rpaclaw-macos/rpaclaw
```

**Step 3:** Commit

```bash
git add rpaclaw.spec .github/ && git commit -m "feat: add PyInstaller spec + GitHub Actions CI for Windows/macOS"
```

---

### Task 6: Update README + Final Push

**Files:**
- Modify: `README.md`
- Modify: `rpaclaw/__init__.py` (bump version to 0.2.0)

**Step 1:** Rewrite README for CLI-first (bilingual, with CLI screenshots)

**Step 2:** Bump version, commit, tag, push

```bash
git add -A && git commit -m "feat: RPAclaw v0.2.0 — CLI-first redesign"
git tag v0.2.0 && git push origin main --tags
```

---

## Execution Order

| Task | Description | Est. Time |
|------|-------------|-----------|
| 1 | Clean up WebUI code | 5 min |
| 2 | Setup Wizard | 10 min |
| 3 | Chat Loop | 15 min |
| 4 | Channel Guidance Docs | 10 min |
| 5 | PyInstaller + CI | 10 min |
| 6 | README + Release | 5 min |
