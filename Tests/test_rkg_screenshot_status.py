import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rkg.qa_plan import build_qa_plan
from rkg.screenshot_status import build_screenshot_status, build_screenshot_status_for_project


def target_spec(screenshots: list[str] | None = None) -> dict:
    return {
        "game": {
            "id": "ring_dash",
            "display_name": "Ring Dash",
            "archetype": "target_shooter",
            "session_seconds": 60,
            "camera": "fixed_non_ar",
            "input": "tap",
            "monetization": "paid",
        },
        "loop": {
            "player_action": "tap targets before they expire",
            "fail_condition": "time expires",
            "scoring": {"hit": 10, "perfect": 25, "streak_bonus": True},
        },
        "assets": {
            "target_basic": {
                "type": "gameplay_target",
                "role": "target",
                "budget": "1500 tris / 512 texture",
                "fallback": "procedural_rings",
            },
            "arena_floor": {
                "type": "environment",
                "role": "arena",
                "budget": "800 tris / 512 texture",
                "fallback": "procedural_grid",
            },
        },
        "release": {
            "devices": ["iPhone 15"],
            "screenshots": screenshots or ["gameplay_start"],
        },
    }


class RkgScreenshotStatusTests(unittest.TestCase):
    def run_rkg(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def write_jpeg_stub(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(
            b"\xff\xd8"
            b"\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
            b"\xff\xc0\x00\x11\x08\x01\xe0\x02\x80\x03\x01\x11\x00\x02\x11\x00\x03\x11\x00"
            b"\xff\xd9"
        )

    def write_sidecar(
        self,
        path: Path,
        *,
        state: str = "gameplay_start",
        visible_roles: list[str] | None = None,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "game_id": "ring_dash",
                    "display_name": "Ring Dash",
                    "archetype": "target_shooter",
                    "state": state,
                    "screenshot_state_case": state,
                    "visible_roles": visible_roles or ["target", "arena"],
                    "expected_evidence": "Declared roles available: target, arena",
                    "automation": "manual_capture",
                    "screenshot": f"Docs/screenshots/{state}.jpg",
                    "scene_snapshot": f"Docs/screenshots/{state}.scene.json",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def write_scene_snapshot(
        self,
        path: Path,
        *,
        state: str = "gameplay_start",
        roles: list[str] | None = None,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        role_values = roles or ["target", "arena"]
        payload = {
            "schema_version": 1,
            "state": state,
            "roles": [
                {
                    "asset_id": f"{role}_proxy",
                    "role": role,
                    "fallback": "procedural_proxy",
                    "entity_name": f"rkg|asset={role}_proxy|role={role}|fallback=procedural_proxy",
                    "is_enabled": True,
                    "position": {"x": 0.0, "y": 0.0, "z": -0.85},
                }
                for role in role_values
            ],
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def write_jpeg_rgb(self, path: Path, rows: list[list[tuple[int, int, int]]]) -> None:
        if shutil.which("sips") is None:
            self.skipTest("sips is required to write JPEG fixtures")
        source_png = path.with_name(path.name + ".source.png")
        self.write_png_rgb(source_png, rows)
        result = subprocess.run(
            ["sips", "-s", "format", "jpeg", str(source_png), "--out", str(path)],
            text=True,
            capture_output=True,
            timeout=10,
        )
        source_png.unlink(missing_ok=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def write_png_rgb(self, path: Path, rows: list[list[tuple[int, int, int]]], filter_type: int = 0) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        height = len(rows)
        width = len(rows[0])
        bytes_per_pixel = 3
        previous = bytearray(width * bytes_per_pixel)
        raw = bytearray()
        for row in rows:
            source = bytearray()
            for red, green, blue in row:
                source.extend((red, green, blue))
            raw.append(filter_type)
            raw.extend(self.encode_png_scanline(source, previous, bytes_per_pixel, filter_type))
            previous = source

        def chunk(kind: bytes, payload: bytes) -> bytes:
            crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
            return len(payload).to_bytes(4, "big") + kind + payload + crc.to_bytes(4, "big")

        header = (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", width.to_bytes(4, "big") + height.to_bytes(4, "big") + b"\x08\x02\x00\x00\x00")
            + chunk(b"IDAT", zlib.compress(bytes(raw)))
            + chunk(b"IEND", b"")
        )
        path.write_bytes(header)

    def encode_png_scanline(
        self,
        source: bytearray,
        previous: bytearray,
        bytes_per_pixel: int,
        filter_type: int,
    ) -> bytes:
        encoded = bytearray()
        for index, value in enumerate(source):
            left = source[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            up = previous[index]
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            else:
                raise ValueError(f"unsupported test png filter: {filter_type}")
            encoded.append((value - predictor) & 0xFF)
        return bytes(encoded)

    def test_build_screenshot_status_reports_missing_files_from_qa_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            project.mkdir()
            plan = build_qa_plan(target_spec())

            payload = build_screenshot_status(project, plan)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["game_id"], "ring_dash")
            self.assertEqual(payload["checks"][0]["state"], "gameplay_start")
            self.assertEqual(payload["checks"][0]["status"], "missing")
            self.assertEqual(payload["checks"][0]["capture_path"], "Docs/screenshots/gameplay_start.jpg")

    def test_build_screenshot_status_accepts_valid_jpeg_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            rows = [
                [((x * 7) % 256, (y * 5) % 256, ((x + y) * 3) % 256) for x in range(320)]
                for y in range(320)
            ]
            self.write_jpeg_rgb(project / "Docs" / "screenshots" / "gameplay_start.jpg", rows)
            self.write_sidecar(project / "Docs" / "screenshots" / "gameplay_start.json")
            self.write_scene_snapshot(project / "Docs" / "screenshots" / "gameplay_start.scene.json")
            plan = build_qa_plan(target_spec())

            payload = build_screenshot_status(project, plan)

            self.assertTrue(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "ok")
            self.assertGreater(payload["checks"][0]["bytes"], 0)

    def test_verify_screenshots_rejects_header_only_jpeg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            self.write_json(project / "GameSpec.json", target_spec())
            fake = project / "Docs" / "screenshots" / "gameplay_start.jpg"
            fake.parent.mkdir(parents=True, exist_ok=True)
            fake.write_bytes(b"\xff\xd8\xff\xe0fake\xff\xd9")

            payload = build_screenshot_status_for_project(project)

            first = payload["checks"][0]
            self.assertFalse(payload["ok"])
            self.assertEqual(first["status"], "invalid_dimensions")

    def test_verify_screenshots_rejects_dimension_only_jpeg_stub(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            self.write_jpeg_stub(project / "Docs" / "screenshots" / "gameplay_start.jpg")
            plan = build_qa_plan(target_spec())

            payload = build_screenshot_status(project, plan)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "invalid_image")

    def test_verify_screenshots_requires_sidecar_for_valid_image_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            rows = [
                [((x * 7) % 256, (y * 5) % 256, ((x + y) * 3) % 256) for x in range(320)]
                for y in range(320)
            ]
            self.write_jpeg_rgb(project / "Docs" / "screenshots" / "gameplay_start.jpg", rows)
            plan = build_qa_plan(target_spec())

            payload = build_screenshot_status(project, plan)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "missing_sidecar")

    def test_verify_screenshots_requires_runtime_scene_snapshot_for_valid_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            rows = [
                [((x * 7) % 256, (y * 5) % 256, ((x + y) * 3) % 256) for x in range(320)]
                for y in range(320)
            ]
            self.write_jpeg_rgb(project / "Docs" / "screenshots" / "gameplay_start.jpg", rows)
            self.write_sidecar(project / "Docs" / "screenshots" / "gameplay_start.json")
            plan = build_qa_plan(target_spec())

            payload = build_screenshot_status(project, plan)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "missing_scene_snapshot")

    def test_verify_screenshots_rejects_runtime_scene_snapshot_role_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            rows = [
                [((x * 7) % 256, (y * 5) % 256, ((x + y) * 3) % 256) for x in range(320)]
                for y in range(320)
            ]
            self.write_jpeg_rgb(project / "Docs" / "screenshots" / "gameplay_start.jpg", rows)
            self.write_sidecar(project / "Docs" / "screenshots" / "gameplay_start.json")
            self.write_scene_snapshot(project / "Docs" / "screenshots" / "gameplay_start.scene.json", roles=["target"])
            plan = build_qa_plan(target_spec())

            payload = build_screenshot_status(project, plan)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "scene_role_mismatch")

    def test_verify_screenshots_rejects_sidecar_role_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            rows = [
                [((x * 7) % 256, (y * 5) % 256, ((x + y) * 3) % 256) for x in range(320)]
                for y in range(320)
            ]
            self.write_jpeg_rgb(project / "Docs" / "screenshots" / "gameplay_start.jpg", rows)
            self.write_sidecar(project / "Docs" / "screenshots" / "gameplay_start.json", visible_roles=["target"])
            plan = build_qa_plan(target_spec())

            payload = build_screenshot_status(project, plan)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "role_evidence_mismatch")

    def test_verify_screenshots_rejects_solid_jpeg_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            solid = [[(244, 244, 244) for _ in range(320)] for _ in range(320)]
            self.write_jpeg_rgb(project / "Docs" / "screenshots" / "gameplay_start.jpg", solid)
            plan = build_qa_plan(target_spec())

            payload = build_screenshot_status(project, plan)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "blank_or_solid")

    def test_verify_screenshots_rejects_duplicate_visual_evidence_across_states(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            rows = [
                [((x * 7) % 256, (y * 5) % 256, ((x + y) * 3) % 256) for x in range(320)]
                for y in range(320)
            ]
            self.write_jpeg_rgb(project / "Docs" / "screenshots" / "gameplay_start.jpg", rows)
            self.write_sidecar(project / "Docs" / "screenshots" / "gameplay_start.json")
            self.write_scene_snapshot(project / "Docs" / "screenshots" / "gameplay_start.scene.json")
            self.write_jpeg_rgb(project / "Docs" / "screenshots" / "results.jpg", rows)
            self.write_sidecar(project / "Docs" / "screenshots" / "results.json", state="results")
            self.write_scene_snapshot(project / "Docs" / "screenshots" / "results.scene.json", state="results")
            plan = build_qa_plan(target_spec(["gameplay_start", "results"]))

            payload = build_screenshot_status(project, plan)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "ok")
            self.assertEqual(payload["checks"][1]["status"], "duplicate_visual_evidence")

    def test_verify_screenshots_rejects_solid_png_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            solid = [[(244, 244, 244) for _ in range(320)] for _ in range(320)]
            self.write_png_rgb(project / "Docs" / "screenshots" / "gameplay_start.png", solid)
            plan = build_qa_plan(target_spec())
            plan["steps"][0]["capture_path"] = "Docs/screenshots/gameplay_start.png"

            payload = build_screenshot_status(project, plan)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "blank_or_solid")

    def test_verify_screenshots_rejects_solid_filtered_png_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            solid = [[(244, 244, 244) for _ in range(320)] for _ in range(320)]
            self.write_png_rgb(project / "Docs" / "screenshots" / "gameplay_start.png", solid, filter_type=1)
            plan = build_qa_plan(target_spec())
            plan["steps"][0]["capture_path"] = "Docs/screenshots/gameplay_start.png"

            payload = build_screenshot_status(project, plan)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "blank_or_solid")

    def test_verify_screenshots_accepts_varied_png_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            rows = [
                [((x * 7) % 256, (y * 5) % 256, ((x + y) * 3) % 256) for x in range(320)]
                for y in range(320)
            ]
            self.write_png_rgb(project / "Docs" / "screenshots" / "gameplay_start.png", rows)
            self.write_sidecar(project / "Docs" / "screenshots" / "gameplay_start.json")
            self.write_scene_snapshot(project / "Docs" / "screenshots" / "gameplay_start.scene.json")
            plan = build_qa_plan(target_spec())
            plan["steps"][0]["capture_path"] = "Docs/screenshots/gameplay_start.png"

            payload = build_screenshot_status(project, plan)

            self.assertTrue(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "ok")

    def test_verify_screenshots_rejects_debug_overlay_like_top_panel(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            rows = []
            for y in range(320):
                if y < 88:
                    rows.append([(176, 176, 176) for _ in range(320)])
                elif y < 250:
                    rows.append([((x * 7) % 180, 24 + (y * 5) % 140, ((x + y) * 3) % 210) for x in range(320)])
                else:
                    rows.append([(24 + (x % 8), 28 + (y % 6), 32) for x in range(320)])
            self.write_png_rgb(project / "Docs" / "screenshots" / "gameplay_start.png", rows)
            self.write_sidecar(project / "Docs" / "screenshots" / "gameplay_start.json")
            self.write_scene_snapshot(project / "Docs" / "screenshots" / "gameplay_start.scene.json")
            plan = build_qa_plan(target_spec())
            plan["steps"][0]["capture_path"] = "Docs/screenshots/gameplay_start.png"

            payload = build_screenshot_status(project, plan)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "semantic_debug_overlay")

    def test_verify_screenshots_accepts_semantically_varied_gameplay_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "RingDash"
            rows = []
            for y in range(320):
                if y < 88:
                    rows.append([(10 + (x % 12), 12 + (y % 10), 16) for x in range(320)])
                elif y < 250:
                    rows.append([((x * 9) % 220, 38 + (y * 5) % 170, 42 + ((x + y) * 4) % 180) for x in range(320)])
                else:
                    rows.append([(30 + (x % 14), 34 + (y % 8), 38) for x in range(320)])
            self.write_png_rgb(project / "Docs" / "screenshots" / "gameplay_start.png", rows)
            self.write_sidecar(project / "Docs" / "screenshots" / "gameplay_start.json")
            self.write_scene_snapshot(project / "Docs" / "screenshots" / "gameplay_start.scene.json")
            plan = build_qa_plan(target_spec())
            plan["steps"][0]["capture_path"] = "Docs/screenshots/gameplay_start.png"

            payload = build_screenshot_status(project, plan)

            self.assertTrue(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "ok")

    def test_verify_screenshots_cli_consumes_qa_plan_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "RingDash"
            project.mkdir()
            plan_path = root / "qa-plan.json"
            self.write_json(plan_path, build_qa_plan(target_spec()))

            result = self.run_rkg(root, "verify-screenshots", str(project), "--plan", str(plan_path), "--json")

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "missing")

    def test_verify_screenshots_cli_reads_generated_project_gamespec_when_plan_is_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "RingDash"
            self.write_json(project / "GameSpec.json", target_spec())
            rows = [
                [((x * 7) % 256, (y * 5) % 256, ((x + y) * 3) % 256) for x in range(320)]
                for y in range(320)
            ]
            self.write_jpeg_rgb(project / "Docs" / "screenshots" / "gameplay_start.jpg", rows)
            self.write_sidecar(project / "Docs" / "screenshots" / "gameplay_start.json")
            self.write_scene_snapshot(project / "Docs" / "screenshots" / "gameplay_start.scene.json")

            result = self.run_rkg(root, "verify-screenshots", str(project), "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
