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
        "screenshot_proofs": {
            "gameplay_start": "Tap Start; state.phase == .playing; target and arena are visible.",
            "mid_session": "Tap Start, then score at least one hit; state.score > 0.",
            "results": "End the session or reset after play; state.phase == .result or result UI is visible.",
        },
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
        "screenshot_proofs": {
            "gameplay_start": "Tap Start; state.phase == .playing; runner, obstacle, and arena are visible.",
            "mid_session": "Tap Start, swipe lanes, then tap Dodge; state.distance > 0.",
            "near_miss": "Swipe next to the obstacle, then tap Dodge; state.nearMisses > 0.",
            "results": "Collide with an obstacle or finish test run; state.phase == .result.",
        },
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
        "screenshot_proofs": {
            "aiming": "Tap Start; state.phase == .playing; throwPower slider is visible.",
            "mid_flight": "Set throwPower outside landing window, then tap Throw; state.lastThrowPower > 0.",
            "landing": "Set throwPower between 45% and 75%, then tap Throw; state.landedInZone == true.",
            "results": "Land in the scoring zone or spend attempts; state.phase == .result.",
        },
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
        "screenshot_proofs": {
            "first_piece": "Tap Start, then Place with Stable on; state.piecesPlaced == 1.",
            "mid_stack": "Place multiple stable pieces; state.stablePieces >= 2.",
            "collapse_or_clear": "Turn Stable off then tap Place, or tap Collapse; state.collapsed == true.",
            "results": "Collapse or complete max pieces; state.phase == .result.",
        },
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
        "screenshot_proofs": {
            "wave_start": "Tap Start; state.phase == .playing; state.threatsRemaining > 0.",
            "mid_wave": "Tap Fire at least once; state.clearedThreats > 0.",
            "low_health": "Tap Damage until health is 1; state.health == 1.",
            "results": "Tap Damage until defeated; state.phase == .result and state.isDefeated == true.",
        },
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
