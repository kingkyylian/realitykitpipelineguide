from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rkg.spec import assert_valid_game_spec

JsonDict = dict[str, Any]


def build_asset_pipeline(spec: Mapping[str, Any], project: Path) -> JsonDict:
    assert_valid_game_spec(spec)
    return {
        "cwd": str(project.resolve()),
        "tasks": [_asset_task(str(asset_id), asset, spec) for asset_id, asset in spec["assets"].items()],
    }


def _asset_task(asset_id: str, asset: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    asset_type = str(asset.get("type") or "prop")
    role = str(asset.get("role") or asset_type)
    screenshot_path = f"Docs/screenshots/{asset_id}_imported.jpg"
    prompt = _asset_prompt(asset_id, role, asset_type, asset, spec)
    return {
        "asset_id": asset_id,
        "role": role,
        "type": asset_type,
        "brief_path": f"Docs/assets/{asset_id}.md",
        "runtime_file": f"Assets/Imported/{asset_id}.usdz",
        "screenshot_path": screenshot_path,
        "commands": [
            {
                "step": "make_asset",
                "command": ["rkp", "make-asset", asset_id, "--type", asset_type, "--prompt", prompt],
            },
            {"step": "build_asset", "command": ["rkp", "build-asset", asset_id]},
            {"step": "inspect_usdz", "command": ["rkp", "inspect-usdz", asset_id, "--json"]},
            {
                "step": "accept_asset",
                "command": ["rkp", "accept-asset", asset_id, "--screenshot", screenshot_path],
            },
        ],
    }


def _asset_prompt(asset_id: str, role: str, asset_type: str, asset: Mapping[str, Any], spec: Mapping[str, Any]) -> str:
    game = spec["game"]
    budget = str(asset.get("budget") or "1500 tris / 512 texture")
    fallback = str(asset.get("fallback") or "procedural_fallback")
    title = str(game["display_name"])
    return f"{asset_id} {role} role {asset_type} for {title}; budget {budget}; fallback {fallback}"
