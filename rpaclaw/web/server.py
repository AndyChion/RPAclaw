"""FastAPI application with WebSocket streaming chat."""

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from loguru import logger


# Global references
_agent_loop = None
_config = None
_config_path = None


def get_config():
    global _config
    return _config


def get_config_path():
    global _config_path
    return _config_path


def create_app(config_path: Path | None = None, dev_mode: bool = False) -> FastAPI:
    """Create the FastAPI application."""
    global _agent_loop, _config, _config_path

    app = FastAPI(title="RPAclaw", version="0.1.0")

    # CORS for dev mode
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if dev_mode else ["http://localhost:18790"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Load nanobot config
    from nanobot.config.loader import load_config, get_config_path as nb_config_path
    _config_path = config_path or Path(nb_config_path())
    _config = load_config(_config_path)

    # Register API routes
    from rpaclaw.web.api_config import router as config_router
    from rpaclaw.web.api_tools import router as tools_router
    from rpaclaw.web.api_rpa import router as rpa_router

    app.include_router(config_router, prefix="/api")
    app.include_router(tools_router, prefix="/api")
    app.include_router(rpa_router, prefix="/api")

    # WebSocket chat endpoint
    @app.websocket("/ws/chat")
    async def ws_chat(websocket: WebSocket):
        await websocket.accept()
        logger.info("WebSocket chat connected")

        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                user_text = msg.get("content", "")
                session_key = msg.get("session_key", "webui:default")

                if not user_text.strip():
                    continue

                # Get or create agent loop
                loop = await _get_or_create_agent(session_key)

                # Stream progress callback
                async def on_progress(content: str, **kwargs):
                    is_hint = kwargs.get("tool_hint", False)
                    await websocket.send_json({
                        "type": "progress",
                        "content": content,
                        "tool_hint": is_hint,
                    })

                # Process message
                try:
                    result = await loop.process_direct(
                        content=user_text,
                        session_key=session_key,
                        channel="webui",
                        chat_id="default",
                        on_progress=on_progress,
                    )
                    await websocket.send_json({
                        "type": "message",
                        "content": result,
                    })
                except Exception as e:
                    logger.exception("Error processing chat message")
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Error: {str(e)}",
                    })

        except WebSocketDisconnect:
            logger.info("WebSocket chat disconnected")
        except Exception as e:
            logger.exception("WebSocket error")

    # Serve frontend static files (production)
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists() and not dev_mode:
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

        @app.get("/{path:path}")
        async def serve_spa(path: str):
            file_path = frontend_dist / path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(frontend_dist / "index.html"))

    return app


async def _get_or_create_agent(session_key: str = "webui:default"):
    """Get or create the AgentLoop singleton."""
    global _agent_loop

    if _agent_loop is not None:
        return _agent_loop

    from nanobot.bus.queue import MessageBus
    from nanobot.providers.base import create_provider
    from nanobot.agent.loop import AgentLoop

    config = get_config()
    bus = MessageBus()

    provider = create_provider(
        config.agents.defaults.provider,
        api_key=config.get_api_key(),
        api_base=config.get_api_base(),
    )

    workspace = config.workspace_path
    workspace.mkdir(parents=True, exist_ok=True)

    _agent_loop = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=workspace,
        model=config.agents.defaults.model,
        max_iterations=config.agents.defaults.max_tool_iterations,
        temperature=config.agents.defaults.temperature,
        max_tokens=config.agents.defaults.max_tokens,
        reasoning_effort=config.agents.defaults.reasoning_effort,
        brave_api_key=config.tools.web.search.api_key or None,
        web_proxy=config.tools.web.proxy,
        exec_config=config.tools.exec,
        restrict_to_workspace=config.tools.restrict_to_workspace,
        mcp_servers={k: v.model_dump(by_alias=True) for k, v in config.tools.mcp_servers.items()} if config.tools.mcp_servers else None,
    )

    return _agent_loop
