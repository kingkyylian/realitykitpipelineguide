from __future__ import annotations

import re
from typing import Any

from rkg.archetypes import describe_archetype

JsonDict = dict[str, Any]
ALLOWED_SYSTEMS = {
    "racing",
    "lap_timer",
    "collision",
    "vehicle",
    "weapon",
    "hitscan",
    "projectile",
    "shooting",
    "enemies",
    "enemy_ai",
    "health",
    "cover",
    "collect",
    "score",
    "timer",
    "physics",
}


def slug_id(title: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return value or "untitled_game"


def build_spec_template(archetype_id: str, title: str) -> JsonDict:
    archetype = describe_archetype(archetype_id)
    if archetype["id"] == "fighter_2_5d":
        return _fighter_spec(title)
    if archetype["id"] == "flappy_side_scroller":
        return _flappy_spec(title)
    raise ValueError(f"unknown archetype template: {archetype_id}")


def build_game_template(title: str, camera: str, input_model: str, systems: list[str]) -> JsonDict:
    normalized_systems = _normalized_systems(systems)
    unsupported = sorted(set(normalized_systems) - ALLOWED_SYSTEMS)
    if unsupported:
        raise ValueError("unsupported systems: " + ", ".join(unsupported))
    archetype = describe_archetype("custom_realitykit")
    if camera not in archetype["camera"]:
        raise ValueError(f"unsupported camera: {camera}")
    if input_model not in archetype["input"]:
        raise ValueError(f"unsupported input: {input_model}")
    return {
        "game": {
            "id": slug_id(title),
            "display_name": title,
            "archetype": "custom_realitykit",
            "session_seconds": 60,
            "camera": camera,
            "input": input_model,
            "monetization": "paid",
            "systems": normalized_systems,
        },
        "loop": _custom_loop(normalized_systems),
        "assets": _custom_assets(normalized_systems),
        "release": {
            "devices": ["iPhone 15", "iPad"],
            "screenshots": ["gameplay_start", "mid_action", "fail_or_hit", "results"],
        },
    }


def _fighter_spec(title: str) -> JsonDict:
    game_id = slug_id(title)
    return {
        "game": {
            "id": game_id,
            "display_name": title,
            "archetype": "fighter_2_5d",
            "session_seconds": 90,
            "camera": "fixed_non_ar",
            "input": "tap_swipe",
            "monetization": "paid",
        },
        "loop": {
            "player_action": "tap attack, swipe dodge, and time guard windows",
            "fail_condition": "fighter health reaches zero",
            "scoring": {"hit": 10, "perfect": 25, "knockout": 100},
        },
        "assets": {
            "fighter_player": {
                "type": "gameplay_actor",
                "role": "player",
                "budget": "1800 tris / 512 texture",
                "fallback": "procedural_capsule",
            },
            "fighter_opponent": {
                "type": "gameplay_actor",
                "role": "opponent",
                "budget": "1800 tris / 512 texture",
                "fallback": "procedural_capsule",
            },
            "duel_arena": {
                "type": "environment",
                "role": "arena",
                "budget": "900 tris / 512 texture",
                "fallback": "procedural_lane",
            },
            "hit_spark": {
                "type": "vfx",
                "role": "hit_vfx",
                "budget": "300 tris / procedural material",
                "fallback": "procedural_spark",
            },
            "guard_ring": {
                "type": "gameplay_cue",
                "role": "guard_cue",
                "budget": "400 tris / 512 texture",
                "fallback": "procedural_ring",
            },
        },
        "release": {
            "devices": ["iPhone 15", "iPad"],
            "screenshots": ["round_start", "mid_combo", "perfect_dodge", "knockout"],
        },
    }


def _flappy_spec(title: str) -> JsonDict:
    game_id = slug_id(title)
    return {
        "game": {
            "id": game_id,
            "display_name": title,
            "archetype": "flappy_side_scroller",
            "session_seconds": 60,
            "camera": "fixed_non_ar",
            "input": "tap",
            "monetization": "paid",
        },
        "loop": {
            "player_action": "tap to flap through scrolling pipe gaps",
            "fail_condition": "hit a pipe or leave the flight band",
            "scoring": {"hit": 10, "perfect": 25, "clear": 100},
        },
        "assets": {
            "bird_player": {
                "type": "gameplay_actor",
                "role": "player",
                "budget": "900 tris / 512 texture",
                "fallback": "procedural_capsule",
            },
            "pipe_gate": {
                "type": "prop",
                "role": "obstacle",
                "budget": "700 tris / 512 texture",
                "fallback": "procedural_gate",
            },
            "reef_lane": {
                "type": "environment",
                "role": "arena",
                "budget": "1200 tris / 512 texture",
                "fallback": "procedural_arena",
            },
        },
        "release": {
            "devices": ["iPhone 15", "iPad"],
            "screenshots": ["gameplay_start", "mid_flight", "near_gap", "collision", "results"],
        },
    }


def _normalized_systems(systems: list[str]) -> list[str]:
    values: list[str] = []
    for raw in systems:
        for part in raw.split(","):
            value = part.strip().lower()
            if value and value not in values:
                values.append(value)
    if not values:
        raise ValueError("at least one gameplay system is required")
    return values


def _custom_loop(systems: list[str]) -> JsonDict:
    system_set = set(systems)
    if "racing" in system_set:
        return {
            "player_action": "steer through the course, avoid obstacles, and complete laps",
            "fail_condition": "collision or timer pressure ends the run",
            "scoring": {"hit": 10, "perfect": 25, "lap": 100},
        }
    if system_set & {"projectile", "shooting"}:
        return {
            "player_action": "aim, charge, and launch projectiles at target lanes",
            "fail_condition": "shots expire before enough projectile hits land",
            "scoring": {"hit": 10, "perfect": 25, "clear": 100},
        }
    if system_set & {"weapon", "hitscan", "enemies"}:
        return {
            "player_action": "move, aim, and fire while managing health and cover",
            "fail_condition": "health reaches zero or enemies overrun the arena",
            "scoring": {"hit": 10, "perfect": 25, "clear": 100},
        }
    if system_set & {"collect", "score", "timer"}:
        return {
            "player_action": "collect pickups, build score streaks, and beat the timer",
            "fail_condition": "timer reaches zero before the pickup route is clear",
            "scoring": {"hit": 10, "perfect": 25, "clear": 100},
        }
    return {
        "player_action": "start the session and exercise the selected RealityKit systems",
        "fail_condition": "session timer or collision proxy ends the run",
        "scoring": {"hit": 10, "perfect": 25},
    }


def _custom_assets(systems: list[str]) -> JsonDict:
    system_set = set(systems)
    if "racing" in system_set:
        assets: JsonDict = {
            "player_vehicle": {
                "type": "vehicle_proxy",
                "role": "player",
                "budget": "1800 tris / 512 texture",
                "fallback": "procedural_vehicle",
            },
            "race_track": {
                "type": "environment",
                "role": "arena",
                "budget": "1200 tris / 512 texture",
                "fallback": "procedural_track",
            },
        }
        if "collision" in system_set:
            assets["track_obstacle"] = {
                "type": "hazard",
                "role": "obstacle",
                "budget": "700 tris / 512 texture",
                "fallback": "procedural_block",
            }
        if "lap_timer" in system_set:
            assets["checkpoint_gate"] = {
                "type": "ui_prop",
                "role": "ui_prop",
                "budget": "500 tris / 512 texture",
                "fallback": "procedural_gate",
            }
        return assets

    assets = {
        "player_proxy": {
            "type": "gameplay_actor",
            "role": "player",
            "budget": "1500 tris / 512 texture",
            "fallback": "procedural_capsule",
        },
        "arena_space": {
            "type": "environment",
            "role": "arena",
            "budget": "1200 tris / 512 texture",
            "fallback": "procedural_arena",
        },
    }
    if system_set & {"weapon", "hitscan", "projectile", "shooting"}:
        assets["weapon_proxy"] = {
            "type": "weapon_proxy",
            "role": "weapon",
            "budget": "700 tris / 512 texture",
            "fallback": "procedural_weapon",
        }
    if system_set & {"projectile", "shooting"}:
        assets["projectile_proxy"] = {
            "type": "projectile",
            "role": "projectile",
            "budget": "400 tris / 512 texture",
            "fallback": "procedural_sphere",
        }
        assets["target_proxy"] = {
            "type": "gameplay_target",
            "role": "target",
            "budget": "700 tris / 512 texture",
            "fallback": "procedural_rings",
        }
    if system_set & {"enemies", "enemy_ai"}:
        assets["enemy_proxy"] = {
            "type": "enemy_proxy",
            "role": "enemy",
            "budget": "1500 tris / 512 texture",
            "fallback": "procedural_enemy",
        }
    if system_set & {"health", "cover"}:
        assets["cover_block"] = {
            "type": "cover",
            "role": "cover",
            "budget": "800 tris / 512 texture",
            "fallback": "procedural_cover",
        }
    if "collect" in system_set:
        assets["pickup_proxy"] = {
            "type": "pickup",
            "role": "pickup",
            "budget": "400 tris / 512 texture",
            "fallback": "procedural_pickup",
        }
    if "timer" in system_set:
        assets["timer_gate"] = {
            "type": "ui_prop",
            "role": "ui_prop",
            "budget": "500 tris / 512 texture",
            "fallback": "procedural_gate",
        }
    return assets
