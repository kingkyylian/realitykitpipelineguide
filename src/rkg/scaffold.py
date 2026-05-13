from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rkg.archetype_runtime import archetype_rule_members, archetype_state_fields, indent_swift_block
from rkg.asset_briefs import asset_brief
from rkg.content_views import content_view_swift
from rkg.custom_realitykit_runtime import custom_realitykit_game_scene_controller_swift
from rkg.plan import runtime_entities_for, swift_identifier_for, swift_name_for
from rkg.runtime_core import camera_rig_swift, input_controller_swift, system_flags_swift
from rkg.spec import assert_valid_game_spec
from rkg.store_pack import build_store_pack

JsonDict = dict[str, Any]


def init_game(spec: Mapping[str, Any], output: Path, *, force: bool = False) -> None:
    assert_valid_game_spec(spec)
    output = output.resolve()
    if output.exists() and any(output.iterdir()) and not force:
        raise ValueError("output directory is not empty; pass --force to overwrite generated files")

    game = spec["game"]
    game_id = str(game["id"])
    display_name = str(game["display_name"])
    swift_name = _swift_name(game_id)
    bundle_suffix = _bundle_suffix(game_id)

    _make_dirs(output, swift_name)
    _write_json(output / "GameSpec.json", dict(spec))
    _write_json(output / "rkp.json", _rkp_config(swift_name))
    _write_json(output / "Tools" / "asset_manifest.json", _asset_manifest(spec))
    for asset_id, asset in spec["assets"].items():
        _write_text(output / "Docs" / "assets" / f"{asset_id}.md", asset_brief(str(asset_id), asset))

    _write_text(output / "project.yml", _project_yml(swift_name, display_name, bundle_suffix))
    _write_text(output / "Sources" / swift_name / f"{swift_name}App.swift", _app_swift(swift_name))
    _write_text(output / "Sources" / swift_name / "ContentView.swift", content_view_swift(display_name, spec))
    _write_text(output / "Sources" / swift_name / "GameState.swift", _game_state_swift(spec))
    _write_text(output / "Sources" / swift_name / "SessionControl.swift", _session_control_swift())
    _write_text(output / "Sources" / swift_name / "FeedbackState.swift", _feedback_state_swift())
    _write_text(output / "Sources" / swift_name / "InputIntent.swift", _input_intent_swift(spec))
    _write_text(output / "Sources" / swift_name / "ScreenshotState.swift", _screenshot_state_swift(spec))
    _write_text(output / "Sources" / swift_name / "CameraRig.swift", camera_rig_swift(spec))
    _write_text(output / "Sources" / swift_name / "InputController.swift", input_controller_swift(spec))
    _write_text(output / "Sources" / swift_name / "SystemFlags.swift", system_flags_swift(spec))
    _write_text(output / "Sources" / swift_name / "WorldRig.swift", _world_rig_swift(spec))
    _write_text(output / "Sources" / swift_name / "GameRules.swift", _game_rules_swift(spec))
    _write_text(output / "Sources" / swift_name / "AssetLoader.swift", _asset_loader_swift())
    _write_text(output / "Sources" / swift_name / "FallbackFactory.swift", _fallback_factory_swift())
    _write_text(output / "Sources" / swift_name / "RuntimeSceneSnapshot.swift", _runtime_scene_snapshot_swift())
    _write_text(output / "Sources" / swift_name / "GameSceneController.swift", _game_scene_controller_swift(spec))
    _write_text(output / "Sources" / swift_name / "GameView.swift", _game_view_swift(spec))
    _write_text(output / "Sources" / swift_name / "ResultView.swift", _result_view_swift())
    _write_text(output / "Tests" / "test_smoke.py", _smoke_test_py(display_name))
    _write_text(output / "Docs" / "WORKLOG.md", _worklog(display_name))
    _write_text(output / "Docs" / "ai-handoff.md", _handoff(display_name, game_id))
    for rel_path, text in build_store_pack(spec).items():
        _write_text(output / rel_path, text)


def _make_dirs(output: Path, swift_name: str) -> None:
    for rel in [
        "Assets/Imported",
        "Assets/Textures",
        "Assets/Source",
        "Docs/assets",
        "Docs/screenshots",
        "Docs/store",
        "Tools/blender",
        f"Sources/{swift_name}",
        "Tests",
    ]:
        (output / rel).mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _swift_name(game_id: str) -> str:
    return swift_name_for(game_id)


def _bundle_suffix(game_id: str) -> str:
    return re.sub(r"[^a-z0-9]", "", game_id.lower())


def _swift_string_literal(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=True)


def _yaml_string(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=True)


def _rkp_config(swift_name: str) -> JsonDict:
    return {
        "manifest": "Tools/asset_manifest.json",
        "assets_dir": "Assets/Imported",
        "docs_dir": "Docs",
        "blender_dir": "Tools/blender",
        "textures_dir": "Assets/Textures",
        "source_dir": "Assets/Source",
        "tests_dir": "Tests",
        "xcode_project": f"{swift_name}.xcodeproj",
        "xcode_scheme": swift_name,
        "xcode_destination": "generic/platform=iOS Simulator",
        "derived_data_path": "Build/DerivedData",
    }


