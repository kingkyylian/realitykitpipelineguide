from __future__ import annotations

import json
import shutil
import subprocess
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from rkg.qa_plan import build_qa_plan
from rkg.spec import load_game_spec

JsonDict = dict[str, Any]
CommandRunner = Callable[[list[str], Path], int]


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
            }
        )
    return {
        "project": str(project),
        "device": device,
        "game_id": game_id,
        "display_name": display_name,
        "archetype": archetype,
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
    sleep_seconds: float = 2.0,
) -> JsonDict:
    project = Path(str(plan["project"]))
    run = runner or _run_command
    completed = []

    for command in [list(plan["build"]), list(plan["install"])]:
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
    sidecar.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _project_relative_path(project: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project.resolve()))
    except ValueError:
        return str(path)


def _run_command(command: list[str], cwd: Path) -> int:
    if command[:2] == ["xcrun", "simctl"] and shutil.which("rtk") is not None:
        command = ["rtk", *command]
    return subprocess.run(command, cwd=cwd).returncode
