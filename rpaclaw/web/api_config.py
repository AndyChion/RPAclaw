"""Configuration management API endpoints."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

router = APIRouter(tags=["config"])


@router.get("/config")
async def get_config():
    """Get the full Nanobot configuration."""
    from rpaclaw.web.server import get_config
    config = get_config()
    return config.model_dump(by_alias=True)


@router.put("/config")
async def update_config(data: dict[str, Any]):
    """Update the full Nanobot configuration."""
    from nanobot.config.schema import Config
    from nanobot.config.loader import save_config
    from rpaclaw.web.server import get_config_path

    try:
        new_config = Config.model_validate(data)
        save_config(new_config, get_config_path())

        # Update in-memory config
        import rpaclaw.web.server as srv
        srv._config = new_config

        return {"status": "ok", "message": "Configuration saved"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config/providers")
async def get_providers():
    """Get LLM provider configurations."""
    from rpaclaw.web.server import get_config
    config = get_config()
    providers = config.providers.model_dump(by_alias=True)
    # Mask API keys for security
    for name, prov in providers.items():
        if isinstance(prov, dict) and prov.get("apiKey"):
            key = prov["apiKey"]
            prov["apiKey"] = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
            prov["_hasKey"] = True
        elif isinstance(prov, dict):
            prov["_hasKey"] = False
    return {"providers": providers}


@router.put("/config/providers")
async def update_providers(data: dict[str, Any]):
    """Update LLM provider configurations."""
    from nanobot.config.loader import save_config
    from rpaclaw.web.server import get_config, get_config_path

    config = get_config()
    providers_data = data.get("providers", data)

    # Preserve existing API keys if masked value sent
    existing = config.providers.model_dump(by_alias=True)
    for name, new_prov in providers_data.items():
        if isinstance(new_prov, dict) and new_prov.get("apiKey", "").endswith("..."):
            # Keep existing key
            if name in existing and existing[name].get("apiKey"):
                new_prov["apiKey"] = existing[name]["apiKey"]
        new_prov.pop("_hasKey", None)

    try:
        from nanobot.config.schema import ProvidersConfig
        config.providers = ProvidersConfig.model_validate(providers_data)
        save_config(config, get_config_path())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config/channels")
async def get_channels():
    """Get channel configurations."""
    from rpaclaw.web.server import get_config
    config = get_config()
    return config.channels.model_dump(by_alias=True)


@router.put("/config/channels")
async def update_channels(data: dict[str, Any]):
    """Update channel configurations."""
    from nanobot.config.loader import save_config
    from rpaclaw.web.server import get_config, get_config_path

    try:
        from nanobot.config.schema import ChannelsConfig
        config = get_config()
        config.channels = ChannelsConfig.model_validate(data)
        save_config(config, get_config_path())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config/agent")
async def get_agent_config():
    """Get agent defaults configuration."""
    from rpaclaw.web.server import get_config
    config = get_config()
    return config.agents.defaults.model_dump(by_alias=True)


@router.put("/config/agent")
async def update_agent_config(data: dict[str, Any]):
    """Update agent defaults."""
    from nanobot.config.loader import save_config
    from rpaclaw.web.server import get_config, get_config_path

    try:
        from nanobot.config.schema import AgentDefaults
        config = get_config()
        config.agents.defaults = AgentDefaults.model_validate(data)
        save_config(config, get_config_path())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
