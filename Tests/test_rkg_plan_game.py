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

from rkg.plan import build_game_plan


def valid_spec() -> dict:
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
            "devices": ["iPhone 15", "iPad"],
            "screenshots": ["gameplay_start", "mid_session", "results"],
        },
    }


def lane_dodger_spec() -> dict:
    spec = valid_spec()
    spec["game"]["id"] = "lane_dash"
    spec["game"]["display_name"] = "Lane Dash"
    spec["game"]["archetype"] = "lane_dodger"
    spec["game"]["input"] = "drag"
    spec["assets"] = {
        "runner": {
            "type": "character",
            "role": "player",
            "budget": "1500 tris / 512 texture",
            "fallback": "procedural_capsule",
        },
        "crate": {
            "type": "hazard",
            "role": "obstacle",
            "budget": "900 tris / 512 texture",
            "fallback": "procedural_box",
        },
        "lane_floor": {
            "type": "environment",
            "role": "arena",
            "budget": "800 tris / 512 texture",
            "fallback": "procedural_grid",
        },
    }
    spec["release"]["screenshots"] = ["gameplay_start", "mid_session", "near_miss", "results"]
    return spec


def fighter_spec() -> dict:
    spec = valid_spec()
    spec["game"]["id"] = "neon_ring_duel"
    spec["game"]["display_name"] = "Neon Ring Duel"
    spec["game"]["archetype"] = "fighter_2_5d"
    spec["game"]["input"] = "tap_swipe"
    spec["loop"]["player_action"] = "tap attack, swipe dodge, and time guard windows"
    spec["loop"]["fail_condition"] = "fighter health reaches zero"
    spec["loop"]["scoring"] = {"hit": 10, "perfect": 25, "knockout": 100}
    spec["assets"] = {
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
    }
    spec["release"]["screenshots"] = ["round_start", "mid_combo", "perfect_dodge", "knockout"]
    return spec


class RkgPlanGameTests(unittest.TestCase):
    def run_rkg(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def write_spec(self, root: Path, spec: dict) -> Path:
        path = root / "GameSpec.json"
        path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
        return path

    def test_build_game_plan_exposes_files_roles_and_screenshots(self) -> None:
        payload = build_game_plan(valid_spec())

        self.assertEqual(payload["game_id"], "ring_dash")
        self.assertEqual(payload["swift_name"], "RingDash")
        self.assertEqual(payload["archetype"]["id"], "target_shooter")
        self.assertIn("Sources/RingDash/GameState.swift", payload["files"])
        self.assertIn("Sources/RingDash/SessionControl.swift", payload["files"])
        self.assertIn("Sources/RingDash/FeedbackState.swift", payload["files"])
        self.assertIn("Sources/RingDash/InputIntent.swift", payload["files"])
        self.assertIn("Sources/RingDash/ScreenshotState.swift", payload["files"])
        self.assertIn("Sources/RingDash/CameraRig.swift", payload["files"])
        self.assertIn("Sources/RingDash/InputController.swift", payload["files"])
        self.assertIn("Sources/RingDash/SystemFlags.swift", payload["files"])
        self.assertIn("Sources/RingDash/FallbackFactory.swift", payload["files"])
        self.assertIn("Sources/RingDash/RuntimeSceneSnapshot.swift", payload["files"])
        self.assertIn("Docs/store/screenshots.md", payload["files"])
        self.assertIn("Docs/store/screenshot-qa.md", payload["files"])
        self.assertIn("Docs/store/monetization.md", payload["files"])
        self.assertEqual(payload["asset_roles"]["target_basic"], "target")
        self.assertEqual(payload["asset_roles"]["arena_floor"], "arena")
        self.assertEqual(payload["screenshot_states"], ["gameplay_start", "mid_session", "results"])
        self.assertIn("screenshot_proofs", payload)
        self.assertIn("state.phase == .playing", payload["screenshot_proofs"]["gameplay_start"])

    def test_build_game_plan_exposes_runtime_entities_for_declared_roles(self) -> None:
        payload = build_game_plan(lane_dodger_spec())

        self.assertEqual(
            payload["runtime_entities"],
            [
                {
                    "asset_id": "runner",
                    "role": "player",
                    "fallback": "procedural_capsule",
                    "variable": "runner",
                    "position": "[0, 0, -0.85]",
                },
                {
                    "asset_id": "crate",
                    "role": "obstacle",
                    "fallback": "procedural_box",
                    "variable": "crate",
                    "position": "[0.00, 0.00, -1.25]",
                },
                {
                    "asset_id": "lane_floor",
                    "role": "arena",
                    "fallback": "procedural_grid",
                    "variable": "laneFloor",
                    "position": "[0, -0.45, 0]",
                },
            ],
        )
        self.assertIn("state.nearMisses > 0", payload["screenshot_proofs"]["near_miss"])

    def test_build_game_plan_exposes_fighter_runtime_entities_and_proofs(self) -> None:
        payload = build_game_plan(fighter_spec())

        self.assertEqual(payload["archetype"]["id"], "fighter_2_5d")
        self.assertEqual(payload["asset_roles"]["fighter_opponent"], "opponent")
        self.assertEqual(payload["screenshot_states"], ["round_start", "mid_combo", "perfect_dodge", "knockout"])
        self.assertIn("state.comboCount > 0", payload["screenshot_proofs"]["mid_combo"])
        self.assertIn("state.isKnockout == true", payload["screenshot_proofs"]["knockout"])
        self.assertEqual(
            payload["runtime_entities"],
            [
                {
                    "asset_id": "fighter_player",
                    "role": "player",
                    "fallback": "procedural_capsule",
                    "variable": "fighterPlayer",
                    "position": "[0, 0, -0.85]",
                },
                {
                    "asset_id": "fighter_opponent",
                    "role": "opponent",
                    "fallback": "procedural_capsule",
                    "variable": "fighterOpponent",
                    "position": "[0.35, 0, -0.85]",
                },
                {
                    "asset_id": "duel_arena",
                    "role": "arena",
                    "fallback": "procedural_lane",
                    "variable": "duelArena",
                    "position": "[0, -0.45, 0]",
                },
            ],
        )

    def test_plan_game_cli_prints_json_without_creating_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, valid_spec())

            result = self.run_rkg(root, "plan-game", str(spec_path), "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["swift_name"], "RingDash")
            self.assertFalse((root / "RingDash").exists())

    def test_plan_game_cli_rejects_invalid_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = valid_spec()
            spec["release"]["screenshots"].append("boss_intro")
            spec_path = self.write_spec(root, spec)

            result = self.run_rkg(root, "plan-game", str(spec_path), "--json")

            self.assertEqual(result.returncode, 1)
            self.assertIn("boss_intro", result.stderr)


if __name__ == "__main__":
    unittest.main()
