#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

from rkp.asset_manifest import asset_usdz_path, expected_texture_name, load_asset, texture_map_names
from rkp.prompt_asset import infer_palette
from rkp.rkp_project import load_project

PROJECT = load_project()


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixels[y * width + x])

    data = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            png_chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(data)


def rgba_to_byte(color: tuple[float, ...]) -> tuple[int, int, int, int]:
    return tuple(max(0, min(255, round(channel * 255))) for channel in color)  # type: ignore[return-value]


def make_texture(asset: dict, path: Path) -> None:
    prompt = asset.get("prompt", "")
    archetype = asset.get("archetype")
    asset_type = asset.get("type", "")
    _, primary, secondary = infer_palette(prompt)
    primary_rgba = rgba_to_byte(primary)
    secondary_rgba = rgba_to_byte(secondary)
    dark = (15, 15, 15, 255)
    white = (255, 255, 255, 255)
    pixels: list[tuple[int, int, int, int]] = []

    for y in range(512):
        for x in range(512):
            u = (x + 0.5) / 512
            v = (y + 0.5) / 512
            dx = u - 0.5
            dy = v - 0.5
            radius = math.sqrt(dx * dx + dy * dy)

            if archetype == "drone":
                sector = int((math.atan2(dy, dx) / (2 * math.pi) + 0.5) * 8)
                color = primary_rgba if sector % 2 == 0 else secondary_rgba
                if abs(dx) < 0.045 or abs(dy) < 0.045:
                    color = dark
                if radius < 0.10:
                    color = white
                if 0.11 < radius < 0.19:
                    color = primary_rgba
            elif archetype == "target" or asset_type in {"gameplay_target", "material_response_showcase"}:
                ring = int(radius * 18)
                color = primary_rgba if ring % 2 == 0 else secondary_rgba
                if radius < 0.08:
                    color = white
                elif radius > 0.48:
                    color = dark
                witness_u = (u - 0.75) / 0.12
                witness_v = (v - 0.27) / 0.12
                if asset_type == "material_response_showcase" and witness_u * witness_u + witness_v * witness_v <= 1.0:
                    color = (178, 184, 188, 255)
            else:
                stripe = (x // 48 + y // 48) % 2 == 0
                color = primary_rgba if stripe else secondary_rgba
            pixels.append(color)

    path.parent.mkdir(parents=True, exist_ok=True)
    write_png(path, 512, 512, pixels)


def make_roughness_texture(path: Path) -> None:
    pixels: list[tuple[int, int, int, int]] = []
    for y in range(512):
        for x in range(512):
            u = (x + 0.5) / 512
            v = (y + 0.5) / 512
            band = int(u * 8) % 2 == 0
            center_lane = 0.43 <= u <= 0.57
            upper_witness = 0.60 <= u <= 0.82 and 0.14 <= v <= 0.36
            value = 8 if band or center_lane or upper_witness else 248
            pixels.append((value, value, value, 255))
    path.parent.mkdir(parents=True, exist_ok=True)
    write_png(path, 512, 512, pixels)


def make_texture_map(asset: dict, map_name: str, path: Path) -> None:
    if map_name == "roughness":
        make_roughness_texture(path)
        return
    make_texture(asset, path)


class MeshBuilder:
    def __init__(self) -> None:
        self.points: list[tuple[float, float, float]] = []
        self.triangles: list[tuple[int, int, int]] = []

    def add_box(self, cx: float, cy: float, cz: float, sx: float, sy: float, sz: float) -> None:
        x0, x1 = cx - sx / 2, cx + sx / 2
        y0, y1 = cy - sy / 2, cy + sy / 2
        z0, z1 = cz - sz / 2, cz + sz / 2
        base = len(self.points)
        self.points.extend(
            [
                (x0, y0, z0),
                (x1, y0, z0),
                (x1, y1, z0),
                (x0, y1, z0),
                (x0, y0, z1),
                (x1, y0, z1),
                (x1, y1, z1),
                (x0, y1, z1),
            ]
        )
        faces = [
            (0, 1, 2, 3),
            (4, 7, 6, 5),
            (0, 4, 5, 1),
            (1, 5, 6, 2),
            (2, 6, 7, 3),
            (3, 7, 4, 0),
        ]
        for a, b, c, d in faces:
            self.triangles.append((base + a, base + b, base + c))
            self.triangles.append((base + a, base + c, base + d))

    def add_cylinder(self, cx: float, cy: float, cz: float, radius: float, depth: float, segments: int = 24) -> None:
        bottom_center = len(self.points)
        top_center = bottom_center + 1
        self.points.append((cx, cy, cz - depth / 2))
        self.points.append((cx, cy, cz + depth / 2))
        bottom: list[int] = []
        top: list[int] = []
        for index in range(segments):
            angle = 2 * math.pi * index / segments
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            bottom.append(len(self.points))
            self.points.append((x, y, cz - depth / 2))
            top.append(len(self.points))
            self.points.append((x, y, cz + depth / 2))
        for index in range(segments):
            nxt = (index + 1) % segments
            self.triangles.append((bottom_center, bottom[nxt], bottom[index]))
            self.triangles.append((top_center, top[index], top[nxt]))
            self.triangles.append((bottom[index], bottom[nxt], top[nxt]))
            self.triangles.append((bottom[index], top[nxt], top[index]))

    def add_ellipsoid(
        self,
        cx: float,
        cy: float,
        cz: float,
        rx: float,
        ry: float,
        rz: float,
        segments: int = 16,
        rings: int = 8,
    ) -> None:
        top = len(self.points)
        self.points.append((cx, cy, cz + rz))
        ring_indices: list[list[int]] = []
        for ring in range(1, rings):
            theta = math.pi * ring / rings
            z = cz + math.cos(theta) * rz
            radius = math.sin(theta)
            row: list[int] = []
            for segment in range(segments):
                angle = 2 * math.pi * segment / segments
                row.append(len(self.points))
                self.points.append((cx + math.cos(angle) * rx * radius, cy + math.sin(angle) * ry * radius, z))
            ring_indices.append(row)
        bottom = len(self.points)
        self.points.append((cx, cy, cz - rz))

        first_ring = ring_indices[0]
        for segment in range(segments):
            nxt = (segment + 1) % segments
            self.triangles.append((top, first_ring[segment], first_ring[nxt]))

        for ring_index in range(len(ring_indices) - 1):
            current = ring_indices[ring_index]
            next_ring = ring_indices[ring_index + 1]
            for segment in range(segments):
                nxt = (segment + 1) % segments
                self.triangles.append((current[segment], next_ring[segment], next_ring[nxt]))
                self.triangles.append((current[segment], next_ring[nxt], current[nxt]))

        last_ring = ring_indices[-1]
        for segment in range(segments):
            nxt = (segment + 1) % segments
            self.triangles.append((bottom, last_ring[nxt], last_ring[segment]))


def drone_mesh() -> MeshBuilder:
    mesh = MeshBuilder()
    mesh.add_box(0, 0, 0, 0.34, 0.22, 0.08)
    mesh.add_box(0, 0, 0.005, 0.86, 0.045, 0.045)
    mesh.add_box(0, 0, 0.005, 0.045, 0.62, 0.045)
    for x, y in [(-0.43, 0), (0.43, 0), (0, -0.31), (0, 0.31)]:
        mesh.add_cylinder(x, y, 0.02, 0.12, 0.035)
        mesh.add_cylinder(x, y, 0.055, 0.06, 0.018)
    return mesh


def target_mesh() -> MeshBuilder:
    mesh = MeshBuilder()
    mesh.add_cylinder(0, 0, 0, 0.32, 0.04, 48)
    return mesh


def material_response_meshes() -> list[tuple[str, MeshBuilder, str]]:
    meshes: list[tuple[str, MeshBuilder, str]] = []
    for name, x_offset, material_name in [
        ("matte_value_panel", -0.62, "mat_matte_value"),
        ("glossy_value_panel", 0.0, "mat_glossy_value"),
        ("roughness_map_panel", 0.62, "mat_roughness_map"),
    ]:
        mesh = MeshBuilder()
        mesh.add_cylinder(x_offset, 0, 0, 0.28, 0.035, 48)
        mesh.add_ellipsoid(x_offset + 0.11, 0.12, 0.045, 0.06, 0.06, 0.04)
        meshes.append((name, mesh, material_name))
    return meshes


def list_value(values: list[object]) -> str:
    return "[" + ", ".join(str(value).replace("'", "") for value in values) + "]"


def mesh_payload(mesh: MeshBuilder) -> dict[str, str]:
    min_x = min(point[0] for point in mesh.points)
    max_x = max(point[0] for point in mesh.points)
    min_y = min(point[1] for point in mesh.points)
    max_y = max(point[1] for point in mesh.points)
    min_z = min(point[2] for point in mesh.points)
    max_z = max(point[2] for point in mesh.points)
    span_x = max(max_x - min_x, 0.001)
    span_y = max(max_y - min_y, 0.001)
    st_values = [((point[0] - min_x) / span_x, (point[1] - min_y) / span_y) for point in mesh.points]
    indices = [index for triangle in mesh.triangles for index in triangle]
    return {
        "points": list_value(mesh.points),
        "counts": list_value([3] * len(mesh.triangles)),
        "face_indices": list_value(indices),
        "st": list_value(st_values),
        "extent": list_value([(min_x, min_y, min_z), (max_x, max_y, max_z)]),
    }


def mesh_block(name: str, mesh: MeshBuilder, material_name: str) -> str:
    payload = mesh_payload(mesh)
    return f'''        def Mesh "{name}" (
            active = true
            prepend apiSchemas = ["MaterialBindingAPI"]
        )
        {{
            uniform bool doubleSided = 1
            float3[] extent = {payload["extent"]}
            int[] faceVertexCounts = {payload["counts"]}
            int[] faceVertexIndices = {payload["face_indices"]}
            rel material:binding = </root/_materials/{material_name}>
            point3f[] points = {payload["points"]}
            texCoord2f[] primvars:st = {payload["st"]} (
                interpolation = "faceVarying"
            )
            int[] primvars:st:indices = {payload["face_indices"]}
            uniform token subdivisionScheme = "none"
        }}'''


def material_block(name: str, basecolor_texture: str, roughness_value: float, roughness_texture: str | None = None) -> str:
    roughness_input = (
        f"float inputs:roughness.connect = </root/_materials/{name}/Roughness_Texture.outputs:r>"
        if roughness_texture
        else f"float inputs:roughness = {roughness_value}"
    )
    roughness_shader = ""
    if roughness_texture:
        roughness_shader = f'''

            def Shader "Roughness_Texture"
            {{
                uniform token info:id = "UsdUVTexture"
                asset inputs:file = @./textures/{roughness_texture}@
                token inputs:sourceColorSpace = "raw"
                float2 inputs:st.connect = </root/_materials/{name}/uvmap.outputs:result>
                token inputs:wrapS = "repeat"
                token inputs:wrapT = "repeat"
                float outputs:r
            }}'''
    return f'''        def Material "{name}"
        {{
            token outputs:surface.connect = </root/_materials/{name}/Preview.outputs:surface>

            def Shader "Preview"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor.connect = </root/_materials/{name}/Image_Texture.outputs:rgb>
                float inputs:metallic = 0
                {roughness_input}
                token outputs:surface
            }}

            def Shader "Image_Texture"
            {{
                uniform token info:id = "UsdUVTexture"
                asset inputs:file = @./textures/{basecolor_texture}@
                token inputs:sourceColorSpace = "sRGB"
                float2 inputs:st.connect = </root/_materials/{name}/uvmap.outputs:result>
                token inputs:wrapS = "repeat"
                token inputs:wrapT = "repeat"
                float3 outputs:rgb
            }}{roughness_shader}

            def Shader "uvmap"
            {{
                uniform token info:id = "UsdPrimvarReader_float2"
                string inputs:varname = "st"
                float2 outputs:result
            }}
        }}'''


def write_material_response_usda(asset: dict, texture_names: dict[str, str], output: Path) -> None:
    basecolor = texture_names["baseColor"]
    roughness = texture_names.get("roughness")
    meshes = "\n\n".join(mesh_block(name, mesh, material_name) for name, mesh, material_name in material_response_meshes())
    materials = "\n\n".join(
        [
            material_block("mat_matte_value", basecolor, 0.98),
            material_block("mat_glossy_value", basecolor, 0.04),
            material_block("mat_roughness_map", basecolor, 0.50, roughness),
        ]
    )
    output.write_text(
        f'''#usda 1.0
(
    defaultPrim = "root"
    doc = "RKP direct USDZ material response fallback builder"
    metersPerUnit = 1
    upAxis = "Z"
)

def Xform "root"
{{
    def Xform "{asset["id"]}"
    {{
{meshes}
    }}

    def Scope "_materials"
    {{
{materials}
    }}
}}
''',
        encoding="utf-8",
    )


def write_usda(asset: dict, texture_names: dict[str, str], output: Path) -> None:
    if asset.get("type") == "material_response_showcase":
        write_material_response_usda(asset, texture_names, output)
        return

    archetype = asset.get("archetype")
    mesh = drone_mesh() if archetype == "drone" else target_mesh()
    payload = mesh_payload(mesh)
    texture_name = texture_names["baseColor"]

    output.write_text(
        f'''#usda 1.0
(
    defaultPrim = "root"
    doc = "RKP direct USDZ fallback builder"
    metersPerUnit = 1
    upAxis = "Z"
)

def Xform "root"
{{
    def Xform "{asset["id"]}"
    {{
        def Mesh "Mesh" (
            active = true
            prepend apiSchemas = ["MaterialBindingAPI"]
        )
        {{
            uniform bool doubleSided = 1
            float3[] extent = {payload["extent"]}
            int[] faceVertexCounts = {payload["counts"]}
            int[] faceVertexIndices = {payload["face_indices"]}
            rel material:binding = </root/_materials/mat_textured>
            point3f[] points = {payload["points"]}
            texCoord2f[] primvars:st = {payload["st"]} (
                interpolation = "faceVarying"
            )
            int[] primvars:st:indices = {payload["face_indices"]}
            uniform token subdivisionScheme = "none"
        }}
    }}

    def Scope "_materials"
    {{
        def Material "mat_textured"
        {{
            token outputs:surface.connect = </root/_materials/mat_textured/Preview.outputs:surface>

            def Shader "Preview"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor.connect = </root/_materials/mat_textured/Image_Texture.outputs:rgb>
                float inputs:metallic = 0
                float inputs:roughness = 0.7
                token outputs:surface
            }}

            def Shader "Image_Texture"
            {{
                uniform token info:id = "UsdUVTexture"
                asset inputs:file = @./textures/{texture_name}@
                token inputs:sourceColorSpace = "sRGB"
                float2 inputs:st.connect = </root/_materials/mat_textured/uvmap.outputs:result>
                token inputs:wrapS = "repeat"
                token inputs:wrapT = "repeat"
                float3 outputs:rgb
            }}

            def Shader "uvmap"
            {{
                uniform token info:id = "UsdPrimvarReader_float2"
                string inputs:varname = "st"
                float2 outputs:result
            }}
        }}
    }}
}}
''',
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a simple USDZ asset without Blender when Blender is unavailable.")
    parser.add_argument("--id", required=True, help="Asset id from Tools/asset_manifest.json")
    args = parser.parse_args()

    asset = load_asset(args.id)
    if asset is None:
        print(f"error: unknown asset id: {args.id}", file=sys.stderr)
        return 1

    usdzip = shutil.which("usdzip")
    if usdzip is None:
        print("error: usdzip not found; direct USDZ fallback cannot run", file=sys.stderr)
        return 127

    output_path = asset_usdz_path(asset, PROJECT)
    texture_names = {
        map_name: expected_name
        for map_name in texture_map_names(asset)
        if (expected_name := expected_texture_name(asset, map_name)) is not None
    }
    if "baseColor" not in texture_names:
        print("error: direct USDZ fallback requires a baseColor texture map", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix=f"rkp_{asset['id']}_") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        usda_path = temp_dir / f"{asset['id']}.usda"
        for map_name, texture_name in texture_names.items():
            texture_path = temp_dir / "textures" / texture_name
            make_texture_map(asset, map_name, texture_path)
            project_texture_path = PROJECT.textures_dir / texture_name
            project_texture_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(texture_path, project_texture_path)
        write_usda(asset, texture_names, usda_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [usdzip, "--arkitAsset", str(usda_path), str(output_path)]
        print("running:", " ".join(command), flush=True)
        result = subprocess.run(command, cwd=temp_dir)
        if result.returncode != 0:
            return result.returncode

    if not output_path.exists() or output_path.stat().st_size <= 0:
        print(f"error: expected USDZ was not created: {PROJECT.rel(output_path)}", file=sys.stderr)
        return 1

    print(f"fallback asset built: {PROJECT.rel(output_path)} ({output_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
