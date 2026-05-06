#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from rkp.rkp_project import ProjectPaths, load_project

PROJECT = load_project()

DEFAULT_BUDGETS = {
    "gameplay_target": {"maxTriangles": 1500, "maxTextureSize": 1024},
    "environment": {"maxTriangles": 1200, "maxTextureSize": 1024},
    "prop": {"maxTriangles": 1000, "maxTextureSize": 1024},
    "projectile": {"maxTriangles": 400, "maxTextureSize": 512},
}


def snake_case(value: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.lower())).strip("_")


def load_manifest(project: ProjectPaths = PROJECT) -> dict:
    return json.loads(project.manifest.read_text(encoding="utf-8"))


def write_manifest(manifest: dict, project: ProjectPaths = PROJECT) -> None:
    project.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
        f'''import json
from pathlib import Path

import bpy


def find_project_root():
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        current = start.resolve()
        for candidate in (current, *current.parents):
            if (candidate / "rkp.json").exists():
                return candidate
    raise FileNotFoundError("could not find rkp.json")


ROOT = find_project_root()
CONFIG = json.loads((ROOT / "rkp.json").read_text(encoding="utf-8"))
IMPORTED_DIR = ROOT / CONFIG.get("assets_dir", "Assets/Imported")
SOURCE_DIR = ROOT / CONFIG.get("source_dir", "Assets/Source")
TEXTURE_DIR = ROOT / CONFIG.get("textures_dir", "Assets/Textures")

ASSET_ID = "{asset_id}"
TEXTURE_PATH = TEXTURE_DIR / f"{{ASSET_ID}}_basecolor.png"
BLEND_PATH = SOURCE_DIR / f"{{ASSET_ID}}.blend"
USDZ_PATH = IMPORTED_DIR / f"{{ASSET_ID}}.usdz"


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_texture():
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    image = bpy.data.images.new(f"{{ASSET_ID}}_basecolor", width=512, height=512)
    pixels = []
    primary = (0.82, 0.10, 0.08, 1.0)
    secondary = (0.98, 0.78, 0.70, 1.0)
    dark = (0.04, 0.04, 0.04, 1.0)

    for y in range(512):
        for x in range(512):
            stripe = (x // 64 + y // 64) % 2 == 0
            border = x < 12 or x >= 500 or y < 12 or y >= 500
            color = dark if border else (primary if stripe else secondary)
            pixels.extend(color)

    image.pixels = pixels
    image.filepath_raw = str(TEXTURE_PATH)
    image.file_format = "PNG"
    image.save()
    return image


def make_material(image):
    material = bpy.data.materials.new(f"mat_{{ASSET_ID}}")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    texture = nodes.new(type="ShaderNodeTexImage")
    texture.image = image
    uv_map = nodes.new(type="ShaderNodeUVMap")
    uv_map.uv_map = "st"
    links = material.node_tree.links
    links.new(uv_map.outputs["UV"], texture.inputs["Vector"])
    links.new(texture.outputs["Color"], principled.inputs["Base Color"])
    principled.inputs["Roughness"].default_value = 0.74
    principled.inputs["Metallic"].default_value = 0.0
    return material


def make_placeholder(material):
    vertices = [(-0.26, 0, -0.26), (0.26, 0, -0.26), (0.26, 0, 0.26), (-0.26, 0, 0.26)]
    mesh = bpy.data.meshes.new(f"{{ASSET_ID}}_mesh")
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.update()
    uv_layer = mesh.uv_layers.new(name="st")
    for loop_index, uv in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv_layer.data[loop_index].uv = uv

    obj = bpy.data.objects.new(ASSET_ID, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
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
        export_textures_mode="NEW",
        overwrite_textures=True,
        export_materials=True,
        export_uvmaps=True,
        export_normals=True,
        triangulate_meshes=True,
        generate_preview_surface=True,
        root_prim_path="/root",
    )


def main():
    reset_scene()
    image = make_texture()
    material = make_material(image)
    obj = make_placeholder(material)
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

    create_brief(asset_id, args.type, PROJECT.docs_assets_dir / f"{asset_id}.md")
    create_blender_stub(asset_id, PROJECT.blender_dir / f"create_{asset_id}.py")
    PROJECT.assets_dir.mkdir(parents=True, exist_ok=True)
    PROJECT.textures_dir.mkdir(parents=True, exist_ok=True)

    print(f"scaffolded asset: {asset_id}")
    print(f"- manifest: {PROJECT.rel(PROJECT.manifest)}")
    print(f"- brief: {PROJECT.rel(PROJECT.docs_assets_dir / f'{asset_id}.md')}")
    print(f"- blender stub: {PROJECT.rel(PROJECT.blender_dir / f'create_{asset_id}.py')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
