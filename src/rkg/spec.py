from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from rkg.archetypes import describe_archetype


JsonDict = dict[str, Any]

SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")
REQUIRED_GAME_FIELDS = [
    "id",
    "display_name",
    "archetype",
    "session_seconds",
    "camera",
    "input",
    "monetization",
]
REQUIRED_LOOP_FIELDS = ["player_action", "fail_condition", "scoring"]
REQUIRED_ASSET_FIELDS = ["type", "budget", "fallback"]
REQUIRED_RELEASE_FIELDS = ["devices", "screenshots"]


class GameSpecError(ValueError):
    def __init__(self, issues: list[str]) -> None:
        self.issues = issues
        super().__init__("invalid GameSpec:\n" + "\n".join(f"- {issue}" for issue in issues))


def load_game_spec(path: Path) -> JsonDict:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        value = json.loads(text)
    else:
        value = _load_yaml_if_available(text)
    if not isinstance(value, dict):
        raise GameSpecError(["GameSpec root must be an object"])
    return value


def _load_yaml_if_available(text: str) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise GameSpecError(["YAML GameSpec files require PyYAML; use JSON or install PyYAML"]) from exc
    return yaml.safe_load(text)


def assert_valid_game_spec(spec: Mapping[str, Any], *, app_store: bool = True) -> None:
    issues = validate_game_spec(spec, app_store=app_store)
    if issues:
        raise GameSpecError(issues)


def validate_game_spec(spec: Mapping[str, Any], *, app_store: bool = True) -> list[str]:
    issues: list[str] = []

    game = _section(spec, "game", issues)
    loop = _section(spec, "loop", issues)
    assets = _section(spec, "assets", issues)
    release = _section(spec, "release", issues)
    archetype: Mapping[str, Any] | None = None

    if game:
        _require_fields(game, "game", REQUIRED_GAME_FIELDS, issues)
        _validate_game(game, app_store, issues)
        archetype = _validate_archetype(game, issues)
        _validate_archetype_runtime_contract(game, archetype, issues)
    if loop:
        _require_fields(loop, "loop", REQUIRED_LOOP_FIELDS, issues)
        if "scoring" in loop and not isinstance(loop["scoring"], Mapping):
            issues.append("loop.scoring must be an object")
    if assets:
        _validate_assets(assets, issues, archetype)
    if release:
        _require_fields(release, "release", REQUIRED_RELEASE_FIELDS, issues)
        _validate_release(release, issues, archetype)

    return issues


def _section(spec: Mapping[str, Any], key: str, issues: list[str]) -> Mapping[str, Any] | None:
    value = spec.get(key)
    if value is None:
        issues.append(f"{key} is required")
        return None
    if not isinstance(value, Mapping):
        issues.append(f"{key} must be an object")
        return None
    return value


def _require_fields(section: Mapping[str, Any], prefix: str, fields: list[str], issues: list[str]) -> None:
    for field in fields:
        value = section.get(field)
        if value is None or value == "":
            issues.append(f"{prefix}.{field} is required")


def _validate_game(game: Mapping[str, Any], app_store: bool, issues: list[str]) -> None:
    game_id = game.get("id")
    if isinstance(game_id, str):
        if not SNAKE_CASE.match(game_id):
            issues.append("game.id must be snake_case")
    elif game_id is not None:
        issues.append("game.id must be a string")

    session_seconds = game.get("session_seconds")
    if isinstance(session_seconds, bool) or not isinstance(session_seconds, int):
        if session_seconds is not None:
            issues.append("game.session_seconds must be an integer")
    elif session_seconds <= 0:
        issues.append("game.session_seconds must be positive")
    elif session_seconds > 180:
        issues.append("game.session_seconds must be 180 or less for first-wave arcade games")

    monetization = game.get("monetization")
    if app_store and monetization == "external_unlock":
        issues.append("game.monetization external_unlock is not allowed for App Store builds")


