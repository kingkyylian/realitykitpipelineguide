from __future__ import annotations

from typing import Any, Mapping

from rkg.archetypes import describe_archetype
from rkg.spec import assert_valid_game_spec


JsonDict = dict[str, Any]

GENERATED_SOURCE_MODULES = [
    "{swift_name}App.swift",
    "ContentView.swift",
    "GameState.swift",
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
        "screenshot_states": list(spec["release"]["screenshots"]),
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