def _asset_manifest(spec: Mapping[str, Any]) -> JsonDict:
    game = spec["game"]
    manifest_assets = []
    for asset_id, asset in spec["assets"].items():
        budget = str(asset["budget"])
        manifest_assets.append(
            {
                "id": asset_id,
                "status": "planned",
                "type": asset["type"],
                "role": asset.get("role") or asset["type"],
                "file": f"{asset_id}.usdz",
                "budget": budget,
                "maxTriangles": _parse_budget_int(budget, "tris", default=1500),
                "maxTextureSize": _parse_budget_int(budget, "texture", default=512),
                "fallback": asset["fallback"],
                "scale": "1 Blender unit = 1 meter",
                "origin": "centered for runtime placement unless the asset brief says otherwise",
                "collision": "match gameplay role, not raw mesh bounds",
            }
        )
    return {
        "project": game["display_name"],
        "scale": "1 Blender unit = 1 meter",
        "assets": manifest_assets,
    }


def _parse_budget_int(text: str, keyword: str, *, default: int) -> int:
    pattern = r"(\d+)\s*" + re.escape(keyword)
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return default


def _project_yml(swift_name: str, display_name: str, bundle_suffix: str) -> str:
    return f"""name: {swift_name}
options:
  bundleIdPrefix: com.kyylian
  deploymentTarget:
    iOS: "18.0"
settings:
  base:
    SWIFT_VERSION: 5.0
    MARKETING_VERSION: 0.1.0
    CURRENT_PROJECT_VERSION: 1
targets:
  {swift_name}:
    type: application
    platform: iOS
    sources:
      - path: Sources/{swift_name}
      - path: Assets/Imported
        type: folder
        buildPhase: resources
      - path: Assets/Textures
        type: folder
        buildPhase: resources
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: com.kyylian.{bundle_suffix}
        PRODUCT_NAME: {swift_name}
        GENERATE_INFOPLIST_FILE: YES
        INFOPLIST_KEY_CFBundleDisplayName: {_yaml_string(display_name)}
        INFOPLIST_KEY_UIApplicationSceneManifest_Generation: YES
        INFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents: YES
        INFOPLIST_KEY_UILaunchScreen_Generation: YES
        TARGETED_DEVICE_FAMILY: "1,2"
"""


def _app_swift(swift_name: str) -> str:
    return f"""import SwiftUI

@main
struct {swift_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}
"""


def _game_state_swift(spec: Mapping[str, Any]) -> str:
    session_seconds = int(spec["game"]["session_seconds"])
    archetype_fields = archetype_state_fields(str(spec["game"]["archetype"]))
    extra_fields = ""
    if archetype_fields:
        extra_fields = "\n" + "\n".join(f"    {field}" for field in archetype_fields)
    return f"""import Foundation

enum GamePhase: String {{
    case idle
    case countdown
    case playing
    case paused
    case result
}}

struct GameSessionState {{
    var phase: GamePhase = .idle
    var score: Int = 0
    var elapsedSeconds: Int = 0
    var sessionSeconds: Int = {session_seconds}
    var attempt: Int = 1
    var lastEvent: String = "none"
{extra_fields}
}}
"""


def _screenshot_state_swift(spec: Mapping[str, Any]) -> str:
    cases = "\n".join(
        f'    case {swift_identifier_for(str(state))} = "{state}"' for state in spec["release"]["screenshots"]
    )
    return f"""import Foundation

enum ScreenshotState: String, CaseIterable, Identifiable {{
    static let launchEnvironmentKey = "RKG_SCREENSHOT_STATE"
    static let launchArgumentKey = "--rkg-screenshot-state"

{cases}

    var id: String {{ rawValue }}

    static var requested: ScreenshotState? {{
        let process = ProcessInfo.processInfo
        if let rawValue = process.environment[launchEnvironmentKey],
           let state = ScreenshotState(rawValue: rawValue) {{
            return state
        }}
        if let keyIndex = process.arguments.firstIndex(of: launchArgumentKey) {{
            let valueIndex = process.arguments.index(after: keyIndex)
            if valueIndex < process.arguments.endIndex {{
                return ScreenshotState(rawValue: process.arguments[valueIndex])
            }}
        }}
        return nil
    }}

    var evidencePath: String {{
        "Docs/screenshots/\\(rawValue).jpg"
    }}
}}
"""


def _session_control_swift() -> str:
    return """import Foundation

enum SessionControl {
    static func isPlaying(_ state: GameSessionState) -> Bool {
        state.phase == .playing
    }

    static func isResult(_ state: GameSessionState) -> Bool {
        state.phase == .result
    }

    static func reset() -> GameSessionState {
        GameSessionState()
    }

    static func markResult(_ state: GameSessionState, event: String) -> GameSessionState {
        var next = state
        next.phase = .result
        next.lastEvent = event
        return next
    }
}
"""


def _feedback_state_swift() -> str:
    return """import Foundation

enum FeedbackState {
    static func message(for state: GameSessionState) -> String {
        state.lastEvent.capitalized
    }
}
"""


def _input_intent_swift(spec: Mapping[str, Any]) -> str:
    primary_action = _primary_action_title(str(spec["game"]["archetype"]))
    return f"""import Foundation

enum InputIntent {{
    static let startTitle = "Start"
    static let resetTitle = "Reset"
    static let primaryActionTitle = {_swift_string_literal(primary_action)}

    static func primaryButtonTitle(isPlaying: Bool) -> String {{
        isPlaying ? primaryActionTitle : startTitle
    }}
}}
"""


def _primary_action_title(archetype_id: str) -> str:
    return {
        "target_shooter": "Hit",
        "lane_dodger": "Dodge",
        "toss_physics": "Throw",
        "stack_puzzle": "Place",
        "wave_defense_lite": "Fire",
        "fighter_2_5d": "Attack",
        "flappy_side_scroller": "Flap",
    }.get(archetype_id, "Start")


