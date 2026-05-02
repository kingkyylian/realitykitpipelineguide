#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from pipeline_doctor import Doctor


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "Tools" / "asset_manifest.json"


def run(command: list[str]) -> int:
    return subprocess.run(command, cwd=ROOT).returncode


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def build_status_payload() -> dict:
    manifest = load_manifest()
    assets = manifest.get("assets", [])
    return {
        "assets": [
            {
                "id": asset.get("id", ""),
                "status": asset.get("status", ""),
                "type": asset.get("type", ""),
                "file": asset.get("file", ""),
                "next": next_action(asset),
            }
            for asset in assets
        ]
    }


def print_asset_table() -> None:
    assets = build_status_payload()["assets"]
    if not assets:
        print("no assets in manifest")
        return

    print("RealityKit Pipeline Status")
    print()
    print(f"{'asset':<28} {'status':<10} {'type':<18} {'file':<28} next")
    print("-" * 104)
    for asset in assets:
        print(f"{asset['id']:<28} {asset['status']:<10} {asset['type']:<18} {asset['file']:<28} {asset['next']}")


def print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def run_doctor_json() -> int:
    doctor = Doctor(ROOT)
    doctor.collect()
    summary = doctor.summary()
    print_json(summary)
    return 0 if summary["ok"] else 1


def next_action(asset: dict) -> str:
    asset_id = asset.get("id", "")
    file_name = asset.get("file", "")
    usdz_path = ROOT / "Assets" / "Imported" / file_name
    blender_path = ROOT / "Tools" / "blender" / f"create_{asset_id}.py"

    if asset.get("status") == "imported":
        return "ready"
    if not blender_path.exists():
        return f"create Tools/blender/create_{asset_id}.py"
    if not usdz_path.exists() or usdz_path.stat().st_size <= 0:
        return f"rkp build-asset {asset_id}"
    return f"rkp accept-asset {asset_id} --screenshot Docs/screenshots/{asset_id}_imported.jpg"


def run_release_check() -> int:
    steps = [
        ("doctor", [sys.executable, "Tools/rkp.py", "doctor"]),
        ("generate", ["xcodegen", "generate"]),
        (
            "validate",
            [
                "node",
                "-e",
                "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')",
            ],
        ),
        (
            "build",
            [
                "xcodebuild",
                "-quiet",
                "-project",
                "RealityKitPipelineDemo.xcodeproj",
                "-scheme",
                "RealityKitPipelineDemo",
                "-destination",
                "generic/platform=iOS Simulator",
                "-derivedDataPath",
                "Build/DerivedData",
                "build",
            ],
        ),
    ]

    for label, command in steps:
        print(f"==> {label}", flush=True)
        status = run(command)
        if status != 0:
            print(f"release-check failed at step: {label}", file=sys.stderr)
            return status
    print("release-check ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="rkp",
        description="RealityKit Pipeline CLI for Blender -> USDZ -> RealityKit asset workflows.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Show manifest assets and the next pipeline action")
    status.add_argument("--json", action="store_true", help="Print machine-readable status")

    doctor = subparsers.add_parser("doctor", help="Run the static pipeline doctor")
    doctor.add_argument("--json", action="store_true", help="Print machine-readable doctor summary")

    subparsers.add_parser("release-check", help="Run doctor, XcodeGen, manifest validation, and iOS build")

    new_asset = subparsers.add_parser("new-asset", help="Scaffold a manifest entry, asset brief, and Blender stub")
    new_asset.add_argument("id", help="Asset id in snake_case")
    new_asset.add_argument("--type", default="prop", help="Asset type, for example gameplay_target or environment")
    new_asset.add_argument("--triangles", type=int, help="Triangle budget override")
    new_asset.add_argument("--texture", type=int, help="Texture size budget override")

    prompt_asset = subparsers.add_parser("prompt-asset", help="Create a prompt-backed asset brief and Blender generator")
    prompt_asset.add_argument("id", help="Asset id in snake_case")
    prompt_asset.add_argument("--prompt", required=True, help="Asset prompt or short art brief")
    prompt_asset.add_argument("--type", default="prop", help="Asset type, for example gameplay_target or environment")
    prompt_asset.add_argument("--build", action="store_true", help="Run Blender build after generating the script")
    prompt_asset.add_argument("--force", action="store_true", help="Overwrite an existing Blender script")

    build_asset = subparsers.add_parser("build-asset", help="Run the Blender build script for one asset")
    build_asset.add_argument("id", help="Asset id from Tools/asset_manifest.json")

    accept_asset = subparsers.add_parser("accept-asset", help="Accept a built asset with required screenshot evidence")
    accept_asset.add_argument("id", help="Asset id from Tools/asset_manifest.json")
    accept_asset.add_argument("--screenshot", required=True, help="Required simulator screenshot path")

    args = parser.parse_args()

    if args.command == "status":
        if args.json:
            print_json(build_status_payload())
            return 0
        print_asset_table()
        return 0
    if args.command == "doctor":
        if args.json:
            return run_doctor_json()
        return run([sys.executable, "Tools/pipeline_doctor.py"])
    if args.command == "release-check":
        return run_release_check()
    if args.command == "new-asset":
        command = [sys.executable, "Tools/new_asset.py", "--id", args.id, "--type", args.type]
        if args.triangles is not None:
            command.extend(["--triangles", str(args.triangles)])
        if args.texture is not None:
            command.extend(["--texture", str(args.texture)])
        return run(command)
    if args.command == "prompt-asset":
        command = [
            sys.executable,
            "Tools/prompt_asset.py",
            args.id,
            "--prompt",
            args.prompt,
            "--type",
            args.type,
        ]
        if args.build:
            command.append("--build")
        if args.force:
            command.append("--force")
        return run(command)
    if args.command == "build-asset":
        return run([sys.executable, "Tools/build_asset.py", "--id", args.id])
    if args.command == "accept-asset":
        return run([sys.executable, "Tools/accept_asset.py", "--id", args.id, "--screenshot", args.screenshot])

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
