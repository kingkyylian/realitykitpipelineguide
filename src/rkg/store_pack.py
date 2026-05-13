from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from rkg.archetypes import describe_archetype
from rkg.qa_plan import qa_steps_for
from rkg.quality import quality_contract_from_spec

StorePack = dict[str, str]


def build_store_pack(spec: Mapping[str, Any]) -> StorePack:
    game = spec["game"]
    display_name = str(game["display_name"])
    archetype = describe_archetype(str(game["archetype"]))
    return {
        "Docs/store/metadata.md": metadata(display_name, spec),
        "Docs/store/review-notes.md": review_notes(display_name, spec),
        "Docs/store/privacy.md": privacy_notes(display_name),
        "Docs/store/screenshots.md": screenshots_checklist(spec, archetype),
        "Docs/store/screenshot-qa.md": screenshot_qa_runbook(spec, archetype),
        "Docs/store/monetization.md": monetization_notes(spec),
    }


def metadata(display_name: str, spec: Mapping[str, Any]) -> str:
    game = spec["game"]
    loop = spec["loop"]
    quality = _quality_metadata(spec)
    return f"""# Store Metadata Draft

App Name: {display_name}
Subtitle: Fast {game["archetype"].replace("_", " ")} sessions
Monetization: {game["monetization"]}

## Description Draft

{display_name} is a short-session arcade game where players {loop["player_action"]}. Sessions last {game["session_seconds"]} seconds and focus on clean input, readable play, and repeatable score improvement.

{quality}

## Screenshot Checklist

See `Docs/store/screenshots.md`.
"""


def review_notes(display_name: str, spec: Mapping[str, Any]) -> str:
    game = spec["game"]
    return f"""# App Review Notes

{display_name} is a standalone RealityKit game.

- Login required: no
- Backend required: no
- Session length: {game["session_seconds"]} seconds
- Core input: {game["input"]}
- Monetization: {game["monetization"]}

All screenshots and metadata should describe actual gameplay before submission.
"""


def privacy_notes(display_name: str) -> str:
    return f"""# Privacy Notes

{display_name} scaffold default:

- No account system.
- No analytics SDK.
- No advertising SDK.
- No network requirement.
- No personal data collection.

Update this file before submission if monetization, analytics, ads, Game Center, or backend services are added.
"""


def screenshots_checklist(spec: Mapping[str, Any], archetype: Mapping[str, Any]) -> str:
    roles = _required_visible_roles(spec, archetype)
    rows = [
        "| State | Purpose | Generated proof cue | Required asset roles | Evidence path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for state in spec["release"]["screenshots"]:
        proof = _screenshot_proof(str(state), archetype)
        rows.append(f"| {state} | {_screenshot_purpose(str(state))} | {proof} | {roles} | Docs/screenshots/{state}.jpg |")
    return "# Screenshot Checklist\n\n" + "\n".join(rows) + "\n"


def screenshot_qa_runbook(spec: Mapping[str, Any], archetype: Mapping[str, Any]) -> str:
    rows = [
        "| Order | State | Drive the game to this state | Expected evidence | Capture path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for step in qa_steps_for(spec, archetype):
        rows.append(
            f"| {step['order']} | {step['state']} | {step['drive']} | {step['expected_evidence']} | "
            f"{step['capture_path']} |"
        )
    return (
        "# Screenshot QA Runbook\n\n"
        "Run `rkg verify-game` before capture. Drive the generated game through these rows in order, "
        "resetting between rows when the previous state ends the session. "
        "Run `rkg verify-screenshots .` after capture.\n\n"
        + _quality_runbook_line(spec)
        + "\n\n"
        + "\n".join(rows)
        + "\n"
    )


def monetization_notes(spec: Mapping[str, Any]) -> str:
    monetization = spec["game"]["monetization"]
    return f"""# Monetization Notes

Model: {monetization}

- No external unlocks.
- No surprise subscriptions.
- No paid content should be advertised before it exists in the generated game.
- Update this file before TestFlight if ads, IAP, paid download, or Game Center rewards are added.
"""


def _required_visible_roles(spec: Mapping[str, Any], archetype: Mapping[str, Any]) -> str:
    roles = []
    for asset in spec["assets"].values():
        if isinstance(asset, Mapping):
            role = asset.get("role")
            if isinstance(role, str) and role not in roles:
                roles.append(role)
    if not roles:
        roles = list(archetype["required_asset_roles"])
    return ", ".join(roles)


def _screenshot_purpose(state: str) -> str:
    labels = {
        "gameplay_start": "Show the starting playable state.",
        "mid_session": "Show actual core gameplay, not title art.",
        "results": "Show score/result state after a real session.",
        "near_miss": "Show readable danger or avoidance moment.",
        "aiming": "Show input preparation.",
        "mid_flight": "Show physics/action in progress.",
        "landing": "Show scoring contact or landing result.",
        "first_piece": "Show first puzzle action.",
        "mid_stack": "Show puzzle progression.",
        "collapse_or_clear": "Show fail or clear feedback.",
        "wave_start": "Show wave setup.",
        "mid_wave": "Show active wave pressure.",
        "low_health": "Show failure tension.",
    }
    return labels.get(state, "Show an actual generated gameplay state.")


def _screenshot_proof(state: str, archetype: Mapping[str, Any]) -> str:
    proof_map = archetype.get("screenshot_proofs", {})
    if isinstance(proof_map, Mapping):
        proof = proof_map.get(state)
        if isinstance(proof, str):
            return proof
    return "Capture after driving the generated game into this release state."


def _quality_metadata(spec: Mapping[str, Any]) -> str:
    quality = quality_contract_from_spec(spec)
    if not quality:
        return "## Quality Contract\n\nNo explicit quality contract declared."

    feel = quality.get("feel", {})
    feedback = quality.get("feedback", {})
    style = quality.get("style", {})
    lines = ["## Quality Contract"]
    if isinstance(feel, Mapping):
        movement = feel.get("movement")
        input_response = feel.get("input_response")
        difficulty_curve = feel.get("difficulty_curve")
        if movement:
            lines.append(f"- Movement feel: {movement}")
        if input_response:
            lines.append(f"- Input response: {input_response}")
        if difficulty_curve:
            lines.append(f"- Difficulty curve: {difficulty_curve}")
    if isinstance(style, Mapping):
        mood = style.get("mood")
        palette = style.get("palette")
        shape_language = style.get("shape_language")
        if mood:
            lines.append(f"- Mood: {mood}")
        if palette:
            lines.append(f"- Palette: {palette}")
        if shape_language:
            lines.append(f"- Shape language: {shape_language}")
    if isinstance(feedback, Mapping):
        for key in ("score", "hit", "fail"):
            values = feedback.get(key)
            if isinstance(values, list) and values:
                lines.append(f"- {key.capitalize()} feedback: {', '.join(str(value) for value in values)}")
    return "\n".join(lines)


def _quality_runbook_line(spec: Mapping[str, Any]) -> str:
    quality = quality_contract_from_spec(spec)
    feel = quality.get("feel", {})
    style = quality.get("style", {})
    if not isinstance(feel, Mapping) or not isinstance(style, Mapping):
        return "Quality contract: not declared."
    movement = feel.get("movement", "unspecified")
    input_response = feel.get("input_response", "unspecified")
    palette = style.get("palette", "unspecified")
    return f"Quality contract: {movement} movement, {input_response} input, {palette} palette."
