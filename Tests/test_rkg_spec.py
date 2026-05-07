import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rkg.spec import GameSpecError, assert_valid_game_spec, validate_game_spec


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
            "scoring": {
                "hit": 10,
                "perfect": 25,
                "streak_bonus": True,
            },
        },
        "assets": {
            "target_basic": {
                "type": "gameplay_target",
                "budget": "1500 tris / 512 texture",
                "fallback": "procedural_rings",
            },
            "arena_floor": {
                "type": "environment",
                "budget": "800 tris / 512 texture",
                "fallback": "procedural_grid",
            },
        },
        "release": {
            "devices": ["iPhone 15", "iPad"],
            "screenshots": ["gameplay_start", "mid_session", "results"],
        },
    }


class GameSpecTests(unittest.TestCase):
    def test_valid_spec_has_no_issues(self) -> None:
        self.assertEqual(validate_game_spec(valid_spec()), [])

    def test_missing_required_game_field_is_reported(self) -> None:
        spec = valid_spec()
        del spec["game"]["display_name"]

        issues = validate_game_spec(spec)

        self.assertIn("game.display_name is required", issues)

    def test_missing_asset_fallback_is_reported(self) -> None:
        spec = valid_spec()
        del spec["assets"]["target_basic"]["fallback"]

        issues = validate_game_spec(spec)

        self.assertIn("assets.target_basic.fallback is required", issues)

    def test_rejects_long_first_wave_arcade_session(self) -> None:
        spec = valid_spec()
        spec["game"]["session_seconds"] = 240

        issues = validate_game_spec(spec)

        self.assertIn("game.session_seconds must be 180 or less for first-wave arcade games", issues)

    def test_rejects_external_unlock_for_app_store_specs(self) -> None:
        spec = valid_spec()
        spec["game"]["monetization"] = "external_unlock"

        issues = validate_game_spec(spec)

        self.assertIn("game.monetization external_unlock is not allowed for App Store builds", issues)

    def test_allows_external_unlock_when_app_store_gate_is_disabled(self) -> None:
        spec = valid_spec()
        spec["game"]["monetization"] = "external_unlock"

        issues = validate_game_spec(spec, app_store=False)

        self.assertNotIn("game.monetization external_unlock is not allowed for App Store builds", issues)

    def test_rejects_empty_release_devices(self) -> None:
        spec = valid_spec()
        spec["release"]["devices"] = []

        issues = validate_game_spec(spec)

        self.assertIn("release.devices must contain at least one device", issues)

    def test_rejects_non_snake_case_game_id(self) -> None:
        spec = valid_spec()
        spec["game"]["id"] = "RingDash"

        issues = validate_game_spec(spec)

        self.assertIn("game.id must be snake_case", issues)

    def test_assert_valid_game_spec_raises_with_all_issues(self) -> None:
        spec = valid_spec()
        spec["game"]["session_seconds"] = 240
        del spec["assets"]["target_basic"]["fallback"]

        with self.assertRaises(GameSpecError) as context:
            assert_valid_game_spec(spec)

        message = str(context.exception)
        self.assertIn("game.session_seconds must be 180 or less for first-wave arcade games", message)
        self.assertIn("assets.target_basic.fallback is required", message)


if __name__ == "__main__":
    unittest.main()
