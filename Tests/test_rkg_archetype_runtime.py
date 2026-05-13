import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rkg.archetype_runtime import archetype_rule_members, archetype_state_fields, indent_swift_block


class RkgArchetypeRuntimeTests(unittest.TestCase):
    def test_lane_dodger_runtime_contract_is_exposed_outside_scaffold(self) -> None:
        fields = archetype_state_fields("lane_dodger")
        rules = "\n".join(archetype_rule_members("lane_dodger"))

        self.assertIn("var currentLane: Int = 1", fields)
        self.assertIn("var obstacleLane: Int = 0", fields)
        self.assertIn("var isDefeated: Bool = false", fields)
        self.assertIn("static func advanceLaneDodgerFrame(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn('next = SessionControl.markResult(next, event: "hit obstacle")', rules)

    def test_wave_defense_runtime_contract_is_exposed_outside_scaffold(self) -> None:
        fields = archetype_state_fields("wave_defense_lite")
        rules = "\n".join(archetype_rule_members("wave_defense_lite"))

        self.assertIn("var health: Int = GameRules.startingHealth", fields)
        self.assertIn("var clearedThreats: Int = 0", fields)
        self.assertIn("static func clearThreat(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func applyThreatDamage(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn('next = SessionControl.markResult(next, event: "base breached")', rules)

    def test_fighter_runtime_contract_is_exposed_outside_scaffold(self) -> None:
        fields = archetype_state_fields("fighter_2_5d")
        rules = "\n".join(archetype_rule_members("fighter_2_5d"))

        self.assertIn("var playerHealth: Int = GameRules.fighterMaxHealth", fields)
        self.assertIn("var opponentHealth: Int = GameRules.fighterMaxHealth", fields)
        self.assertIn("var comboCount: Int = 0", fields)
        self.assertIn("var guardMeter: Int = GameRules.startingGuardMeter", fields)
        self.assertIn("var isDodging: Bool = false", fields)
        self.assertIn("var isKnockout: Bool = false", fields)
        self.assertIn("static func startFighterDuelSession(sessionSeconds: Int) -> GameSessionState", rules)
        self.assertIn("static func recordFighterAttack(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func performPerfectDodge(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func applyFighterDamage(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func fighterScreenshotSession(for screenshotState: ScreenshotState?", rules)
        self.assertIn('case "mid_combo":', rules)
        self.assertIn("while state.opponentHealth > 0", rules)
        self.assertIn('next = SessionControl.markResult(next, event: "knockout")', rules)

    def test_flappy_runtime_contract_is_exposed_outside_scaffold(self) -> None:
        fields = archetype_state_fields("flappy_side_scroller")
        rules = "\n".join(archetype_rule_members("flappy_side_scroller"))

        self.assertIn("var birdY: Double = GameRules.flappyStartY", fields)
        self.assertIn("var birdVelocity: Double = 0", fields)
        self.assertIn("var obstacleX: Double = GameRules.flappyStartObstacleX", fields)
        self.assertIn("var gapY: Double = GameRules.flappyStartGapY", fields)
        self.assertIn("var pipesPassed: Int = 0", fields)
        self.assertIn("var isCollision: Bool = false", fields)
        self.assertIn("static let flappyGravity", rules)
        self.assertIn("static func startFlappySession(sessionSeconds: Int) -> GameSessionState", rules)
        self.assertIn("static func flapBird(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func advanceFlappyFrame(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func hasFlappyCollision(birdY: Double, obstacleX: Double, gapY: Double) -> Bool", rules)
        self.assertIn("static func flappyScreenshotSession(for screenshotState: ScreenshotState?", rules)
        self.assertIn('case "near_gap":', rules)
        self.assertIn('next = SessionControl.markResult(next, event: "collision")', rules)

    def test_stack_puzzle_runtime_contract_is_exposed_outside_scaffold(self) -> None:
        fields = archetype_state_fields("stack_puzzle")
        rules = "\n".join(archetype_rule_members("stack_puzzle"))

        self.assertIn("var piecesPlaced: Int = 0", fields)
        self.assertIn("var stablePieces: Int = 0", fields)
        self.assertIn("var collapsed: Bool = false", fields)
        self.assertIn("static func startStackPuzzleSession(sessionSeconds: Int) -> GameSessionState", rules)
        self.assertIn("static func placeStackPiece(_ state: GameSessionState, stable: Bool) -> GameSessionState", rules)
        self.assertIn("static func collapseStack(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn('next = SessionControl.markResult(next, event: "collapsed")', rules)

    def test_toss_physics_result_transitions_use_session_control(self) -> None:
        rules = "\n".join(archetype_rule_members("toss_physics"))

        self.assertIn('next = SessionControl.markResult(next, event: "landed")', rules)
        self.assertIn('next = SessionControl.markResult(next, event: "attempts spent")', rules)

    def test_target_shooter_runtime_contract_is_exposed_outside_scaffold(self) -> None:
        fields = archetype_state_fields("target_shooter")
        rules = "\n".join(archetype_rule_members("target_shooter"))

        self.assertIn("var targetsHit: Int = 0", fields)
        self.assertIn("var perfectHits: Int = 0", fields)
        self.assertIn("static func startTargetShooterSession(sessionSeconds: Int) -> GameSessionState", rules)
        self.assertIn("static func recordTargetHit(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func finishTargetShooterSession(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn('SessionControl.markResult(next, event: "session complete")', rules)

    def test_unknown_archetype_uses_empty_runtime_contract(self) -> None:
        self.assertEqual(archetype_state_fields("unknown"), [])
        self.assertEqual(archetype_rule_members("unknown"), [])

    def test_indent_swift_block_indents_multiline_members(self) -> None:
        text = "static func sample() {\n    1\n}"

        self.assertEqual(indent_swift_block(text, spaces=4), "    static func sample() {\n        1\n    }")


if __name__ == "__main__":
    unittest.main()
