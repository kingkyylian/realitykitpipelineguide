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


class StorePackTests(unittest.TestCase):
    def test_store_pack_includes_screenshots_and_monetization_files(self) -> None:
        pack = build_store_pack(valid_spec())

        self.assertIn("Docs/store/screenshots.md", pack)
        self.assertIn("Docs/store/screenshot-qa.md", pack)
        self.assertIn("Docs/store/monetization.md", pack)
        screenshots = pack["Docs/store/screenshots.md"]
        self.assertIn("| gameplay_start |", screenshots)
        self.assertIn("Docs/screenshots/gameplay_start.jpg", screenshots)
        self.assertIn("target, arena", screenshots)
        monetization = pack["Docs/store/monetization.md"]
        self.assertIn("Model: paid", monetization)
        self.assertIn("No external unlocks", monetization)

    def test_screenshot_checklist_includes_generated_proof_cues(self) -> None:
        pack = build_store_pack(lane_dodger_spec())

        screenshots = pack["Docs/store/screenshots.md"]
        self.assertIn("| State | Purpose | Generated proof cue | Required asset roles | Evidence path |", screenshots)
        self.assertIn("state.phase == .playing", screenshots)
        self.assertIn("state.nearMisses > 0", screenshots)
        self.assertIn("| near_miss |", screenshots)

    def test_screenshot_qa_runbook_sequences_generated_proof_cues(self) -> None:
        pack = build_store_pack(lane_dodger_spec())

        runbook = pack["Docs/store/screenshot-qa.md"]
        self.assertIn("| Order | State | Drive the game to this state | Expected evidence | Capture path |", runbook)
        self.assertIn("| 1 | gameplay_start | Tap Start; state.phase == .playing;", runbook)
        self.assertIn("| 3 | near_miss | Swipe next to the obstacle, then tap Dodge; state.nearMisses > 0.", runbook)
        self.assertIn("Required roles visible: player, obstacle, arena", runbook)


if __name__ == "__main__":
    unittest.main()
