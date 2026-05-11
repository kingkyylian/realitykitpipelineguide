import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RkgNewGameTests(unittest.TestCase):
    def run_rkg(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def test_new_game_writes_racing_realitykit_skeleton_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "GameSpec.json"

            result = self.run_rkg(
                root,
                "new-game",
                "--title",
                "Desert Chase",
                "--camera",
                "chase",
                "--input",
                "tilt_tap",
                "--systems",
                "racing,lap_timer,collision",
                "--output",
                str(spec_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            self.assertEqual(spec["game"]["id"], "desert_chase")
            self.assertEqual(spec["game"]["archetype"], "custom_realitykit")
            self.assertEqual(spec["game"]["camera"], "chase")
            self.assertEqual(spec["game"]["input"], "tilt_tap")
            self.assertEqual(spec["game"]["systems"], ["racing", "lap_timer", "collision"])
            self.assertEqual(spec["assets"]["player_vehicle"]["role"], "player")
            self.assertEqual(spec["assets"]["race_track"]["role"], "arena")
            self.assertEqual(spec["assets"]["track_obstacle"]["role"], "obstacle")
            self.assertEqual(spec["release"]["screenshots"], ["gameplay_start", "mid_action", "fail_or_hit", "results"])

            validate = self.run_rkg(root, "validate-spec", str(spec_path))
            self.assertEqual(validate.returncode, 0, validate.stderr)
            self.assertIn("GameSpec ok", validate.stdout)

    def test_new_game_writes_fps_shooter_realitykit_skeleton_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = root / "GameSpec.json"

            result = self.run_rkg(
                root,
                "new-game",
                "--title",
                "Room Breach",
                "--camera",
                "first_person",
                "--input",
                "dual_stick",
                "--systems",
                "weapon,hitscan,enemies,health",
                "--output",
                str(spec_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            self.assertEqual(spec["game"]["id"], "room_breach")
            self.assertEqual(spec["game"]["camera"], "first_person")
            self.assertEqual(spec["game"]["input"], "dual_stick")
            self.assertEqual(spec["assets"]["player_proxy"]["role"], "player")
            self.assertEqual(spec["assets"]["weapon_proxy"]["role"], "weapon")
            self.assertEqual(spec["assets"]["enemy_proxy"]["role"], "enemy")
            self.assertEqual(spec["assets"]["cover_block"]["role"], "cover")

            validate = self.run_rkg(root, "validate-spec", str(spec_path), "--json")
            self.assertEqual(validate.returncode, 0, validate.stderr)
            payload = json.loads(validate.stdout)
            self.assertTrue(payload["ok"])

    def test_new_game_rejects_unsupported_system(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = self.run_rkg(
                root,
                "new-game",
                "--title",
                "Infinite City",
                "--camera",
                "third_person",
                "--input",
                "dual_stick",
                "--systems",
                "mmo_backend",
                "--output",
                "GameSpec.json",
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("unsupported systems: mmo_backend", result.stderr)

    def test_new_game_rejects_unsupported_camera(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = self.run_rkg(
                root,
                "new-game",
                "--title",
                "Bad Camera",
                "--camera",
                "orbit",
                "--input",
                "tap",
                "--systems",
                "score",
                "--output",
                "GameSpec.json",
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("unsupported camera: orbit", result.stderr)

    def test_new_game_rejects_unsupported_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = self.run_rkg(
                root,
                "new-game",
                "--title",
                "Bad Input",
                "--camera",
                "fixed_non_ar",
                "--input",
                "voice",
                "--systems",
                "score",
                "--output",
                "GameSpec.json",
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("unsupported input: voice", result.stderr)


if __name__ == "__main__":
    unittest.main()