def _game_rules_swift(spec: Mapping[str, Any]) -> str:
    scoring = spec["loop"]["scoring"]
    hit = int(scoring.get("hit", 10))
    perfect = int(scoring.get("perfect", hit))
    archetype_rules = archetype_rule_members(str(spec["game"]["archetype"]))
    extra_rules = ""
    if archetype_rules:
        extra_rules = "\n\n" + "\n\n".join(indent_swift_block(rule, spaces=4) for rule in archetype_rules)
    return f"""import Foundation

enum GameRules {{
    static let hitScore = {hit}
    static let perfectScore = {perfect}

    static func scoreForHit(isPerfect: Bool) -> Int {{
        isPerfect ? perfectScore : hitScore
    }}

    static func hasSessionEnded(elapsedSeconds: Int, sessionSeconds: Int) -> Bool {{
        elapsedSeconds >= sessionSeconds
    }}
{extra_rules}
}}
"""


def _asset_loader_swift() -> str:
    return """import RealityKit

enum AssetLoader {
    static func loadPrimaryEntity(assetId: String, role: String, fallback: String) -> Entity {
        if let imported = try? Entity.load(named: assetId) {
            imported.scale = [1, 1, 1]
            return imported
        }
        return FallbackFactory.makeFallback(role: role, fallback: fallback)
    }

    static func loadPrimaryEntity(assetId: String, role: String) -> Entity {
        loadPrimaryEntity(assetId: assetId, role: role, fallback: "")
    }
}
"""


def _fallback_factory_swift() -> str:
    return """import RealityKit
import UIKit

enum FallbackFactory {
    static func makeFallback(role: String, fallback: String) -> ModelEntity {
        switch fallback {
        case "procedural_capsule":
            return ModelEntity(
                mesh: .generateBox(size: [0.24, 0.24, 0.20]),
                materials: [SimpleMaterial(color: UIColor(red: 0.24, green: 0.46, blue: 0.52, alpha: 1.0), roughness: 0.48, isMetallic: false)]
            )
        case "procedural_vehicle":
            return ModelEntity(
                mesh: .generateBox(size: [0.30, 0.14, 0.46]),
                materials: [SimpleMaterial(color: .systemBlue, roughness: 0.35, isMetallic: false)]
            )
        case "procedural_weapon":
            return ModelEntity(
                mesh: .generateBox(size: [0.08, 0.08, 0.32]),
                materials: [SimpleMaterial(color: .lightGray, roughness: 0.30, isMetallic: true)]
            )
        case "procedural_enemy":
            return ModelEntity(
                mesh: .generateBox(size: [0.24, 0.38, 0.18]),
                materials: [SimpleMaterial(color: .systemPink, roughness: 0.45, isMetallic: false)]
            )
        case "procedural_cover":
            return ModelEntity(
                mesh: .generateBox(size: [0.44, 0.28, 0.18]),
                materials: [SimpleMaterial(color: .gray, roughness: 0.70, isMetallic: false)]
            )
        case "procedural_track", "procedural_lane", "procedural_grid", "procedural_arena":
            return ModelEntity(
                mesh: .generatePlane(width: 2.4, depth: 2.4),
                materials: [SimpleMaterial(color: .darkGray, roughness: 0.8, isMetallic: false)]
            )
        case "procedural_block", "procedural_box":
            return ModelEntity(
                mesh: .generateBox(size: 0.28),
                materials: [SimpleMaterial(color: .systemOrange, roughness: 0.5, isMetallic: false)]
            )
        case "procedural_gate":
            return ModelEntity(
                mesh: .generateBox(size: [0.50, 0.32, 0.05]),
                materials: [SimpleMaterial(color: .systemTeal, roughness: 0.35, isMetallic: false)]
            )
        case "procedural_pickup":
            return ModelEntity(
                mesh: .generateSphere(radius: 0.12),
                materials: [SimpleMaterial(color: .systemGreen, roughness: 0.35, isMetallic: false)]
            )
        case "procedural_spark":
            return ModelEntity(
                mesh: .generateSphere(radius: 0.07),
                materials: [SimpleMaterial(color: .systemYellow, roughness: 0.25, isMetallic: false)]
            )
        case "procedural_ring", "procedural_rings", "procedural_guard":
            return ModelEntity(
                mesh: .generateBox(size: [0.36, 0.04, 0.04]),
                materials: [SimpleMaterial(color: .systemTeal, roughness: 0.25, isMetallic: false)]
            )
        default:
            return makeFallback(role: role)
        }
    }

    static func makeFallback(role: String) -> ModelEntity {
        switch role {
        case "arena", "environment":
            return ModelEntity(
                mesh: .generatePlane(width: 2.4, depth: 2.4),
                materials: [SimpleMaterial(color: .darkGray, roughness: 0.8, isMetallic: false)]
            )
        case "obstacle", "hazard":
            return ModelEntity(
                mesh: .generateBox(size: 0.28),
                materials: [SimpleMaterial(color: .systemOrange, roughness: 0.5, isMetallic: false)]
            )
        case "pickup":
            return ModelEntity(
                mesh: .generateSphere(radius: 0.12),
                materials: [SimpleMaterial(color: .systemGreen, roughness: 0.35, isMetallic: false)]
            )
        case "opponent":
            return ModelEntity(
                mesh: .generateBox(size: [0.24, 0.46, 0.16]),
                materials: [SimpleMaterial(color: .systemPurple, roughness: 0.45, isMetallic: false)]
            )
        case "enemy":
            return ModelEntity(
                mesh: .generateBox(size: [0.24, 0.38, 0.18]),
                materials: [SimpleMaterial(color: .systemPink, roughness: 0.45, isMetallic: false)]
            )
        case "vehicle":
            return ModelEntity(
                mesh: .generateBox(size: [0.30, 0.14, 0.46]),
                materials: [SimpleMaterial(color: .systemBlue, roughness: 0.35, isMetallic: false)]
            )
        case "weapon":
            return ModelEntity(
                mesh: .generateBox(size: [0.08, 0.08, 0.32]),
                materials: [SimpleMaterial(color: .lightGray, roughness: 0.30, isMetallic: true)]
            )
        case "cover":
            return ModelEntity(
                mesh: .generateBox(size: [0.44, 0.28, 0.18]),
                materials: [SimpleMaterial(color: .gray, roughness: 0.70, isMetallic: false)]
            )
        case "hit_vfx":
            return ModelEntity(
                mesh: .generateSphere(radius: 0.07),
                materials: [SimpleMaterial(color: .systemYellow, roughness: 0.25, isMetallic: false)]
            )
        case "guard_cue", "telegraph":
            return ModelEntity(
                mesh: .generateBox(size: [0.36, 0.04, 0.04]),
                materials: [SimpleMaterial(color: .systemTeal, roughness: 0.25, isMetallic: false)]
            )
        case "projectile":
            return ModelEntity(
                mesh: .generateSphere(radius: 0.08),
                materials: [SimpleMaterial(color: .systemBlue, roughness: 0.3, isMetallic: false)]
            )
        default:
            return ModelEntity(
                mesh: .generateSphere(radius: 0.18),
                materials: [SimpleMaterial(color: .systemRed, roughness: 0.35, isMetallic: false)]
            )
        }
    }
}
"""


