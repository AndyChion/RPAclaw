"""RPA workflow → Skill converter."""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Any


class RPASkillCreator:
    """Convert RPA tool call sequences from chat history into reusable Skills."""

    def __init__(self, skills_dir: Path | None = None):
        self.skills_dir = skills_dir or Path.home() / ".nanobot" / "workspace" / "skills"

    def extract_workflow_from_chat(self, messages: list[dict]) -> dict:
        """Extract RPA tool calls from conversation messages."""
        steps = []
        for msg in messages:
            if msg.get("role") == "assistant" and msg.get("type") == "progress":
                content = msg.get("content", "")
                if content.startswith("🔧"):
                    steps.append({"type": "tool_hint", "content": content})
            elif msg.get("role") == "assistant":
                content = msg.get("content", "")
                # Look for RPA tool call patterns
                if any(kw in content for kw in ["rpa_browser", "rpa_desktop", "rpa_pdf", "rpa_excel", "rpa_email"]):
                    steps.append({"type": "rpa_action", "content": content})
            elif msg.get("role") == "user":
                steps.append({"type": "user_instruction", "content": msg.get("content", "")})

        return {
            "steps": steps,
            "extracted_at": datetime.now().isoformat(),
            "total_messages": len(messages),
            "rpa_steps": len([s for s in steps if s["type"] == "rpa_action"]),
        }

    def generate_skill_md(self, workflow: dict, name: str, description: str = "") -> str:
        """Generate SKILL.md content from extracted workflow."""
        desc = description or f"RPA workflow: {name}"
        steps_md = []

        for i, step in enumerate(workflow.get("steps", []), 1):
            if step["type"] == "user_instruction":
                steps_md.append(f"### Step {i}: User Request\n{step['content']}\n")
            elif step["type"] == "rpa_action":
                steps_md.append(f"### Step {i}: RPA Action\n```\n{step['content'][:500]}\n```\n")
            elif step["type"] == "tool_hint":
                steps_md.append(f"### Step {i}: Tool Operation\n{step['content']}\n")

        steps_text = "\n".join(steps_md)

        return f"""---
name: rpa-{self._slug(name)}
description: "{desc}"
---

# {name}

> Auto-generated from RPA workflow on {workflow.get('extracted_at', 'unknown')}

## Overview

{desc}

## Execution Steps

{steps_text}

## Notes

- This workflow was verified during creation
- If elements have changed on target pages, use `rpa_browser(action="analyze")` to re-inspect
- Always verify results with `rpa_browser(action="screenshot")` after critical steps
"""

    def save_skill(self, name: str, content: str) -> Path:
        """Save skill to the skills directory."""
        slug = self._slug(name)
        skill_dir = self.skills_dir / f"rpa-{slug}"
        skill_dir.mkdir(parents=True, exist_ok=True)

        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(content, encoding="utf-8")

        return skill_path

    def create_skill_from_chat(self, name: str, messages: list[dict], description: str = "") -> Path:
        """Full pipeline: extract → generate → save."""
        workflow = self.extract_workflow_from_chat(messages)
        content = self.generate_skill_md(workflow, name, description)
        return self.save_skill(name, content)

    @staticmethod
    def _slug(name: str) -> str:
        """Convert name to slug."""
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
