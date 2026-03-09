"""RPAclaw first-run setup wizard."""

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

# Map choice → (display_name, nanobot_provider_field, api_base, default_model)
PROVIDERS = {
    "1": ("Minimax",        "minimax",    "https://api.minimax.chat/v1",   "minimax-m2.5"),
    "2": ("Kimi (Moonshot)", "moonshot",   "https://api.moonshot.cn/v1",    "kimi-k2.5"),
    "3": ("DeepSeek",       "deepseek",   "https://api.deepseek.com",      "deepseek-chat"),
    "4": ("OpenAI",         "openai",     "https://api.openai.com/v1",     "gpt-4.1"),
    "5": ("Anthropic",      "anthropic",  "https://api.anthropic.com",     "claude-sonnet-4-20250514"),
    "6": ("OpenRouter",     "openrouter", "https://openrouter.ai/api/v1",  "openai/gpt-4.1"),
    "7": ("自定义 / Custom",  "custom",     "",                              ""),
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
  [dim]AI-Powered RPA Automation Platform  v0.2.0[/dim]
"""


def get_config_path() -> Path:
    """Return nanobot config path."""
    return Path.home() / ".nanobot" / "config.json"


def get_state_path() -> Path:
    """Return RPAclaw internal state file (not parsed by Nanobot)."""
    return Path.home() / ".nanobot" / ".rpaclaw_state.json"


def load_config() -> dict:
    """Load existing config or return empty dict."""
    path = get_config_path()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(config: dict):
    """Save config to disk."""
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def load_state() -> dict:
    """Load RPAclaw internal state."""
    path = get_state_path()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_state(state: dict):
    """Save RPAclaw internal state."""
    path = get_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def run_setup_if_needed(config_path: str | None = None):
    """Run setup wizard only if no valid API key is configured."""
    cfg = load_config()
    providers = cfg.get("providers", {})
    has_key = False
    if isinstance(providers, dict):
        for prov in providers.values():
            if isinstance(prov, dict) and prov.get("apiKey"):
                has_key = True
                break
    if not has_key:
        run_setup_wizard()


def run_setup_wizard(force: bool = False):
    """Interactive first-run setup wizard."""
    console.print(LOGO)
    console.print(Panel(
        "首次启动配置 / First-Time Setup",
        style="bold green",
        subtitle="[dim]按提示选择即可 / Follow the prompts[/dim]",
    ))

    # ─── Step 1: LLM Provider ─────────────────────────────────
    console.print("\n[bold]📡  选择大模型供应商 / Select LLM Provider:[/bold]\n")
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="cyan bold", width=4)
    table.add_column()
    table.add_column(style="dim")
    for k, (display, _, _, model) in PROVIDERS.items():
        table.add_row(k, display, f"({model})" if model else "")
    console.print(table)

    choice = Prompt.ask(
        "\n请选择 / Choose",
        choices=list(PROVIDERS.keys()),
        default="1",
    )
    display_name, provider_field, api_base, default_model = PROVIDERS[choice]

    if choice == "7":
        display_name = Prompt.ask("  供应商名称 / Provider name")
        api_base = Prompt.ask("  API Base URL")
        default_model = Prompt.ask("  模型名称 / Model name")

    # API Key
    api_key = Prompt.ask(
        f"\n🔑  输入 {display_name} API Key",
        password=True,
    )

    # Verify
    console.print("\n[yellow]⏳  验证连接中 / Verifying...[/yellow]", end=" ")
    ok = _verify_api_key(api_base, api_key, default_model)
    if ok:
        console.print("[green]✅ 成功 / Success![/green]")
    else:
        console.print("[red]⚠️  验证失败，配置已保存 / Verification failed, config saved[/red]")

    # Save — using Nanobot's exact schema (camelCase)
    cfg = load_config()

    # providers.<field>.apiKey / apiBase
    cfg.setdefault("providers", {})
    provider_entry = {"apiKey": api_key}
    if api_base:
        provider_entry["apiBase"] = api_base
    cfg["providers"][provider_field] = provider_entry

    # agents.defaults.model / provider
    cfg.setdefault("agents", {})
    cfg["agents"].setdefault("defaults", {})
    cfg["agents"]["defaults"]["model"] = default_model
    cfg["agents"]["defaults"]["provider"] = provider_field

    save_config(cfg)
    console.print(f"\n[green]✅  配置已保存 → {get_config_path()}[/green]")

    # ─── Step 2: Channel Configuration ────────────────────────
    _setup_channels()

    console.print("\n" + "─" * 50)
    console.print("[bold green]🎉  配置完成，进入对话模式！/ Setup complete![/bold green]\n")


def _verify_api_key(api_base: str, api_key: str, model: str) -> bool:
    """Quick API connectivity check."""
    if not api_base or not api_key or not model:
        return False
    try:
        import httpx

        headers = {"Content-Type": "application/json"}
        body = {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5,
        }

        # Anthropic uses different auth
        if "anthropic" in api_base.lower():
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
            url = f"{api_base}/v1/messages"
        else:
            headers["Authorization"] = f"Bearer {api_key}"
            url = f"{api_base}/chat/completions"

        resp = httpx.post(url, headers=headers, json=body, timeout=15)
        return resp.status_code == 200
    except Exception:
        return False


def _setup_channels():
    """Offer channel configuration options."""
    console.print("\n" + "─" * 50)
    console.print("\n[bold]📱  配置消息渠道 / Configure Messaging Channel[/bold]\n")
    console.print("  [cyan]1[/cyan]  Telegram")
    console.print("  [cyan]2[/cyan]  微信 (WeChat via WeCom/Mochat)")
    console.print("  [cyan]3[/cyan]  钉钉 (DingTalk)")
    console.print("  [cyan]4[/cyan]  飞书 (Feishu / Lark)")
    console.print("  [cyan]0[/cyan]  暂不配置，直接对话 / Skip → chat now\n")

    choice = Prompt.ask(
        "选择 / Choose",
        choices=["0", "1", "2", "3", "4"],
        default="0",
    )

    if choice == "0":
        console.print("[dim]  随时可以让 AI 指导你配置渠道 / Ask AI to set up channels anytime[/dim]")
        return

    channel_map = {"1": "telegram", "2": "wechat", "3": "dingtalk", "4": "feishu"}
    channel_name = channel_map[choice]

    console.print(f"\n[yellow]💡  进入对话后，AI 将指导你配置 {channel_name}[/yellow]")
    console.print("[dim]  The AI will guide you through the setup in chat[/dim]")

    # Store in RPAclaw's own state file (NOT in nanobot config.json)
    state = load_state()
    state["pending_channel"] = channel_name
    save_state(state)