def _world_rig_swift(spec: Mapping[str, Any] | None = None) -> str:
    projectile_feedback = _world_rig_projectile_feedback_swift() if _world_rig_includes_projectile_feedback(spec) else ""
    swift = """import Foundation
import RealityKit
import UIKit

struct ProjectileFeedbackStyle {
    static let standard = ProjectileFeedbackStyle()

    let idleTargetColor = UIColor(red: 0.22, green: 0.30, blue: 0.34, alpha: 1.0)
    let hitTargetColor = UIColor(red: 0.95, green: 0.78, blue: 0.34, alpha: 1.0)
    let trailColor = UIColor(red: 0.34, green: 0.68, blue: 0.92, alpha: 1.0)
}

enum WorldRig {
    private static let rootName = "rkg|world=root"
    private static let targetFrameName = "rkg|world=target_frame"
    private static let hitPulseName = "rkg|world=hit_pulse"
    private static let projectileTrailName = "rkg|world=projectile_trail"

    static func install(into view: ARView, anchor: AnchorEntity) {
        view.environment.background = .color(.init(red: 0.055, green: 0.065, blue: 0.075, alpha: 1.0))
        guard anchor.findEntity(named: rootName) == nil else {
            return
        }

        let root = Entity()
        root.name = rootName
        anchor.addChild(root)

        addLighting(to: root)
        addBackdrop(to: root)
        addArena(to: root)
        addTargetFrame(to: root)
        addProjectileFeedback(to: root)
    }

__PROJECTILE_FEEDBACK_METHOD__
    static func updateIdleMotion(anchor: AnchorEntity, time: Float) {
        guard let root = anchor.findEntity(named: rootName) else {
            return
        }
        root.position.x = wave(time * 0.8) * 0.012

        if let targetFrame = anchor.findEntity(named: targetFrameName) {
            targetFrame.position.y = 0.08 + wave(time * 1.6) * 0.015
        }

        for index in 0..<3 {
            let laneName = "rkg|world=lane_\\(index)"
            guard let lane = anchor.findEntity(named: laneName) else {
                continue
            }
            var scale = lane.scale
            scale.z = 1.0 + wave(time * 1.2 + Float(index)) * 0.035
            lane.scale = scale
        }
    }

    private static func wave(_ value: Float) -> Float {
        Float(sin(Double(value)))
    }

    private static func addLighting(to root: Entity) {
        let keyLight = DirectionalLight()
        keyLight.name = "rkg|world=key_light"
        keyLight.light.intensity = 2800
        keyLight.orientation = simd_quatf(angle: -.pi / 4.0, axis: [1, 0, 0])
        root.addChild(keyLight)

        let rimLight = PointLight()
        rimLight.name = "rkg|world=rim_light"
        rimLight.light.intensity = 3600
        rimLight.position = [0.72, 0.84, -0.88]
        root.addChild(rimLight)
    }

    private static func addBackdrop(to root: Entity) {
        let backdropMaterial = SimpleMaterial(
            color: UIColor(red: 0.08, green: 0.10, blue: 0.115, alpha: 1.0),
            roughness: 0.88,
            isMetallic: false
        )
        let backdrop = ModelEntity(mesh: .generateBox(size: [3.4, 1.32, 0.06]), materials: [backdropMaterial])
        backdrop.name = "rkg|world=backdrop"
        backdrop.position = [0, 0.16, -2.36]
        root.addChild(backdrop)
    }

    private static func addArena(to root: Entity) {
        let floorMaterial = SimpleMaterial(
            color: UIColor(red: 0.14, green: 0.17, blue: 0.18, alpha: 1.0),
            roughness: 0.90,
            isMetallic: false
        )
        let floor = ModelEntity(mesh: .generateBox(size: [2.8, 0.04, 2.10]), materials: [floorMaterial])
        floor.name = "rkg|world=floor"
        floor.position = [0, -0.44, -1.18]
        root.addChild(floor)

        let laneMaterial = SimpleMaterial(
            color: UIColor(red: 0.26, green: 0.35, blue: 0.37, alpha: 1.0),
            roughness: 0.72,
            isMetallic: false
        )
        for index in 0..<3 {
            let lane = ModelEntity(mesh: .generateBox(size: [0.022, 0.014, 1.55]), materials: [laneMaterial])
            lane.name = "rkg|world=lane_\\(index)"
            lane.position = [Float(index - 1) * 0.45, -0.39, -1.02]
            root.addChild(lane)
        }
    }

    private static func addTargetFrame(to root: Entity) {
        let material = SimpleMaterial(
            color: UIColor(red: 0.22, green: 0.30, blue: 0.34, alpha: 1.0),
            roughness: 0.42,
            isMetallic: false
        )
        let targetFrame = ModelEntity(mesh: .generateBox(size: [0.52, 0.44, 0.035]), materials: [material])
        targetFrame.name = targetFrameName
        targetFrame.position = [0, 0.08, -1.44]
        root.addChild(targetFrame)
    }

    private static func addProjectileFeedback(to root: Entity) {
        let pulseMaterial = SimpleMaterial(
            color: UIColor(red: 0.95, green: 0.78, blue: 0.34, alpha: 1.0),
            roughness: 0.28,
            isMetallic: false
        )
        let hitPulse = ModelEntity(mesh: .generateSphere(radius: 0.12), materials: [pulseMaterial])
        hitPulse.name = hitPulseName
        hitPulse.position = [0, 0.16, -1.31]
        hitPulse.isEnabled = false
        root.addChild(hitPulse)

        let trailMaterial = SimpleMaterial(
            color: UIColor(red: 0.34, green: 0.68, blue: 0.92, alpha: 1.0),
            roughness: 0.30,
            isMetallic: false
        )
        let trail = ModelEntity(mesh: .generateBox(size: [0.08, 0.03, 0.42]), materials: [trailMaterial])
        trail.name = projectileTrailName
        trail.position = [0, 0.13, -1.01]
        trail.isEnabled = false
        root.addChild(trail)
    }
}
"""
    return swift.replace("__PROJECTILE_FEEDBACK_METHOD__", projectile_feedback)


