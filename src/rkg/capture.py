from __future__ import annotations

import json
import math
import shutil
import subprocess
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from rkg.qa_plan import build_qa_plan
from rkg.spec import load_game_spec
from rkp.runtime import package_env

JsonDict = dict[str, Any]
CommandRunner = Callable[[list[str], Path], int]
AppContainerResolver = Callable[[str, str, Path], Path]


def build_capture_plan(project: Path, *, device: str) -> JsonDict:
    project = project.resolve()
    spec = load_game_spec(project / "GameSpec.json")
    qa = build_qa_plan(spec)
    game_id = str(spec["game"]["id"])
    display_name = str(spec["game"]["display_name"])
    archetype = str(spec["game"]["archetype"])
    swift_name = _swift_name(game_id)
    bundle_id = "com.kyylian." + "".join(ch for ch in game_id.lower() if ch.isalnum())
    app_path = project / "Build" / "DerivedData" / "Build" / "Products" / "Debug-iphonesimulator" / f"{swift_name}.app"
    steps = []
    for step in qa["steps"]:
        state = str(step["state"])
        capture_path = project / str(step["capture_path"])
        sidecar_path = project / str(step["sidecar_path"])
        scene_snapshot_path = project / str(step["scene_snapshot_path"])
        steps.append(
            {
                "order": step["order"],
                "state": state,
                "screenshot_state_case": step["screenshot_state_case"],
                "visible_roles": step["visible_roles"],
                "drive": step["drive"],
                "expected_evidence": step["expected_evidence"],
                "automation": step["automation"],
                "launch": [
                    "xcrun",
                    "simctl",
                    "launch",
                    "--terminate-running-process",
                    device,
                    bundle_id,
                    "--rkg-screenshot-state",
                    state,
                ],
                "screenshot": str(capture_path),
                "sidecar": str(sidecar_path),
                "scene_snapshot": str(scene_snapshot_path),
                "runtime_scene_snapshot": f"Documents/rkg-scene-snapshot-{state}.json",
            }
        )
    return {
        "project": str(project),
        "device": device,
        "game_id": game_id,
        "display_name": display_name,
        "archetype": archetype,
        "generate": ["xcodegen", "generate"] if (project / "project.yml").exists() else [],
        "bundle_id": bundle_id,
        "build": [
            "xcodebuild",
            "-quiet",
            "-project",
            f"{swift_name}.xcodeproj",
            "-scheme",
            swift_name,
            "-destination",
            "generic/platform=iOS Simulator",
            "-derivedDataPath",
            "Build/DerivedData",
            "build",
        ],
        "install": ["xcrun", "simctl", "install", device, str(app_path)],
        "steps": steps,
    }


def _swift_name(game_id: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in game_id.split("_") if part)


def execute_capture_plan(
    plan: Mapping[str, Any],
    *,
    runner: CommandRunner | None = None,
    app_container_resolver: AppContainerResolver | None = None,
    sleep_seconds: float = 2.0,
) -> JsonDict:
    project = Path(str(plan["project"]))
    run = runner or _run_command
    completed = []

    for command in [list(plan.get("generate", [])), list(plan["build"]), list(plan["install"])]:
        if not command:
            continue
        exit_code = run(command, project)
        completed.append({"command": command, "exit_code": exit_code})
        if exit_code != 0:
            return {"ok": False, "completed": completed}

    for step in plan["steps"]:
        launch = list(step["launch"])
        exit_code = run(launch, project)
        completed.append({"command": launch, "exit_code": exit_code})
        if exit_code != 0:
            return {"ok": False, "completed": completed}
        time.sleep(sleep_seconds)

        screenshot = ["xcrun", "simctl", "io", str(plan["device"]), "screenshot", str(step["screenshot"])]
        exit_code = run(screenshot, project)
        completed.append({"command": screenshot, "exit_code": exit_code})
        if exit_code != 0:
            return {"ok": False, "completed": completed}

        try:
            _copy_runtime_scene_snapshot(plan, step, project, app_container_resolver)
        except OSError as exc:
            command = ["copy-scene-snapshot", str(step.get("scene_snapshot", ""))]
            completed.append({"command": command, "exit_code": 1, "error": str(exc)})
            return {"ok": False, "completed": completed}

        try:
            _write_capture_sidecar(plan, step, project)
        except OSError as exc:
            command = ["write-sidecar", str(step.get("sidecar", ""))]
            completed.append({"command": command, "exit_code": 1, "error": str(exc)})
            return {"ok": False, "completed": completed}
    return {"ok": True, "completed": completed}


