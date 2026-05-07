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

    def test_wave_defense_runtime_contract_is_exposed_outside_scaffold(self) -> None:
        fields = archetype_state_fields("wave_defense_lite")
        rules = "\n".join(archetype_rule_members("wave_defense_lite"))

        self.assertIn("var health: Int = GameRules.startingHealth", fields)
        self.assertIn("var clearedThreats: Int = 0", fields)
        self.assertIn("static func clearThreat(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func applyThreatDamage(_ state: GameSessionState) -> GameSessionState", rules)

    def test_unknown_archetype_uses_empty_runtime_contract(self) -> None:
        self.assertEqual(archetype_state_fields("target_shooter"), [])
        self.assertEqual(archetype_rule_members("target_shooter"), [])

    def test_indent_swift_block_indents_multiline_members(self) -> None:
        text = "static func sample() {\n    1\n}"

        self.assertEqual(indent_swift_block(text, spaces=4), "    static func sample() {\n        1\n    }")


if __name__ == "__main__":
    unittest.main()
