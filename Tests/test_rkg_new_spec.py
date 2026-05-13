import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RkgNewSpecTests(unittest.TestCase):
    def run_rkg(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def test_new_spec_writes_valid_fighter_game_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "GameSpec.json"

            result = self.run_rkg(
                root,
                "new-spec",
                "fighter_2_5d",
                "--title",
                "Neon Ring Duel",
                "--output",
                str(spec_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            self.assertEqual(spec["game"]["id"], "neon_ring_duel")
            self.assertEqual(spec["game"]["display_name"], "Neon Ring Duel")
            self.assertEqual(spec["game"]["archetype"], "fighter_2_5d")
            self.assertEqual(spec["game"]["input"], "tap_swipe")
            self.assertEqual(spec["assets"]["fighter_player"]["role"], "player")
            self.assertEqual(spec["assets"]["fighter_opponent"]["role"], "opponent")
            self.assertEqual(spec["assets"]["duel_arena"]["role"], "arena")
            self.assertEqual(spec["release"]["screenshots"], ["round_start", "mid_combo", "perfect_dodge", "knockout"])

    def test_new_spec_writes_valid_flappy_game_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "GameSpec.json"

            result = self.run_rkg(
                root,
                "new-spec",
                "flappy_side_scroller",
                "--title",
                "Flappy Reef",
                "--output",
                str(spec_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            self.assertEqual(spec["game"]["id"], "flappy_reef")
            self.assertEqual(spec["game"]["display_name"], "Flappy Reef")
            self.assertEqual(spec["game"]["archetype"], "flappy_side_scroller")
            self.assertEqual(spec["game"]["input"], "tap")
            self.assertEqual(spec["assets"]["bird_player"]["role"], "player")
            self.assertEqual(spec["assets"]["pipe_gate"]["role"], "obstacle")
            self.assertEqual(spec["assets"]["reef_lane"]["role"], "arena")
            self.assertEqual(
                spec["release"]["screenshots"],
                ["gameplay_start", "mid_flight", "near_gap", "collision", "results"],
            )

    def test_new_spec_refuses_unknown_archetype(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = self.run_rkg(root, "new-spec", "open_world_mmo", "--title", "Too Big", "--output", "GameSpec.json")

            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown archetype", result.stderr)


if __name__ == "__main__":
    unittest.main()
