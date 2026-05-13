import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def projectile_spec() -> dict:
    return {
        "game": {
            "id": "shard_volley",
            "display_name": "Shard Volley",
            "archetype": "custom_realitykit",
            "session_seconds": 60,
            "camera": "third_person",
            "input": "drag",
            "monetization": "paid",
            "systems": ["projectile", "shooting", "score"],
        },
        "loop": {
            "player_action": "aim, charge, and launch projectiles at target lanes",
            "fail_condition": "shots expire before enough projectile hits land",
            "scoring": {"hit": 10, "perfect": 25, "clear": 100},
        },
        "assets": {
            "player_proxy": {
                "type": "gameplay_actor",
                "role": "player",
                "budget": "1500 tris / 512 texture",
                "fallback": "procedural_capsule",
            },
            "arena_space": {
                "type": "environment",
                "role": "arena",
                "budget": "1200 tris / 512 texture",
                "fallback": "procedural_arena",
            },
            "weapon_proxy": {
                "type": "weapon_proxy",
                "role": "weapon",
                "budget": "700 tris / 512 texture",
                "fallback": "procedural_weapon",
            },
            "projectile_proxy": {
                "type": "projectile",
                "role": "projectile",
                "budget": "400 tris / 512 texture",
                "fallback": "procedural_sphere",
            },
            "target_proxy": {
                "type": "gameplay_target",
                "role": "target",
                "budget": "700 tris / 512 texture",
                "fallback": "procedural_rings",
            },
        },
        "release": {
            "devices": ["iPhone 15", "iPad"],
            "screenshots": ["gameplay_start", "mid_action", "fail_or_hit", "results"],
        },
    }


