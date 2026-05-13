from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from rkg.archetypes import describe_archetype
from rkg.custom_realitykit_runtime import custom_realitykit_adapter_for_systems
from rkg.plan import swift_identifier_for
from rkg.spec import assert_valid_game_spec

JsonDict = dict[str, Any]


def build_qa_plan(spec: Mapping[str, Any]) -> JsonDict:
    assert_valid_game_spec(spec)

    game = spec["game"]
    archetype = describe_archetype(str(game["archetype"]))
    return {
        "game_id": str(game["id"]),
        "display_name": str(game["display_name"]),
        "archetype": str(game["archetype"]),
        "preflight": ["rkg verify-game <generated-project>"],
        "capture_root": "Docs/screenshots",
        "steps": qa_steps_for(spec, archetype),
    }


def qa_steps_for(spec: Mapping[str, Any], archetype: Mapping[str, Any]) -> list[JsonDict]:
    roles = _visible_roles(spec, archetype)
    proof_map = _screenshot_proofs_for(spec, archetype)
    steps: list[JsonDict] = []
    for index, state in enumerate(spec["release"]["screenshots"], start=1):
        state_name = str(state)
        steps.append(
            {
                "order": index,
                "state": state_name,
                "screenshot_state_case": swift_identifier_for(state_name),
                "drive": _screenshot_proof(state_name, proof_map),
                "visible_roles": roles,
                "expected_evidence": "Declared roles available: " + ", ".join(roles),
                "capture_path": f"Docs/screenshots/{state_name}.jpg",
                "sidecar_path": f"Docs/screenshots/{state_name}.json",
                "scene_snapshot_path": f"Docs/screenshots/{state_name}.scene.json",
                "automation": _capture_automation(str(spec["game"]["archetype"]), state_name),
                "semantic_visual_contract": _semantic_visual_contract(str(spec["game"]["archetype"]), state_name),
            }
        )
    return steps


def _visible_roles(spec: Mapping[str, Any], archetype: Mapping[str, Any]) -> list[str]:
    roles: list[str] = []
    for asset in spec["assets"].values():
        if isinstance(asset, Mapping):
            role = asset.get("role")
            if isinstance(role, str) and role not in roles:
                roles.append(role)
    if not roles:
        roles = [str(role) for role in archetype["required_asset_roles"]]
    return roles


def _screenshot_proofs_for(spec: Mapping[str, Any], archetype: Mapping[str, Any]) -> Mapping[str, str]:
    game = spec["game"]
    if str(game["archetype"]) == "custom_realitykit":
        systems = game.get("systems", [])
        if isinstance(systems, list):
            adapter = custom_realitykit_adapter_for_systems(str(system) for system in systems)
            if adapter is not None and adapter.screenshot_proofs:
                return adapter.screenshot_proofs

    proof_map = archetype.get("screenshot_proofs", {})
    if isinstance(proof_map, Mapping):
        return {str(key): str(value) for key, value in proof_map.items() if isinstance(value, str)}
    return {}


def _screenshot_proof(state: str, proof_map: Mapping[str, str]) -> str:
    proof = proof_map.get(state)
    if isinstance(proof, str):
        return proof
    return "Capture after driving the generated game into this release state."


def _capture_automation(archetype_id: str, state: str) -> str:
    if archetype_id in {"fighter_2_5d", "custom_realitykit"}:
        return f"launch_arg --rkg-screenshot-state {state}"
    return "manual_capture"


def _semantic_visual_contract(archetype_id: str, state: str) -> JsonDict:
    contract: JsonDict = {
        "top_band_fraction": 0.24,
        "max_top_light_coverage": 0.34,
        "light_luma_threshold": 160,
        "bottom_band_fraction": 0.2,
        "max_bottom_light_coverage": 0.82,
        "bottom_light_luma_threshold": 170,
        "scene_band_top_fraction": 0.24,
        "scene_band_bottom_fraction": 0.78,
        "min_scene_luma_span": 18,
        "min_scene_bright_ratio": 0.015,
        "scene_bright_luma_threshold": 58,
    }
    if state == "results":
        contract["scene_band_bottom_fraction"] = 0.72
    if archetype_id == "custom_realitykit":
        contract["min_scene_luma_span"] = 16
    return contract