def _validate_archetype(game: Mapping[str, Any], issues: list[str]) -> Mapping[str, Any] | None:
    archetype_id = game.get("archetype")
    if archetype_id is None or archetype_id == "":
        return None
    if not isinstance(archetype_id, str):
        issues.append("game.archetype must be a string")
        return None
    try:
        return describe_archetype(archetype_id)
    except ValueError:
        issues.append(f"game.archetype is not supported: {archetype_id}")
        return None


def _validate_archetype_runtime_contract(
    game: Mapping[str, Any],
    archetype: Mapping[str, Any] | None,
    issues: list[str],
) -> None:
    if archetype is None:
        return
    _validate_registry_value(game, "input", archetype, "input", issues)
    _validate_registry_value(game, "camera", archetype, "camera", issues)


def _validate_registry_value(
    game: Mapping[str, Any],
    game_key: str,
    archetype: Mapping[str, Any],
    registry_key: str,
    issues: list[str],
) -> None:
    value = game.get(game_key)
    if value is None or value == "":
        return
    if not isinstance(value, str):
        issues.append(f"game.{game_key} must be a string")
        return
    if value not in archetype[registry_key]:
        issues.append(f"game.{game_key} {value} is not supported by {archetype['id']}")


def _validate_assets(assets: Mapping[str, Any], issues: list[str], archetype: Mapping[str, Any] | None) -> None:
    if not assets:
        issues.append("assets must contain at least one asset")
        return

    declared_roles: set[str] = set()
    for asset_id, asset in assets.items():
        if not isinstance(asset_id, str) or not SNAKE_CASE.match(asset_id):
            issues.append(f"assets.{asset_id} id must be snake_case")
        if not isinstance(asset, Mapping):
            issues.append(f"assets.{asset_id} must be an object")
            continue
        role = asset.get("role")
        if isinstance(role, str) and role:
            declared_roles.add(role)
        _require_fields(asset, f"assets.{asset_id}", REQUIRED_ASSET_FIELDS, issues)
        _validate_asset_role(asset_id, asset, archetype, issues)
    _validate_required_asset_roles(declared_roles, archetype, issues)


def _validate_required_asset_roles(
    declared_roles: set[str],
    archetype: Mapping[str, Any] | None,
    issues: list[str],
) -> None:
    if archetype is None:
        return
    for role in archetype["required_asset_roles"]:
        if role not in declared_roles:
            issues.append(f"assets missing required role {role} for {archetype['id']}")


def _validate_asset_role(
    asset_id: object,
    asset: Mapping[str, Any],
    archetype: Mapping[str, Any] | None,
    issues: list[str],
) -> None:
    role = asset.get("role")
    if role is None or role == "":
        return
    if not isinstance(role, str):
        issues.append(f"assets.{asset_id} role must be a string")
        return
    if archetype is None:
        return
    allowed_roles = set(archetype["required_asset_roles"]) | set(archetype["optional_asset_roles"])
    if role not in allowed_roles:
        issues.append(f"assets.{asset_id} role {role} is not used by {archetype['id']}")


def _validate_release(
    release: Mapping[str, Any],
    issues: list[str],
    archetype: Mapping[str, Any] | None,
) -> None:
    devices = release.get("devices")
    if devices is not None and (not isinstance(devices, list) or not all(isinstance(device, str) for device in devices)):
        issues.append("release.devices must be a list of strings")
    elif devices == []:
        issues.append("release.devices must contain at least one device")

    screenshots = release.get("screenshots")
    if screenshots is not None and (
        not isinstance(screenshots, list) or not all(isinstance(screenshot, str) for screenshot in screenshots)
    ):
        issues.append("release.screenshots must be a list of strings")
    elif screenshots == []:
        issues.append("release.screenshots must contain at least one screenshot")
    elif archetype is not None and isinstance(screenshots, list):
        allowed_states = set(archetype["screenshot_states"])
        for screenshot in screenshots:
            if screenshot not in allowed_states:
                issues.append(f"release.screenshots state {screenshot} is not used by {archetype['id']}")
