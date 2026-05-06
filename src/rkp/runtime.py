from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from rkp.rkp_project import ProjectPaths, load_project


def package_env() -> dict[str, str]:
    env = dict(os.environ)
    source_root = Path(__file__).resolve().parents[1]
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(source_root) if not pythonpath else f"{source_root}:{pythonpath}"
    return env


def module_command(module: str, *args: str) -> list[str]:
    return [sys.executable, "-m", module, *args]


def run(command: list[str], active_project: ProjectPaths | None = None) -> int:
    active_project = active_project or load_project()
    return subprocess.run(command, cwd=active_project.root, env=package_env()).returncode
