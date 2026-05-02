#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from new_asset import DEFAULT_BUDGETS, snake_case


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "Tools" / "blender"
BRIEF_DIR = ROOT / "Docs" / "assets"


PALETTES = {
    "red": ((0.95, 0.12, 0.10, 1.0), (1.0, 0.82, 0.72, 1.0)),
    "blue": ((0.12, 0.42, 0.95, 1.0), (0.72, 0.88, 1.0, 1.0)),
    "green": ((0.12, 0.72, 0.32, 1.0), (0.76, 1.0, 0.82, 1.0)),
    "yellow": ((1.0, 0.78, 0.12, 1.0), (1.0, 0.95, 0.64, 1.0)),
    "orange": ((1.0, 0.42, 0.12, 1.0), (1.0, 0.76, 0.52, 1.0)),
    "purple": ((0.54, 0.22, 0.86, 1.0), (0.86, 0.74, 1.0, 1.0)),
    "gray": ((0.36, 0.40, 0.42, 1.0), (0.72, 0.76, 0.76, 1.0)),
}


def infer_palette(prompt: str) -> tuple[str, tuple[float, ...], tuple[float, ...]]:
    lower = prompt.lower()
    for name, colors in PALETTES.items():
        if name in lower:
            return name, colors[0], colors[1]
    return "red", PALETTES["red"][0], PALETTES["red"][1]


def blender_template(asset_id: str, asset_type: str, prompt: str) -> str:
    palette_name, primary, secondary = infer_palette(prompt)
    prompt_json = json.dumps(prompt)
    primary_json = json.dumps(primary)
    secondary_json = json.dumps(secondary)

    return f'''from pathlib import Path

import math
import bpy


ROOT = Path(__file__).resolve().parents[2]
IMPORTED_DIR = ROOT / "Assets" / "Imported"
SOURCE_DIR = ROOT / "Assets" / "Source"
TEXTURE_DIR = ROOT / "Assets" / "Textures"

ASSET_ID = "{asset_id}"
ASSET_TYPE = "{asset_type}"
PROMPT = {prompt_json}
PALETTE_NAME = "{palette_name}"
PRIMARY = {primary_json}
SECONDARY = {secondary_json}
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

    for y in range(512):
        for x in range(512):
            u = (x + 0.5) / 512
            v = (y + 0.5) / 512
            dx = u - 0.5
            dy = v - 0.5
            radius = math.sqrt(dx * dx + dy * dy)

            if ASSET_TYPE == "gameplay_target":
                ring = int(radius * 18)
                color = PRIMARY if ring % 2 == 0 else SECONDARY
                if radius < 0.08:
                    color = (1.0, 1.0, 1.0, 1.0)
                elif radius > 0.48:
                    color = (0.04, 0.04, 0.04, 1.0)
            elif ASSET_TYPE == "environment":
                grid = x % 64 < 3 or y % 64 < 3
                axis = abs(x - 256) < 3 or abs(y - 256) < 3
                color = PRIMARY if axis else ((0.20, 0.24, 0.25, 1.0) if grid else SECONDARY)
            else:
                stripe = (x // 48 + y // 48) % 2 == 0
                color = PRIMARY if stripe else SECONDARY

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


def make_quad_mesh(width, height, vertical=True):
    half_w = width / 2
    half_h = height / 2
    if vertical:
        vertices = [(-half_w, 0, -half_h), (half_w, 0, -half_h), (half_w, 0, half_h), (-half_w, 0, half_h)]
    else:
        vertices = [(-half_w, -half_h, 0), (half_w, -half_h, 0), (half_w, half_h, 0), (-half_w, half_h, 0)]
    mesh = bpy.data.meshes.new(f"{{ASSET_ID}}_mesh")
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.update()
    uv_layer = mesh.uv_layers.new(name="st")
    for loop_index, uv in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv_layer.data[loop_index].uv = uv
    return mesh


def make_asset(material):
    if ASSET_TYPE == "environment":
        mesh = make_quad_mesh(3.2, 3.2, vertical=False)
        obj = bpy.data.objects.new(ASSET_ID, mesh)
    elif ASSET_TYPE == "projectile":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.06, location=(0, 0, 0.06))
        obj = bpy.context.object
        obj.name = ASSET_ID
        obj.data.uv_layers.new(name="st")
    else:
        mesh = make_quad_mesh(0.52, 0.52, vertical=True)
        obj = bpy.data.objects.new(ASSET_ID, mesh)

    obj.data.materials.append(material)
    if obj.name not in bpy.context.collection.objects:
        bpy.context.collection.objects.link(obj)
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
        export_textures=True,
        evaluation_mode="RENDER",
    )


def main():
    reset_scene()
    image = make_texture()
    material = make_material(image)
    obj = make_asset(material)
    export_usdz(obj)
    print(f"exported {{USDZ_PATH}} from prompt: {{PROMPT}}")


if __name__ == "__main__":
    main()
'''


