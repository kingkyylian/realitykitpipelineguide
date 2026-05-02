#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "Tools" / "asset_manifest.json"

DEFAULT_BUDGETS = {
    "gameplay_target": {"maxTriangles": 1500, "maxTextureSize": 1024},
    "environment": {"maxTriangles": 1200, "maxTextureSize": 1024},
    "prop": {"maxTriangles": 1000, "maxTextureSize": 1024},
    "projectile": {"maxTriangles": 400, "maxTextureSize": 512},
}


def snake_case(value: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.lower())).strip("_")


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def write_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def create_brief(asset_id: str, asset_type: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        return

    output.write_text(
        f"""# Asset Brief: {asset_id}

## Purpose

Gameplay purpose:

## Runtime Contract

- Asset id: `{asset_id}`
- Type: `{asset_type}`
- Runtime USDZ path: `Assets/Imported/{asset_id}.usdz`
- Fallback behavior:
- Collision expectation:

## Blender Contract

- Approximate size in meters:
- Origin/pivot:
- Forward/up orientation:
- Triangle budget:
- Texture budget:
- UV primvar:
- Material count:

## Acceptance Criteria

- [ ] USDZ exported to `Assets/Imported/{asset_id}.usdz`.
- [ ] `Tools/asset_manifest.json` status changed from `planned` to `imported`.
- [ ] `make doctor` passes without new errors.
- [ ] `make release-check` passes.
- [ ] Simulator screenshot captured if visual.
- [ ] `Docs/WORKLOG.md` lesson added.
""",
        encoding="utf-8",
    )


def create_blender_stub(asset_id: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        return

    output.write_text(
        f'''from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
IMPORTED_DIR = ROOT / "Assets" / "Imported"
SOURCE_DIR = ROOT / "Assets" / "Source"
TEXTURE_DIR = ROOT / "Assets" / "Textures"

ASSET_ID = "{asset_id}"
BLEND_PATH = SOURCE_DIR / f"{{ASSET_ID}}.blend"
USDZ_PATH = IMPORTED_DIR / f"{{ASSET_ID}}.usdz"


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_placeholder():
    bpy.ops.mesh.primitive_cube_add(size=0.4, location=(0, 0, 0.2))
    obj = bpy.context.object
    obj.name = ASSET_ID

    material = bpy.data.materials.new(f"mat_{{ASSET_ID}}")
    material.diffuse_color = (0.8, 0.1, 0.1, 1.0)
    obj.data.materials.append(material)
    return obj


def export_usdz(obj):
    IMPORTED_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.wm.usd_export(
        filepath=str(USDZ_PATH),
        selected_objects_only=True,
        export_textures=True,
        evaluation_mode="RENDER",
    )


def main():
    reset_scene()
    obj = make_placeholder()
    export_usdz(obj)
    print(f"exported {{USDZ_PATH}}")


if __name__ == "__main__":
    main()
''',
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a new RealityKit pipeline asset.")
    parser.add_argument("--id", required=True, help="Asset id in snake_case, for example enemy_drone")
    parser.add_argument("--type", default="prop", choices=sorted(DEFAULT_BUDGETS), help="Asset type")
    parser.add_argument("--triangles", type=int, help="Triangle budget override")
    parser.add_argument("--texture", type=int, help="Texture size budget override")
    args = parser.parse_args()

    asset_id = snake_case(args.id)
    if asset_id != args.id:
        print(f"error: asset id must already be snake_case; suggested id: {asset_id}", file=sys.stderr)
        return 2

    manifest = load_manifest()
    assets = manifest.setdefault("assets", [])
    if any(asset.get("id") == asset_id for asset in assets):
        print(f"error: asset id already exists: {asset_id}", file=sys.stderr)
        return 1
    if any(asset.get("file") == f"{asset_id}.usdz" for asset in assets):
        print(f"error: asset file already exists in manifest: {asset_id}.usdz", file=sys.stderr)
        return 1

    budgets = DEFAULT_BUDGETS[args.type]
    entry = {
        "id": asset_id,
        "file": f"{asset_id}.usdz",
        "type": args.type,
        "status": "planned",
        "maxTriangles": args.triangles or budgets["maxTriangles"],
        "maxTextureSize": args.texture or budgets["maxTextureSize"],
        "textureMaps": ["baseColor"],
        "notes": "Scaffolded asset. Fill in size, origin, UV/material, export, simulator screenshot, and worklog notes before marking imported.",
    }
    assets.append(entry)
    write_manifest(manifest)

    create_brief(asset_id, args.type, ROOT / "Docs" / "assets" / f"{asset_id}.md")
    create_blender_stub(asset_id, ROOT / "Tools" / "blender" / f"create_{asset_id}.py")
    (ROOT / "Assets" / "Imported").mkdir(parents=True, exist_ok=True)
    (ROOT / "Assets" / "Textures").mkdir(parents=True, exist_ok=True)

    print(f"scaffolded asset: {asset_id}")
    print(f"- manifest: Tools/asset_manifest.json")
    print(f"- brief: Docs/assets/{asset_id}.md")
    print(f"- blender stub: Tools/blender/create_{asset_id}.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
