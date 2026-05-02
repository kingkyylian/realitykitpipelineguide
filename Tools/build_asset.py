#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "Tools" / "asset_manifest.json"


def load_asset(asset_id: str) -> dict | None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for asset in manifest.get("assets", []):
        if asset.get("id") == asset_id:
            return asset
    return None


def blender_executable() -> str | None:
    override = os.environ.get("BLENDER")
    if override:
        return override
    return shutil.which("blender")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Blender build script for one asset.")
    parser.add_argument("--id", required=True, help="Asset id from Tools/asset_manifest.json")
    args = parser.parse_args()

    asset = load_asset(args.id)
    if asset is None:
        print(f"error: unknown asset id: {args.id}", file=sys.stderr)
        return 1

    script_path = ROOT / "Tools" / "blender" / f"create_{args.id}.py"
    if not script_path.exists():
        print(f"error: missing Blender script: {script_path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    blender = blender_executable()
    if blender is None:
        print(
            "error: Blender executable not found. Install Blender or run with "
            "BLENDER=/path/to/blender make build-asset id=<asset_id>",
            file=sys.stderr,
        )
        return 127

    output_path = ROOT / "Assets" / "Imported" / asset["file"]
    command = [blender, "--background", "--python", str(script_path)]
    print("running:", " ".join(command))
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        return result.returncode

    if not output_path.exists():
        print(f"error: expected USDZ was not created: {output_path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    size = output_path.stat().st_size
    if size <= 0:
        print(f"error: USDZ is empty: {output_path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    print(f"asset built: {output_path.relative_to(ROOT)} ({size} bytes)")
    print("manifest status is unchanged; run accept-asset later after visual verification")
    return 0


if __name__ == "__main__":
    sys.exit(main())
