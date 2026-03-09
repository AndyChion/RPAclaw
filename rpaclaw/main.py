"""RPAclaw CLI — start the WebUI server."""

import sys
from pathlib import Path

import typer

app = typer.Typer(help="RPAclaw — Nanobot + RPA management platform")


@app.command()
def start(
    host: str = typer.Option("127.0.0.1", help="Bind host"),
    port: int = typer.Option(18790, help="Bind port"),
    config: str = typer.Option(None, help="Path to nanobot config.json"),
    dev: bool = typer.Option(False, help="Enable frontend dev proxy"),
):
    """Start the RPAclaw WebUI server."""
    import uvicorn
    from rpaclaw.web.server import create_app

    config_path = Path(config) if config else None
    application = create_app(config_path=config_path, dev_mode=dev)

    typer.echo(f"🚀 RPAclaw starting at http://{host}:{port}")
    typer.echo("   Press Ctrl+C to stop")

    uvicorn.run(application, host=host, port=port, log_level="info")


@app.command()
def version():
    """Show RPAclaw version."""
    from rpaclaw import __version__
    typer.echo(f"RPAclaw v{__version__}")


if __name__ == "__main__":
    app()
