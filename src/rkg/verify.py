from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REQUIRED_FILES = [
    "GameSpec.json",
    "rkp.json",
    "project.yml",
    "Tools/asset_manifest.json",
]


def required_project_files() -> list[Path]:
    return [Path(path) for path in REQUIRED_FILES]


def verification_commands(project: Path) -> list[list[str]]:
    commands: list[list[str]] = []
    tests_dir = project / "Tests"
    if tests_dir.exists() and any(tests_dir.glob("test*.py")):
        commands.append([sys.executable, "-m", "unittest", "discover", "-s", "Tests"])
    commands.append(["rkp", "doctor"])
    commands.append(["rkp", "release-check"])
    return commands


def verify_game(project: Path) -> int:
    project = project.resolve()
    if not project.exists() or not project.is_dir():
        print(f"error: generated project does not exist: {project}", file=sys.stderr)
        return 1

    missing = [path for path in required_project_files() if not (project / path).exists()]
    if missing:
        for path in missing:
            print(f"error: missing generated project file: {path}", file=sys.stderr)
        return 1

    for command in verification_commands(project):
        print("==> " + " ".join(command), flush=True)
        status = run_command(command, project)
        if status != 0:
            print(f"verify-game failed at step: {' '.join(command)}", file=sys.stderr)
            return status

    print("verify-game ok")
    return 0


def run_command(command: list[str], cwd: Path) -> int:
    return subprocess.run(command, cwd=cwd).returncode