class RkgAssetAcceptanceTests(unittest.TestCase):
    def run_rkg(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def test_accept_first_asset_dry_run_selects_target_and_acceptance_screenshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "GameSpec.json"
            spec_path.write_text(json.dumps(projectile_spec(), indent=2) + "\n", encoding="utf-8")
            project = root / "ShardVolley"
            init_result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(project))
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = self.run_rkg(root, "accept-first-asset", str(project), "--dry-run", "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["project"], str(project.resolve()))
            self.assertEqual(payload["asset_id"], "target_proxy")
            self.assertEqual(payload["role"], "target")
            self.assertEqual(payload["source_state"], "fail_or_hit")
            self.assertEqual(payload["source_screenshot"], "Docs/screenshots/fail_or_hit.jpg")
            self.assertEqual(payload["acceptance_screenshot"], "Docs/screenshots/target_proxy_imported.jpg")
            self.assertEqual(
                [step["step"] for step in payload["steps"]],
                [
                    "make_asset",
                    "build_asset",
                    "inspect_usdz",
                    "capture_screenshots",
                    "verify_screenshots",
                    "copy_acceptance_screenshot",
                    "accept_asset",
                    "release_check_assets",
                ],
            )
            self.assertEqual(payload["steps"][0]["command"][:3], ["rkp", "make-asset", "target_proxy"])
            self.assertEqual(payload["steps"][3]["command"], ["rkg", "capture-screenshots", ".", "--device", "booted"])
            self.assertEqual(payload["steps"][4]["command"], ["rkg", "verify-screenshots", "."])
            self.assertEqual(
                payload["steps"][5]["command"],
                ["copy", "Docs/screenshots/fail_or_hit.jpg", "Docs/screenshots/target_proxy_imported.jpg"],
            )
            self.assertEqual(payload["steps"][-1]["command"], ["rkp", "release-check", "--assets"])

    def test_accept_assets_dry_run_plans_all_roles_with_one_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "GameSpec.json"
            spec_path.write_text(json.dumps(projectile_spec(), indent=2) + "\n", encoding="utf-8")
            project = root / "ShardVolley"
            init_result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(project))
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = self.run_rkg(root, "accept-assets", str(project), "--dry-run", "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(
                [asset["asset_id"] for asset in payload["assets"]],
                ["target_proxy", "projectile_proxy", "weapon_proxy", "player_proxy", "arena_space"],
            )
            self.assertEqual(
                {asset["asset_id"]: asset["source_state"] for asset in payload["assets"]},
                {
                    "target_proxy": "fail_or_hit",
                    "projectile_proxy": "mid_action",
                    "weapon_proxy": "mid_action",
                    "player_proxy": "gameplay_start",
                    "arena_space": "gameplay_start",
                },
            )
            step_names = [step["step"] for step in payload["steps"]]
            self.assertEqual(step_names.count("capture_screenshots"), 1)
            self.assertEqual(step_names.count("verify_screenshots"), 1)
            self.assertEqual(step_names.count("release_check_assets"), 1)
            self.assertEqual(step_names.count("make_asset"), 5)
            self.assertEqual(step_names.count("copy_acceptance_screenshot"), 5)
            self.assertEqual(step_names.count("accept_asset"), 5)

    def test_accept_first_asset_dry_run_skips_make_when_blender_script_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "GameSpec.json"
            spec_path.write_text(json.dumps(projectile_spec(), indent=2) + "\n", encoding="utf-8")
            project = root / "ShardVolley"
            init_result = self.run_rkg(root, "init-game", str(spec_path), "--output", str(project))
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            script = project / "Tools" / "blender" / "create_target_proxy.py"
            script.parent.mkdir(parents=True, exist_ok=True)
            script.write_text("print('existing target script')\n", encoding="utf-8")

            result = self.run_rkg(root, "accept-first-asset", str(project), "--dry-run", "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["asset_id"], "target_proxy")
            self.assertEqual(
                [step["step"] for step in payload["steps"]],
                [
                    "build_asset",
                    "inspect_usdz",
                    "capture_screenshots",
                    "verify_screenshots",
                    "copy_acceptance_screenshot",
                    "accept_asset",
                    "release_check_assets",
                ],
            )

    def test_accept_first_asset_execution_captures_copies_and_runs_acceptance_commands(self) -> None:
        from rkg.asset_acceptance import execute_first_asset_acceptance_plan

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "Generated"
            project.mkdir()
            plan = {
                "project": str(project),
                "device": "booted",
                "asset_id": "target_proxy",
                "role": "target",
                "steps": [
                    {"step": "make_asset", "command": ["rkp", "make-asset", "target_proxy"]},
                    {"step": "build_asset", "command": ["rkp", "build-asset", "target_proxy"]},
                    {"step": "inspect_usdz", "command": ["rkp", "inspect-usdz", "target_proxy", "--json"]},
                    {"step": "capture_screenshots", "command": ["rkg", "capture-screenshots", ".", "--device", "booted"]},
                    {"step": "verify_screenshots", "command": ["rkg", "verify-screenshots", "."]},
                    {
                        "step": "copy_acceptance_screenshot",
                        "command": ["copy", "Docs/screenshots/fail_or_hit.jpg", "Docs/screenshots/target_proxy_imported.jpg"],
                    },
                    {
                        "step": "accept_asset",
                        "command": [
                            "rkp",
                            "accept-asset",
                            "target_proxy",
                            "--screenshot",
                            "Docs/screenshots/target_proxy_imported.jpg",
                        ],
                    },
                    {"step": "release_check_assets", "command": ["rkp", "release-check", "--assets"]},
                ],
            }
            calls = []

            def fake_runner(command: list[str], cwd: Path) -> int:
                calls.append((command, cwd))
                return 0

            def fake_capture(project_root: Path, device: str) -> dict:
                screenshot = project_root / "Docs" / "screenshots" / "fail_or_hit.jpg"
                screenshot.parent.mkdir(parents=True)
                screenshot.write_bytes(b"\xff\xd8screenshot\xff\xd9")
                return {"ok": True, "completed": []}

            result = execute_first_asset_acceptance_plan(
                plan,
                runner=fake_runner,
                capture_executor=fake_capture,
                screenshot_verifier=lambda project_root: {"ok": True, "checks": []},
            )

            self.assertTrue(result["ok"])
            self.assertEqual([call[0][1] for call in calls], ["make-asset", "build-asset", "inspect-usdz", "accept-asset", "release-check"])
            self.assertTrue((project / "Docs" / "screenshots" / "target_proxy_imported.jpg").exists())
            self.assertEqual(result["completed"][3]["step"], "capture_screenshots")
            self.assertEqual(result["completed"][4]["step"], "verify_screenshots")
            self.assertEqual(result["completed"][5]["step"], "copy_acceptance_screenshot")

    def test_accept_assets_execution_captures_once_and_accepts_each_asset(self) -> None:
        from rkg.asset_acceptance import execute_asset_acceptance_plan

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "Generated"
            project.mkdir()
            plan = {
                "project": str(project),
                "device": "booted",
                "assets": [
                    {"asset_id": "target_proxy", "role": "target"},
                    {"asset_id": "projectile_proxy", "role": "projectile"},
                ],
                "steps": [
                    {"step": "make_asset", "command": ["rkp", "make-asset", "target_proxy"]},
                    {"step": "build_asset", "command": ["rkp", "build-asset", "target_proxy"]},
                    {"step": "inspect_usdz", "command": ["rkp", "inspect-usdz", "target_proxy", "--json"]},
                    {"step": "make_asset", "command": ["rkp", "make-asset", "projectile_proxy"]},
                    {"step": "build_asset", "command": ["rkp", "build-asset", "projectile_proxy"]},
                    {"step": "inspect_usdz", "command": ["rkp", "inspect-usdz", "projectile_proxy", "--json"]},
                    {"step": "capture_screenshots", "command": ["rkg", "capture-screenshots", ".", "--device", "booted"]},
                    {"step": "verify_screenshots", "command": ["rkg", "verify-screenshots", "."]},
                    {
                        "step": "copy_acceptance_screenshot",
                        "command": ["copy", "Docs/screenshots/fail_or_hit.jpg", "Docs/screenshots/target_proxy_imported.jpg"],
                    },
                    {
                        "step": "accept_asset",
                        "command": [
                            "rkp",
                            "accept-asset",
                            "target_proxy",
                            "--screenshot",
                            "Docs/screenshots/target_proxy_imported.jpg",
                        ],
                    },
                    {
                        "step": "copy_acceptance_screenshot",
                        "command": ["copy", "Docs/screenshots/mid_action.jpg", "Docs/screenshots/projectile_proxy_imported.jpg"],
                    },
                    {
                        "step": "accept_asset",
                        "command": [
                            "rkp",
                            "accept-asset",
                            "projectile_proxy",
                            "--screenshot",
                            "Docs/screenshots/projectile_proxy_imported.jpg",
                        ],
                    },
                    {"step": "release_check_assets", "command": ["rkp", "release-check", "--assets"]},
                ],
            }
            calls = []
            capture_calls = []

            def fake_runner(command: list[str], cwd: Path) -> int:
                calls.append((command, cwd))
                return 0

            def fake_capture(project_root: Path, device: str) -> dict:
                capture_calls.append((project_root, device))
                screenshot_root = project_root / "Docs" / "screenshots"
                screenshot_root.mkdir(parents=True)
                (screenshot_root / "fail_or_hit.jpg").write_bytes(b"\xff\xd8hit\xff\xd9")
                (screenshot_root / "mid_action.jpg").write_bytes(b"\xff\xd8mid\xff\xd9")
                return {"ok": True, "completed": []}

            result = execute_asset_acceptance_plan(
                plan,
                runner=fake_runner,
                capture_executor=fake_capture,
                screenshot_verifier=lambda project_root: {"ok": True, "checks": []},
            )

            self.assertTrue(result["ok"])
            self.assertEqual(len(capture_calls), 1)
            self.assertEqual([call[0][1] for call in calls], ["make-asset", "build-asset", "inspect-usdz", "make-asset", "build-asset", "inspect-usdz", "accept-asset", "accept-asset", "release-check"])
            self.assertTrue((project / "Docs" / "screenshots" / "target_proxy_imported.jpg").exists())
            self.assertTrue((project / "Docs" / "screenshots" / "projectile_proxy_imported.jpg").exists())

    def test_accept_assets_execution_reports_role_pixel_evidence_per_asset(self) -> None:
        from rkg.asset_acceptance import execute_asset_acceptance_plan

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "Generated"
            project.mkdir()
            plan = {
                "project": str(project),
                "device": "booted",
                "assets": [
                    {
                        "asset_id": "target_proxy",
                        "role": "target",
                        "source_state": "fail_or_hit",
                        "source_screenshot": "Docs/screenshots/fail_or_hit.jpg",
                        "acceptance_screenshot": "Docs/screenshots/target_proxy_imported.jpg",
                    },
                    {
                        "asset_id": "projectile_proxy",
                        "role": "projectile",
                        "source_state": "mid_action",
                        "source_screenshot": "Docs/screenshots/mid_action.jpg",
                        "acceptance_screenshot": "Docs/screenshots/projectile_proxy_imported.jpg",
                    },
                ],
                "steps": [
                    {"step": "capture_screenshots", "command": ["rkg", "capture-screenshots", ".", "--device", "booted"]},
                    {"step": "verify_screenshots", "command": ["rkg", "verify-screenshots", "."]},
                    {
                        "step": "copy_acceptance_screenshot",
                        "command": ["copy", "Docs/screenshots/fail_or_hit.jpg", "Docs/screenshots/target_proxy_imported.jpg"],
                    },
                    {
                        "step": "accept_asset",
                        "command": [
                            "rkp",
                            "accept-asset",
                            "target_proxy",
                            "--screenshot",
                            "Docs/screenshots/target_proxy_imported.jpg",
                        ],
                    },
                    {
                        "step": "copy_acceptance_screenshot",
                        "command": ["copy", "Docs/screenshots/mid_action.jpg", "Docs/screenshots/projectile_proxy_imported.jpg"],
                    },
                    {
                        "step": "accept_asset",
                        "command": [
                            "rkp",
                            "accept-asset",
                            "projectile_proxy",
                            "--screenshot",
                            "Docs/screenshots/projectile_proxy_imported.jpg",
                        ],
                    },
                    {"step": "release_check_assets", "command": ["rkp", "release-check", "--assets"]},
                ],
            }

            def fake_capture(project_root: Path, device: str) -> dict:
                screenshot_root = project_root / "Docs" / "screenshots"
                screenshot_root.mkdir(parents=True)
                (screenshot_root / "fail_or_hit.jpg").write_bytes(b"\xff\xd8hit\xff\xd9")
                (screenshot_root / "mid_action.jpg").write_bytes(b"\xff\xd8mid\xff\xd9")
                (screenshot_root / "fail_or_hit.json").write_text(
                    json.dumps(
                        {
                            "role_pixel_evidence": {
                                "target": {
                                    "asset_id": "target_proxy",
                                    "region": {"x": 0.42, "y": 0.22, "width": 0.2, "height": 0.24},
                                    "source": "runtime_scene_snapshot",
                                }
                            }
                        }
                    ),
                    encoding="utf-8",
                )
                (screenshot_root / "mid_action.json").write_text(
                    json.dumps(
                        {
                            "role_pixel_evidence": {
                                "projectile": {
                                    "asset_id": "projectile_proxy",
                                    "region": {"x": 0.48, "y": 0.36, "width": 0.18, "height": 0.18},
                                    "source": "runtime_scene_snapshot",
                                }
                            }
                        }
                    ),
                    encoding="utf-8",
                )
                return {"ok": True, "completed": []}

            result = execute_asset_acceptance_plan(
                plan,
                runner=lambda command, cwd: 0,
                capture_executor=fake_capture,
                screenshot_verifier=lambda project_root: {
                    "ok": True,
                    "checks": [
                        {"state": "fail_or_hit", "status": "ok"},
                        {"state": "mid_action", "status": "ok"},
                    ],
                },
            )

            self.assertTrue(result["ok"])
            reports = {report["asset_id"]: report for report in result["asset_reports"]}
            self.assertEqual(reports["target_proxy"]["role_pixel_evidence_status"], "present")
            self.assertEqual(reports["target_proxy"]["screenshot_status"], "ok")
            self.assertEqual(reports["target_proxy"]["role_pixel_evidence"]["region"]["x"], 0.42)
            self.assertEqual(reports["projectile_proxy"]["role_pixel_evidence"]["asset_id"], "projectile_proxy")

    def test_acceptance_runner_prefers_workspace_pythonpath_for_cli_entrypoints(self) -> None:
        from rkg.asset_acceptance import _run_command

        with patch("rkg.asset_acceptance.subprocess.run") as run:
            run.return_value.returncode = 0

            exit_code = _run_command(["rkp", "status"], Path("/tmp"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(run.call_args.args[0], [sys.executable, "-m", "rkp.cli", "status"])
        env = run.call_args.kwargs["env"]
        self.assertIn(str(ROOT / "src"), env["PYTHONPATH"])

    def test_acceptance_runner_dispatches_rkg_entrypoint_through_workspace_module(self) -> None:
        from rkg.asset_acceptance import _run_command

        with patch("rkg.asset_acceptance.subprocess.run") as run:
            run.return_value.returncode = 0

            exit_code = _run_command(["rkg", "qa-plan", "GameSpec.json"], Path("/tmp"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(run.call_args.args[0], [sys.executable, "-m", "rkg.cli", "qa-plan", "GameSpec.json"])


if __name__ == "__main__":
    unittest.main()
