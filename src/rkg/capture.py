from __future__ import annotations

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
    swift_name = _swift_name(game_id)
    bundle_id = "com.kyylian." + "".join(ch for ch in game_id.lower() if ch.isalnum())
    app_path = project / "Build" / "DerivedData" / "Build" / "Products" / "Debug-iphonesimulator" / f"{swift_name}.app"
    steps = []
    for step in qa["steps"]:
        state = str(step["state"])
        capture_path = project / str(step["capture_path"])
        steps.append(
            {
                "order": step["order"],
                "state": state,
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
            }
        )
    return {
        "project": str(project),
        "device": device,
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
    commands = [list(plan["build"]), list(plan["install"])]
    for step in plan["steps"]:
        commands.append(list(step["launch"]))
        commands.append(["xcrun", "simctl", "io", str(plan["device"]), "screenshot", str(step["screenshot"])])

    completed = []
    for command in commands:
        exit_code = run(command, project)
        completed.append({"command": command, "exit_code": exit_code})
        if exit_code != 0:
            return {"ok": False, "completed": completed}
        if command[:4] == ["xcrun", "simctl", "launch", "--terminate-running-process"]:
            time.sleep(sleep_seconds)
    return {"ok": True, "completed": completed}


def _run_command(command: list[str], cwd: Path) -> int:
    if command[:2] == ["xcrun", "simctl"] and shutil.which("rtk") is not None:
        command = ["rtk", *command]
    return subprocess.run(command, cwd=cwd).returncode
