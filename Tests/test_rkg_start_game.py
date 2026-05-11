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

from rkg.start_game import recommend_start_from_idea


def projectile_idea() -> dict:
    return {
        "idea": {
            "title": "Shard Volley",
            "player_action": "aim, charge, and launch projectiles at crystal targets",
            "differentiator": "the projectile lane shifts after every charged hit",
            "first_playable_assets": ["player_proxy", "weapon_proxy", "projectile_proxy", "target_proxy"],
            "video_hook": "a thirty-second clip shows charging, a projectile arc, a hit, and the result screen",
            "app_review_risk": "low",
            "monetization": "paid",
            "scope_flags": [],
        }
    }


class RkgStartGameTests(unittest.TestCase):
    def run_rkg(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def test_recommend_start_from_projectile_idea_selects_runtime_systems(self) -> None:
        payload = recommend_start_from_idea(projectile_idea())

        self.assertEqual(payload["title"], "Shard Volley")
        self.assertEqual(payload["archetype"], "custom_realitykit")
        self.assertEqual(payload["camera"], "third_person")
        self.assertEqual(payload["input"], "drag")
        self.assertEqual(payload["systems"], ["projectile", "shooting", "score"])
        self.assertIn("projectile", payload["reason"])

    def test_start_game_scores_idea_writes_spec_project_and_qa_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            idea = root / "idea.json"
            output = root / "ShardVolley"
            idea.write_text(json.dumps(projectile_idea(), indent=2) + "\n", encoding="utf-8")

            result = self.run_rkg(root, "start-game", str(idea), "--output", str(output), "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["score"]["verdict"], "pass")
            self.assertEqual(payload["recommendation"]["systems"], ["projectile", "shooting", "score"])
            self.assertTrue(payload["paths"]["spec"].endswith("GameSpec.json"))
            self.assertEqual(payload["qa_plan"]["steps"][1]["state"], "mid_action")
            self.assertEqual(payload["qa_plan"]["steps"][1]["scene_snapshot_path"], "Docs/screenshots/mid_action.scene.json")
            spec = json.loads((output / "GameSpec.json").read_text(encoding="utf-8"))
            self.assertEqual(spec["game"]["id"], "shard_volley")
            self.assertEqual(spec["game"]["camera"], "third_person")
            self.assertEqual(spec["game"]["input"], "drag")
            self.assertEqual(spec["game"]["systems"], ["projectile", "shooting", "score"])
            self.assertTrue((output / "Sources" / "ShardVolley" / "RuntimeSceneSnapshot.swift").exists())
            self.assertTrue((output / "Docs" / "store" / "screenshot-qa.md").exists())

    def test_start_game_refuses_rejected_idea_without_writing_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            idea_payload = projectile_idea()
            idea_payload["idea"]["scope_flags"] = ["open_world", "backend"]
            idea = root / "idea.json"
            output = root / "TooLarge"
            idea.write_text(json.dumps(idea_payload, indent=2) + "\n", encoding="utf-8")

            result = self.run_rkg(root, "start-game", str(idea), "--output", str(output), "--json")

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["score"]["verdict"], "reject")
            self.assertIn("idea verdict reject", result.stderr)
            self.assertFalse((output / "GameSpec.json").exists())


if __name__ == "__main__":
    unittest.main()
