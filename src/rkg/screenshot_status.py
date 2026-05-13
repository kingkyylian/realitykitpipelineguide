from __future__ import annotations

import hashlib
import json
import math
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
RgbGridSamples = list[tuple[int, int, int, int, int]]


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

    checks = [_check_step(project, qa_plan, step) for step in _qa_steps(qa_plan)]
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


def _check_step(project: Path, qa_plan: Mapping[str, Any], step: Mapping[str, Any]) -> JsonDict:
    capture_path = str(step.get("capture_path", ""))
    path = project / capture_path
    status, size, visual_fingerprint = _image_file_status(path)
    if status == "ok":
        status = _sidecar_status(project, qa_plan, step, path)
    if status == "ok":
        status = _semantic_visual_status(path, step)
    return {
        "order": int(step.get("order", 0)),
        "state": str(step.get("state", "")),
        "capture_path": capture_path,
        "status": status,
        "bytes": size,
        "_visual_fingerprint": visual_fingerprint,
    }


def _sidecar_status(project: Path, qa_plan: Mapping[str, Any], step: Mapping[str, Any], capture_path: Path) -> str:
    sidecar = _sidecar_path(project, step, capture_path)
    if not sidecar.exists():
        return "missing_sidecar"
    if not sidecar.is_file():
        return "invalid_sidecar"
    try:
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return "invalid_sidecar"
    if not isinstance(payload, Mapping):
        return "invalid_sidecar"
    if payload.get("schema_version") != 1:
        return "invalid_sidecar"
    if str(payload.get("game_id", "")) != str(qa_plan.get("game_id", "")):
        return "invalid_sidecar"
    if str(payload.get("state", "")) != str(step.get("state", "")):
        return "invalid_sidecar"
    if str(payload.get("automation", "")) != str(step.get("automation", "")):
        return "invalid_sidecar"

    expected_roles = {str(role) for role in step.get("visible_roles", [])}
    actual_roles = payload.get("visible_roles")
    if not isinstance(actual_roles, list) or {str(role) for role in actual_roles} != expected_roles:
        return "role_evidence_mismatch"
    return _scene_snapshot_status(project, step, payload, expected_roles)


def _sidecar_path(project: Path, step: Mapping[str, Any], capture_path: Path) -> Path:
    sidecar_path = step.get("sidecar_path")
    if isinstance(sidecar_path, str) and sidecar_path:
        return project / sidecar_path
    return capture_path.with_suffix(".json")


