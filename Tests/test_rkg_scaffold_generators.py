import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rkg.scaffold as scaffold


def scene_spec() -> dict:
    return {
        "game": {
            "id": "scene_test",
            "display_name": "Scene Test",
            "archetype": "lane_dodger",
            "session_seconds": 60,
            "camera": "fixed_non_ar",
            "input": "drag",
            "monetization": "paid",
        },
        "loop": {
            "player_action": "test state binding",
            "fail_condition": "test failure",
            "scoring": {"hit": 10, "perfect": 25},
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
            "spike": {
                "type": "hazard",
                "role": "obstacle",
                "budget": "900 tris / 512 texture",
                "fallback": "procedural_box",
            },
        },
        "release": {
            "devices": ["iPhone 15"],
            "screenshots": ["gameplay_start", "mid_session", "results"],
        },
    }


class RkgScaffoldGeneratorTests(unittest.TestCase):
    def test_state_bound_game_view_generator_is_archetype_neutral(self) -> None:
        self.assertTrue(hasattr(scaffold, "_state_bound_game_view_swift"))
        self.assertFalse(hasattr(scaffold, "_lane_dodger_game_view_swift"))

        game_view = scaffold._state_bound_game_view_swift()

        self.assertIn("let state: GameSessionState", game_view)
        self.assertIn("func makeCoordinator() -> Coordinator", game_view)
        self.assertIn("context.coordinator.controller.update(state: state)", game_view)

    def test_scene_entity_setup_lines_load_and_bind_first_matching_roles(self) -> None:
        self.assertTrue(hasattr(scaffold, "_scene_entity_setup_lines"))

        entity_lines = scaffold._scene_entity_setup_lines(
            scene_spec(),
            [
                ("playerEntity", {"player"}),
                ("obstacleEntity", {"obstacle", "hazard"}),
            ],
        )

        self.assertIn('let runner = AssetLoader.loadPrimaryEntity(assetId: "runner", role: "player")', entity_lines)
        self.assertIn("playerEntity = runner", entity_lines)
        self.assertIn('let crate = AssetLoader.loadPrimaryEntity(assetId: "crate", role: "obstacle")', entity_lines)
        self.assertIn("obstacleEntity = crate", entity_lines)
        self.assertIn('let spike = AssetLoader.loadPrimaryEntity(assetId: "spike", role: "obstacle")', entity_lines)
        self.assertEqual(entity_lines.count("obstacleEntity ="), 1)


if __name__ == "__main__":
    unittest.main()
