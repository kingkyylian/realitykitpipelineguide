import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def fighter_spec() -> dict:
    return {
        "game": {
            "id": "neon_ring_duel",
            "display_name": "Neon Ring Duel",
            "archetype": "fighter_2_5d",
            "session_seconds": 90,
            "camera": "fixed_non_ar",
            "input": "tap_swipe",
            "monetization": "paid",
        },
        "loop": {
            "player_action": "tap attack and swipe dodge",
            "fail_condition": "fighter health reaches zero",
            "scoring": {"hit": 10, "perfect": 25, "knockout": 100},
        },
        "assets": {
            "fighter_player": {
                "type": "gameplay_actor",
                "role": "player",
                "budget": "1800 tris / 512 texture",
                "fallback": "procedural_capsule",
            },
            "fighter_opponent": {
                "type": "gameplay_actor",
                "role": "opponent",
                "budget": "1800 tris / 512 texture",
                "fallback": "procedural_capsule",
            },
            "duel_arena": {
                "type": "environment",
                "role": "arena",
                "budget": "900 tris / 512 texture",
                "fallback": "procedural_lane",
            },
        },
        "release": {"devices": ["iPhone 15"], "screenshots": ["round_start", "mid_combo", "perfect_dodge", "knockout"]},
    }


class RkgCaptureTests(unittest.TestCase):
    def run_rkg(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def test_capture_screenshots_dry_run_lists_fighter_launch_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "GameSpec.json"
            spec_path.write_text(json.dumps(fighter_spec(), indent=2) + "\n", encoding="utf-8")
            project = root / "NeonRingDuel"
            init_result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(project))
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = self.run_rkg(root, "capture-screenshots", str(project), "--device", "booted", "--dry-run", "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(Path(payload["project"]), project.resolve())
            self.assertEqual(payload["device"], "booted")
            self.assertEqual(payload["steps"][1]["state"], "mid_combo")
            self.assertIn("--rkg-screenshot-state", payload["steps"][1]["launch"])
            self.assertTrue(payload["steps"][1]["screenshot"].endswith("Docs/screenshots/mid_combo.jpg"))

    def test_capture_execution_runs_build_install_launch_and_screenshot_steps(self) -> None:
        from rkg.capture import execute_capture_plan

        plan = {
            "project": "/tmp/Generated",
            "device": "booted",
            "build": ["xcodebuild", "build"],
            "install": ["xcrun", "simctl", "install", "booted", "App.app"],
            "steps": [
                {
                    "order": 1,
                    "state": "round_start",
                    "launch": [
                        "xcrun",
                        "simctl",
                        "launch",
                        "booted",
                        "com.example.game",
                        "--rkg-screenshot-state",
                        "round_start",
                    ],
                    "screenshot": "/tmp/Generated/Docs/screenshots/round_start.jpg",
                }
            ],
        }
        calls = []

        def fake_runner(command: list[str], cwd: Path) -> int:
            calls.append((command, cwd))
            return 0

        result = execute_capture_plan(plan, runner=fake_runner, sleep_seconds=0)

        self.assertTrue(result["ok"])
        self.assertEqual(calls[0][0], ["xcodebuild", "build"])
        self.assertEqual(calls[1][0], ["xcrun", "simctl", "install", "booted", "App.app"])
        self.assertEqual(calls[2][0][-1], "round_start")
        self.assertEqual(
            calls[3][0],
            ["xcrun", "simctl", "io", "booted", "screenshot", "/tmp/Generated/Docs/screenshots/round_start.jpg"],
        )

    def test_capture_execution_waits_long_enough_after_launch_by_default(self) -> None:
        from rkg.capture import execute_capture_plan

        plan = {
            "project": "/tmp/Generated",
            "device": "booted",
            "build": ["xcodebuild", "build"],
            "install": ["xcrun", "simctl", "install", "booted", "App.app"],
            "steps": [
                {
                    "order": 1,
                    "state": "gameplay_start",
                    "launch": [
                        "xcrun",
                        "simctl",
                        "launch",
                        "--terminate-running-process",
                        "booted",
                        "com.example.game",
                        "--rkg-screenshot-state",
                        "gameplay_start",
                    ],
                    "screenshot": "/tmp/Generated/Docs/screenshots/gameplay_start.jpg",
                }
            ],
        }

        def fake_runner(command: list[str], cwd: Path) -> int:
            return 0

        with patch("rkg.capture.time.sleep") as sleep:
            result = execute_capture_plan(plan, runner=fake_runner)

        self.assertTrue(result["ok"])
        sleep.assert_called_once_with(2.0)


if __name__ == "__main__":
    unittest.main()
