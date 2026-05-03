#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from rkp.cli import module_command, package_env
from rkp.rkp_project import ProjectPaths, load_project

PROJECT = load_project()
MACOS_BLENDER_APP = Path("/Applications/Blender.app/Contents/MacOS/Blender")


def load_asset(asset_id: str, project: ProjectPaths = PROJECT) -> dict | None:
    manifest = json.loads(project.manifest.read_text(encoding="utf-8"))
    for asset in manifest.get("assets", []):
        if asset.get("id") == asset_id:
            return asset
    return None


def blender_executable() -> str | None:
    override = os.environ.get("BLENDER")
    if override:
        return override
    executable = shutil.which("blender")
    if executable:
        return executable
    if MACOS_BLENDER_APP.exists():
        return str(MACOS_BLENDER_APP)
    return None


def is_executable(path: str) -> bool:
    return Path(path).exists() and os.access(path, os.X_OK)


def latest_blender_crash_log() -> Path | None:
    crash_log = Path(tempfile.gettempdir()) / "blender.crash.txt"
    if crash_log.exists():
        return crash_log
    return None


def run_direct_usdz_fallback(asset_id: str, project: ProjectPaths = PROJECT) -> int:
    print("warning: Blender failed; trying direct USDZ fallback builder", file=sys.stderr)
    return subprocess.run(
        module_command("rkp.usdz_fallback_builder", "--id", asset_id),
        cwd=project.root,
        env=package_env(),
    ).returncode


def expected_basecolor_texture(asset: dict, project: ProjectPaths = PROJECT) -> Path | None:
    texture_maps = asset.get("textureMaps")
    if texture_maps is not None and "baseColor" not in texture_maps:
        return None
    return project.textures_dir / f"{asset['id']}_basecolor.png"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Blender build script for one asset.")
    parser.add_argument("--id", required=True, help="Asset id from Tools/asset_manifest.json")
    args = parser.parse_args()

    asset = load_asset(args.id)
    if asset is None:
        print(f"error: unknown asset id: {args.id}", file=sys.stderr)
        return 1

    script_path = PROJECT.blender_dir / f"create_{args.id}.py"
    if not script_path.exists():
        print(f"error: missing Blender script: {PROJECT.rel(script_path)}", file=sys.stderr)
        return 1

    blender = blender_executable()
    if blender is None:
        print(
            "error: Blender executable not found. Install Blender or run with "
            "BLENDER=/path/to/blender make build-asset id=<asset_id>",
            file=sys.stderr,
        )
        return 127
    if not is_executable(blender):
        output_path = PROJECT.assets_dir / asset["file"]
        print(
            f"error: Blender executable is not available: {blender}. "
            f"Expected USDZ would be {PROJECT.rel(output_path)}",
            file=sys.stderr,
        )
        return 127

    output_path = PROJECT.assets_dir / asset["file"]
    command = [blender, "--background", "--factory-startup", "--python", str(script_path)]
    print("running:", " ".join(command), flush=True)
    result = subprocess.run(command, cwd=PROJECT.root)
    if result.returncode != 0:
        print(
            f"error: Blender build failed before creating {PROJECT.rel(output_path)} "
            f"(exit {result.returncode})",
            file=sys.stderr,
        )
        print(f"hint: Blender executable: {blender}", file=sys.stderr)
        crash_log = latest_blender_crash_log()
        if crash_log:
            print(f"hint: Blender crash log: {crash_log}", file=sys.stderr)
        fallback_status = run_direct_usdz_fallback(args.id)
        if fallback_status != 0:
            return result.returncode

    if not output_path.exists():
        print(f"error: expected USDZ was not created: {PROJECT.rel(output_path)}", file=sys.stderr)
        return 1

    size = output_path.stat().st_size
    if size <= 0:
        print(f"error: USDZ is empty: {PROJECT.rel(output_path)}", file=sys.stderr)
        return 1

    print(f"asset built: {PROJECT.rel(output_path)} ({size} bytes)")
    texture_path = expected_basecolor_texture(asset)
    if texture_path is not None and not texture_path.exists():
        print(
            "info: no texture file found - USDZ built without texture "
            f"(expected {PROJECT.rel(texture_path)})"
        )
    print("manifest status is unchanged; run accept-asset later after visual verification")
    return 0


if __name__ == "__main__":
    sys.exit(main())
