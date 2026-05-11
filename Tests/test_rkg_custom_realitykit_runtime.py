import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rkg.custom_realitykit_runtime import (
    custom_realitykit_adapter_content_sections,
    custom_realitykit_game_scene_controller_swift,
    custom_realitykit_rule_members,
    custom_realitykit_state_fields,
)


def custom_shooter_spec() -> dict:
    return {
        "game": {
            "id": "room_breach",
            "display_name": "Room Breach",
            "archetype": "custom_realitykit",
            "session_seconds": 60,
            "camera": "first_person",
            "input": "dual_stick",
            "monetization": "paid",
            "systems": ["weapon", "hitscan", "enemies", "health", "cover"],
        },
        "loop": {
            "player_action": "move, aim, and fire while managing health and cover",
            "fail_condition": "health reaches zero or enemies overrun the arena",
            "scoring": {"hit": 10, "perfect": 25, "clear": 100},
        },
        "assets": {
            "player_proxy": {
                "type": "gameplay_actor",
                "role": "player",
                "budget": "1500 tris / 512 texture",
                "fallback": "procedural_capsule",
            },
            "weapon_proxy": {
                "type": "weapon_proxy",
                "role": "weapon",
                "budget": "700 tris / 512 texture",
                "fallback": "procedural_weapon",
            },
            "enemy_proxy": {
                "type": "enemy_proxy",
                "role": "enemy",
                "budget": "1500 tris / 512 texture",
                "fallback": "procedural_enemy",
            },
            "cover_block": {
                "type": "cover",
                "role": "cover",
                "budget": "800 tris / 512 texture",
                "fallback": "procedural_cover",
            },
        },
        "release": {
            "devices": ["iPhone 15"],
            "screenshots": ["gameplay_start", "mid_action", "fail_or_hit", "results"],
        },
    }


class RkgCustomRealityKitRuntimeTests(unittest.TestCase):
    def test_custom_runtime_module_owns_state_rules_content_and_scene_strings(self) -> None:
        fields = custom_realitykit_state_fields()
        rules = "\n".join(custom_realitykit_rule_members())
        content_sections = custom_realitykit_adapter_content_sections()
        scene_controller = custom_realitykit_game_scene_controller_swift(custom_shooter_spec())

        self.assertIn("var raceDistance: Int = 0", fields)
        self.assertIn("var shooterHealth: Int = GameRules.shooterMaxHealth", fields)
        self.assertIn("static func advanceRacingFrame(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func fireShooterWeapon(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("Button(\"Aim Left\")", content_sections)
        self.assertIn("Button(\"Left\")", content_sections)
        self.assertIn("private var weaponEntity: Entity?", scene_controller)
        self.assertIn("func updateShooter(state: GameSessionState)", scene_controller)


if __name__ == "__main__":
    unittest.main()
