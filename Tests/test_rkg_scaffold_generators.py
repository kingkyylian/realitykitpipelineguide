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

        self.assertIn(
            'let runner = AssetLoader.loadPrimaryEntity(assetId: "runner", role: "player", fallback: "procedural_capsule")',
            entity_lines,
        )
        self.assertIn("playerEntity = runner", entity_lines)
        self.assertIn(
            'let crate = AssetLoader.loadPrimaryEntity(assetId: "crate", role: "obstacle", fallback: "procedural_box")',
            entity_lines,
        )
        self.assertIn("obstacleEntity = crate", entity_lines)
        self.assertIn(
            'let spike = AssetLoader.loadPrimaryEntity(assetId: "spike", role: "obstacle", fallback: "procedural_box")',
            entity_lines,
        )
        self.assertEqual(entity_lines.count("obstacleEntity ="), 1)

    def test_screenshot_state_generator_emits_typed_release_states(self) -> None:
        self.assertTrue(hasattr(scaffold, "_screenshot_state_swift"))

        swift = scaffold._screenshot_state_swift(scene_spec())

        self.assertIn("enum ScreenshotState: String, CaseIterable, Identifiable", swift)
        self.assertIn('static let launchEnvironmentKey = "RKG_SCREENSHOT_STATE"', swift)
        self.assertIn('static let launchArgumentKey = "--rkg-screenshot-state"', swift)
        self.assertIn('case gameplayStart = "gameplay_start"', swift)
        self.assertIn('case midSession = "mid_session"', swift)
        self.assertIn('case results = "results"', swift)
        self.assertIn("static var requested: ScreenshotState?", swift)
        self.assertIn("process.environment[launchEnvironmentKey]", swift)
        self.assertIn("process.arguments.firstIndex(of: launchArgumentKey)", swift)
        self.assertIn("var evidencePath: String", swift)
        self.assertIn('"Docs/screenshots/\\(rawValue).jpg"', swift)

    def test_session_control_generator_emits_shared_session_helpers(self) -> None:
        self.assertTrue(hasattr(scaffold, "_session_control_swift"))

        swift = scaffold._session_control_swift()

        self.assertIn("enum SessionControl", swift)
        self.assertIn("static func isPlaying(_ state: GameSessionState) -> Bool", swift)
        self.assertIn("state.phase == .playing", swift)
        self.assertIn("static func isResult(_ state: GameSessionState) -> Bool", swift)
        self.assertIn("state.phase == .result", swift)
        self.assertIn("static func reset() -> GameSessionState", swift)
        self.assertIn("static func markResult(_ state: GameSessionState, event: String) -> GameSessionState", swift)

    def test_feedback_state_generator_emits_display_message_helper(self) -> None:
        self.assertTrue(hasattr(scaffold, "_feedback_state_swift"))

        swift = scaffold._feedback_state_swift()

        self.assertIn("enum FeedbackState", swift)
        self.assertIn("static func message(for state: GameSessionState) -> String", swift)
        self.assertIn("state.lastEvent.capitalized", swift)

    def test_input_intent_generator_emits_primary_button_titles(self) -> None:
        self.assertTrue(hasattr(scaffold, "_input_intent_swift"))

        swift = scaffold._input_intent_swift(scene_spec())

        self.assertIn("enum InputIntent", swift)
        self.assertIn('static let startTitle = "Start"', swift)
        self.assertIn('static let resetTitle = "Reset"', swift)
        self.assertIn('static let primaryActionTitle = "Dodge"', swift)
        self.assertIn("static func primaryButtonTitle(isPlaying: Bool) -> String", swift)

    def test_result_view_generator_uses_shared_reset_title(self) -> None:
        self.assertTrue(hasattr(scaffold, "_result_view_swift"))

        swift = scaffold._result_view_swift()

        self.assertIn("struct ResultView: View", swift)
        self.assertIn('Text("Score \\(state.score)")', swift)
        self.assertIn("Button(InputIntent.resetTitle, action: onReset)", swift)


if __name__ == "__main__":
    unittest.main()
