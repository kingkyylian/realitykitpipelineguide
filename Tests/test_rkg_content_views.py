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
        self.assertIn("FeedbackState.message(for: state)", content)
        self.assertIn("Button(InputIntent.primaryButtonTitle(isPlaying: isPlaying))", content)
        self.assertIn("state = SessionControl.reset()", content)
        self.assertIn("if SessionControl.isResult(state)", content)
        self.assertIn("ResultView(state: state)", content)
        self.assertIn("throwPower = 0.5", content)
        self.assertIn("state = GameRules.resolveToss(state, power: throwPower)", content)

    def test_stack_puzzle_content_view_contract_is_outside_scaffold(self) -> None:
        content = content_view_swift("Stack Tower", spec_for("stack_puzzle"))

        self.assertIn("@State private var state = GameSessionState()", content)
        self.assertIn("@State private var stablePlacement = true", content)
        self.assertIn("SessionControl.isPlaying(state)", content)
        self.assertIn("FeedbackState.message(for: state)", content)
        self.assertIn("GameView(state: state)", content)
        self.assertIn('Text("Pieces \\(state.piecesPlaced)/\\(GameRules.maxPieces)")', content)
        self.assertIn('Toggle("Stable", isOn: $stablePlacement)', content)
        self.assertIn("Button(InputIntent.primaryButtonTitle(isPlaying: isPlaying))", content)
        self.assertIn('Button("Collapse")', content)
        self.assertIn("Button(InputIntent.resetTitle)", content)
        self.assertIn("state = SessionControl.reset()", content)
        self.assertIn("if SessionControl.isResult(state)", content)
        self.assertIn("ResultView(state: state)", content)
        self.assertIn("stablePlacement = true", content)
        self.assertIn("state = GameRules.placeStackPiece(state, stable: stablePlacement)", content)

    def test_fighter_content_view_contract_is_outside_scaffold(self) -> None:
        content = content_view_swift("Neon Ring Duel", spec_for("fighter_2_5d"))

        self.assertIn("@State private var state = GameRules.fighterScreenshotSession(", content)
        self.assertIn("for: ScreenshotState.requested", content)
        self.assertIn("fallback: GameSessionState()", content)
        self.assertIn("SessionControl.isPlaying(state)", content)
        self.assertIn("GameView(state: state)", content)
        self.assertIn('Text("HP \\(state.playerHealth)")', content)
        self.assertIn('Text("Opponent \\(state.opponentHealth)")', content)
        self.assertIn('Text("Combo \\(state.comboCount)")', content)
        self.assertIn('Text("Guard \\(state.guardMeter)")', content)
        self.assertIn("Button(InputIntent.primaryButtonTitle(isPlaying: isPlaying))", content)
        self.assertIn('Button("Dodge")', content)
        self.assertIn("if !SessionControl.isResult(state)", content)
        self.assertIn('Button("Damage")', content)
        self.assertIn(".controlSize(.small)", content)
        self.assertIn("DragGesture(minimumDistance: 20).onEnded", content)
        self.assertIn("state = GameRules.startFighterDuelSession(sessionSeconds: state.sessionSeconds)", content)
        self.assertIn("state = GameRules.recordFighterAttack(state)", content)
        self.assertIn("state = GameRules.performPerfectDodge(state)", content)
        self.assertIn("state = GameRules.applyFighterDamage(state)", content)

    def test_generic_content_view_contract_remains_available_for_unknown_archetype(self) -> None:
        content = content_view_swift('Ring "Dash"', spec_for("prototype"))

        self.assertIn('Text("Ring \\"Dash\\"")', content)
        self.assertIn("@State private var score = 0", content)
        self.assertIn("Button(isPlaying ? InputIntent.resetTitle : InputIntent.startTitle)", content)


if __name__ == "__main__":
    unittest.main()
