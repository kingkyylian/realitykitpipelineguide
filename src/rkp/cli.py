#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from rkp import __version__
from rkp.asset_manifest import imported_asset_ids, load_manifest
from rkp.pipeline_doctor import Doctor
from rkp.rkp_project import CONFIG_FILE, DEFAULT_CONFIG, ProjectPaths, load_project
from rkp.runtime import module_command, run

_PROJECT: ProjectPaths | None = None


def project() -> ProjectPaths:
    global _PROJECT
    if _PROJECT is None:
        _PROJECT = load_project()
    return _PROJECT


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


def run_doctor_json(include_blender: bool = False) -> int:
    doctor = Doctor(project())
    doctor.collect(include_blender=include_blender)
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


def run_release_check(include_assets: bool = False) -> int:
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
        manifest = load_manifest(active_project)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"release-check failed at step: validate ({exc})", file=sys.stderr)
        return 1
    print("manifest ok")

    if include_assets:
        print("==> assets", flush=True)
        imported_assets = imported_asset_ids(manifest)
        if not imported_assets:
            print("skip assets: no imported assets")
        for asset_id in imported_assets:
            status = run(module_command("rkp.inspect_usdz", asset_id), active_project)
            if status != 0:
                print(f"release-check failed at step: assets ({asset_id})", file=sys.stderr)
                return status

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


def run_make_asset_meshy(args: argparse.Namespace) -> int:
    from rkp.meshy_asset import generate_usdz

    api_key = os.environ.get("MESHY_API_KEY")
    if not api_key:
        print("error: MESHY_API_KEY not set. Get a key at meshy.ai and run:", file=sys.stderr)
        print("  export MESHY_API_KEY=your_key_here", file=sys.stderr)
        print("  (test key: msy_dummy_api_key_for_test_mode_12345678)", file=sys.stderr)
        return 1

    print("==> new-asset", flush=True)
    rc = run(module_command("rkp.new_asset", "--id", args.id, "--type", args.type))
    if rc not in (0, 1):
        return rc

    proj = project()
    output_path = proj.assets_dir / f"{args.id}.usdz"
    refine = args.quality == "refine"

    print("==> meshy", flush=True)
    try:
        generate_usdz(args.prompt, args.id, output_path, api_key=api_key, refine=refine)
    except Exception as exc:
        print(f"error: Meshy generation failed: {exc}", file=sys.stderr)
        return 1

    print(f"asset ready: {proj.rel(output_path)} ({output_path.stat().st_size} bytes)")
    if getattr(args, "screenshot", None):
        print("==> accept-asset", flush=True)
        rc = run(module_command("rkp.accept_asset", "--id", args.id, "--screenshot", args.screenshot))
        if rc != 0:
            print("make-asset stopped at step: accept-asset", file=sys.stderr)
            return rc

    if getattr(args, "release_check", False):
        print("==> release-check", flush=True)
        rc = run(module_command("rkp.cli", "release-check"))
        if rc != 0:
            print("make-asset stopped at step: release-check", file=sys.stderr)
            return rc

    print(f"make-asset done: {args.id}")
    if not getattr(args, "screenshot", None):
        print(f"next: rkp inspect-usdz {args.id}")
        print(f"next: rkp accept-asset {args.id} --screenshot Docs/screenshots/{args.id}_imported.jpg")
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
    if getattr(args, "generator", "template") != "template":
        steps[0][1].extend(["--generator", args.generator])
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
        print(f"next: rkp inspect-usdz {args.id}")
        print(f"next: rkp accept-asset {args.id} --screenshot Docs/screenshots/{args.id}_imported.jpg")
    return 0


