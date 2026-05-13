from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from rkg.asset_pipeline import build_asset_pipeline
from rkg.capture import build_capture_plan, execute_capture_plan
from rkg.qa_plan import build_qa_plan
from rkg.screenshot_status import build_screenshot_status_for_project
from rkg.spec import load_game_spec
from rkp.runtime import module_command, package_env

JsonDict = dict[str, Any]
CommandRunner = Callable[[list[str], Path], int]
CaptureExecutor = Callable[[Path, str], JsonDict]
ScreenshotVerifier = Callable[[Path], JsonDict]

ROLE_PRIORITY = [
    "target",
    "enemy",
    "opponent",
    "projectile",
    "weapon",
    "player",
    "vehicle",
    "pickup",
    "obstacle",
    "cover",
    "arena",
]

ROLE_STATE_PREFERENCES = {
    "target": ["fail_or_hit", "mid_action", "gameplay_start"],
    "enemy": ["fail_or_hit", "mid_action", "gameplay_start"],
    "opponent": ["knockout", "mid_combo", "round_start"],
    "projectile": ["mid_action", "fail_or_hit", "gameplay_start"],
    "weapon": ["mid_action", "gameplay_start"],
    "player": ["gameplay_start", "round_start", "mid_action"],
}


def build_first_asset_acceptance_plan(
    project: Path,
    *,
    asset_id: str | None = None,
    device: str = "booted",
    source_state: str | None = None,
) -> JsonDict:
    project = project.resolve()
    spec = load_game_spec(project / "GameSpec.json")
    pipeline = build_asset_pipeline(spec, project)
    task = _select_task(pipeline["tasks"], asset_id)
    qa = build_qa_plan(spec)
    qa_step = _select_screenshot_step(qa["steps"], str(task["role"]), source_state)
    source_screenshot = str(qa_step["capture_path"])
    acceptance_screenshot = str(task["screenshot_path"])

    steps = [
        _task_step(task, "build_asset"),
        _task_step(task, "inspect_usdz"),
        {"step": "capture_screenshots", "command": ["rkg", "capture-screenshots", ".", "--device", device]},
        {"step": "verify_screenshots", "command": ["rkg", "verify-screenshots", "."]},
        {
            "step": "copy_acceptance_screenshot",
            "command": ["copy", source_screenshot, acceptance_screenshot],
        },
        _task_step(task, "accept_asset"),
        {"step": "release_check_assets", "command": ["rkp", "release-check", "--assets"]},
    ]
    if not _blender_script_exists(project, str(task["asset_id"])):
        steps.insert(0, _task_step(task, "make_asset"))
    return {
        "project": str(project),
        "device": device,
        "asset_id": task["asset_id"],
        "role": task["role"],
        "type": task["type"],
        "source_state": qa_step["state"],
        "source_screenshot": source_screenshot,
        "acceptance_screenshot": acceptance_screenshot,
        "steps": steps,
    }


def build_asset_acceptance_plan(
    project: Path,
    *,
    asset_ids: list[str] | None = None,
    device: str = "booted",
    source_state: str | None = None,
) -> JsonDict:
    project = project.resolve()
    spec = load_game_spec(project / "GameSpec.json")
    pipeline = build_asset_pipeline(spec, project)
    qa = build_qa_plan(spec)
    tasks = _select_tasks(pipeline["tasks"], asset_ids)
    assets = []
    steps = []

    for task in tasks:
        qa_step = _select_screenshot_step(qa["steps"], str(task["role"]), source_state)
        assets.append(_asset_record(task, qa_step))
        if not _blender_script_exists(project, str(task["asset_id"])):
            steps.append(_task_step(task, "make_asset"))
        steps.append(_task_step(task, "build_asset"))
        steps.append(_task_step(task, "inspect_usdz"))

    steps.append({"step": "capture_screenshots", "command": ["rkg", "capture-screenshots", ".", "--device", device]})
    steps.append({"step": "verify_screenshots", "command": ["rkg", "verify-screenshots", "."]})

    for asset, task in zip(assets, tasks, strict=True):
        steps.append(
            {
                "step": "copy_acceptance_screenshot",
                "command": ["copy", asset["source_screenshot"], asset["acceptance_screenshot"]],
            }
        )
        steps.append(_task_step(task, "accept_asset"))

    steps.append({"step": "release_check_assets", "command": ["rkp", "release-check", "--assets"]})
    return {
        "project": str(project),
        "device": device,
        "assets": assets,
        "steps": steps,
    }


