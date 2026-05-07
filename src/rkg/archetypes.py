from __future__ import annotations

from copy import deepcopy
from typing import Any


JsonDict = dict[str, Any]

RUNTIME_MODULES = [
    "GameState",
    "GameRules",
    "GameSceneController",
    "AssetLoader",
    "FallbackFactory",
]

ARCHETYPES: list[JsonDict] = [
    {
        "id": "target_shooter",
        "display_name": "Target Shooter",
        "mechanic": "tap or aim at spawned targets before time expires",
        "input": ["tap"],
        "camera": ["fixed_non_ar"],
        "required_asset_roles": ["target", "arena"],
        "optional_asset_roles": ["projectile", "ui_prop", "environment"],
        "runtime_modules": RUNTIME_MODULES,
        "screenshot_states": ["gameplay_start", "mid_session", "results"],
        "scope_risk": "low",
    },
    {
        "id": "lane_dodger",
        "display_name": "Lane Dodger",
        "mechanic": "move between lanes to avoid hazards and collect pickups",
        "input": ["drag", "tap"],
        "camera": ["fixed_non_ar"],
        "required_asset_roles": ["player", "obstacle", "arena"],
        "optional_asset_roles": ["pickup", "ui_prop", "environment"],
        "runtime_modules": RUNTIME_MODULES,
        "screenshot_states": ["gameplay_start", "mid_session", "near_miss", "results"],
        "scope_risk": "low",
    },
    {
        "id": "toss_physics",
        "display_name": "Toss Physics",
        "mechanic": "drag and release a physics object toward a scoring zone",
        "input": ["drag"],
        "camera": ["fixed_non_ar"],
        "required_asset_roles": ["player", "projectile", "target", "arena"],
        "optional_asset_roles": ["obstacle", "ui_prop", "environment"],
        "runtime_modules": RUNTIME_MODULES,
        "screenshot_states": ["aiming", "mid_flight", "landing", "results"],
        "scope_risk": "medium",
    },
    {
        "id": "stack_puzzle",
        "display_name": "Stack Puzzle",
        "mechanic": "place pieces into a stable stack before the session ends",
        "input": ["tap", "drag"],
        "camera": ["fixed_non_ar"],
        "required_asset_roles": ["player", "obstacle", "arena"],
        "optional_asset_roles": ["pickup", "ui_prop", "environment"],
        "runtime_modules": RUNTIME_MODULES,
        "screenshot_states": ["first_piece", "mid_stack", "collapse_or_clear", "results"],
        "scope_risk": "medium",
    },
    {
        "id": "wave_defense_lite",
        "display_name": "Wave Defense Lite",
        "mechanic": "survive small waves by clearing threats before health runs out",
        "input": ["tap"],
        "camera": ["fixed_non_ar"],
        "required_asset_roles": ["player", "target", "arena"],
        "optional_asset_roles": ["projectile", "hazard", "ui_prop", "environment"],
        "runtime_modules": RUNTIME_MODULES,
        "screenshot_states": ["wave_start", "mid_wave", "low_health", "results"],
        "scope_risk": "medium",
    },
]


def list_archetypes() -> list[JsonDict]:
    return deepcopy(ARCHETYPES)


def describe_archetype(archetype_id: str) -> JsonDict:
    for record in ARCHETYPES:
        if record["id"] == archetype_id:
            return deepcopy(record)
    raise ValueError(f"unknown archetype: {archetype_id}")
