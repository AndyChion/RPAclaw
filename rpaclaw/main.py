"""RPAclaw — AI-powered RPA automation platform (CLI-first)."""

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