def _scene_snapshot_status(
    project: Path,
    step: Mapping[str, Any],
    sidecar: Mapping[str, Any],
    expected_roles: set[str],
) -> str:
    scene_snapshot_path = sidecar.get("scene_snapshot") or step.get("scene_snapshot_path")
    if not isinstance(scene_snapshot_path, str) or not scene_snapshot_path:
        return "invalid_sidecar"
    snapshot = project / scene_snapshot_path
    if not snapshot.exists():
        return "missing_scene_snapshot"
    if not snapshot.is_file():
        return "invalid_scene_snapshot"
    try:
        payload = json.loads(snapshot.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return "invalid_scene_snapshot"
    if not isinstance(payload, Mapping):
        return "invalid_scene_snapshot"
    if payload.get("schema_version") != 1:
        return "invalid_scene_snapshot"
    if str(payload.get("state", "")) != str(step.get("state", "")):
        return "invalid_scene_snapshot"
    roles = payload.get("roles")
    if not isinstance(roles, list):
        return "invalid_scene_snapshot"
    visibility_contract = step.get("role_visibility_contract")
    if not isinstance(visibility_contract, Mapping):
        visibility_contract = {}
    actual_roles: set[str] = set()
    enabled_roles: set[str] = set()
    visible_roles: set[str] = set()
    for role_record in roles:
        if not isinstance(role_record, Mapping):
            return "invalid_scene_snapshot"
        role = role_record.get("role")
        if not isinstance(role, str) or not role:
            return "invalid_scene_snapshot"
        if not _scene_role_record_has_valid_visibility_metadata(role_record):
            return "invalid_scene_snapshot"
        actual_roles.add(role)
        if role_record["is_enabled"]:
            enabled_roles.add(role)
            if _scene_role_record_has_measurable_visual_bounds(role_record, visibility_contract):
                visible_roles.add(role)
    if not expected_roles.issubset(actual_roles):
        return "scene_role_mismatch"
    if not expected_roles.issubset(enabled_roles):
        return "scene_role_not_visible"
    if not expected_roles.issubset(visible_roles):
        return "scene_role_not_visible"
    return "ok"


def _scene_role_record_has_valid_visibility_metadata(role_record: Mapping[str, Any]) -> bool:
    entity_name = role_record.get("entity_name")
    if not isinstance(entity_name, str) or not entity_name.startswith("rkg|"):
        return False
    if not isinstance(role_record.get("is_enabled"), bool):
        return False
    position = role_record.get("position")
    if not isinstance(position, Mapping):
        return False
    if not all(_is_finite_number(position.get(axis)) for axis in ("x", "y", "z")):
        return False
    visual_bounds = role_record.get("visual_bounds")
    if not isinstance(visual_bounds, Mapping):
        return False
    center = visual_bounds.get("center")
    extents = visual_bounds.get("extents")
    if not isinstance(center, Mapping) or not isinstance(extents, Mapping):
        return False
    if not all(_is_finite_number(center.get(axis)) for axis in ("x", "y", "z")):
        return False
    return all(_is_non_negative_finite_number(extents.get(axis)) for axis in ("x", "y", "z"))


def _scene_role_record_has_measurable_visual_bounds(
    role_record: Mapping[str, Any],
    visibility_contract: Mapping[str, Any],
) -> bool:
    visual_bounds = role_record.get("visual_bounds")
    if not isinstance(visual_bounds, Mapping):
        return False
    extents = visual_bounds.get("extents")
    if not isinstance(extents, Mapping):
        return False
    has_contract_min = isinstance(visibility_contract.get("min_visual_extent"), (int, float))
    min_visual_extent = _contract_float(visibility_contract, "min_visual_extent", 0.001)
    max_extent = max(float(extents[axis]) for axis in ("x", "y", "z"))
    if has_contract_min:
        return max_extent >= min_visual_extent
    return max_extent > min_visual_extent


def _is_finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _is_non_negative_finite_number(value: object) -> bool:
    return _is_finite_number(value) and float(value) >= 0.0


def _semantic_visual_status(path: Path, step: Mapping[str, Any]) -> str:
    contract = step.get("semantic_visual_contract")
    if not isinstance(contract, Mapping):
        return "ok"
    try:
        data = path.read_bytes()
    except OSError:
        return "invalid_image"
    grid, decode_failed = _image_rgb_sample_grid(data)
    if decode_failed:
        return "invalid_image"
    if grid is None:
        return "ok"
    width, height, samples = grid
    return _semantic_visual_grid_status(width, height, samples, contract) or "ok"


def _semantic_visual_grid_status(
    width: int,
    height: int,
    samples: RgbGridSamples,
    contract: Mapping[str, Any],
) -> str | None:
    if width <= 0 or height <= 0 or not samples:
        return None

    top_fraction = _contract_float(contract, "top_band_fraction", 0.24)
    max_top_light_coverage = _contract_float(contract, "max_top_light_coverage", 0.34)
    light_luma_threshold = _contract_float(contract, "light_luma_threshold", 112.0)
    top_samples = _samples_between_y_fractions(samples, height, 0.0, top_fraction)
    if top_samples:
        light_coverage = _luma_coverage(top_samples, light_luma_threshold)
        if light_coverage > max_top_light_coverage:
            return "semantic_debug_overlay"

    bottom_fraction = _contract_float(contract, "bottom_band_fraction", 0.2)
    max_bottom_light_coverage = _contract_float(contract, "max_bottom_light_coverage", 0.82)
    bottom_light_luma_threshold = _contract_float(contract, "bottom_light_luma_threshold", 170.0)
    bottom_samples = _samples_between_y_fractions(samples, height, 1.0 - bottom_fraction, 1.0)
    if bottom_samples:
        light_coverage = _luma_coverage(bottom_samples, bottom_light_luma_threshold)
        if light_coverage > max_bottom_light_coverage:
            return "semantic_control_occlusion"

    center_top = _contract_float(contract, "center_band_top_fraction", 0.34)
    center_bottom = _contract_float(contract, "center_band_bottom_fraction", 0.66)
    max_center_light_coverage = _contract_float(contract, "max_center_light_coverage", 0.88)
    center_light_luma_threshold = _contract_float(contract, "center_light_luma_threshold", 170.0)
    center_samples = _samples_between_y_fractions(samples, height, center_top, center_bottom)
    if center_samples:
        light_coverage = _luma_coverage(center_samples, center_light_luma_threshold)
        if light_coverage > max_center_light_coverage:
            return "semantic_center_occlusion"

    scene_top = _contract_float(contract, "scene_band_top_fraction", 0.24)
    scene_bottom = _contract_float(contract, "scene_band_bottom_fraction", 0.78)
    scene_samples = _samples_between_y_fractions(samples, height, scene_top, scene_bottom)
    if not scene_samples:
        return None

    min_scene_luma_span = _contract_float(contract, "min_scene_luma_span", 18.0)
    if _luma_span(scene_samples) < min_scene_luma_span:
        return "semantic_flat_scene"

    min_scene_bright_ratio = _contract_float(contract, "min_scene_bright_ratio", 0.015)
    scene_bright_luma_threshold = _contract_float(contract, "scene_bright_luma_threshold", 58.0)
    if _luma_coverage(scene_samples, scene_bright_luma_threshold) < min_scene_bright_ratio:
        return "semantic_scene_too_dark"
    return None


def _contract_float(contract: Mapping[str, Any], key: str, default: float) -> float:
    value = contract.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _samples_between_y_fractions(
    samples: RgbGridSamples,
    height: int,
    start_fraction: float,
    end_fraction: float,
) -> RgbGridSamples:
    start_y = max(0.0, min(1.0, start_fraction)) * float(height)
    end_y = max(start_y, min(1.0, end_fraction) * float(height))
    return [sample for sample in samples if start_y <= float(sample[1]) < end_y]


def _luma_coverage(samples: RgbGridSamples, threshold: float) -> float:
    if not samples:
        return 0.0
    light_count = sum(1 for sample in samples if _sample_luma(sample) >= threshold)
    return light_count / len(samples)


def _luma_span(samples: RgbGridSamples) -> float:
    if not samples:
        return 0.0
    lumas = [_sample_luma(sample) for sample in samples]
    return max(lumas) - min(lumas)


def _sample_luma(sample: tuple[int, int, int, int, int]) -> float:
    return 0.2126 * sample[2] + 0.7152 * sample[3] + 0.0722 * sample[4]


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


def _image_rgb_sample_grid(data: bytes) -> tuple[tuple[int, int, RgbGridSamples] | None, bool]:
    grid = _png_rgb_sample_grid(data)
    if grid is not None:
        return grid, False
    if data.startswith(b"\xff\xd8"):
        return _jpeg_rgb_sample_grid(data)
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


def _jpeg_rgb_sample_grid(data: bytes) -> tuple[tuple[int, int, RgbGridSamples] | None, bool]:
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
        grid = _png_rgb_sample_grid(output_path.read_bytes())
        if grid is None:
            return None, True
        return grid, False


def _png_rgb_samples(data: bytes) -> RgbSamples | None:
    grid = _png_rgb_sample_grid(data)
    if grid is None:
        return None
    _, _, samples = grid
    return [(red, green, blue) for _, _, red, green, blue in samples]


def _png_rgb_sample_grid(data: bytes) -> tuple[int, int, RgbGridSamples] | None:
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
    samples: RgbGridSamples = []
    for y in range(0, height, row_step):
        row = rows[y]
        for x in range(0, width, column_step):
            offset = x * bytes_per_pixel
            samples.append((x, y, row[offset], row[offset + 1], row[offset + 2]))
    return width, height, samples


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
