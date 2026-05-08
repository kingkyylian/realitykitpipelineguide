import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rkg.content_views import content_view_swift


def spec_for(archetype: str) -> dict:
    return {
        "game": {
            "archetype": archetype,
            "session_seconds": 60,
        },
        "loop": {
            "player_action": "play the generated loop",
        },
    }


class RkgContentViewTests(unittest.TestCase):
    def test_toss_physics_content_view_contract_is_outside_scaffold(self) -> None:
        content = content_view_swift("Toss Arc", spec_for("toss_physics"))

        self.assertIn("@State private var state = GameSessionState()", content)
        self.assertIn("@State private var throwPower = 0.5", content)
        self.assertIn("SessionControl.isPlaying(state)", content)
        self.assertIn('Button(isPlaying ? "Throw" : "Start")', content)
        self.assertIn("state = SessionControl.reset()", content)
        self.assertIn("state = GameRules.resolveToss(state, power: throwPower)", content)

    def test_stack_puzzle_content_view_contract_is_outside_scaffold(self) -> None:
        content = content_view_swift("Stack Tower", spec_for("stack_puzzle"))

        self.assertIn("@State private var state = GameSessionState()", content)
        self.assertIn("@State private var stablePlacement = true", content)
        self.assertIn("SessionControl.isPlaying(state)", content)
        self.assertIn("GameView(state: state)", content)
        self.assertIn('Text("Pieces \\(state.piecesPlaced)/\\(GameRules.maxPieces)")', content)
        self.assertIn('Toggle("Stable", isOn: $stablePlacement)', content)
        self.assertIn('Button(isPlaying ? "Place" : "Start")', content)
        self.assertIn('Button("Collapse")', content)
        self.assertIn("state = SessionControl.reset()", content)
        self.assertIn("state = GameRules.placeStackPiece(state, stable: stablePlacement)", content)

    def test_generic_content_view_contract_remains_available(self) -> None:
        content = content_view_swift('Ring "Dash"', spec_for("target_shooter"))

        self.assertIn('Text("Ring \\"Dash\\"")', content)
        self.assertIn("@State private var score = 0", content)
        self.assertIn('Button(isPlaying ? "Reset" : "Start")', content)


if __name__ == "__main__":
    unittest.main()
