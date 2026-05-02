#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

from prompt_asset import infer_palette


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "Tools" / "asset_manifest.json"


def load_asset(asset_id: str) -> dict | None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for asset in manifest.get("assets", []):
        if asset.get("id") == asset_id:
            return asset
    return None


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
            elif archetype == "target" or asset_type == "gameplay_target":
                ring = int(radius * 18)
                color = primary_rgba if ring % 2 == 0 else secondary_rgba
                if radius < 0.08:
                    color = white
                elif radius > 0.48:
                    color = dark
            else:
                stripe = (x // 48 + y // 48) % 2 == 0
                color = primary_rgba if stripe else secondary_rgba
            pixels.append(color)

    path.parent.mkdir(parents=True, exist_ok=True)
    write_png(path, 512, 512, pixels)


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


def write_usda(asset: dict, texture_name: str, output: Path) -> None:
    archetype = asset.get("archetype")
    mesh = drone_mesh() if archetype == "drone" else target_mesh()
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

    def list_value(values: list[object]) -> str:
        return "[" + ", ".join(str(value).replace("'", "") for value in values) + "]"

    points = list_value(mesh.points)
    counts = list_value([3] * len(mesh.triangles))
    face_indices = list_value(indices)
    st = list_value(st_values)
    extent = list_value([(min_x, min_y, min_z), (max_x, max_y, max_z)])

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
            float3[] extent = {extent}
            int[] faceVertexCounts = {counts}
            int[] faceVertexIndices = {face_indices}
            rel material:binding = </root/_materials/mat_textured>
            point3f[] points = {points}
            texCoord2f[] primvars:st = {st} (
                interpolation = "faceVarying"
            )
            int[] primvars:st:indices = {face_indices}
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

    output_path = ROOT / "Assets" / "Imported" / asset["file"]
    texture_name = f"{asset['id']}_basecolor.png"
    with tempfile.TemporaryDirectory(prefix=f"rkp_{asset['id']}_") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        usda_path = temp_dir / f"{asset['id']}.usda"
        texture_path = temp_dir / "textures" / texture_name
        make_texture(asset, texture_path)
        write_usda(asset, texture_name, usda_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [usdzip, "--arkitAsset", str(usda_path), str(output_path)]
        print("running:", " ".join(command), flush=True)
        result = subprocess.run(command, cwd=temp_dir)
        if result.returncode != 0:
            return result.returncode

    if not output_path.exists() or output_path.stat().st_size <= 0:
        print(f"error: expected USDZ was not created: {output_path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    print(f"fallback asset built: {output_path.relative_to(ROOT)} ({output_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
