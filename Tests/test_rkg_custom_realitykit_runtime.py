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
    custom_realitykit_runtime_adapters,
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


def custom_collector_spec() -> dict:
    spec = custom_shooter_spec()
    spec["game"]["id"] = "orb_sprint"
    spec["game"]["display_name"] = "Orb Sprint"
    spec["game"]["camera"] = "top_down"
    spec["game"]["input"] = "tap_swipe"
    spec["game"]["systems"] = ["collect", "score", "timer"]
    spec["loop"]["player_action"] = "collect pickups before the timer expires"
    spec["loop"]["fail_condition"] = "timer reaches zero"
    spec["assets"] = {
        "player_proxy": {
            "type": "gameplay_actor",
            "role": "player",
            "budget": "1500 tris / 512 texture",
            "fallback": "procedural_capsule",
        },
        "arena_space": {
            "type": "environment",
            "role": "arena",
            "budget": "1200 tris / 512 texture",
            "fallback": "procedural_arena",
        },
        "pickup_proxy": {
            "type": "pickup",
            "role": "pickup",
            "budget": "400 tris / 512 texture",
            "fallback": "procedural_pickup",
        },
        "timer_gate": {
            "type": "ui_prop",
            "role": "ui_prop",
            "budget": "500 tris / 512 texture",
            "fallback": "procedural_gate",
        },
    }
    return spec


class RkgCustomRealityKitRuntimeTests(unittest.TestCase):
    def test_runtime_adapters_are_declared_as_registry_entries(self) -> None:
        adapters = custom_realitykit_runtime_adapters()

        self.assertEqual(["racing", "shooter", "collector"], [adapter.id for adapter in adapters])
        self.assertEqual(("racing", "lap_timer", "collision"), adapters[0].systems)
        self.assertEqual(("weapon", "hitscan", "enemies", "health", "cover"), adapters[1].systems)
        self.assertEqual(("collect", "score", "timer"), adapters[2].systems)
        self.assertIn("var raceDistance: Int = 0", adapters[0].state_fields)
        self.assertIn("var shooterHealth: Int = GameRules.shooterMaxHealth", adapters[1].state_fields)
        self.assertIn("var collectedItems: Int = 0", adapters[2].state_fields)
        self.assertIn("static func startRacingSession(sessionSeconds: Int) -> GameSessionState", "\n".join(adapters[0].rule_members))
        self.assertIn("static func startShooterSession(sessionSeconds: Int) -> GameSessionState", "\n".join(adapters[1].rule_members))
        self.assertIn("static func startCollectorSession(sessionSeconds: Int) -> GameSessionState", "\n".join(adapters[2].rule_members))
        self.assertIn("Button(\"Left\")", adapters[0].content_section)
        self.assertIn("Button(\"Aim Left\")", adapters[1].content_section)
        self.assertIn("Button(\"Collect\")", adapters[2].content_section)
        self.assertIn("vehicleEntity", adapters[0].scene_properties)
        self.assertIn("weaponEntity", adapters[1].scene_properties)
        self.assertIn("pickupEntity", adapters[2].scene_properties)

    def test_custom_runtime_module_owns_state_rules_content_and_scene_strings(self) -> None:
        fields = custom_realitykit_state_fields()
        rules = "\n".join(custom_realitykit_rule_members())
        content_sections = custom_realitykit_adapter_content_sections()
        scene_controller = custom_realitykit_game_scene_controller_swift(custom_collector_spec())

        self.assertIn("var raceDistance: Int = 0", fields)
        self.assertIn("var shooterHealth: Int = GameRules.shooterMaxHealth", fields)
        self.assertIn("var collectionTimer: Int = GameRules.collectionTimerSeconds", fields)
        self.assertIn("static func advanceRacingFrame(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func fireShooterWeapon(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func collectPickup(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("Button(\"Aim Left\")", content_sections)
        self.assertIn("Button(\"Left\")", content_sections)
        self.assertIn("Button(\"Collect\")", content_sections)
        self.assertIn("private var pickupEntity: Entity?", scene_controller)
        self.assertIn("func updateCollector(state: GameSessionState)", scene_controller)


if __name__ == "__main__":
    unittest.main()
