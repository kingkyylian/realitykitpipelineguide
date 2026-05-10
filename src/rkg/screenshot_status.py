from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rkg.qa_plan import build_qa_plan
from rkg.spec import load_game_spec

JsonDict = dict[str, Any]


def load_qa_plan(path: Path) -> JsonDict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("qa plan root must be an object")
    return value


def build_screenshot_status_for_project(project: Path) -> JsonDict:
    spec_path = project / "GameSpec.json"
    if not spec_path.exists():
        raise ValueError("missing GameSpec.json; pass --plan to verify against an external qa-plan JSON file")
    return build_screenshot_status(project, build_qa_plan(load_game_spec(spec_path)))


def build_screenshot_status(project: Path, qa_plan: Mapping[str, Any]) -> JsonDict:
    project = project.resolve()
    if not project.exists() or not project.is_dir():
        raise ValueError(f"generated project does not exist: {project}")

    checks = [_check_step(project, step) for step in _qa_steps(qa_plan)]
    return {
        "game_id": str(qa_plan.get("game_id", "")),
        "display_name": str(qa_plan.get("display_name", "")),
        "archetype": str(qa_plan.get("archetype", "")),
        "ok": all(check["status"] == "ok" for check in checks),
        "checks": checks,
    }


def _qa_steps(qa_plan: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    steps = qa_plan.get("steps")
    if not isinstance(steps, list):
        raise ValueError("qa plan steps must be a list")
    for step in steps:
        if not isinstance(step, Mapping):
            raise ValueError("qa plan steps must contain objects")
    return steps


def _check_step(project: Path, step: Mapping[str, Any]) -> JsonDict:
    capture_path = str(step.get("capture_path", ""))
    path = project / capture_path
    status, size = _image_file_status(path)
    return {
        "order": int(step.get("order", 0)),
        "state": str(step.get("state", "")),
        "capture_path": capture_path,
        "status": status,
        "bytes": size,
    }


def _image_file_status(path: Path) -> tuple[str, int]:
    if not path.exists():
        return "missing", 0
    if not path.is_file():
        return "not_file", 0
    size = path.stat().st_size
    if size == 0:
        return "empty", 0
    with path.open("rb") as handle:
        header = handle.read(12)
    if _is_supported_image_header(header):
        return "ok", size
    return "invalid_image", size


def _is_supported_image_header(header: bytes) -> bool:
    return header.startswith(b"\xff\xd8\xff") or header.startswith(b"\x89PNG\r\n\x1a\n")
