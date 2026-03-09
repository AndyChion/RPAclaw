"""RPAclaw Rich terminal chat loop — wraps Nanobot AgentLoop."""

import asyncio
import signal
import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

EXIT_COMMANDS = {"exit", "quit", "/exit", "/quit", ":q"}


def start_chat(config_path: str | None = None, workspace: str | None = None):
    """Start the RPAclaw interactive chat session."""
    from loguru import logger

    from nanobot.agent.loop import AgentLoop
    from nanobot.bus.queue import MessageBus
    from nanobot.config.loader import load_config
    from nanobot.config.paths import get_cron_dir, get_workspace_path
    from nanobot.cron.service import CronService

    logger.disable("nanobot")

    # Load Nanobot config
    config = load_config()

    # Sync workspace
    workspace_path = Path(workspace) if workspace else config.workspace_path
    if not workspace_path.exists():
        workspace_path.mkdir(parents=True, exist_ok=True)
    from nanobot.cli.commands import sync_workspace_templates, _make_provider
    sync_workspace_templates(workspace_path)

    # Create provider, bus, cron
    bus = MessageBus()
    provider = _make_provider(config)
    cron_store_path = get_cron_dir() / "jobs.json"
    cron = CronService(cron_store_path)

    # Create AgentLoop with full Nanobot config
    agent_loop = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=workspace_path,
        model=config.agents.defaults.model,
        temperature=config.agents.defaults.temperature,
        max_tokens=config.agents.defaults.max_tokens,
        max_iterations=config.agents.defaults.max_tool_iterations,
        memory_window=config.agents.defaults.memory_window,
        reasoning_effort=config.agents.defaults.reasoning_effort,
        brave_api_key=getattr(config.tools.web.search, "api_key", None),
        web_proxy=getattr(config.tools.web, "proxy", None) or None,
        exec_config=config.tools.exec,
        cron_service=cron,
        restrict_to_workspace=config.tools.restrict_to_workspace,
        mcp_servers=config.tools.mcp_servers,
        channels_config=config.channels,
    )

    # Register RPA tools
    _register_rpa_tools(agent_loop)

    # Inject channel guidance
    _inject_channel_guidance(agent_loop)

    # Check pending channel setup
    pending_channel = config.raw.get("_rpaclaw_pending_channel")
    if pending_channel:
        console.print(f"[yellow]📱  AI 将指导你配置 {pending_channel}[/yellow]\n")

    console.print("[bold green]🤖  RPAclaw 已就绪 / Ready[/bold green]")
    console.print("[dim]  输入消息对话 • /exit 退出 • /help 帮助[/dim]")
    console.print("[dim]  Type to chat  • /exit quit • /help for help[/dim]\n")

    # Prompt session with history
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory

    history_path = Path.home() / ".nanobot" / ".rpaclaw_history"
    session = PromptSession(history=FileHistory(str(history_path)))

    # Signal handling
    def _handle_signal(signum, _frame):
        console.print("\n[dim]👋  再见 / Goodbye![/dim]")
        sys.exit(0)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # ─── Main loop ────────────────────────────────────────────
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

            # First message: inject channel guidance if pending
            actual_input = user_input
            if pending_channel:
                guidance = _load_channel_doc(pending_channel)
                if guidance:
                    actual_input = (
                        f"[System: 用户想要配置 {pending_channel} 渠道。"
                        f"请根据以下指南逐步指导用户完成配置。]\n\n"
                        f"{guidance}\n\n"
                        f"用户消息: {user_input}"
                    )
                pending_channel = None
                # Clear pending flag
                from rpaclaw.setup import load_config as _load, save_config as _save
                cfg = _load()
                cfg.pop("_rpaclaw_pending_channel", None)
                _save(cfg)

            # Run conversation turn
            _run_turn(agent_loop, actual_input)

    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(agent_loop.close_mcp())
        console.print("\n[dim]👋  再见 / Goodbye![/dim]")


def _run_turn(agent_loop, message: str):
    """Execute one chat turn with Rich output."""

    async def _progress(content: str, *, tool_hint: bool = False):
        prefix = "🔧" if tool_hint else "⏳"
        console.print(f"  [dim]{prefix} {content}[/dim]")

    try:
        with console.status("[bold cyan]思考中 / Thinking...[/bold cyan]", spinner="dots"):
            response = asyncio.run(
                agent_loop.process_direct(
                    message,
                    session_id="cli:rpaclaw",
                    on_progress=_progress,
                )
            )

        if response:
            console.print()
            try:
                md = Markdown(response)
                console.print(Panel(md, title="[bold cyan]🤖 RPAclaw[/bold cyan]", border_style="cyan", padding=(1, 2)))
            except Exception:
                console.print(Panel(response, title="🤖 RPAclaw", border_style="cyan"))
    except Exception as e:
        console.print(f"\n[red]❌  错误 / Error: {e}[/red]")


def _register_rpa_tools(agent_loop):
    """Register RPA tools with the AgentLoop."""
    try:
        from nanobot.agent.tools.rpa import (
            RPABrowserTool,
            RPAExcelTool,
            RPAPDFTool,
            RPAEmailTool,
            RPADesktopTool,
        )
        for tool_cls in [RPABrowserTool, RPAExcelTool, RPAPDFTool, RPAEmailTool, RPADesktopTool]:
            try:
                agent_loop.register_tool(tool_cls())
            except Exception:
                pass
    except ImportError:
        pass


def _inject_channel_guidance(agent_loop):
    """Load all channel docs into agent system context."""
    channels_dir = Path(__file__).parent / "channels"
    if not channels_dir.exists():
        return

    parts = []
    for md_file in sorted(channels_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        parts.append(f"## {md_file.stem} 渠道配置指南\n\n{content}")

    if parts:
        combined = "\n\n---\n\n".join(parts)
        # Use agent's system context if available
        try:
            agent_loop.add_system_context(
                "rpaclaw_channel_guidance",
                f"以下是各消息渠道的配置指南。当用户询问渠道配置时，请据此逐步指导:\n\n{combined}",
            )
        except (AttributeError, TypeError):
            pass


def _load_channel_doc(channel: str) -> str | None:
    """Load a single channel guidance document."""
    doc_path = Path(__file__).parent / "channels" / f"{channel}.md"
    if doc_path.exists():
        return doc_path.read_text(encoding="utf-8")
    return None


def _show_help():
    """Show help panel."""
    console.print(Panel(
        "[bold]命令 / Commands:[/bold]\n"
        "  /exit     退出 / Exit\n"
        "  /help     帮助 / Help\n\n"
        "[bold]RPA 能力 / RPA Capabilities:[/bold]\n"
        "  🌐 浏览器自动化 (Playwright headless)\n"
        "  📄 PDF 文本/表格提取\n"
        "  📊 Excel 读写创建\n"
        "  📧 邮件收发 (IMAP/SMTP)\n"
        "  🖥️ 桌面控制 (macOS/Windows)\n\n"
        "[bold]使用方法 / Usage:[/bold]\n"
        "  直接用自然语言描述任务，AI 会自动选择工具\n"
        "  Just describe your task, AI picks the right tools\n\n"
        "[bold]渠道配置 / Channel Config:[/bold]\n"
        "  告诉 AI: \"帮我配置 Telegram\" 即可\n"
        "  Say: \"Help me set up Telegram\"",
        title="[bold blue]帮助 / Help[/bold blue]",
        border_style="blue",
        padding=(1, 2),
    ))
