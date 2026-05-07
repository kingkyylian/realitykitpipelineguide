import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rkg.store_pack import build_store_pack


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


class StorePackTests(unittest.TestCase):
    def test_store_pack_includes_screenshots_and_monetization_files(self) -> None:
        pack = build_store_pack(valid_spec())

        self.assertIn("Docs/store/screenshots.md", pack)
        self.assertIn("Docs/store/monetization.md", pack)
        screenshots = pack["Docs/store/screenshots.md"]
        self.assertIn("| gameplay_start |", screenshots)
        self.assertIn("Docs/screenshots/gameplay_start.jpg", screenshots)
        self.assertIn("target, arena", screenshots)
        monetization = pack["Docs/store/monetization.md"]
        self.assertIn("Model: paid", monetization)
        self.assertIn("No external unlocks", monetization)


if __name__ == "__main__":
    unittest.main()
