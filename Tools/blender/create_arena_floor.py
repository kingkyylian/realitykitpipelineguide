from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
IMPORTED_DIR = ROOT / "Assets" / "Imported"
SOURCE_DIR = ROOT / "Assets" / "Source"
TEXTURE_DIR = ROOT / "Assets" / "Textures"

ASSET_ID = "arena_floor"
TEXTURE_PATH = TEXTURE_DIR / "arena_floor_basecolor.png"
BLEND_PATH = SOURCE_DIR / "arena_floor.blend"
USDZ_PATH = IMPORTED_DIR / "arena_floor.usdz"


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_texture():
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)

    image = bpy.data.images.new("arena_floor_basecolor", width=512, height=512)
    pixels = []

    for y in range(512):
        for x in range(512):
            grid = x % 64 < 3 or y % 64 < 3
            axis = abs(x - 256) < 3 or abs(y - 256) < 3
            if axis:
                color = (0.90, 0.20, 0.12, 1.0)
            elif grid:
                color = (0.18, 0.22, 0.24, 1.0)
            else:
                color = (0.42, 0.46, 0.43, 1.0)
            pixels.extend(color)

    image.pixels = pixels
    image.filepath_raw = str(TEXTURE_PATH)
    image.file_format = "PNG"
    image.save()
    return image


def make_material(image):
    material = bpy.data.materials.new("mat_arena_floor")
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
    principled.inputs["Roughness"].default_value = 0.92
    principled.inputs["Metallic"].default_value = 0.0

    return material


def make_floor(material):
    mesh = bpy.data.meshes.new(f"{ASSET_ID}_mesh")
    segments = 8
    size = 3.2
    half_size = size / 2
    step = size / segments

    vertices = []
    for y in range(segments + 1):
        for x in range(segments + 1):
            vertices.append((-half_size + x * step, -half_size + y * step, 0.0))

    faces = []
    for y in range(segments):
        for x in range(segments):
            lower_left = y * (segments + 1) + x
            lower_right = lower_left + 1
            upper_left = lower_left + segments + 1
            upper_right = upper_left + 1
            faces.append((lower_left, lower_right, upper_right, upper_left))

    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    uv_layer = mesh.uv_layers.new(name="st")
    for polygon in mesh.polygons:
        for loop_index in polygon.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]
            u = (vertex.co.x + half_size) / size
            v = (vertex.co.y + half_size) / size
            uv_layer.data[loop_index].uv = (u, v)

    obj = bpy.data.objects.new(ASSET_ID, mesh)
    obj.data.materials.append(material)
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
    floor = make_floor(material)
    export_usdz(floor)
    print(f"exported {USDZ_PATH}")


if __name__ == "__main__":
    main()