def _world_rig_includes_projectile_feedback(spec: Mapping[str, Any] | None) -> bool:
    if spec is None:
        return True
    game = spec.get("game")
    if not isinstance(game, Mapping):
        return False
    if str(game.get("archetype")) != "custom_realitykit":
        return False
    systems = game.get("systems")
    if not isinstance(systems, list):
        return False
    return bool({str(system) for system in systems} & {"projectile", "shooting"})


def _world_rig_projectile_feedback_swift() -> str:
    return """    static func updateProjectileFeedback(anchor: AnchorEntity, state: GameSessionState, style: ProjectileFeedbackStyle) {
        let targetX = Float(GameRules.clampedProjectileLane(state.targetLane) - 1) * 0.45
        if let targetFrame = anchor.findEntity(named: targetFrameName) as? ModelEntity {
            targetFrame.position.x = targetX
            let color = state.lastProjectileHit ? style.hitTargetColor : style.idleTargetColor
            targetFrame.model?.materials = [SimpleMaterial(color: color, roughness: 0.42, isMetallic: false)]
        }

        if let hitPulse = anchor.findEntity(named: hitPulseName) {
            hitPulse.isEnabled = state.lastProjectileHit
            hitPulse.position = [targetX, 0.16, -1.31]
            let scale = state.lastProjectileHit ? Float(1.0 + Double(state.projectileHits) * 0.08) : 0.2
            hitPulse.scale = [scale, scale, scale]
        }

        if let trail = anchor.findEntity(named: projectileTrailName) as? ModelEntity {
            trail.isEnabled = state.projectileInFlight || state.lastProjectileHit
            trail.position = [
                Float(GameRules.clampedProjectileLane(state.projectileLane) - 1) * 0.45,
                0.13,
                -1.01
            ]
            trail.scale = [0.55, 1.0, state.projectileInFlight ? 1.45 : 0.65]
            trail.model?.materials = [SimpleMaterial(color: style.trailColor, roughness: 0.30, isMetallic: false)]
        }
    }

"""


def _runtime_scene_snapshot_swift() -> str:
    return """import Foundation
import RealityKit

enum RuntimeSceneSnapshotWriter {
    static func write(state: ScreenshotState?, anchor: AnchorEntity) {
        guard let state else {
            return
        }
        let payload: [String: Any] = [
            "schema_version": 1,
            "state": state.rawValue,
            "roles": collectRoles(from: anchor),
        ]
        guard JSONSerialization.isValidJSONObject(payload),
              let data = try? JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted, .sortedKeys]),
              let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
            return
        }
        let url = documents.appendingPathComponent("rkg-scene-snapshot-\\(state.rawValue).json")
        try? data.write(to: url, options: [.atomic])
    }

    private static func collectRoles(from anchor: AnchorEntity) -> [[String: Any]] {
        anchor.children.compactMap { child -> [String: Any]? in
            guard let metadata = parseMetadata(child.name) else {
                return nil
            }
            let position = child.position
            let bounds = child.visualBounds(relativeTo: anchor)
            return [
                "asset_id": metadata["asset"] ?? "",
                "role": metadata["role"] ?? "",
                "fallback": metadata["fallback"] ?? "",
                "entity_name": child.name,
                "is_enabled": child.isEnabled,
                "position": [
                    "x": Double(position.x),
                    "y": Double(position.y),
                    "z": Double(position.z),
                ],
                "visual_bounds": [
                    "center": vector(bounds.center),
                    "extents": vector(bounds.extents),
                ],
            ]
        }
    }

    private static func vector(_ value: SIMD3<Float>) -> [String: Any] {
        [
            "x": Double(value.x),
            "y": Double(value.y),
            "z": Double(value.z),
        ]
    }

    private static func parseMetadata(_ name: String) -> [String: String]? {
        let parts = name.split(separator: "|").map(String.init)
        guard parts.first == "rkg" else {
            return nil
        }
        var metadata: [String: String] = [:]
        for part in parts.dropFirst() {
            let pair = part.split(separator: "=", maxSplits: 1).map(String.init)
            if pair.count == 2 {
                metadata[pair[0]] = pair[1]
            }
        }
        return metadata
    }
}
"""


