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


def lane_dodger_spec() -> dict:
    return {
        "game": {
            "id": "lane_dash",
            "display_name": "Lane Dash",
            "archetype": "lane_dodger",
            "session_seconds": 60,
            "camera": "fixed_non_ar",
            "input": "drag",
            "monetization": "paid",
        },
        "loop": {
            "player_action": "drag between lanes to dodge obstacles",
            "fail_condition": "hit an obstacle",
            "scoring": {"hit": 10, "perfect": 25, "streak_bonus": True},
        },
        "assets": {
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
        },
        "release": {
            "devices": ["iPhone 15", "iPad"],
            "screenshots": ["gameplay_start", "mid_session", "near_miss", "results"],
        },
    }


class RkgQaPlanTests(unittest.TestCase):
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

    def test_build_qa_plan_sequences_screenshot_proofs_for_capture(self) -> None:
        payload = build_qa_plan(lane_dodger_spec())

        self.assertEqual(payload["game_id"], "lane_dash")
        self.assertEqual(payload["display_name"], "Lane Dash")
        self.assertEqual(payload["archetype"], "lane_dodger")
        self.assertEqual(payload["preflight"], ["rkg verify-game <generated-project>"])
        self.assertEqual(payload["steps"][0]["order"], 1)
        self.assertEqual(payload["steps"][0]["state"], "gameplay_start")
        self.assertEqual(payload["steps"][0]["screenshot_state_case"], "gameplayStart")
        self.assertIn("state.phase == .playing", payload["steps"][0]["drive"])
        self.assertEqual(payload["steps"][2]["state"], "near_miss")
        self.assertEqual(payload["steps"][2]["screenshot_state_case"], "nearMiss")
        self.assertIn("state.nearMisses > 0", payload["steps"][2]["drive"])
        self.assertEqual(payload["steps"][2]["visible_roles"], ["player", "obstacle", "arena"])
        self.assertEqual(payload["steps"][2]["capture_path"], "Docs/screenshots/near_miss.jpg")

    def test_qa_plan_cli_prints_json_without_creating_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, lane_dodger_spec())

            result = self.run_rkg(root, "qa-plan", str(spec_path), "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["steps"][2]["state"], "near_miss")
            self.assertIn("state.nearMisses > 0", payload["steps"][2]["drive"])
            self.assertFalse((root / "LaneDash").exists())

    def test_qa_plan_cli_prints_manual_capture_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, lane_dodger_spec())

            result = self.run_rkg(root, "qa-plan", str(spec_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("qa plan: Lane Dash (lane_dash)", result.stdout)
            self.assertIn("preflight: rkg verify-game <generated-project>", result.stdout)
            self.assertIn("3. near_miss -> Docs/screenshots/near_miss.jpg", result.stdout)
            self.assertIn("drive: Swipe next to the obstacle, then tap Dodge; state.nearMisses > 0.", result.stdout)

    def test_qa_plan_cli_rejects_invalid_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = lane_dodger_spec()
            spec["release"]["screenshots"].append("boss_intro")
            spec_path = self.write_spec(root, spec)

            result = self.run_rkg(root, "qa-plan", str(spec_path), "--json")

            self.assertEqual(result.returncode, 1)
            self.assertIn("boss_intro", result.stderr)


if __name__ == "__main__":
    unittest.main()