def _write_capture_sidecar(plan: Mapping[str, Any], step: Mapping[str, Any], project: Path) -> None:
    sidecar_value = step.get("sidecar")
    if not isinstance(sidecar_value, str) or not sidecar_value:
        return
    sidecar = Path(sidecar_value)
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "game_id": str(plan.get("game_id", "")),
        "display_name": str(plan.get("display_name", "")),
        "archetype": str(plan.get("archetype", "")),
        "state": str(step.get("state", "")),
        "screenshot_state_case": str(step.get("screenshot_state_case", "")),
        "visible_roles": [str(role) for role in step.get("visible_roles", [])],
        "drive": str(step.get("drive", "")),
        "expected_evidence": str(step.get("expected_evidence", "")),
        "automation": str(step.get("automation", "")),
        "screenshot": _project_relative_path(project, Path(str(step.get("screenshot", "")))),
    }
    scene_snapshot_value = step.get("scene_snapshot")
    if isinstance(scene_snapshot_value, str) and scene_snapshot_value:
        payload["scene_snapshot"] = _project_relative_path(project, Path(scene_snapshot_value))
        role_pixel_evidence = _role_pixel_evidence_from_scene_snapshot(
            Path(scene_snapshot_value),
            [str(role) for role in step.get("visible_roles", [])],
        )
        if role_pixel_evidence:
            payload["role_pixel_evidence"] = role_pixel_evidence
    sidecar.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _role_pixel_evidence_from_scene_snapshot(scene_snapshot: Path, visible_roles: list[str]) -> JsonDict:
    if not scene_snapshot.is_file():
        return {}
    try:
        payload = json.loads(scene_snapshot.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    roles = payload.get("roles")
    if not isinstance(roles, list):
        return {}
    expected_roles = {role for role in visible_roles if role}
    evidence: JsonDict = {}
    evidence_sizes: dict[str, float] = {}
    for role_record in roles:
        if not isinstance(role_record, Mapping):
            continue
        role = role_record.get("role")
        if not isinstance(role, str) or role not in expected_roles:
            continue
        if role_record.get("is_enabled") is not True:
            continue
        region = _role_pixel_region_for_scene_record(role_record)
        if region is None:
            continue
        size = float(region["width"]) * float(region["height"])
        if role in evidence and size <= evidence_sizes[role]:
            continue
        evidence_sizes[role] = size
        evidence[role] = {
            "asset_id": str(role_record.get("asset_id", "")),
            "entity_name": str(role_record.get("entity_name", "")),
            "region": region,
            "source": "runtime_scene_snapshot",
        }
    return evidence


def _role_pixel_region_for_scene_record(role_record: Mapping[str, Any]) -> JsonDict | None:
    role = role_record.get("role")
    if role == "arena":
        return {"x": 0.05, "y": 0.3, "width": 0.9, "height": 0.48}

    visual_bounds = role_record.get("visual_bounds")
    if not isinstance(visual_bounds, Mapping):
        return None
    center = visual_bounds.get("center")
    extents = visual_bounds.get("extents")
    if not isinstance(center, Mapping) or not isinstance(extents, Mapping):
        return None
    if not all(_is_finite_number(center.get(axis)) for axis in ("x", "y", "z")):
        return None
    if not all(_is_non_negative_finite_number(extents.get(axis)) for axis in ("x", "y", "z")):
        return None

    max_extent = max(float(extents[axis]) for axis in ("x", "y", "z"))
    if max_extent <= 0:
        return None

    width = _clamp(0.18 + min(max_extent, 0.8) * 0.18, 0.16, 0.32)
    height = _clamp(0.18 + min(max_extent, 0.8) * 0.16, 0.16, 0.32)
    screen_x = _clamp(0.5 + float(center["x"]) * 0.30, 0.12, 0.88)
    screen_y = _clamp(0.47 - float(center["y"]) * 0.20 + (float(center["z"]) + 0.8) * 0.035, 0.24, 0.72)
    return {
        "x": _rounded_fraction(_clamp(screen_x - width / 2.0, 0.02, 0.98 - width)),
        "y": _rounded_fraction(_clamp(screen_y - height / 2.0, 0.02, 0.98 - height)),
        "width": _rounded_fraction(width),
        "height": _rounded_fraction(height),
    }


def _is_finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _is_non_negative_finite_number(value: object) -> bool:
    return _is_finite_number(value) and float(value) >= 0.0


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return min(maximum, max(minimum, value))


def _rounded_fraction(value: float) -> float:
    return round(value, 4)


def _copy_runtime_scene_snapshot(
    plan: Mapping[str, Any],
    step: Mapping[str, Any],
    project: Path,
    resolver: AppContainerResolver | None,
) -> None:
    scene_snapshot_value = step.get("scene_snapshot")
    runtime_snapshot_value = step.get("runtime_scene_snapshot")
    if not isinstance(scene_snapshot_value, str) or not scene_snapshot_value:
        return
    if not isinstance(runtime_snapshot_value, str) or not runtime_snapshot_value:
        return

    device = str(plan.get("device", ""))
    bundle_id = str(plan.get("bundle_id", ""))
    if not device or not bundle_id:
        raise OSError("capture plan is missing device or bundle id for runtime scene snapshot")

    app_container = (resolver or _resolve_app_data_container)(device, bundle_id, project)
    source = app_container / runtime_snapshot_value
    if not source.is_file():
        raise OSError(f"runtime scene snapshot not found: {source}")

    destination = Path(scene_snapshot_value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def _resolve_app_data_container(device: str, bundle_id: str, project: Path) -> Path:
    command = ["xcrun", "simctl", "get_app_container", device, bundle_id, "data"]
    if shutil.which("rtk") is not None:
        command = ["rtk", *command]
    result = subprocess.run(command, cwd=project, text=True, capture_output=True)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise OSError(stderr or "failed to resolve app data container")
    path = result.stdout.strip()
    if not path:
        raise OSError("empty app data container path")
    return Path(path)


def _project_relative_path(project: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project.resolve()))
    except ValueError:
        return str(path)


def _run_command(command: list[str], cwd: Path) -> int:
    if command[:2] == ["xcrun", "simctl"] and shutil.which("rtk") is not None:
        command = ["rtk", *command]
    return subprocess.run(command, cwd=cwd, env=package_env()).returncode
