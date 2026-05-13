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
            self.assertEqual(payload["generate"], ["xcodegen", "generate"])
            self.assertEqual(payload["steps"][1]["state"], "mid_combo")
            self.assertIn("--rkg-screenshot-state", payload["steps"][1]["launch"])
            self.assertTrue(payload["steps"][1]["screenshot"].endswith("Docs/screenshots/mid_combo.jpg"))
            self.assertTrue(payload["steps"][1]["sidecar"].endswith("Docs/screenshots/mid_combo.json"))
            self.assertTrue(payload["steps"][1]["scene_snapshot"].endswith("Docs/screenshots/mid_combo.scene.json"))
            self.assertEqual(payload["steps"][1]["runtime_scene_snapshot"], "Documents/rkg-scene-snapshot-mid_combo.json")
            self.assertEqual(payload["steps"][1]["visible_roles"], ["player", "opponent", "arena"])
            self.assertIn("state.comboCount", payload["steps"][1]["drive"])

    def test_capture_execution_runs_build_install_launch_and_screenshot_steps(self) -> None:
        from rkg.capture import execute_capture_plan

        plan = {
            "project": "/tmp/Generated",
            "device": "booted",
            "generate": ["xcodegen", "generate"],
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
        self.assertEqual(calls[0][0], ["xcodegen", "generate"])
        self.assertEqual(calls[1][0], ["xcodebuild", "build"])
        self.assertEqual(calls[2][0], ["xcrun", "simctl", "install", "booted", "App.app"])
        self.assertEqual(calls[3][0][-1], "round_start")
        self.assertEqual(
            calls[4][0],
            ["xcrun", "simctl", "io", "booted", "screenshot", "/tmp/Generated/Docs/screenshots/round_start.jpg"],
        )

    def test_capture_execution_writes_sidecar_after_successful_screenshot(self) -> None:
        from rkg.capture import execute_capture_plan

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "Generated"
            project.mkdir()
            sidecar = project / "Docs" / "screenshots" / "round_start.json"
            plan = {
                "project": str(project),
                "device": "booted",
                "game_id": "neon_ring_duel",
                "display_name": "Neon Ring Duel",
                "archetype": "fighter_2_5d",
                "build": ["xcodebuild", "build"],
                "install": ["xcrun", "simctl", "install", "booted", "App.app"],
                "steps": [
                    {
                        "order": 1,
                        "state": "round_start",
                        "screenshot_state_case": "roundStart",
                        "visible_roles": ["player", "opponent", "arena"],
                        "drive": "Launch with round_start; state.phase == .playing.",
                        "expected_evidence": "Declared roles available: player, opponent, arena",
                        "automation": "launch_arg --rkg-screenshot-state round_start",
                        "launch": [
                            "xcrun",
                            "simctl",
                            "launch",
                            "booted",
                            "com.example.game",
                            "--rkg-screenshot-state",
                            "round_start",
                        ],
                        "screenshot": str(project / "Docs" / "screenshots" / "round_start.jpg"),
                        "sidecar": str(sidecar),
                    }
                ],
            }

            def fake_runner(command: list[str], cwd: Path) -> int:
                return 0

            result = execute_capture_plan(plan, runner=fake_runner, sleep_seconds=0)

            self.assertTrue(result["ok"])
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["game_id"], "neon_ring_duel")
            self.assertEqual(payload["state"], "round_start")
            self.assertEqual(payload["drive"], "Launch with round_start; state.phase == .playing.")
            self.assertEqual(payload["visible_roles"], ["player", "opponent", "arena"])
            self.assertEqual(payload["automation"], "launch_arg --rkg-screenshot-state round_start")

    def test_capture_execution_copies_runtime_scene_snapshot_after_successful_screenshot(self) -> None:
        from rkg.capture import execute_capture_plan

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "Generated"
            container = root / "AppData"
            project.mkdir()
            runtime_snapshot = container / "Documents" / "rkg-scene-snapshot-round_start.json"
            runtime_snapshot.parent.mkdir(parents=True)
            runtime_snapshot.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "state": "round_start",
                        "roles": [{"asset_id": "fighter_player", "role": "player", "is_enabled": True}],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            scene_snapshot = project / "Docs" / "screenshots" / "round_start.scene.json"
            plan = {
                "project": str(project),
                "device": "booted",
                "bundle_id": "com.example.game",
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
                        "screenshot": str(project / "Docs" / "screenshots" / "round_start.jpg"),
                        "sidecar": str(project / "Docs" / "screenshots" / "round_start.json"),
                        "scene_snapshot": str(scene_snapshot),
                        "runtime_scene_snapshot": "Documents/rkg-scene-snapshot-round_start.json",
                    }
                ],
            }

            def fake_runner(command: list[str], cwd: Path) -> int:
                return 0

            result = execute_capture_plan(
                plan,
                runner=fake_runner,
                sleep_seconds=0,
                app_container_resolver=lambda device, bundle_id, cwd: container,
            )

            self.assertTrue(result["ok"])
            self.assertEqual(json.loads(scene_snapshot.read_text(encoding="utf-8"))["state"], "round_start")

    def test_capture_execution_writes_role_pixel_evidence_from_runtime_scene_snapshot(self) -> None:
        from rkg.capture import execute_capture_plan

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "Generated"
            container = root / "AppData"
            project.mkdir()
            runtime_snapshot = container / "Documents" / "rkg-scene-snapshot-round_start.json"
            runtime_snapshot.parent.mkdir(parents=True)
            runtime_snapshot.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "state": "round_start",
                        "roles": [
                            {
                                "asset_id": "fighter_player",
                                "role": "player",
                                "entity_name": "rkg|asset=fighter_player|role=player",
                                "is_enabled": True,
                                "position": {"x": -0.42, "y": 0.02, "z": -0.82},
                                "visual_bounds": {
                                    "center": {"x": -0.42, "y": 0.02, "z": -0.82},
                                    "extents": {"x": 0.24, "y": 0.24, "z": 0.2},
                                },
                            },
                            {
                                "asset_id": "duel_arena",
                                "role": "arena",
                                "entity_name": "rkg|asset=duel_arena|role=arena",
                                "is_enabled": True,
                                "position": {"x": 0.0, "y": -0.45, "z": -0.08},
                                "visual_bounds": {
                                    "center": {"x": 0.0, "y": -0.45, "z": -0.08},
                                    "extents": {"x": 2.4, "y": 0.0, "z": 2.4},
                                },
                            },
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            sidecar = project / "Docs" / "screenshots" / "round_start.json"
            scene_snapshot = project / "Docs" / "screenshots" / "round_start.scene.json"
            plan = {
                "project": str(project),
                "device": "booted",
                "bundle_id": "com.example.game",
                "game_id": "neon_ring_duel",
                "display_name": "Neon Ring Duel",
                "archetype": "fighter_2_5d",
                "build": ["xcodebuild", "build"],
                "install": ["xcrun", "simctl", "install", "booted", "App.app"],
                "steps": [
                    {
                        "order": 1,
                        "state": "round_start",
                        "screenshot_state_case": "roundStart",
                        "visible_roles": ["player", "arena"],
                        "drive": "Launch with round_start.",
                        "expected_evidence": "Declared roles available: player, arena",
                        "automation": "launch_arg --rkg-screenshot-state round_start",
                        "launch": [
                            "xcrun",
                            "simctl",
                            "launch",
                            "booted",
                            "com.example.game",
                            "--rkg-screenshot-state",
                            "round_start",
                        ],
                        "screenshot": str(project / "Docs" / "screenshots" / "round_start.jpg"),
                        "sidecar": str(sidecar),
                        "scene_snapshot": str(scene_snapshot),
                        "runtime_scene_snapshot": "Documents/rkg-scene-snapshot-round_start.json",
                    }
                ],
            }

            def fake_runner(command: list[str], cwd: Path) -> int:
                return 0

            result = execute_capture_plan(
                plan,
                runner=fake_runner,
                sleep_seconds=0,
                app_container_resolver=lambda device, bundle_id, cwd: container,
            )

            self.assertTrue(result["ok"])
            evidence = json.loads(sidecar.read_text(encoding="utf-8"))["role_pixel_evidence"]
            self.assertEqual(evidence["player"]["asset_id"], "fighter_player")
            self.assertEqual(evidence["player"]["source"], "runtime_scene_snapshot")
            self.assertGreater(evidence["player"]["region"]["width"], 0)
            self.assertLess(evidence["player"]["region"]["x"] + evidence["player"]["region"]["width"], 1)
            self.assertEqual(evidence["arena"]["region"], {"x": 0.05, "y": 0.3, "width": 0.9, "height": 0.48})

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