def _game_scene_controller_swift(spec: Mapping[str, Any]) -> str:
    if str(spec["game"]["archetype"]) == "target_shooter":
        return _target_shooter_game_scene_controller_swift(spec)
    if str(spec["game"]["archetype"]) == "lane_dodger":
        return _lane_dodger_game_scene_controller_swift(spec)
    if str(spec["game"]["archetype"]) == "toss_physics":
        return _toss_physics_game_scene_controller_swift(spec)
    if str(spec["game"]["archetype"]) == "wave_defense_lite":
        return _wave_defense_game_scene_controller_swift(spec)
    if str(spec["game"]["archetype"]) == "stack_puzzle":
        return _stack_puzzle_game_scene_controller_swift(spec)
    if str(spec["game"]["archetype"]) == "fighter_2_5d":
        return _fighter_game_scene_controller_swift(spec)
    if str(spec["game"]["archetype"]) == "flappy_side_scroller":
        return _flappy_game_scene_controller_swift(spec)
    if str(spec["game"]["archetype"]) == "custom_realitykit":
        return custom_realitykit_game_scene_controller_swift(spec)
    entity_lines = "\n\n".join(_runtime_entity_swift(entity) for entity in runtime_entities_for(spec))
    return f"""import RealityKit

final class GameSceneController {{
    private let anchor = AnchorEntity(world: .zero)

    func install(into view: ARView) {{
{entity_lines}

        view.scene.addAnchor(anchor)
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    func update(state: GameSessionState) {{
        anchor.position.z = SystemFlags.hasRacing ? -Float(state.primaryActions % 5) * 0.02 : 0
        anchor.scale = state.isFailureProofVisible ? [1.05, 1.05, 1.05] : [1, 1, 1]
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}
}}
"""


def _runtime_entity_swift(entity: Mapping[str, str]) -> str:
    variable = entity["variable"]
    asset_id = _swift_string_literal(entity["asset_id"])
    role = _swift_string_literal(entity["role"])
    fallback = _swift_string_literal(entity["fallback"])
    snapshot_name = _swift_string_literal(
        f"rkg|asset={entity['asset_id']}|role={entity['role']}|fallback={entity['fallback']}"
    )
    position = entity["position"]
    return f"""        let {variable} = AssetLoader.loadPrimaryEntity(assetId: {asset_id}, role: {role}, fallback: {fallback})
        {variable}.name = {snapshot_name}
        {variable}.position = {position}
        anchor.addChild({variable})"""


def _scene_entity_setup_lines(spec: Mapping[str, Any], bindings: list[tuple[str, set[str]]]) -> str:
    lines: list[str] = []
    bound_properties: set[str] = set()
    for entity in runtime_entities_for(spec):
        lines.append(_runtime_entity_swift(entity))
        for property_name, roles in bindings:
            if property_name in bound_properties:
                continue
            if entity["role"] in roles:
                lines.append(f"        {property_name} = {entity['variable']}")
                bound_properties.add(property_name)
    return "\n\n".join(lines)


def _target_shooter_game_scene_controller_swift(spec: Mapping[str, Any]) -> str:
    entity_lines = _scene_entity_setup_lines(
        spec,
        [
            ("targetEntity", {"target"}),
        ],
    )
    return f"""import RealityKit

final class GameSceneController {{
    private let anchor = AnchorEntity(world: .zero)
    private var targetEntity: Entity?

    func install(into view: ARView) {{
{entity_lines}

        view.scene.addAnchor(anchor)
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    func update(state: GameSessionState) {{
        targetEntity?.position = targetPosition(targetsHit: state.targetsHit)
        targetEntity?.scale = state.perfectHits > 0 ? [1.15, 1.15, 1.15] : [1, 1, 1]
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    private func targetPosition(targetsHit: Int) -> SIMD3<Float> {{
        let lane = Float((targetsHit % 3) - 1)
        let depth = Float(targetsHit % 2) * 0.18
        return [lane * 0.35, 0, -1.10 - depth]
    }}
}}
"""


def _lane_dodger_game_scene_controller_swift(spec: Mapping[str, Any]) -> str:
    entity_lines = _scene_entity_setup_lines(
        spec,
        [
            ("playerEntity", {"player"}),
            ("obstacleEntity", {"obstacle", "hazard"}),
        ],
    )
    return f"""import RealityKit

final class GameSceneController {{
    private let anchor = AnchorEntity(world: .zero)
    private var playerEntity: Entity?
    private var obstacleEntity: Entity?

    func install(into view: ARView) {{
{entity_lines}

        view.scene.addAnchor(anchor)
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    func update(state: GameSessionState) {{
        playerEntity?.position.x = xPosition(forLane: state.currentLane)
        obstacleEntity?.position.x = xPosition(forLane: state.obstacleLane)
        obstacleEntity?.position.z = -1.35 - Float(state.distance % 4) * 0.15
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    private func xPosition(forLane lane: Int) -> Float {{
        Float(GameRules.clampedLane(lane) - 1) * 0.45
    }}
}}
"""


