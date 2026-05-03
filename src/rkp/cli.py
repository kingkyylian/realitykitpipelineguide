#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from rkp import __version__
from rkp.pipeline_doctor import Doctor
from rkp.rkp_project import CONFIG_FILE, DEFAULT_CONFIG, ProjectPaths, load_project


_PROJECT: ProjectPaths | None = None


def project() -> ProjectPaths:
    global _PROJECT
    if _PROJECT is None:
        _PROJECT = load_project()
    return _PROJECT


def package_env() -> dict[str, str]:
    env = dict(os.environ)
    source_root = Path(__file__).resolve().parents[1]
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(source_root) if not pythonpath else f"{source_root}:{pythonpath}"
    return env


def module_command(module: str, *args: str) -> list[str]:
    return [sys.executable, "-m", module, *args]


def run(command: list[str], active_project: ProjectPaths | None = None) -> int:
    active_project = active_project or project()
    return subprocess.run(command, cwd=active_project.root, env=package_env()).returncode


def load_manifest(active_project: ProjectPaths | None = None) -> dict:
    active_project = active_project or project()
    return json.loads(active_project.manifest.read_text(encoding="utf-8"))


def build_status_payload(active_project: ProjectPaths | None = None) -> dict:
    active_project = active_project or project()
    manifest = load_manifest(active_project)
    assets = manifest.get("assets", [])
    return {
        "project": manifest.get("project", ""),
        "scale": manifest.get("scale", ""),
        "assets": [
            {
                "id": asset.get("id", ""),
                "status": asset.get("status", ""),
                "type": asset.get("type", ""),
                "file": asset.get("file", ""),
                "archetype": asset.get("archetype") or infer_script_archetype(asset.get("id", ""), active_project),
                "next": next_action(asset, active_project),
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
    print(f"{'asset':<28} {'status':<10} {'type':<18} {'archetype':<14} {'file':<28} next")
    print("-" * 119)
    for asset in assets:
        archetype = asset["archetype"] or "-"
        print(
            f"{asset['id']:<28} {asset['status']:<10} {asset['type']:<18} "
            f"{archetype:<14} {asset['file']:<28} {asset['next']}"
        )


def print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def run_doctor_json() -> int:
    doctor = Doctor(project())
    doctor.collect()
    summary = doctor.summary()
    print_json(summary)
    return 0 if summary["ok"] else 1


def infer_script_archetype(asset_id: str, active_project: ProjectPaths | None = None) -> str | None:
    if not asset_id:
        return None
    active_project = active_project or project()
    script_path = active_project.blender_dir / f"create_{asset_id}.py"
    if not script_path.exists():
        return None
    match = re.search(r'^ARCHETYPE\s*=\s*["\']([^"\']+)["\']', script_path.read_text(encoding="utf-8"), re.MULTILINE)
    if match:
        return match.group(1)
    return None


def next_action(asset: dict, active_project: ProjectPaths | None = None) -> str:
    active_project = active_project or project()
    asset_id = asset.get("id", "")
    file_name = asset.get("file", "")
    usdz_path = active_project.assets_dir / file_name
    blender_path = active_project.blender_dir / f"create_{asset_id}.py"

    if asset.get("status") == "imported":
        return "ready"
    if not blender_path.exists():
        return f"create {active_project.rel(blender_path)}"
    if not usdz_path.exists() or usdz_path.stat().st_size <= 0:
        return f"rkp build-asset {asset_id}"
    return f"rkp accept-asset {asset_id} --screenshot Docs/screenshots/{asset_id}_imported.jpg"


def run_init(args: argparse.Namespace) -> int:
    root = Path.cwd().resolve()
    config_path = root / CONFIG_FILE
    config = dict(DEFAULT_CONFIG)
    manifest_path = root / config["manifest"]

    if not args.force and (config_path.exists() or manifest_path.exists()):
        print("error: already initialized, use --force to reinitialize", file=sys.stderr)
        return 1

    project_name = args.project_name or root.name
    manifest = {
        "project": project_name,
        "scale": "1 Blender unit = 1 meter",
        "assets": [],
    }

    for rel_path in [
        config["assets_dir"],
        config["textures_dir"],
        config["source_dir"],
        str(Path(config["docs_dir"]) / "assets"),
        str(Path(config["docs_dir"]) / "screenshots"),
        config["blender_dir"],
    ]:
        (root / rel_path).mkdir(parents=True, exist_ok=True)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"initialized rkp project: {project_name}")
    print(f"config: {CONFIG_FILE}")
    print(f"manifest: {config['manifest']}")
    return 0


def run_release_check() -> int:
    active_project = project()
    print("==> doctor", flush=True)
    status = Doctor(active_project).run()
    if status != 0:
        print("release-check failed at step: doctor", file=sys.stderr)
        return status

    print("==> tests", flush=True)
    if active_project.tests_dir.exists():
        status = run(
            [sys.executable, "-m", "unittest", "discover", "-s", active_project.rel(active_project.tests_dir)],
            active_project,
        )
        if status != 0:
            print("release-check failed at step: tests", file=sys.stderr)
            return status
    else:
        print(f"skip tests: {active_project.rel(active_project.tests_dir)} not found")

    print("==> validate", flush=True)
    try:
        load_manifest(active_project)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"release-check failed at step: validate ({exc})", file=sys.stderr)
        return 1
    print("manifest ok")

    xcode_project = active_project.xcode_project
    if xcode_project is None:
        print("skip xcode: xcode_project not configured")
        print("release-check ok")
        return 0

    project_yml = active_project.root / "project.yml"
    if project_yml.exists():
        print("==> generate", flush=True)
        status = run(["xcodegen", "generate"], active_project)
        if status != 0:
            print("release-check failed at step: generate", file=sys.stderr)
            return status
    else:
        print("skip generate: project.yml not found")

    if not xcode_project.exists():
        print(f"release-check failed at step: build (missing {active_project.rel(xcode_project)})", file=sys.stderr)
        return 1

    scheme = active_project.xcode_scheme or xcode_project.stem
    print("==> build", flush=True)
    status = run(
        [
            "xcodebuild",
            "-quiet",
            "-project",
            active_project.rel(xcode_project),
            "-scheme",
            scheme,
            "-destination",
            active_project.xcode_destination,
            "-derivedDataPath",
            active_project.rel(active_project.derived_data_path),
            "build",
        ],
        active_project,
    )
    if status != 0:
        print("release-check failed at step: build", file=sys.stderr)
        return status
    print("release-check ok")
    return 0


def run_make_asset(args: argparse.Namespace) -> int:
    steps = [
        (
            "prompt-asset",
            [
                sys.executable,
                "-m",
                "rkp.prompt_asset",
                args.id,
                "--prompt",
                args.prompt,
                "--type",
                args.type,
            ],
        )
    ]

    if args.force:
        steps[0][1].append("--force")
    if args.build:
        steps.append(("build-asset", module_command("rkp.build_asset", "--id", args.id)))
    if args.screenshot:
        if not args.build:
            print("error: --screenshot requires --build because acceptance needs a built USDZ", file=sys.stderr)
            return 2
        steps.append(
            (
                "accept-asset",
                module_command("rkp.accept_asset", "--id", args.id, "--screenshot", args.screenshot),
            )
        )
    if args.release_check:
        steps.append(("release-check", module_command("rkp.cli", "release-check")))

    for label, command in steps:
        print(f"==> {label}", flush=True)
        status = run(command)
        if status != 0:
            print(f"make-asset stopped at step: {label}", file=sys.stderr)
            return status

    print(f"make-asset done: {args.id}")
    if not args.build:
        print(f"next: rkp build-asset {args.id}")
    elif not args.screenshot:
        print(f"next: rkp accept-asset {args.id} --screenshot Docs/screenshots/{args.id}_imported.jpg")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="rkp",
        description="RealityKit Pipeline CLI for Blender -> USDZ -> RealityKit asset workflows.",
    )
    parser.add_argument("--version", action="version", version=f"rkp {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Initialize a minimal RKP config in the current project")
    init.add_argument("--force", action="store_true", help="Overwrite existing rkp.json and manifest")
    init.add_argument("--project-name", help="Project name written to the new manifest")

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

    make_asset = subparsers.add_parser("make-asset", help="Run prompt, optional build, optional accept, and optional release gate")
    make_asset.add_argument("id", help="Asset id in snake_case")
    make_asset.add_argument("--prompt", required=True, help="Asset prompt or short art brief")
    make_asset.add_argument("--type", default="prop", help="Asset type, for example gameplay_target or environment")
    make_asset.add_argument("--build", action="store_true", help="Run Blender build after prompt scaffolding")
    make_asset.add_argument("--screenshot", help="Accept the asset with required simulator screenshot evidence")
    make_asset.add_argument("--release-check", action="store_true", help="Run the full release gate after prior steps")
    make_asset.add_argument("--force", action="store_true", help="Overwrite an existing Blender script")

    build_asset = subparsers.add_parser("build-asset", help="Run the Blender build script for one asset")
    build_asset.add_argument("id", help="Asset id from Tools/asset_manifest.json")

    accept_asset = subparsers.add_parser("accept-asset", help="Accept a built asset with required screenshot evidence")
    accept_asset.add_argument("id", help="Asset id from Tools/asset_manifest.json")
    accept_asset.add_argument("--screenshot", required=True, help="Required simulator screenshot path")

    args = parser.parse_args()

    if args.command == "init":
        return run_init(args)
    if args.command == "status":
        if args.json:
            print_json(build_status_payload())
            return 0
        print_asset_table()
        return 0
    if args.command == "doctor":
        if args.json:
            return run_doctor_json()
        return Doctor(project()).run()
    if args.command == "release-check":
        return run_release_check()
    if args.command == "new-asset":
        command = module_command("rkp.new_asset", "--id", args.id, "--type", args.type)
        if args.triangles is not None:
            command.extend(["--triangles", str(args.triangles)])
        if args.texture is not None:
            command.extend(["--texture", str(args.texture)])
        return run(command)
    if args.command == "prompt-asset":
        command = [
            sys.executable,
            "-m",
            "rkp.prompt_asset",
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
    if args.command == "make-asset":
        return run_make_asset(args)
    if args.command == "build-asset":
        return run(module_command("rkp.build_asset", "--id", args.id))
    if args.command == "accept-asset":
        return run(module_command("rkp.accept_asset", "--id", args.id, "--screenshot", args.screenshot))

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
