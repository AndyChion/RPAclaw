"""RPAclaw — AI-powered RPA automation platform (CLI-first)."""

import sys
from pathlib import Path

import typer
from rich.console import Console

console = Console()


def _start_impl(
    config: str = None,
    workspace: str = None,
):
    """Launch RPAclaw interactive session."""
    try:
        from rpaclaw.setup import run_setup_if_needed
        from rpaclaw.chat import start_chat

        run_setup_if_needed(config_path=config)
        start_chat(config_path=config, workspace=workspace)
    except KeyboardInterrupt:
        console.print("\n[dim]👋 Goodbye![/dim]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        input("\n按 Enter 退出 / Press Enter to exit...")
        sys.exit(1)


app = typer.Typer(
    help="RPAclaw — AI-powered RPA automation platform",
    invoke_without_command=True,
)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Default: run 'start' when no subcommand is given (e.g. double-click exe)."""
    if ctx.invoked_subcommand is None:
        _start_impl()


@app.command()
def start(
    config: str = typer.Option(None, "--config", "-c", help="Path to config file"),
    workspace: str = typer.Option(None, "--workspace", "-w", help="Workspace dir"),
):
    """Launch RPAclaw interactive session."""
    _start_impl(config=config, workspace=workspace)


@app.command()
def setup():
    """Re-run the setup wizard."""
    try:
        from rpaclaw.setup import run_setup_wizard
        run_setup_wizard(force=True)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        input("\n按 Enter 退出 / Press Enter to exit...")


@app.command()
def version():
    """Show version."""
    from rpaclaw import __version__
    console.print(f"RPAclaw v{__version__}")


if __name__ == "__main__":
    app()
