#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from rkp.cli import module_command, package_env
from rkp.new_asset import DEFAULT_BUDGETS, snake_case
from rkp.rkp_project import ProjectPaths, load_project


PROJECT = load_project()


PALETTES = {
    "red": ((0.95, 0.12, 0.10, 1.0), (1.0, 0.82, 0.72, 1.0)),
    "blue": ((0.12, 0.42, 0.95, 1.0), (0.72, 0.88, 1.0, 1.0)),
    "green": ((0.12, 0.72, 0.32, 1.0), (0.76, 1.0, 0.82, 1.0)),
    "yellow": ((1.0, 0.78, 0.12, 1.0), (1.0, 0.95, 0.64, 1.0)),
    "orange": ((1.0, 0.42, 0.12, 1.0), (1.0, 0.76, 0.52, 1.0)),
    "purple": ((0.54, 0.22, 0.86, 1.0), (0.86, 0.74, 1.0, 1.0)),
    "gray": ((0.36, 0.40, 0.42, 1.0), (0.72, 0.76, 0.76, 1.0)),
}

ARCHETYPE_KEYWORDS: dict[str, list[str]] = {
    "drone":      ["drone", "flying", "quadcopter", "rotor", "hover"],
    "tower":      ["tower", "turret", "pillar", "beacon", "post"],
    "crate":      ["crate", "box", "container", "pickup", "supply"],
    "projectile": ["projectile", "bullet", "orb", "ball", "shot"],
    "target":     ["target", "bullseye", "ring", "board"],
}

_ARCHETYPE_PRIORITY = ["drone", "tower", "crate", "projectile", "target"]


def infer_palette(prompt: str) -> tuple[str, tuple[float, ...], tuple[float, ...]]:
    lower = prompt.lower()
    for name, colors in PALETTES.items():
        if name in lower:
            return name, colors[0], colors[1]
    return "red", PALETTES["red"][0], PALETTES["red"][1]


def infer_archetype(prompt: str) -> str | None:
    lower = prompt.lower()
    for archetype in _ARCHETYPE_PRIORITY:
        for keyword in ARCHETYPE_KEYWORDS[archetype]:
            if keyword in lower:
                return archetype
    return None


def blender_template(asset_id: str, asset_type: str, prompt: str, archetype: str | None) -> str:
    palette_name, primary, secondary = infer_palette(prompt)
    prompt_json = json.dumps(prompt)
    primary_json = json.dumps(primary)
    secondary_json = json.dumps(secondary)
    archetype_repr = repr(archetype)

    return f'''import json
from pathlib import Path

import math
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
ASSET_TYPE = "{asset_type}"
PROMPT = {prompt_json}
ARCHETYPE = {archetype_repr}
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

            if ARCHETYPE == "target" or (ARCHETYPE is None and ASSET_TYPE == "gameplay_target"):
                ring = int(radius * 18)
                color = PRIMARY if ring % 2 == 0 else SECONDARY
                if radius < 0.08:
                    color = (1.0, 1.0, 1.0, 1.0)
                elif radius > 0.48:
                    color = (0.04, 0.04, 0.04, 1.0)
            elif ARCHETYPE == "drone":
                sector = int((math.atan2(dy, dx) / (2 * math.pi) + 0.5) * 8)
                color = PRIMARY if sector % 2 == 0 else SECONDARY
            elif ARCHETYPE == "tower":
                band = int(v * 8)
                color = PRIMARY if band % 2 == 0 else SECONDARY
            elif ARCHETYPE == "crate":
                in_seam = (x % 128) < 4 or (y % 128) < 4
                color = (0.06, 0.06, 0.06, 1.0) if in_seam else PRIMARY
            elif ARCHETYPE == "projectile" or (ARCHETYPE is None and ASSET_TYPE == "projectile"):
                color = PRIMARY
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


def join_and_uv(parts):
    """Join parts into one object, Smart UV Project, rename UV layer to 'st'."""
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    if len(parts) > 1:
        bpy.ops.object.join()
    obj = bpy.context.active_object
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    if obj.data.uv_layers:
        obj.data.uv_layers[0].name = "st"
    return obj


def make_drone_parts():
    parts = []
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.12, location=(0, 0, 0))
    parts.append(bpy.context.active_object)
    for angle_deg in (0, 90, 180, 270):
        rad = math.radians(angle_deg)
        arm_cx = math.cos(rad) * 0.14
        arm_cy = math.sin(rad) * 0.14
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.018, depth=0.28, location=(arm_cx, arm_cy, 0))
        arm = bpy.context.active_object
        arm.rotation_euler[2] = rad + math.pi / 2
        parts.append(arm)
        tip_x = math.cos(rad) * 0.28
        tip_y = math.sin(rad) * 0.28
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.085, depth=0.008, location=(tip_x, tip_y, 0.018))
        parts.append(bpy.context.active_object)
    return parts


def make_tower_parts():
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.12, depth=0.48, location=(0, 0, 0.24))
    parts.append(bpy.context.active_object)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.072, depth=0.22, location=(0, 0, 0.59))
    parts.append(bpy.context.active_object)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.18, depth=0.034, location=(0, 0, 0.72))
    parts.append(bpy.context.active_object)
    return parts


def make_crate_parts():
    bpy.ops.mesh.primitive_cube_add(size=0.40, location=(0, 0, 0.20))
    obj = bpy.context.active_object
    mod = obj.modifiers.new("bevel", "BEVEL")
    mod.width = 0.018
    mod.segments = 2
    bpy.ops.object.modifier_apply(modifier="bevel")
    return [obj]


def make_asset(material):
    if ARCHETYPE == "drone":
        obj = join_and_uv(make_drone_parts())
    elif ARCHETYPE == "tower":
        obj = join_and_uv(make_tower_parts())
    elif ARCHETYPE == "crate":
        obj = join_and_uv(make_crate_parts())
    elif ARCHETYPE == "projectile" or (ARCHETYPE is None and ASSET_TYPE == "projectile"):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.06, location=(0, 0, 0.06))
        obj = join_and_uv([bpy.context.active_object])
    elif ASSET_TYPE == "environment":
        mesh = make_quad_mesh(3.2, 3.2, vertical=False)
        obj = bpy.data.objects.new(ASSET_ID, mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
    else:
        mesh = make_quad_mesh(0.52, 0.52, vertical=True)
        obj = bpy.data.objects.new(ASSET_ID, mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

    obj.name = ASSET_ID
    obj.data.materials.clear()
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.material_index = 0
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
    obj = make_asset(material)
    export_usdz(obj)
    print(f"exported {{USDZ_PATH}} (archetype={{ARCHETYPE}}, prompt={{PROMPT}})")


if __name__ == "__main__":
    main()
'''