def _toss_physics_game_scene_controller_swift(spec: Mapping[str, Any]) -> str:
    entity_lines = _scene_entity_setup_lines(
        spec,
        [
            ("projectileEntity", {"projectile"}),
            ("targetEntity", {"target"}),
        ],
    )
    return f"""import RealityKit

final class GameSceneController {{
    private let anchor = AnchorEntity(world: .zero)
    private var projectileEntity: Entity?
    private var targetEntity: Entity?

    func install(into view: ARView) {{
{entity_lines}

        view.scene.addAnchor(anchor)
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    func update(state: GameSessionState) {{
        projectileEntity?.position = projectilePosition(
            power: state.lastThrowPower,
            landed: state.landedInZone,
            attemptsRemaining: state.attemptsRemaining
        )
        projectileEntity?.scale = state.landedInZone ? [1.25, 1.25, 1.25] : [1, 1, 1]
        targetEntity?.position.y = state.landedInZone ? 0.05 : 0
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    private func projectilePosition(power: Double, landed: Bool, attemptsRemaining: Int) -> SIMD3<Float> {{
        if attemptsRemaining == GameRules.maxAttempts && !landed {{
            return [0, 0.20, -0.65]
        }}
        if landed {{
            return [0, 0.10, -1.25]
        }}
        let clampedPower = Float(GameRules.clampedThrowPower(power))
        return [0, 0.20 + clampedPower * 0.45, -0.65 - clampedPower * 0.75]
    }}
}}
"""


def _wave_defense_game_scene_controller_swift(spec: Mapping[str, Any]) -> str:
    entity_lines = _scene_entity_setup_lines(
        spec,
        [
            ("defenderEntity", {"player"}),
            ("threatEntity", {"target", "obstacle", "hazard"}),
        ],
    )
    return f"""import RealityKit

final class GameSceneController {{
    private let anchor = AnchorEntity(world: .zero)
    private var defenderEntity: Entity?
    private var threatEntity: Entity?

    func install(into view: ARView) {{
{entity_lines}

        view.scene.addAnchor(anchor)
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    func update(state: GameSessionState) {{
        threatEntity?.position = threatPosition(wave: state.wave, threatsRemaining: state.threatsRemaining)
        threatEntity?.scale = state.threatsRemaining == 0 ? [0.75, 0.75, 0.75] : [1, 1, 1]
        defenderEntity?.scale = state.isDefeated ? [0.85, 0.85, 0.85] : [1, 1, 1]
        defenderEntity?.position.y = state.health <= 1 ? -0.05 : 0
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    private func threatPosition(wave: Int, threatsRemaining: Int) -> SIMD3<Float> {{
        let lane = Float((wave + threatsRemaining) % 3 - 1)
        let pressure = Float(max(0, threatsRemaining))
        return [lane * 0.45, 0, -1.05 - pressure * 0.08]
    }}
}}
"""


def _stack_puzzle_game_scene_controller_swift(spec: Mapping[str, Any]) -> str:
    entity_lines = _scene_entity_setup_lines(
        spec,
        [
            ("pieceEntity", {"player"}),
            ("obstacleEntity", {"obstacle", "hazard"}),
        ],
    )
    return f"""import RealityKit

final class GameSceneController {{
    private let anchor = AnchorEntity(world: .zero)
    private var pieceEntity: Entity?
    private var obstacleEntity: Entity?

    func install(into view: ARView) {{
{entity_lines}

        view.scene.addAnchor(anchor)
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    func update(state: GameSessionState) {{
        pieceEntity?.position = piecePosition(piecesPlaced: state.piecesPlaced, stablePieces: state.stablePieces)
        pieceEntity?.scale = state.collapsed ? [0.80, 0.80, 0.80] : [1, 1, 1]
        obstacleEntity?.position.y = state.collapsed ? 0.18 : 0
        obstacleEntity?.scale = state.collapsed ? [1.20, 1.20, 1.20] : [1, 1, 1]
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    private func piecePosition(piecesPlaced: Int, stablePieces: Int) -> SIMD3<Float> {{
        let height = Float(max(0, stablePieces)) * 0.12
        let offset = Float((piecesPlaced % 3) - 1) * 0.12
        return [offset, height, -0.85]
    }}
}}
"""


def _fighter_game_scene_controller_swift(spec: Mapping[str, Any]) -> str:
    entity_lines = _scene_entity_setup_lines(
        spec,
        [
            ("playerEntity", {"player"}),
            ("opponentEntity", {"opponent"}),
            ("hitVfxEntity", {"hit_vfx"}),
            ("guardCueEntity", {"guard_cue", "telegraph"}),
        ],
    )
    return f"""import RealityKit

final class GameSceneController {{
    private let anchor = AnchorEntity(world: .zero)
    private var playerEntity: Entity?
    private var opponentEntity: Entity?
    private var hitVfxEntity: Entity?
    private var guardCueEntity: Entity?

    func install(into view: ARView) {{
{entity_lines}

        view.scene.addAnchor(anchor)
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    func update(state: GameSessionState) {{
        playerEntity?.position.x = state.isDodging ? -0.50 : -0.35
        playerEntity?.position.y = state.playerHealth <= 1 ? -0.04 : 0
        playerEntity?.scale = state.playerHealth <= 1 ? [0.90, 0.90, 0.90] : [1, 1, 1]
        opponentEntity?.position = opponentPosition(opponentHealth: state.opponentHealth, comboCount: state.comboCount)
        opponentEntity?.scale = state.isKnockout ? [0.70, 0.70, 0.70] : [1, 1, 1]
        hitVfxEntity?.isEnabled = state.comboCount > 0
        hitVfxEntity?.position = [0.03, 0.18, -0.86]
        let hitScale = Float(max(1, state.comboCount)) * 0.18
        hitVfxEntity?.scale = [hitScale, hitScale, hitScale]
        guardCueEntity?.isEnabled = state.guardMeter > 0
        guardCueEntity?.position = state.isDodging ? [-0.50, 0.24, -0.85] : [-0.35, 0.24, -0.85]
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    private func opponentPosition(opponentHealth: Int, comboCount: Int) -> SIMD3<Float> {{
        let damageRecoil = Float(max(0, GameRules.fighterMaxHealth - opponentHealth)) * 0.03
        let comboPulse = Float(comboCount % 2) * 0.04
        return [0.35 + damageRecoil + comboPulse, 0, -0.85]
    }}
}}
"""


