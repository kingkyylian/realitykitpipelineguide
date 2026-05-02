#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys


REQUIRED_PATHS = [
    "README.md",
    "Docs/guide.md",
    "Docs/production-playbook.md",
    "Docs/new-game-startup.md",
    "Docs/WORKLOG.md",
    "Docs/ai-handoff.md",
    "Tools/asset_manifest.json",
    "Assets/Imported",
    "Sources/RealityKitPipelineDemo",
    "project.yml",
    "Makefile",
]


def main() -> int:
    root = Path.cwd()
    missing = [path for path in REQUIRED_PATHS if not (root / path).exists()]

    manifest_path = root / "Tools/asset_manifest.json"
    manifest_errors: list[str] = []
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            assets = manifest.get("assets", [])
            if not isinstance(assets, list) or not assets:
                manifest_errors.append("manifest assets must be a non-empty list")
            for asset in assets:
                asset_id = asset.get("id")
                file_name = asset.get("file")
                if not asset_id or not file_name:
                    manifest_errors.append(f"asset missing id/file: {asset!r}")
                    continue
                if asset.get("status") == "imported" and not (root / "Assets/Imported" / file_name).exists():
                    manifest_errors.append(f"imported asset file missing: {file_name}")
        except json.JSONDecodeError as exc:
            manifest_errors.append(f"manifest JSON error: {exc}")

    if missing or manifest_errors:
        print("RealityKit pipeline check failed")
        for path in missing:
            print(f"missing path: {path}")
        for error in manifest_errors:
            print(f"manifest: {error}")
        return 1

    print("RealityKit pipeline structure ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