def append_prompt_to_brief(
    asset_id: str,
    prompt: str,
    asset_type: str,
    archetype: str | None,
    project: ProjectPaths = PROJECT,
) -> None:
    brief_path = project.docs_assets_dir / f"{asset_id}.md"
    if not brief_path.exists():
        return
    text = brief_path.read_text(encoding="utf-8")
    if "## Prompt Source" in text:
        return
    archetype_line = f"- Inferred archetype: `{archetype}`\n" if archetype else ""
    text += f"""
## Prompt Source

```text
{prompt}
```

## Prompt Pipeline Notes

{archetype_line}- Generated through `rkp prompt-asset {asset_id} --type {asset_type} --prompt ...`.
- Treat the Blender script as a first procedural draft, not final art direction.
- Build creates USDZ; acceptance still requires simulator screenshot evidence.
"""
    brief_path.write_text(text, encoding="utf-8")


def update_manifest_prompt_metadata(
    asset_id: str,
    prompt: str,
    archetype: str | None,
    project: ProjectPaths = PROJECT,
) -> None:
    manifest = json.loads(project.manifest.read_text(encoding="utf-8"))
    for asset in manifest.get("assets", []):
        if asset.get("id") == asset_id:
            asset["prompt"] = prompt
            asset["archetype"] = archetype
            notes = asset.get("notes", "")
            note = f" Prompt-backed draft; archetype={archetype or 'type-default'}."
            if note.strip() not in notes:
                asset["notes"] = (notes.rstrip() + note).strip()
            break
    project.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_blender_script(
    asset_id: str,
    asset_type: str,
    prompt: str,
    archetype: str | None,
    force: bool,
    project: ProjectPaths = PROJECT,
) -> Path:
    project.blender_dir.mkdir(parents=True, exist_ok=True)
    script_path = project.blender_dir / f"create_{asset_id}.py"
    if script_path.exists() and not force:
        raise FileExistsError(f"Blender script already exists: {project.rel(script_path)}")
    script_path.write_text(blender_template(asset_id, asset_type, prompt, archetype), encoding="utf-8")
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

    archetype = infer_archetype(args.prompt)

    new_asset_result = subprocess.run(
        module_command("rkp.new_asset", "--id", asset_id, "--type", args.type),
        cwd=PROJECT.root,
        env=package_env(),
    )
    if new_asset_result.returncode not in (0, 1):
        return new_asset_result.returncode
    if new_asset_result.returncode == 1:
        print(f"asset already exists, updating prompt script: {asset_id}")

    try:
        script_path = write_blender_script(
            asset_id,
            args.type,
            args.prompt,
            archetype,
            force=args.force or new_asset_result.returncode == 0,
        )
    except FileExistsError as exc:
        print(f"error: {exc}. Use --force to replace it.", file=sys.stderr)
        return 1

    append_prompt_to_brief(asset_id, args.prompt, args.type, archetype)
    update_manifest_prompt_metadata(asset_id, args.prompt, archetype)

    archetype_label = archetype or "type-default"
    print(f"prompt asset ready: {asset_id} (archetype: {archetype_label})")
    print(f"- prompt: {args.prompt}")
    print(f"- blender script: {PROJECT.rel(script_path)}")
    print(f"- next: rkp build-asset {asset_id}")

    if args.build:
        return subprocess.run(
            module_command("rkp.build_asset", "--id", asset_id),
            cwd=PROJECT.root,
            env=package_env(),
        ).returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
