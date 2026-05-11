from __future__ import annotations

import math
from pathlib import Path

import bpy

ASSET_ID = "material_response_targets"
ROOT = Path(__file__).resolve().parents[2]
IMPORTED_DIR = ROOT / "Assets" / "Imported"
SOURCE_DIR = ROOT / "Assets" / "Source"
TEXTURE_DIR = ROOT / "Assets" / "Textures"
USDZ_PATH = IMPORTED_DIR / f"{ASSET_ID}.usdz"
BLEND_PATH = SOURCE_DIR / f"{ASSET_ID}.blend"
BASECOLOR_PATH = TEXTURE_DIR / f"{ASSET_ID}_basecolor.png"
ROUGHNESS_PATH = TEXTURE_DIR / f"{ASSET_ID}_roughness.png"


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def write_texture(path: Path, roughness: bool = False) -> bpy.types.Image:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = bpy.data.images.new(path.stem, width=512, height=512)
    pixels: list[float] = []

    for y in range(512):
        for x in range(512):
            u = (x + 0.5) / 512
            v = (y + 0.5) / 512
            dx = u - 0.5
            dy = v - 0.5
            radius = math.sqrt(dx * dx + dy * dy)

            if roughness:
                stripe = int(u * 10) % 2 == 0
                value = 0.18 if stripe else 0.88
                pixels.extend([value, value, value, 1.0])
            elif radius < 0.13:
                pixels.extend([0.92, 0.07, 0.04, 1.0])
            elif radius < 0.27:
                pixels.extend([0.96, 0.94, 0.88, 1.0])
            elif radius < 0.41:
                pixels.extend([0.74, 0.04, 0.03, 1.0])
            else:
                pixels.extend([0.05, 0.055, 0.06, 1.0])

    image.pixels[:] = pixels
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    image.save()
    return image


def make_material(
    name: str,
    base_image: bpy.types.Image,
    roughness_value: float,
    roughness_image: bpy.types.Image | None = None,
    metallic_value: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    texture = nodes.new(type="ShaderNodeTexImage")
    texture.image = base_image
    uv_map = nodes.new(type="ShaderNodeUVMap")
    uv_map.uv_map = "st"
    links = material.node_tree.links
    links.new(uv_map.outputs["UV"], texture.inputs["Vector"])
    links.new(texture.outputs["Color"], principled.inputs["Base Color"])
    principled.inputs["Roughness"].default_value = roughness_value
    principled.inputs["Metallic"].default_value = metallic_value

    if roughness_image is not None:
        roughness = nodes.new(type="ShaderNodeTexImage")
        roughness.image = roughness_image
        roughness_uv = nodes.new(type="ShaderNodeUVMap")
        roughness_uv.uv_map = "st"
        links.new(roughness_uv.outputs["UV"], roughness.inputs["Vector"])
        links.new(roughness.outputs["Color"], principled.inputs["Roughness"])

    return material


def create_panel(name: str, x_offset: float, material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.28, depth=0.035, location=(x_offset, 0, 0))
    panel = bpy.context.object
    panel.name = name
    panel.data.name = f"{name}_mesh"
    panel.data.materials.append(material)

    uv_layer = panel.data.uv_layers.new(name="st") if not panel.data.uv_layers else panel.data.uv_layers[0]
    uv_layer.name = "st"
    for polygon in panel.data.polygons:
        for loop_index in polygon.loop_indices:
            vertex = panel.data.vertices[panel.data.loops[loop_index].vertex_index].co
            uv_layer.data[loop_index].uv = ((vertex.x - x_offset) / 0.56 + 0.5, vertex.y / 0.56 + 0.5)

    return panel


def main() -> None:
    reset_scene()
    IMPORTED_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)

    base_image = write_texture(BASECOLOR_PATH)
    roughness_image = write_texture(ROUGHNESS_PATH, roughness=True)
    matte = make_material("matte_value_roughness_088", base_image, 0.88)
    glossy = make_material("glossy_value_roughness_018", base_image, 0.18)
    mapped = make_material("mapped_roughness_bands", base_image, 0.50, roughness_image)
    metallic = make_material("metallic_value_roughness_018", base_image, 0.18, metallic_value=1.0)

    panels = [
        create_panel("matte_value_panel", -0.72, matte),
        create_panel("glossy_value_panel", -0.24, glossy),
        create_panel("roughness_map_panel", 0.24, mapped),
        create_panel("metallic_value_panel", 0.72, metallic),
    ]

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    bpy.ops.object.select_all(action="DESELECT")
    for panel in panels:
        panel.select_set(True)
    bpy.context.view_layer.objects.active = panels[0]
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
    print(f"exported {USDZ_PATH}")


if __name__ == "__main__":
    main()
