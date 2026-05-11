from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import zlib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rkg.qa_plan import build_qa_plan
from rkg.spec import load_game_spec

JsonDict = dict[str, Any]
RgbSamples = list[tuple[int, int, int]]


def load_qa_plan(path: Path) -> JsonDict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("qa plan root must be an object")
    return value


def build_screenshot_status_for_project(project: Path) -> JsonDict:
    spec_path = project / "GameSpec.json"
    if not spec_path.exists():
        raise ValueError("missing GameSpec.json; pass --plan to verify against an external qa-plan JSON file")
    return build_screenshot_status(project, build_qa_plan(load_game_spec(spec_path)))


def build_screenshot_status(project: Path, qa_plan: Mapping[str, Any]) -> JsonDict:
    project = project.resolve()
    if not project.exists() or not project.is_dir():
        raise ValueError(f"generated project does not exist: {project}")

    checks = [_check_step(project, step) for step in _qa_steps(qa_plan)]
    _mark_duplicate_visual_evidence(checks)
    for check in checks:
        check.pop("_visual_fingerprint", None)
    return {
        "game_id": str(qa_plan.get("game_id", "")),
        "display_name": str(qa_plan.get("display_name", "")),
        "archetype": str(qa_plan.get("archetype", "")),
        "ok": all(check["status"] == "ok" for check in checks),
        "checks": checks,
    }


