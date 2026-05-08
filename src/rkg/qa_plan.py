from __future__ import annotations

from typing import Any, Mapping

from rkg.archetypes import describe_archetype
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
    steps: list[JsonDict] = []
    for index, state in enumerate(spec["release"]["screenshots"], start=1):
        state_name = str(state)
        steps.append(
            {
                "order": index,
                "state": state_name,
                "screenshot_state_case": swift_identifier_for(state_name),
                "drive": _screenshot_proof(state_name, archetype),
                "visible_roles": roles,
                "expected_evidence": "Required roles visible: " + ", ".join(roles),
                "capture_path": f"Docs/screenshots/{state_name}.jpg",
                "automation": "manual_capture",
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


def _screenshot_proof(state: str, archetype: Mapping[str, Any]) -> str:
    proof_map = archetype.get("screenshot_proofs", {})
    if isinstance(proof_map, Mapping):
        proof = proof_map.get(state)
        if isinstance(proof, str):
            return proof
    return "Capture after driving the generated game into this release state."
