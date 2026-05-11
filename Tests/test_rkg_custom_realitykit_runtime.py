import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rkg.custom_realitykit_runtime import (
    custom_realitykit_adapter_capabilities,
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


def custom_projectile_spec() -> dict:
    spec = custom_shooter_spec()
    spec["game"]["id"] = "arc_volley"
    spec["game"]["display_name"] = "Arc Volley"
    spec["game"]["camera"] = "third_person"
    spec["game"]["input"] = "drag"
    spec["game"]["systems"] = ["projectile", "shooting", "score"]
    spec["loop"]["player_action"] = "aim, charge, and launch projectiles at target lanes"
    spec["loop"]["fail_condition"] = "attempts expire before enough hits land"
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
        "weapon_proxy": {
            "type": "weapon_proxy",
            "role": "weapon",
            "budget": "700 tris / 512 texture",
            "fallback": "procedural_weapon",
        },
        "projectile_proxy": {
            "type": "projectile",
            "role": "projectile",
            "budget": "400 tris / 512 texture",
            "fallback": "procedural_sphere",
        },
        "target_proxy": {
            "type": "gameplay_target",
            "role": "target",
            "budget": "700 tris / 512 texture",
            "fallback": "procedural_rings",
        },
    }
    return spec


class RkgCustomRealityKitRuntimeTests(unittest.TestCase):
    def test_runtime_adapters_are_declared_as_registry_entries(self) -> None:
        adapters = custom_realitykit_runtime_adapters()
        by_id = {adapter.id: adapter for adapter in adapters}

        self.assertEqual(["racing", "projectile", "shooter", "collector"], [adapter.id for adapter in adapters])
        self.assertEqual(("racing", "lap_timer", "collision"), by_id["racing"].systems)
        self.assertEqual(("projectile", "shooting", "score"), by_id["projectile"].systems)
        self.assertEqual(("weapon", "hitscan", "enemies", "health", "cover"), by_id["shooter"].systems)
        self.assertEqual(("collect", "score", "timer"), by_id["collector"].systems)
        self.assertIn("var raceDistance: Int = 0", by_id["racing"].state_fields)
        self.assertIn("var projectileShots: Int = 0", by_id["projectile"].state_fields)
        self.assertIn("var shooterHealth: Int = GameRules.shooterMaxHealth", by_id["shooter"].state_fields)
        self.assertIn("var collectedItems: Int = 0", by_id["collector"].state_fields)
        self.assertIn("static func startRacingSession(sessionSeconds: Int) -> GameSessionState", "\n".join(by_id["racing"].rule_members))
        self.assertIn("static func launchProjectile(_ state: GameSessionState) -> GameSessionState", "\n".join(by_id["projectile"].rule_members))
        self.assertIn("static func startShooterSession(sessionSeconds: Int) -> GameSessionState", "\n".join(by_id["shooter"].rule_members))
        self.assertIn("static func startCollectorSession(sessionSeconds: Int) -> GameSessionState", "\n".join(by_id["collector"].rule_members))
        self.assertIn("Button(\"Left\")", by_id["racing"].content_section)
        self.assertIn("Button(\"Launch\")", by_id["projectile"].content_section)
        self.assertIn("Button(\"Aim Left\")", by_id["shooter"].content_section)
        self.assertIn("Button(\"Collect\")", by_id["collector"].content_section)
        self.assertIn("vehicleEntity", by_id["racing"].scene_properties)
        self.assertIn("projectileEntity", by_id["projectile"].scene_properties)
        self.assertIn("weaponEntity", by_id["shooter"].scene_properties)
        self.assertIn("pickupEntity", by_id["collector"].scene_properties)

    def test_runtime_adapter_capabilities_are_machine_readable(self) -> None:
        capabilities = custom_realitykit_adapter_capabilities()
        by_id = {record["id"]: record for record in capabilities}

        self.assertEqual(["racing", "projectile", "shooter", "collector"], [record["id"] for record in capabilities])
        self.assertEqual(["projectile", "shooting", "score"], by_id["projectile"]["systems"])
        self.assertIn("projectileShots", by_id["projectile"]["state_fields"])
        self.assertIn("launchProjectile", by_id["projectile"]["rule_members"])
        self.assertIn("projectileEntity", by_id["projectile"]["scene_properties"])
        self.assertIn("projectile", by_id["projectile"]["scene_roles"])
        self.assertIn("target", by_id["projectile"]["scene_roles"])

    def test_custom_runtime_module_owns_state_rules_content_and_scene_strings(self) -> None:
        fields = custom_realitykit_state_fields()
        rules = "\n".join(custom_realitykit_rule_members())
        content_sections = custom_realitykit_adapter_content_sections()
        scene_controller = custom_realitykit_game_scene_controller_swift(custom_projectile_spec())

        self.assertIn("var raceDistance: Int = 0", fields)
        self.assertIn("var projectileShots: Int = 0", fields)
        self.assertIn("var shooterHealth: Int = GameRules.shooterMaxHealth", fields)
        self.assertIn("var collectionTimer: Int = GameRules.collectionTimerSeconds", fields)
        self.assertIn("static func advanceRacingFrame(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func launchProjectile(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func fireShooterWeapon(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("static func collectPickup(_ state: GameSessionState) -> GameSessionState", rules)
        self.assertIn("Button(\"Launch\")", content_sections)
        self.assertIn("Button(\"Aim Left\")", content_sections)
        self.assertIn("Button(\"Left\")", content_sections)
        self.assertIn("Button(\"Collect\")", content_sections)
        self.assertIn("private var projectileEntity: Entity?", scene_controller)
        self.assertIn("private var targetEntity: Entity?", scene_controller)
        self.assertIn("func updateProjectile(state: GameSessionState)", scene_controller)

    def test_list_adapters_cli_exposes_capability_matrix(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkg.py"), "list-adapters", "--json"],
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(["racing", "projectile", "shooter", "collector"], [record["id"] for record in payload])
        projectile = payload[1]
        self.assertEqual(["projectile", "shooting", "score"], projectile["systems"])
        self.assertIn("projectileEntity", projectile["scene_properties"])


if __name__ == "__main__":
    unittest.main()