def _qa_steps(qa_plan: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    steps = qa_plan.get("steps")
    if not isinstance(steps, list):
        raise ValueError("qa plan steps must be a list")
    for step in steps:
        if not isinstance(step, Mapping):
            raise ValueError("qa plan steps must contain objects")
    return steps


def _check_step(project: Path, step: Mapping[str, Any]) -> JsonDict:
    capture_path = str(step.get("capture_path", ""))
    path = project / capture_path
    status, size, visual_fingerprint = _image_file_status(path)
    return {
        "order": int(step.get("order", 0)),
        "state": str(step.get("state", "")),
        "capture_path": capture_path,
        "status": status,
        "bytes": size,
        "_visual_fingerprint": visual_fingerprint,
    }


def _mark_duplicate_visual_evidence(checks: list[JsonDict]) -> None:
    seen: set[str] = set()
    for check in checks:
        if check["status"] != "ok":
            continue
        fingerprint = check.get("_visual_fingerprint")
        if not isinstance(fingerprint, str):
            continue
        if fingerprint in seen:
            check["status"] = "duplicate_visual_evidence"
            continue
        seen.add(fingerprint)


def _image_file_status(path: Path) -> tuple[str, int, str | None]:
    if not path.exists():
        return "missing", 0, None
    if not path.is_file():
        return "not_file", 0, None
    size = path.stat().st_size
    if size == 0:
        return "empty", 0, None
    with path.open("rb") as handle:
        data = handle.read()
    if not _is_supported_image_header(data[:12]):
        return "invalid_image", size, None
    dimensions = _image_dimensions(data)
    if dimensions is None or dimensions[0] < 300 or dimensions[1] < 300:
        return "invalid_dimensions", size, None
    visual_status, visual_fingerprint = _image_visual_status(data)
    if visual_status is not None:
        return visual_status, size, visual_fingerprint
    return "ok", size, visual_fingerprint


def _image_dimensions(data: bytes) -> tuple[int, int] | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data.startswith(b"\xff\xd8"):
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
            length = int.from_bytes(data[index:index + 2], "big")
            if marker in {0xC0, 0xC1, 0xC2} and index + 7 < len(data):
                height = int.from_bytes(data[index + 3:index + 5], "big")
                width = int.from_bytes(data[index + 5:index + 7], "big")
                return width, height
            index += max(length, 2)
    return None


def _is_supported_image_header(header: bytes) -> bool:
    return header.startswith(b"\xff\xd8\xff") or header.startswith(b"\x89PNG\r\n\x1a\n")


def _image_visual_status(data: bytes) -> tuple[str | None, str | None]:
    samples, decode_failed = _image_rgb_samples(data)
    if decode_failed:
        return "invalid_image", None
    if samples is None:
        return None, None
    fingerprint = _rgb_sample_fingerprint(samples)
    if samples and _rgb_sample_span(samples) <= 3:
        return "blank_or_solid", fingerprint
    return None, fingerprint


def _image_rgb_samples(data: bytes) -> tuple[RgbSamples | None, bool]:
    samples = _png_rgb_samples(data)
    if samples is not None:
        return samples, False
    if data.startswith(b"\xff\xd8"):
        return _jpeg_rgb_samples(data)
    return None, False


def _rgb_sample_span(samples: RgbSamples) -> int:
    red = [sample[0] for sample in samples]
    green = [sample[1] for sample in samples]
    blue = [sample[2] for sample in samples]
    return max(
        max(red) - min(red),
        max(green) - min(green),
        max(blue) - min(blue),
    )


def _rgb_sample_fingerprint(samples: RgbSamples) -> str:
    digest = hashlib.sha256()
    for red, green, blue in samples:
        digest.update(bytes((red, green, blue)))
    return digest.hexdigest()


def _jpeg_rgb_samples(data: bytes) -> tuple[RgbSamples | None, bool]:
    decoder = shutil.which("sips")
    if decoder is None:
        return None, False
    with tempfile.TemporaryDirectory(prefix="rkg-screenshot-") as tmp:
        input_path = Path(tmp) / "capture.jpg"
        output_path = Path(tmp) / "capture.png"
        input_path.write_bytes(data)
        try:
            result = subprocess.run(
                [decoder, "-s", "format", "png", str(input_path), "--out", str(output_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None, True
        if result.returncode != 0 or not output_path.exists():
            return None, True
        samples = _png_rgb_samples(output_path.read_bytes())
        if samples is None:
            return None, True
        return samples, False


def _png_rgb_samples(data: bytes) -> RgbSamples | None:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    if len(data) < 33:
        return None

    width: int | None = None
    height: int | None = None
    color_type: int | None = None
    bit_depth: int | None = None
    idat = bytearray()
    index = 8
    while index + 12 <= len(data):
        length = int.from_bytes(data[index:index + 4], "big")
        chunk_type = data[index + 4:index + 8]
        chunk_start = index + 8
        chunk_end = chunk_start + length
        if chunk_end + 4 > len(data):
            return None
        payload = data[chunk_start:chunk_end]
        if chunk_type == b"IHDR" and len(payload) >= 13:
            width = int.from_bytes(payload[0:4], "big")
            height = int.from_bytes(payload[4:8], "big")
            bit_depth = payload[8]
            color_type = payload[9]
        elif chunk_type == b"IDAT":
            idat.extend(payload)
        elif chunk_type == b"IEND":
            break
        index = chunk_end + 4

    if width is None or height is None or bit_depth != 8 or color_type not in {2, 6}:
        return None

    bytes_per_pixel = 4 if color_type == 6 else 3
    stride = width * bytes_per_pixel
    try:
        raw = zlib.decompress(bytes(idat))
    except zlib.error:
        return None
    if len(raw) < (stride + 1) * height:
        return None

    rows = _png_unfiltered_scanlines(raw, width, height, bytes_per_pixel)
    if rows is None:
        return None

    row_step = max(1, height // 128)
    column_step = max(1, width // 128)
    samples: list[tuple[int, int, int]] = []
    for y in range(0, height, row_step):
        row = rows[y]
        for x in range(0, width, column_step):
            offset = x * bytes_per_pixel
            samples.append((row[offset], row[offset + 1], row[offset + 2]))
    return samples


def _png_unfiltered_scanlines(raw: bytes, width: int, height: int, bytes_per_pixel: int) -> list[bytes] | None:
    stride = width * bytes_per_pixel
    rows: list[bytes] = []
    previous = bytes(stride)
    offset = 0
    for _ in range(height):
        if offset + stride + 1 > len(raw):
            return None
        filter_type = raw[offset]
        offset += 1
        filtered = raw[offset:offset + stride]
        offset += stride
        row = _png_unfiltered_scanline(filtered, previous, bytes_per_pixel, filter_type)
        if row is None:
            return None
        rows.append(row)
        previous = row
    return rows


def _png_unfiltered_scanline(
    filtered: bytes,
    previous: bytes,
    bytes_per_pixel: int,
    filter_type: int,
) -> bytes | None:
    row = bytearray(len(filtered))
    for index, value in enumerate(filtered):
        left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
        up = previous[index]
        up_left = previous[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
        if filter_type == 0:
            predictor = 0
        elif filter_type == 1:
            predictor = left
        elif filter_type == 2:
            predictor = up
        elif filter_type == 3:
            predictor = (left + up) // 2
        elif filter_type == 4:
            predictor = _png_paeth_predictor(left, up, up_left)
        else:
            return None
        row[index] = (value + predictor) & 0xFF
    return bytes(row)


def _png_paeth_predictor(left: int, up: int, up_left: int) -> int:
    estimate = left + up - up_left
    left_distance = abs(estimate - left)
    up_distance = abs(estimate - up)
    up_left_distance = abs(estimate - up_left)
    if left_distance <= up_distance and left_distance <= up_left_distance:
        return left
    if up_distance <= up_left_distance:
        return up
    return up_left