def execute_asset_acceptance_plan(
    plan: Mapping[str, Any],
    *,
    runner: CommandRunner | None = None,
    capture_executor: CaptureExecutor | None = None,
    screenshot_verifier: ScreenshotVerifier | None = None,
) -> JsonDict:
    project = Path(str(plan["project"]))
    run = runner or _run_command
    completed = []
    for step in plan["steps"]:
        step_name = str(step["step"])
        command = [str(part) for part in step["command"]]
        if step_name == "capture_screenshots":
            result = (
                capture_executor(project, str(plan["device"]))
                if capture_executor
                else execute_capture_plan(build_capture_plan(project, device=str(plan["device"])))
            )
            exit_code = 0 if result.get("ok") else 1
            completed.append({"step": step_name, "command": command, "exit_code": exit_code})
            if exit_code != 0:
                return {"ok": False, "completed": completed}
            continue
        if step_name == "verify_screenshots":
            status = (screenshot_verifier or build_screenshot_status_for_project)(project)
            exit_code = 0 if status.get("ok") else 1
            completed.append({"step": step_name, "command": command, "exit_code": exit_code})
            if exit_code != 0:
                return {"ok": False, "completed": completed}
            continue
        if step_name == "copy_acceptance_screenshot":
            try:
                _copy_screenshot(project, command[1], command[2])
            except OSError as exc:
                completed.append({"step": step_name, "command": command, "exit_code": 1, "error": str(exc)})
                return {"ok": False, "completed": completed}
            completed.append({"step": step_name, "command": command, "exit_code": 0})
            continue

        exit_code = run(command, project)
        completed.append({"step": step_name, "command": command, "exit_code": exit_code})
        if exit_code != 0:
            return {"ok": False, "completed": completed}
    return {"ok": True, "completed": completed}


def execute_first_asset_acceptance_plan(
    plan: Mapping[str, Any],
    *,
    runner: CommandRunner | None = None,
    capture_executor: CaptureExecutor | None = None,
    screenshot_verifier: ScreenshotVerifier | None = None,
) -> JsonDict:
    return execute_asset_acceptance_plan(
        plan,
        runner=runner,
        capture_executor=capture_executor,
        screenshot_verifier=screenshot_verifier,
    )


def _select_task(tasks: list[Mapping[str, Any]], asset_id: str | None) -> Mapping[str, Any]:
    if asset_id:
        for task in tasks:
            if task["asset_id"] == asset_id:
                return task
        raise ValueError(f"unknown asset id for generated project: {asset_id}")
    by_priority = {role: index for index, role in enumerate(ROLE_PRIORITY)}
    return min(tasks, key=lambda task: by_priority.get(str(task["role"]), len(ROLE_PRIORITY)))


def _select_tasks(tasks: list[Mapping[str, Any]], asset_ids: list[str] | None) -> list[Mapping[str, Any]]:
    if asset_ids:
        return [_select_task(tasks, asset_id) for asset_id in asset_ids]
    by_priority = {role: index for index, role in enumerate(ROLE_PRIORITY)}
    return sorted(tasks, key=lambda task: by_priority.get(str(task["role"]), len(ROLE_PRIORITY)))


def _asset_record(task: Mapping[str, Any], qa_step: Mapping[str, Any]) -> JsonDict:
    return {
        "asset_id": task["asset_id"],
        "role": task["role"],
        "type": task["type"],
        "source_state": qa_step["state"],
        "source_screenshot": qa_step["capture_path"],
        "acceptance_screenshot": task["screenshot_path"],
    }


def _select_screenshot_step(
    steps: list[Mapping[str, Any]],
    role: str,
    requested_state: str | None,
) -> Mapping[str, Any]:
    visible = [step for step in steps if role in {str(value) for value in step.get("visible_roles", [])}]
    candidates = visible or steps
    if requested_state:
        for step in candidates:
            if step["state"] == requested_state:
                return step
        raise ValueError(f"screenshot state does not show role {role}: {requested_state}")
    preferences = ROLE_STATE_PREFERENCES.get(role, [])
    for state in preferences:
        for step in candidates:
            if step["state"] == state:
                return step
    return candidates[0]


def _task_step(task: Mapping[str, Any], step_name: str) -> JsonDict:
    for step in task["commands"]:
        if step["step"] == step_name:
            return {"step": step_name, "command": list(step["command"])}
    raise ValueError(f"asset task is missing command step: {step_name}")


def _copy_screenshot(project: Path, source: str, destination: str) -> None:
    source_path = project / source
    destination_path = project / destination
    if not source_path.is_file():
        raise FileNotFoundError(f"source screenshot is missing: {source}")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, destination_path)


def _blender_script_exists(project: Path, asset_id: str) -> bool:
    return (project / "Tools" / "blender" / f"create_{asset_id}.py").is_file()


def _run_command(command: list[str], cwd: Path) -> int:
    return subprocess.run(_execution_command(command), cwd=cwd, env=package_env()).returncode


def _execution_command(command: list[str]) -> list[str]:
    if not command:
        return command
    if command[0] == "rkp":
        return module_command("rkp.cli", *command[1:])
    if command[0] == "rkg":
        return module_command("rkg.cli", *command[1:])
    return command
