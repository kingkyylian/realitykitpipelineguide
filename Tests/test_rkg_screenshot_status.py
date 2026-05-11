import json
import subprocess
import sys
import tempfile
import unittest
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
            self.write_jpeg_stub(project / "Docs" / "screenshots" / "gameplay_start.jpg")
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
            self.write_jpeg_stub(project / "Docs" / "screenshots" / "gameplay_start.jpg")

            result = self.run_rkg(root, "verify-screenshots", str(project), "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["checks"][0]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
