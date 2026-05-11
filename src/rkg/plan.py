from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from rkg.archetypes import describe_archetype
from rkg.spec import assert_valid_game_spec

JsonDict = dict[str, Any]

GENERATED_SOURCE_MODULES = [
    "{swift_name}App.swift",
    "ContentView.swift",
    "GameState.swift",
    "SessionControl.swift",
    "FeedbackState.swift",
    "InputIntent.swift",
    "ScreenshotState.swift",
    "GameRules.swift",
    "GameSceneController.swift",
    "GameView.swift",
    "AssetLoader.swift",
    "FallbackFactory.swift",
    "ResultView.swift",
]
GENERATED_STORE_FILES = [
    "Docs/store/metadata.md",
    "Docs/store/review-notes.md",
    "Docs/store/privacy.md",
    "Docs/store/screenshots.md",
    "Docs/store/screenshot-qa.md",
    "Docs/store/monetization.md",
]


def build_game_plan(spec: Mapping[str, Any]) -> JsonDict:
    assert_valid_game_spec(spec)

    game = spec["game"]
    game_id = str(game["id"])
    swift_name = swift_name_for(game_id)
    archetype = describe_archetype(str(game["archetype"]))

    return {
        "game_id": game_id,
        "display_name": game["display_name"],
        "swift_name": swift_name,
        "archetype": archetype,
        "files": _planned_files(swift_name),
        "asset_roles": _asset_roles(spec),
        "runtime_entities": runtime_entities_for(spec),
        "screenshot_states": list(spec["release"]["screenshots"]),
        "screenshot_proofs": _screenshot_proofs(spec, archetype),
    }


def swift_name_for(game_id: str) -> str:
    return "".join(part.capitalize() for part in game_id.split("_"))


def _planned_files(swift_name: str) -> list[str]:
    files = [
        "GameSpec.json",
        "rkp.json",
        "Tools/asset_manifest.json",
        "project.yml",
        "Docs/WORKLOG.md",
        "Docs/ai-handoff.md",
    ]
    files.extend(f"Sources/{swift_name}/{module.format(swift_name=swift_name)}" for module in GENERATED_SOURCE_MODULES)
    files.extend(GENERATED_STORE_FILES)
    return files


def _asset_roles(spec: Mapping[str, Any]) -> dict[str, str]:
    roles: dict[str, str] = {}
    for asset_id, asset in spec["assets"].items():
        role = asset.get("role") or asset.get("type")
        roles[str(asset_id)] = str(role)
    return roles


def _screenshot_proofs(spec: Mapping[str, Any], archetype: Mapping[str, Any]) -> dict[str, str]:
    proof_map = archetype.get("screenshot_proofs", {})
    if not isinstance(proof_map, Mapping):
        return {}
    proofs: dict[str, str] = {}
    for state in spec["release"]["screenshots"]:
        proof = proof_map.get(state)
        if isinstance(proof, str):
            proofs[str(state)] = proof
    return proofs


def runtime_entities_for(spec: Mapping[str, Any]) -> list[JsonDict]:
    entities = []
    for index, (asset_id, asset) in enumerate(spec["assets"].items()):
        if not isinstance(asset, Mapping):
            continue
        role = _asset_role(asset)
        entities.append(
            {
                "asset_id": str(asset_id),
                "role": role,
                "variable": swift_identifier_for(str(asset_id)),
                "position": _entity_position_for(role, index),
            }
        )
    return entities


def swift_identifier_for(asset_id: str) -> str:
    parts = [part for part in asset_id.split("_") if part]
    if not parts:
        return "entity"
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def _asset_role(asset: Mapping[str, Any]) -> str:
    return str(asset.get("role") or asset.get("type") or "prop")


def _entity_position_for(role: str, index: int) -> str:
    if role in {"arena", "environment"}:
        return "[0, -0.45, 0]"
    if role == "player":
        return "[0, 0, -0.85]"
    if role == "opponent":
        return "[0.35, 0, -0.85]"
    if role in {"target", "obstacle", "hazard"}:
        x = -0.45 + (index % 3) * 0.45
        z = -1.25 - (index // 3) * 0.25
        return _vector_literal(x, 0, z)
    if role == "pickup":
        return "[0.45, 0.12, -1.0]"
    if role == "projectile":
        return "[0, 0.2, -0.65]"
    if role == "hit_vfx":
        return "[0.03, 0.18, -0.86]"
    if role in {"guard_cue", "telegraph"}:
        return "[-0.35, 0.24, -0.85]"
    return _vector_literal(-0.3 + (index % 3) * 0.3, 0, -1.0)


def _vector_literal(x: float, y: float, z: float) -> str:
    return f"[{x:.2f}, {y:.2f}, {z:.2f}]"