def run_verify_asset(args: argparse.Namespace) -> int:
    steps: list[tuple[str, list[str]]] = []
    if args.build:
        steps.append(("build-asset", module_command("rkp.build_asset", "--id", args.id)))
    steps.append(("inspect-usdz", module_command("rkp.inspect_usdz", args.id)))
    if args.screenshot:
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
            print(f"verify-asset stopped at step: {label}", file=sys.stderr)
            return status

    print(f"verify-asset ok: {args.id}")
    if not args.screenshot:
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
    doctor.add_argument("--blender", action="store_true", help="Also verify Blender executable discovery")

    release_check = subparsers.add_parser("release-check", help="Run doctor, XcodeGen, manifest validation, and iOS build")
    release_check.add_argument("--assets", action="store_true", help="Inspect all imported USDZ assets before Xcode build")

    clean = subparsers.add_parser("clean", help="List or remove ignored local scratch files")
    clean_mode = clean.add_mutually_exclusive_group(required=True)
    clean_mode.add_argument("--dry-run", action="store_true", help="List cleanup candidates without removing them")
    clean_mode.add_argument("--apply", action="store_true", help="Remove cleanup candidates")

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
    prompt_asset.add_argument("--generator", choices=["template", "claude"], default="template", help="Blender script generator (default: deterministic template)")

    make_asset = subparsers.add_parser("make-asset", help="Run prompt, optional build, optional accept, and optional release gate")
    make_asset.add_argument("id", help="Asset id in snake_case")
    make_asset.add_argument("--prompt", required=True, help="Asset prompt or short art brief")
    make_asset.add_argument("--type", default="prop", help="Asset type, for example gameplay_target or environment")
    make_asset.add_argument("--build", action="store_true", help="Run Blender build after prompt scaffolding")
    make_asset.add_argument("--screenshot", help="Accept the asset with required simulator screenshot evidence")
    make_asset.add_argument("--release-check", action="store_true", help="Run the full release gate after prior steps")
    make_asset.add_argument("--force", action="store_true", help="Overwrite an existing Blender script")
    make_asset.add_argument("--backend", choices=["blender", "meshy"], default="blender", help="3D generation backend (default: blender)")
    make_asset.add_argument("--quality", choices=["preview", "refine"], default="preview", help="Meshy quality: preview (geometry only) or refine (+ PBR texture)")
    make_asset.add_argument("--generator", choices=["template", "claude"], default="template", help="Blender script generator when --backend blender")

    build_asset = subparsers.add_parser("build-asset", help="Run the Blender build script for one asset")
    build_asset.add_argument("id", help="Asset id from Tools/asset_manifest.json")
    build_asset.add_argument(
        "--fallback-only",
        action="store_true",
        help="Skip Blender and build a prompt-backed procedural USDZ draft with the direct fallback builder",
    )

    inspect_usdz = subparsers.add_parser("inspect-usdz", help="Inspect a built USDZ against manifest expectations")
    inspect_usdz.add_argument("id", help="Asset id from Tools/asset_manifest.json")
    inspect_usdz.add_argument("--json", action="store_true", help="Print machine-readable inspection result")

    verify_asset = subparsers.add_parser("verify-asset", help="Run the asset quality gate: optional build, inspect, optional accept, optional release")
    verify_asset.add_argument("id", help="Asset id from Tools/asset_manifest.json")
    verify_asset.add_argument("--build", action="store_true", help="Build the USDZ before inspection")
    verify_asset.add_argument("--screenshot", help="Accept the asset after inspection with screenshot evidence")
    verify_asset.add_argument("--release-check", action="store_true", help="Run release-check after prior verification steps")

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
            return run_doctor_json(include_blender=args.blender)
        return Doctor(project()).run(include_blender=args.blender)
    if args.command == "release-check":
        return run_release_check(include_assets=args.assets)
    if args.command == "clean":
        command = module_command("rkp.cleanup", "--apply" if args.apply else "--dry-run")
        return run(command)
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
        if args.generator != "template":
            command.extend(["--generator", args.generator])
        return run(command)
    if args.command == "make-asset":
        if getattr(args, "backend", "blender") == "meshy" and getattr(args, "generator", "template") != "template":
            print("error: --generator is only supported with --backend blender", file=sys.stderr)
            return 2
        if getattr(args, "backend", "blender") == "meshy":
            return run_make_asset_meshy(args)
        return run_make_asset(args)
    if args.command == "build-asset":
        command = module_command("rkp.build_asset", "--id", args.id)
        if args.fallback_only:
            command.append("--fallback-only")
        return run(command)
    if args.command == "inspect-usdz":
        command = module_command("rkp.inspect_usdz", args.id)
        if args.json:
            command.append("--json")
        return run(command)
    if args.command == "verify-asset":
        return run_verify_asset(args)
    if args.command == "accept-asset":
        return run(module_command("rkp.accept_asset", "--id", args.id, "--screenshot", args.screenshot))

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
