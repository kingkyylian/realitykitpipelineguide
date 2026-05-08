from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

MACOS_BLENDER_APP = Path("/Applications/Blender.app/Contents/MacOS/Blender")


@dataclass(frozen=True)
class ToolResolution:
    name: str
    path: Path | None
    source: str | None
    is_executable: bool
    error: str | None = None


def resolve_blender() -> ToolResolution:
    override = os.environ.get("BLENDER")
    if override:
        path = Path(override)
        is_executable = path.exists() and os.access(path, os.X_OK)
        return ToolResolution(
            name="blender",
            path=path,
            source="BLENDER",
            is_executable=is_executable,
            error=None if is_executable else f"Blender executable is not available: {override}",
        )

    executable = shutil.which("blender")
    if executable:
        return ToolResolution("blender", Path(executable), "PATH", True)

    if MACOS_BLENDER_APP.exists():
        is_executable = os.access(MACOS_BLENDER_APP, os.X_OK)
        return ToolResolution(
            name="blender",
            path=MACOS_BLENDER_APP,
            source="macOS app",
            is_executable=is_executable,
            error=None if is_executable else f"Blender executable is not available: {MACOS_BLENDER_APP}",
        )

    return ToolResolution(
        name="blender",
        path=None,
        source=None,
        is_executable=False,
        error="Blender executable not found. Install Blender or set BLENDER=/path/to/blender.",
    )
