"""Tools, MCP, Skills, and Cron API endpoints."""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["tools"])


@router.get("/tools")
async def list_tools():
    """List registered tools."""
    from rpaclaw.web.server import _agent_loop
    if not _agent_loop:
        return {"tools": []}

    tools = []
    for name, tool in _agent_loop.tools._tools.items():
        tools.append({
            "name": name,
            "description": tool.description,
            "parameters": tool.parameters,
        })
    return {"tools": tools}


@router.get("/mcp")
async def get_mcp_servers():
    """Get MCP server configurations."""
    from rpaclaw.web.server import get_config
    config = get_config()
    servers = {}
    for name, srv in config.tools.mcp_servers.items():
        servers[name] = srv.model_dump(by_alias=True)
    return {"mcp_servers": servers}


@router.put("/mcp")
async def update_mcp_servers(data: dict[str, Any]):
    """Update MCP server configurations."""
    from nanobot.config.loader import save_config
    from nanobot.config.schema import MCPServerConfig
    from rpaclaw.web.server import get_config, get_config_path

    try:
        config = get_config()
        new_servers = {}
        for name, srv_data in data.get("mcp_servers", data).items():
            new_servers[name] = MCPServerConfig.model_validate(srv_data)
        config.tools.mcp_servers = new_servers
        save_config(config, get_config_path())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/skills")
async def list_skills():
    """List available skills."""
    from rpaclaw.web.server import get_config
    config = get_config()
    workspace = config.workspace_path

    skills = []
    skills_dir = workspace / "skills"
    if not skills_dir.exists():
        # Try nanobot built-in skills
        nanobot_skills = Path(__file__).parent.parent.parent / "nanobot_project" / "nanobot" / "nanobot" / "skills"
        if nanobot_skills.exists():
            skills_dir = nanobot_skills

    if skills_dir.exists():
        for skill_dir in sorted(skills_dir.iterdir()):
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text(encoding="utf-8")
                # Parse frontmatter
                name = skill_dir.name
                description = ""
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        for line in parts[1].strip().split("\n"):
                            if line.startswith("description:"):
                                description = line.split(":", 1)[1].strip().strip('"\'')
                            elif line.startswith("name:"):
                                name = line.split(":", 1)[1].strip().strip('"\'')
                skills.append({
                    "name": name,
                    "directory": str(skill_dir),
                    "description": description,
                    "content_preview": content[:500],
                })

    return {"skills": skills}


@router.get("/skills/{skill_name}")
async def get_skill(skill_name: str):
    """Get full skill content."""
    from rpaclaw.web.server import get_config
    config = get_config()
    workspace = config.workspace_path

    for base_dir in [workspace / "skills", Path(__file__).parent.parent.parent / "nanobot_project" / "nanobot" / "nanobot" / "skills"]:
        skill_md = base_dir / skill_name / "SKILL.md"
        if skill_md.exists():
            return {"name": skill_name, "content": skill_md.read_text(encoding="utf-8")}

    raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")


@router.get("/cron")
async def list_cron_jobs():
    """List cron/heartbeat jobs."""
    from rpaclaw.web.server import get_config
    config = get_config()
    return {
        "heartbeat": config.gateway.heartbeat.model_dump(by_alias=True),
        "jobs": [],  # TODO: read from cron service
    }


@router.put("/cron/heartbeat")
async def update_heartbeat(data: dict[str, Any]):
    """Update heartbeat configuration."""
    from nanobot.config.loader import save_config
    from nanobot.config.schema import HeartbeatConfig
    from rpaclaw.web.server import get_config, get_config_path

    try:
        config = get_config()
        config.gateway.heartbeat = HeartbeatConfig.model_validate(data)
        save_config(config, get_config_path())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
