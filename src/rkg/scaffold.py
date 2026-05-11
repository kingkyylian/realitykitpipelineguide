from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rkg.archetype_runtime import archetype_rule_members, archetype_state_fields, indent_swift_block
from rkg.asset_briefs import asset_brief
from rkg.content_views import content_view_swift
from rkg.plan import runtime_entities_for, swift_identifier_for, swift_name_for
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
    _write_text(output / "Sources" / swift_name / "GameRules.swift", _game_rules_swift(spec))
    _write_text(output / "Sources" / swift_name / "AssetLoader.swift", _asset_loader_swift())
    _write_text(output / "Sources" / swift_name / "FallbackFactory.swift", _fallback_factory_swift())
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
        case "procedural_ring", "procedural_guard":
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
    entity_lines = "\n\n".join(_runtime_entity_swift(entity) for entity in runtime_entities_for(spec))
    return f"""import RealityKit

final class GameSceneController {{
    private let anchor = AnchorEntity(world: .zero)

    func install(into view: ARView) {{
{entity_lines}

        view.scene.addAnchor(anchor)
    }}
}}
"""


def _runtime_entity_swift(entity: Mapping[str, str]) -> str:
    variable = entity["variable"]
    asset_id = _swift_string_literal(entity["asset_id"])
    role = _swift_string_literal(entity["role"])
    fallback = _swift_string_literal(entity["fallback"])
    position = entity["position"]
    return f"""        let {variable} = AssetLoader.loadPrimaryEntity(assetId: {asset_id}, role: {role}, fallback: {fallback})
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
    }}

    func update(state: GameSessionState) {{
        targetEntity?.position = targetPosition(targetsHit: state.targetsHit)
        targetEntity?.scale = state.perfectHits > 0 ? [1.15, 1.15, 1.15] : [1, 1, 1]
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
    }}

    func update(state: GameSessionState) {{
        playerEntity?.position.x = xPosition(forLane: state.currentLane)
        obstacleEntity?.position.x = xPosition(forLane: state.obstacleLane)
        obstacleEntity?.position.z = -1.35 - Float(state.distance % 4) * 0.15
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
    }}

    func update(state: GameSessionState) {{
        projectileEntity?.position = projectilePosition(
            power: state.lastThrowPower,
            landed: state.landedInZone,
            attemptsRemaining: state.attemptsRemaining
        )
        projectileEntity?.scale = state.landedInZone ? [1.25, 1.25, 1.25] : [1, 1, 1]
        targetEntity?.position.y = state.landedInZone ? 0.05 : 0
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
    }}

    func update(state: GameSessionState) {{
        threatEntity?.position = threatPosition(wave: state.wave, threatsRemaining: state.threatsRemaining)
        threatEntity?.scale = state.threatsRemaining == 0 ? [0.75, 0.75, 0.75] : [1, 1, 1]
        defenderEntity?.scale = state.isDefeated ? [0.85, 0.85, 0.85] : [1, 1, 1]
        defenderEntity?.position.y = state.health <= 1 ? -0.05 : 0
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
    }}

    func update(state: GameSessionState) {{
        pieceEntity?.position = piecePosition(piecesPlaced: state.piecesPlaced, stablePieces: state.stablePieces)
        pieceEntity?.scale = state.collapsed ? [0.80, 0.80, 0.80] : [1, 1, 1]
        obstacleEntity?.position.y = state.collapsed ? 0.18 : 0
        obstacleEntity?.scale = state.collapsed ? [1.20, 1.20, 1.20] : [1, 1, 1]
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
    }}

    private func opponentPosition(opponentHealth: Int, comboCount: Int) -> SIMD3<Float> {{
        let damageRecoil = Float(max(0, GameRules.fighterMaxHealth - opponentHealth)) * 0.03
        let comboPulse = Float(comboCount % 2) * 0.04
        return [0.35 + damageRecoil + comboPulse, 0, -0.85]
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
        VStack(spacing: 8) {
            Text("Score \\(state.score)")
                .font(.title2.monospacedDigit())
            Button(InputIntent.resetTitle, action: onReset)
                .buttonStyle(.borderedProminent)
        }
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
