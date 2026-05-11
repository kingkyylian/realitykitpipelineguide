from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def camera_rig_swift(spec: Mapping[str, Any]) -> str:
    camera = str(spec["game"]["camera"])
    camera_literal = _swift_string_literal(camera)
    return f"""import RealityKit
import simd

enum CameraRig {{
    static let id = {camera_literal}

    static func configure(_ view: ARView) {{
        _ = view
        _ = transform
    }}

    static var transform: Transform {{
        Transform(
            scale: SIMD3<Float>(1, 1, 1),
            rotation: rotation,
            translation: translation
        )
    }}

    private static var translation: SIMD3<Float> {{
        switch id {{
        case "chase":
            return SIMD3<Float>(0, 0.45, 1.65)
        case "first_person":
            return SIMD3<Float>(0, 0.20, 0.15)
        case "third_person":
            return SIMD3<Float>(0, 0.65, 1.95)
        case "top_down":
            return SIMD3<Float>(0, 2.25, 0.05)
        default:
            return SIMD3<Float>(0, 0.55, 1.55)
        }}
    }}

    private static var rotation: simd_quatf {{
        switch id {{
        case "top_down":
            return simd_quatf(angle: -Float.pi / 2.0, axis: SIMD3<Float>(1, 0, 0))
        case "chase":
            return simd_quatf(angle: -Float.pi / 10.0, axis: SIMD3<Float>(1, 0, 0))
        case "third_person":
            return simd_quatf(angle: -Float.pi / 8.0, axis: SIMD3<Float>(1, 0, 0))
        default:
            return simd_quatf(angle: 0, axis: SIMD3<Float>(0, 1, 0))
        }}
    }}
}}
"""


def input_controller_swift(spec: Mapping[str, Any]) -> str:
    input_model = str(spec["game"]["input"])
    input_literal = _swift_string_literal(input_model)
    return f"""import Foundation

enum InputController {{
    static let id = {input_literal}

    static var supportsDrag: Bool {{
        id == "drag" || id == "dual_stick" || id == "tap_swipe" || id == "gamepad_touch"
    }}

    static var supportsTilt: Bool {{
        id == "tilt_tap"
    }}

    static var primaryActionLabel: String {{
        switch id {{
        case "tilt_tap":
            return "Tilt + Tap"
        case "dual_stick":
            return "Move + Fire"
        case "tap_swipe":
            return "Tap / Swipe"
        case "drag":
            return "Drag"
        case "gamepad_touch":
            return "Gamepad"
        default:
            return "Tap"
        }}
    }}

    static var controlSummary: String {{
        if supportsTilt {{
            return "Tilt steering enabled"
        }}
        if supportsDrag {{
            return "Directional input enabled"
        }}
        return "Tap input enabled"
    }}
}}
"""


def system_flags_swift(spec: Mapping[str, Any]) -> str:
    systems = sorted({str(system) for system in spec["game"].get("systems", [])})
    system_set = set(systems)
    system_list = ", ".join(_swift_string_literal(system) for system in systems)
    return f"""import Foundation

enum SystemFlags {{
    static let systems: Set<String> = [{system_list}]
    static let hasRacing = {str("racing" in systems).lower()}
    static let hasLapTimer = {str("lap_timer" in systems).lower()}
    static let hasCollision = {str("collision" in systems).lower()}
    static let hasWeapon = {str(bool({"weapon", "hitscan"} & system_set)).lower()}
    static let hasProjectile = {str("projectile" in systems).lower()}
    static let hasShooting = {str(bool({"projectile", "shooting"} & system_set)).lower()}
    static let hasEnemies = {str(bool({"enemies", "enemy_ai"} & system_set)).lower()}
    static let hasHealth = {str("health" in systems).lower()}
    static let hasCover = {str("cover" in systems).lower()}
    static let hasCollect = {str("collect" in systems).lower()}
    static let hasScore = {str("score" in systems).lower()}
    static let hasTimer = {str("timer" in systems).lower()}

    static var summary: String {{
        systems.sorted().joined(separator: ", ")
    }}

    static func has(_ system: String) -> Bool {{
        systems.contains(system)
    }}
}}
"""


def _swift_string_literal(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=True)
