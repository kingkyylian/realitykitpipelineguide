import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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


class RkgValidateSpecCliTests(unittest.TestCase):
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

    def test_validate_spec_cli_returns_zero_for_valid_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.write_spec(root, valid_spec())

            result = self.run_rkg(root, "validate-spec", str(spec_path), "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["issues"], [])

    def test_validate_spec_cli_returns_nonzero_for_invalid_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = valid_spec()
            spec["game"]["archetype"] = "city_builder"
            spec_path = self.write_spec(root, spec)

            result = self.run_rkg(root, "validate-spec", str(spec_path), "--json")

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertIn("game.archetype is not supported: city_builder", payload["issues"])

    def test_validate_spec_cli_rejects_missing_required_archetype_roles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = valid_spec()
            spec["game"]["archetype"] = "lane_dodger"
            spec["game"]["input"] = "drag"
            spec["assets"] = {
                "runner": {
                    "type": "character",
                    "role": "player",
                    "budget": "1500 tris / 512 texture",
                    "fallback": "procedural_capsule",
                },
                "lane_floor": {
                    "type": "environment",
                    "role": "arena",
                    "budget": "800 tris / 512 texture",
                    "fallback": "procedural_grid",
                },
            }
            spec["release"]["screenshots"] = ["gameplay_start", "mid_session", "near_miss", "results"]
            spec_path = self.write_spec(root, spec)

            result = self.run_rkg(root, "validate-spec", str(spec_path), "--json")

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertIn("assets missing required role obstacle for lane_dodger", payload["issues"])

    def test_validate_spec_cli_rejects_input_not_supported_by_archetype(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = valid_spec()
            spec["game"]["input"] = "drag"
            spec_path = self.write_spec(root, spec)

            result = self.run_rkg(root, "validate-spec", str(spec_path), "--json")

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertIn("game.input drag is not supported by target_shooter", payload["issues"])

    def test_validate_spec_cli_rejects_camera_not_supported_by_archetype(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = valid_spec()
            spec["game"]["camera"] = "ar_world"
            spec_path = self.write_spec(root, spec)

            result = self.run_rkg(root, "validate-spec", str(spec_path), "--json")

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertIn("game.camera ar_world is not supported by target_shooter", payload["issues"])


if __name__ == "__main__":
    unittest.main()
