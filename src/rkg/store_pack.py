from __future__ import annotations

from typing import Any, Mapping

from rkg.archetypes import describe_archetype


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
        "Docs/store/monetization.md": monetization_notes(spec),
    }


def metadata(display_name: str, spec: Mapping[str, Any]) -> str:
    game = spec["game"]
    loop = spec["loop"]
    return f"""# Store Metadata Draft

App Name: {display_name}
Subtitle: Fast {game["archetype"].replace("_", " ")} sessions
Monetization: {game["monetization"]}

## Description Draft

{display_name} is a short-session arcade game where players {loop["player_action"]}. Sessions last {game["session_seconds"]} seconds and focus on clean input, readable play, and repeatable score improvement.

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
        "| State | Purpose | Required asset roles | Evidence path |",
        "| --- | --- | --- | --- |",
    ]
    for state in spec["release"]["screenshots"]:
        rows.append(f"| {state} | {_screenshot_purpose(str(state))} | {roles} | Docs/screenshots/{state}.jpg |")
    return "# Screenshot Checklist\n\n" + "\n".join(rows) + "\n"


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
