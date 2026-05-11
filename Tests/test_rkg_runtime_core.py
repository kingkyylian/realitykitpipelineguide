import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rkg.runtime_core import camera_rig_swift, input_controller_swift, system_flags_swift


def custom_racing_spec() -> dict:
    return {
        "game": {
            "id": "desert_chase",
            "display_name": "Desert Chase",
            "archetype": "custom_realitykit",
            "session_seconds": 60,
            "camera": "chase",
            "input": "tilt_tap",
            "monetization": "paid",
            "systems": ["racing", "lap_timer", "collision"],
        },
        "loop": {
            "player_action": "steer through the course",
            "fail_condition": "collision ends the run",
            "scoring": {"hit": 10, "perfect": 25, "lap": 100},
        },
        "assets": {
            "player_vehicle": {
                "type": "vehicle_proxy",
                "role": "player",
                "budget": "1800 tris / 512 texture",
                "fallback": "procedural_vehicle",
            },
            "race_track": {
                "type": "environment",
                "role": "arena",
                "budget": "1200 tris / 512 texture",
                "fallback": "procedural_track",
            },
        },
        "release": {
            "devices": ["iPhone 15"],
            "screenshots": ["gameplay_start", "mid_action", "fail_or_hit", "results"],
        },
    }


def custom_collector_spec() -> dict:
    spec = custom_racing_spec()
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


class RkgRuntimeCoreTests(unittest.TestCase):
    def test_camera_rig_swift_binds_selected_camera(self) -> None:
        swift = camera_rig_swift(custom_racing_spec())

        self.assertIn('static let id = "chase"', swift)
        self.assertIn("static func configure(_ view: ARView)", swift)
        self.assertIn('case "chase":', swift)
        self.assertIn("static var transform: Transform", swift)

    def test_input_controller_swift_binds_selected_input(self) -> None:
        swift = input_controller_swift(custom_racing_spec())

        self.assertIn('static let id = "tilt_tap"', swift)
        self.assertIn("static var supportsTilt: Bool", swift)
        self.assertIn("static var supportsDrag: Bool", swift)
        self.assertIn('return "Tilt + Tap"', swift)

    def test_system_flags_swift_binds_selected_systems(self) -> None:
        swift = system_flags_swift(custom_racing_spec())

        self.assertIn('static let systems: Set<String> = ["collision", "lap_timer", "racing"]', swift)
        self.assertIn('static func has(_ system: String) -> Bool', swift)
        self.assertIn('static let hasRacing = true', swift)
        self.assertIn('static let hasWeapon = false', swift)
        self.assertIn('static let hasCollision = true', swift)

    def test_system_flags_swift_binds_collector_systems(self) -> None:
        swift = system_flags_swift(custom_collector_spec())

        self.assertIn('static let systems: Set<String> = ["collect", "score", "timer"]', swift)
        self.assertIn("static let hasCollect = true", swift)
        self.assertIn("static let hasScore = true", swift)
        self.assertIn("static let hasTimer = true", swift)
        self.assertIn("static let hasRacing = false", swift)


if __name__ == "__main__":
    unittest.main()
