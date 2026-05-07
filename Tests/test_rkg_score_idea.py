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

from rkg.idea_score import score_game_idea


def focused_idea() -> dict:
    return {
        "idea": {
            "title": "Ring Dash",
            "player_action": "tap moving targets every few seconds",
            "differentiator": "precision rings shrink as the streak grows",
            "first_playable_assets": ["target_basic", "arena_floor", "timer_gate"],
            "video_hook": "a thirty-second clip shows shrinking rings, streaks, and the result screen",
            "app_review_risk": "low",
            "monetization": "paid",
            "scope_flags": [],
        }
    }


class IdeaScoreTests(unittest.TestCase):
    def test_focused_small_arcade_idea_passes_factory_gate(self) -> None:
        result = score_game_idea(focused_idea())

        self.assertEqual(result.verdict, "pass")
        self.assertGreaterEqual(result.score, 80)
        self.assertEqual(result.issues, [])
        self.assertIn("small first playable asset count", result.strengths)

    def test_large_backend_heavy_idea_is_rejected(self) -> None:
        idea = focused_idea()
        idea["idea"]["first_playable_assets"] = [
            "hero",
            "city",
            "traffic",
            "enemy",
            "npc",
            "shop",
            "quest_board",
        ]
        idea["idea"]["scope_flags"] = ["multiplayer", "open_world", "backend"]

        result = score_game_idea(idea)

        self.assertEqual(result.verdict, "reject")
        self.assertLess(result.score, 60)
        self.assertIn("scope flag multiplayer is too large for the first factory wave", result.issues)
        self.assertIn("first_playable_assets should contain 3 to 5 asset classes", result.issues)

    def test_missing_required_answer_is_reported(self) -> None:
        idea = focused_idea()
        del idea["idea"]["differentiator"]

        result = score_game_idea(idea)

        self.assertEqual(result.verdict, "reject")
        self.assertIn("idea.differentiator is required", result.issues)


class RkgScoreIdeaCliTests(unittest.TestCase):
    def run_rkg(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def test_score_idea_prints_json_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "idea.json"
            path.write_text(json.dumps(focused_idea(), indent=2) + "\n", encoding="utf-8")

            result = self.run_rkg(root, "score-idea", str(path), "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["verdict"], "pass")
            self.assertGreaterEqual(payload["score"], 80)

    def test_score_idea_returns_nonzero_for_rejected_idea(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            idea = focused_idea()
            idea["idea"]["scope_flags"] = ["user_generated_content"]
            path = root / "idea.json"
            path.write_text(json.dumps(idea, indent=2) + "\n", encoding="utf-8")

            result = self.run_rkg(root, "score-idea", str(path), "--json")

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["verdict"], "reject")


if __name__ == "__main__":
    unittest.main()
