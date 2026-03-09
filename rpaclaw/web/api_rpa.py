"""RPA workflow management API endpoints."""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/rpa", tags=["rpa"])

# In-memory workflow storage (simple for MVP)
_workflows: dict[str, dict] = {}


@router.get("/workflows")
async def list_workflows():
    """List saved RPA workflows."""
    return {"workflows": [
        {"name": name, "steps": len(w.get("messages", [])), "created": w.get("created")}
        for name, w in _workflows.items()
    ]}


@router.post("/workflows")
async def save_workflow(data: dict[str, Any]):
    """Save an RPA workflow from chat messages."""
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Workflow name required")

    from datetime import datetime
    _workflows[name] = {
        "messages": data.get("messages", []),
        "created": datetime.now().isoformat(),
    }

    return {"status": "ok", "name": name}


@router.post("/workflows/{name}/to-skill")
async def workflow_to_skill(name: str):
    """Convert a saved workflow to a Skill."""
    if name not in _workflows:
        raise HTTPException(status_code=404, detail=f"Workflow '{name}' not found")

    from rpaclaw.rpa_skill_creator import RPASkillCreator

    workflow_data = _workflows[name]
    creator = RPASkillCreator()
    path = creator.create_skill_from_chat(
        name=name,
        messages=workflow_data.get("messages", []),
        description=f"Auto-generated RPA workflow: {name}",
    )

    return {"status": "ok", "skill_path": str(path), "name": name}


@router.get("/skills")
async def list_rpa_skills():
    """List RPA-specific skills."""
    from rpaclaw.rpa_skill_creator import RPASkillCreator
    creator = RPASkillCreator()

    skills = []
    if creator.skills_dir.exists():
        for skill_dir in creator.skills_dir.iterdir():
            if skill_dir.name.startswith("rpa-") and (skill_dir / "SKILL.md").exists():
                content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                skills.append({
                    "name": skill_dir.name,
                    "path": str(skill_dir),
                    "content_preview": content[:300],
                })

    return {"skills": skills}
