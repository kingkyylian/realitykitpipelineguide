#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

from rkp.asset_manifest import asset_usdz_path, expected_basecolor_name, load_asset
from rkp.rkp_project import ProjectPaths, load_project


PROJECT = load_project()


def _read_text_members(archive: zipfile.ZipFile) -> str:
    chunks: list[str] = []
    for name in archive.namelist():
        if Path(name).suffix.lower() not in {".usda", ".usd"}:
            continue
        try:
            chunks.append(archive.read(name).decode("utf-8"))
        except UnicodeDecodeError:
            continue
    return "\n".join(chunks)


def _read_usdcat_text(usdz_path: Path, entries: list[str]) -> str:
    if not any(Path(name).suffix.lower() in {".usdc", ".usd"} for name in entries):
        return ""
    usdcat = shutil.which("usdcat")
    if not usdcat:
        return ""
    result = subprocess.run([usdcat, str(usdz_path)], text=True, capture_output=True)
    if result.returncode != 0:
        return ""
    return result.stdout


def _parse_face_vertex_counts(text: str) -> int | None:
    counts: list[int] = []
    for match in re.finditer(r"faceVertexCounts\s*=\s*\[([^\]]*)\]", text, re.DOTALL):
        counts.extend(int(value) for value in re.findall(r"\d+", match.group(1)))
    if not counts:
        return None
    return sum(max(count - 2, 0) for count in counts)


def _png_dimensions(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 24:
        return None
    if data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def _jpeg_dimensions(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    index = 2
    while index + 9 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > len(data):
            return None
        segment_length = int.from_bytes(data[index : index + 2], "big")
        if segment_length < 2 or index + segment_length > len(data):
            return None
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            if segment_length < 7:
                return None
            height = int.from_bytes(data[index + 3 : index + 5], "big")
            width = int.from_bytes(data[index + 5 : index + 7], "big")
            return width, height
        index += segment_length
    return None


def image_dimensions(data: bytes) -> tuple[int, int] | None:
    return _png_dimensions(data) or _jpeg_dimensions(data)


def inspect_asset(asset_id: str, project: ProjectPaths = PROJECT) -> dict:
    asset = load_asset(asset_id, project)
    if asset is None:
        return {"ok": False, "asset": asset_id, "errors": [f"unknown asset id: {asset_id}"]}

    usdz_path = asset_usdz_path(asset, project)
    payload: dict = {
        "ok": False,
        "asset": asset_id,
        "path": project.rel(usdz_path),
        "exists": usdz_path.exists(),
        "sizeBytes": usdz_path.stat().st_size if usdz_path.exists() else 0,
        "entries": [],
        "triangles": None,
        "maxTriangles": asset.get("maxTriangles"),
        "triangleStatus": "unknown",
        "baseColorTexture": {
            "expected": expected_basecolor_name(asset),
            "present": False,
            "width": None,
            "height": None,
            "maxSize": asset.get("maxTextureSize"),
            "sizeStatus": "unknown",
        },
        "uv": {"st": None, "status": "unknown"},
        "errors": [],
    }

    if not usdz_path.exists():
        payload["errors"].append(f"missing USDZ: {project.rel(usdz_path)}")
        return payload
    if payload["sizeBytes"] <= 0:
        payload["errors"].append(f"empty USDZ: {project.rel(usdz_path)}")
        return payload

    try:
        with zipfile.ZipFile(usdz_path) as archive:
            entries = archive.namelist()
            payload["entries"] = entries
            expected_texture = payload["baseColorTexture"]["expected"]
            if expected_texture:
                texture_member = next((name for name in entries if Path(name).name == expected_texture), None)
                payload["baseColorTexture"]["present"] = texture_member is not None
                if texture_member:
                    dimensions = image_dimensions(archive.read(texture_member))
                    if dimensions:
                        width, height = dimensions
                        payload["baseColorTexture"]["width"] = width
                        payload["baseColorTexture"]["height"] = height
                        max_size = payload["baseColorTexture"]["maxSize"]
                        if max_size is not None:
                            payload["baseColorTexture"]["sizeStatus"] = (
                                "ok" if max(width, height) <= max_size else "over"
                            )
            else:
                payload["baseColorTexture"]["present"] = None
                payload["baseColorTexture"]["sizeStatus"] = "not_required"
            text = _read_text_members(archive)
            if not text:
                text = _read_usdcat_text(usdz_path, entries)
    except zipfile.BadZipFile:
        payload["errors"].append("USDZ is not a readable zip package")
        return payload

    triangles = _parse_face_vertex_counts(text)
    payload["triangles"] = triangles
    if triangles is not None and payload["maxTriangles"] is not None:
        payload["triangleStatus"] = "ok" if triangles <= payload["maxTriangles"] else "over"
    if text:
        payload["uv"]["st"] = "primvars:st" in text
        payload["uv"]["status"] = "present" if payload["uv"]["st"] else "missing"

    if payload["triangleStatus"] == "over":
        payload["errors"].append("triangle budget exceeded")
    if payload["baseColorTexture"]["expected"] and not payload["baseColorTexture"]["present"]:
        payload["errors"].append("baseColor texture missing from USDZ")
    if payload["baseColorTexture"]["sizeStatus"] == "over":
        payload["errors"].append("baseColor texture exceeds manifest maxTextureSize")
    if payload["uv"]["status"] == "missing":
        payload["errors"].append("st UV primvar missing from text USD")

    payload["ok"] = not payload["errors"]
    return payload


def print_text(payload: dict) -> None:
    print(f"asset: {payload['asset']}")
    print(f"path: {payload.get('path', '-')}")
    print(f"exists: {str(payload.get('exists', False)).lower()}")
    print(f"size: {payload.get('sizeBytes', 0)} bytes")
    triangles = payload.get("triangles")
    max_triangles = payload.get("maxTriangles")
    triangle_value = "unknown" if triangles is None else str(triangles)
    budget_suffix = "" if max_triangles is None else f" / {max_triangles}"
    print(f"triangles: {triangle_value}{budget_suffix}")
    print(f"triangle budget: {payload.get('triangleStatus', 'unknown')}")
    texture = payload.get("baseColorTexture", {})
    if texture.get("expected") is None:
        print("baseColor texture: not required")
    else:
        print("baseColor texture: " + ("present" if texture.get("present") else "missing"))
        width = texture.get("width")
        height = texture.get("height")
        max_size = texture.get("maxSize")
        if width is None or height is None:
            print("baseColor size: unknown")
        else:
            suffix = "" if max_size is None else f" / {max_size} ({texture.get('sizeStatus', 'unknown')})"
            print(f"baseColor size: {width}x{height}{suffix}")
    print(f"uv st: {payload.get('uv', {}).get('status', 'unknown')}")
    entries = payload.get("entries", [])
    print(f"entries: {len(entries)}")
    for error in payload.get("errors", []):
        print(f"error: {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a built USDZ against the RKP asset contract.")
    parser.add_argument("id", help="Asset id from the manifest")
    parser.add_argument("--json", action="store_true", help="Print machine-readable inspection result")
    args = parser.parse_args()

    payload = inspect_asset(args.id)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