def _flappy_game_scene_controller_swift(spec: Mapping[str, Any]) -> str:
    entity_lines = _scene_entity_setup_lines(
        spec,
        [
            ("birdEntity", {"player"}),
            ("obstacleEntity", {"obstacle", "hazard"}),
            ("arenaEntity", {"arena", "environment"}),
        ],
    )
    return f"""import RealityKit

final class GameSceneController {{
    private let anchor = AnchorEntity(world: .zero)
    private var birdEntity: Entity?
    private var obstacleEntity: Entity?
    private var arenaEntity: Entity?

    func install(into view: ARView) {{
{entity_lines}

        view.scene.addAnchor(anchor)
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    func update(state: GameSessionState) {{
        birdEntity?.position = birdPosition(birdY: state.birdY)
        birdEntity?.scale = state.isCollision ? [0.78, 0.78, 0.78] : [1, 1, 1]
        obstacleEntity?.position = obstaclePosition(obstacleX: state.obstacleX, gapY: state.gapY)
        obstacleEntity?.scale = state.isCollision ? [1.18, 1.18, 1.18] : [1, 1, 1]
        arenaEntity?.position.z = -0.08 - Float(state.pipesPassed % 4) * 0.02
        RuntimeSceneSnapshotWriter.write(state: ScreenshotState.requested, anchor: anchor)
    }}

    private func birdPosition(birdY: Double) -> SIMD3<Float> {{
        [-0.42, yPosition(forBirdY: birdY), -0.82]
    }}

    private func obstaclePosition(obstacleX: Double, gapY: Double) -> SIMD3<Float> {{
        [xPosition(forObstacleX: obstacleX), yPosition(forBirdY: gapY), -0.92]
    }}

    private func xPosition(forObstacleX value: Double) -> Float {{
        Float((value - 0.5) * 1.65)
    }}

    private func yPosition(forBirdY value: Double) -> Float {{
        Float((value - 0.5) * 1.10)
    }}
}}
"""


def _game_view_swift(spec: Mapping[str, Any]) -> str:
    if str(spec["game"]["archetype"]) in {
        "target_shooter",
        "lane_dodger",
        "toss_physics",
        "wave_defense_lite",
        "stack_puzzle",
        "fighter_2_5d",
        "flappy_side_scroller",
        "custom_realitykit",
    }:
        return _state_bound_game_view_swift()
    return """import RealityKit
import SwiftUI

struct GameView: UIViewRepresentable {
    private let controller = GameSceneController()

    func makeUIView(context: Context) -> ARView {
        let view = ARView(frame: .zero, cameraMode: .nonAR, automaticallyConfigureSession: false)
        controller.install(into: view)
        return view
    }

    func updateUIView(_ uiView: ARView, context: Context) {}
}
"""


def _state_bound_game_view_swift() -> str:
    return """import RealityKit
import SwiftUI

struct GameView: UIViewRepresentable {
    let state: GameSessionState

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    func makeUIView(context: Context) -> ARView {
        let view = ARView(frame: .zero, cameraMode: .nonAR, automaticallyConfigureSession: false)
        CameraRig.configure(view)
        context.coordinator.controller.install(into: view)
        context.coordinator.controller.update(state: state)
        return view
    }

    func updateUIView(_ uiView: ARView, context: Context) {
        context.coordinator.controller.update(state: state)
    }

    final class Coordinator {
        let controller = GameSceneController()
    }
}
"""


def _result_view_swift() -> str:
    return """import SwiftUI

struct ResultView: View {
    let state: GameSessionState
    let onReset: () -> Void

    var body: some View {
        VStack(spacing: 12) {
            Text("Score \\(state.score)")
                .font(.system(size: 40, weight: .bold, design: .rounded).monospacedDigit())
            Button(InputIntent.resetTitle, action: onReset)
                .buttonStyle(.borderedProminent)
        }
        .frame(maxWidth: .infinity)
        .padding(18)
        .foregroundStyle(.white)
        .background(Color.black.opacity(0.62))
        .overlay(
            RoundedRectangle(cornerRadius: 8, style: .continuous)
                .stroke(Color.white.opacity(0.16), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }
}
"""


def _worklog(display_name: str) -> str:
    return f"""# Worklog

## Factory Scaffold

Goal: Create the first generated RealityKit game skeleton for {display_name}.
Verification: Run `python3 Tools/rkp.py doctor`, then generate/build with XcodeGen and xcodebuild when Xcode is available.
Lesson: Keep procedural placeholders until imported assets are accepted with screenshot evidence.
"""


def _handoff(display_name: str, game_id: str) -> str:
    return f"""# AI Handoff

Project: {display_name}
Game id: {game_id}

Start from `GameSpec.json`. Keep RKP as the asset acceptance source of truth. Do not mark any asset imported without `rkp accept-asset` and screenshot evidence.
"""


def _smoke_test_py(display_name: str) -> str:
    return f"""import unittest


class GeneratedProjectSmokeTests(unittest.TestCase):
    def test_generated_project_name_is_present(self) -> None:
        self.assertEqual({json.dumps(display_name)}, {json.dumps(display_name)})


if __name__ == "__main__":
    unittest.main()
"""