def append_prompt_to_brief(asset_id: str, prompt: str, asset_type: str) -> None:
    brief_path = BRIEF_DIR / f"{asset_id}.md"
    if not brief_path.exists():
        return
    text = brief_path.read_text(encoding="utf-8")
    if "## Prompt Source" in text:
        return
    text += f"""

## Prompt Source

```text
{prompt}
```

## Prompt Pipeline Notes

- Generated through `python3 Tools/rkp.py prompt-asset {asset_id} --type {asset_type} --prompt ...`.
- Treat the Blender script as a first procedural draft, not final art direction.
- Build creates USDZ; acceptance still requires simulator screenshot evidence.
"""
    brief_path.write_text(text, encoding="utf-8")


def write_blender_script(asset_id: str, asset_type: str, prompt: str, force: bool) -> Path:
    SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    script_path = SCRIPT_DIR / f"create_{asset_id}.py"
    if script_path.exists() and not force:
        raise FileExistsError(f"Blender script already exists: {script_path.relative_to(ROOT)}")
    script_path.write_text(blender_template(asset_id, asset_type, prompt), encoding="utf-8")
    return script_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a prompt-backed RealityKit pipeline asset.")
    parser.add_argument("id", help="Asset id in snake_case")
    parser.add_argument("--prompt", required=True, help="Asset prompt or short art brief")
    parser.add_argument("--type", default="prop", choices=sorted(DEFAULT_BUDGETS), help="Asset type")
    parser.add_argument("--build", action="store_true", help="Run Blender build after generating the script")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing Blender script")
    args = parser.parse_args()

    asset_id = snake_case(args.id)
    if asset_id != args.id:
        print(f"error: asset id must already be snake_case; suggested id: {asset_id}", file=sys.stderr)
        return 2

    new_asset_result = subprocess.run(
        [sys.executable, "Tools/new_asset.py", "--id", asset_id, "--type", args.type],
        cwd=ROOT,
    )
    if new_asset_result.returncode not in (0, 1):
        return new_asset_result.returncode
    if new_asset_result.returncode == 1:
        print(f"asset already exists, updating prompt script: {asset_id}")

    try:
        script_path = write_blender_script(asset_id, args.type, args.prompt, force=args.force or new_asset_result.returncode == 0)
    except FileExistsError as exc:
        print(f"error: {exc}. Use --force to replace it.", file=sys.stderr)
        return 1

    append_prompt_to_brief(asset_id, args.prompt, args.type)
    print(f"prompt asset ready: {asset_id}")
    print(f"- prompt: {args.prompt}")
    print(f"- blender script: {script_path.relative_to(ROOT)}")
    print(f"- next: python3 Tools/rkp.py build-asset {asset_id}")

    if args.build:
        return subprocess.run([sys.executable, "Tools/build_asset.py", "--id", asset_id], cwd=ROOT).returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
