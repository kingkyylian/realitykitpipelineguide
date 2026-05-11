from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from rkg.plan import runtime_entities_for


def custom_realitykit_state_fields() -> list[str]:
    return [
        "var primaryActions: Int = 0",
        "var isFailureProofVisible: Bool = false",
        "var raceDistance: Int = 0",
        "var currentLap: Int = 0",
        "var checkpointIndex: Int = 0",
        "var vehicleLane: Int = 1",
        "var obstacleLane: Int = 0",
        "var isRaceCollision: Bool = false",
        "var shooterHealth: Int = GameRules.shooterMaxHealth",
        "var enemiesRemaining: Int = GameRules.startingEnemyCount",
        "var shotsFired: Int = 0",
        "var aimLane: Int = 1",
        "var enemyLane: Int = 1",
        "var isTakingCover: Bool = false",
        "var isShooterDefeated: Bool = false",
        "var lastShotHit: Bool = false",
    ]


def custom_realitykit_rule_members() -> list[str]:
    return [
        "static let raceLaneCount = 3",
        "static let checkpointCount = 3",
        """static func clampedRaceLane(_ lane: Int) -> Int {
    min(max(lane, 0), raceLaneCount - 1)
}""",
        """static func laneAfterSteer(currentLane: Int, direction: Int) -> Int {
    clampedRaceLane(currentLane + direction)
}""",
        """static func nextRaceObstacleLane(after distance: Int) -> Int {
    (distance + 2) % raceLaneCount
}""",
        """static func nextCheckpointIndex(after distance: Int) -> Int {
    distance % checkpointCount
}""",
        """static func hasRaceCollision(vehicleLane: Int, obstacleLane: Int, distance: Int) -> Bool {
    SystemFlags.hasCollision && distance >= 2 && vehicleLane == obstacleLane
}""",
        """static func scoreForRace(distance: Int, currentLap: Int) -> Int {
    max(0, distance) * hitScore + max(0, currentLap - 1) * perfectScore
}""",
        """static func startRacingSession(sessionSeconds: Int) -> GameSessionState {
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.currentLap = 1
    state.checkpointIndex = 0
    state.vehicleLane = 1
    state.obstacleLane = nextRaceObstacleLane(after: 0)
    state.lastEvent = "race started"
    return state
}""",
        """static func advanceRacingFrame(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return startRacingSession(sessionSeconds: next.sessionSeconds)
    }
    next.primaryActions += 1
    next.elapsedSeconds += 1
    next.raceDistance += 1
    next.obstacleLane = nextRaceObstacleLane(after: next.raceDistance)
    next.checkpointIndex = nextCheckpointIndex(after: next.raceDistance)
    let completedLap = next.raceDistance > 0 && next.checkpointIndex == 0
    if completedLap {
        next.currentLap += 1
    }
    next.score = scoreForRace(distance: next.raceDistance, currentLap: next.currentLap)
    if hasRaceCollision(vehicleLane: next.vehicleLane, obstacleLane: next.obstacleLane, distance: next.raceDistance) {
        next.isRaceCollision = true
        next.isFailureProofVisible = true
        next = SessionControl.markResult(next, event: "collision")
    } else if completedLap {
        next.lastEvent = "lap complete"
    } else {
        next.lastEvent = "checkpoint \\(next.checkpointIndex + 1)"
    }
    return next
}""",
        "static let shooterLaneCount = 3",
        "static let shooterMaxHealth = 3",
        "static let startingEnemyCount = 3",
        """static func clampedShooterLane(_ lane: Int) -> Int {
    min(max(lane, 0), shooterLaneCount - 1)
}""",
        """static func aimLaneAfterMove(currentLane: Int, direction: Int) -> Int {
    clampedShooterLane(currentLane + direction)
}""",
        """static func nextShooterEnemyLane(after shotsFired: Int) -> Int {
    (shotsFired + 1) % shooterLaneCount
}""",
        """static func startShooterSession(sessionSeconds: Int) -> GameSessionState {
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.shooterHealth = shooterMaxHealth
    state.enemiesRemaining = startingEnemyCount
    state.aimLane = 1
    state.enemyLane = 1
    state.lastEvent = "breach started"
    return state
}""",
        """static func toggleShooterCover(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return next
    }
    next.isTakingCover.toggle()
    next.lastEvent = next.isTakingCover ? "in cover" : "leaving cover"
    return next
}""",
        """static func applyShooterDamage(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return next
    }
    if next.isTakingCover {
        next.lastEvent = "covered"
        return next
    }
    next.shooterHealth = max(0, next.shooterHealth - 1)
    if next.shooterHealth <= 0 {
        next.isShooterDefeated = true
        next.isFailureProofVisible = true
        next = SessionControl.markResult(next, event: "health depleted")
    } else {
        next.lastEvent = "took damage"
    }
    return next
}""",
        """static func fireShooterWeapon(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return startShooterSession(sessionSeconds: next.sessionSeconds)
    }
    next.primaryActions += 1
    next.elapsedSeconds += 1
    next.shotsFired += 1
    let hit = SystemFlags.hasWeapon && next.enemiesRemaining > 0 && next.aimLane == next.enemyLane
    next.lastShotHit = hit
    if hit {
        next.enemiesRemaining = max(0, next.enemiesRemaining - 1)
        next.score += scoreForHit(isPerfect: next.shotsFired % 3 == 0)
        next.lastEvent = "hit"
    } else if next.enemiesRemaining > 0 {
        next = applyShooterDamage(next)
    } else {
        next.lastEvent = "clear"
    }
    if next.enemiesRemaining <= 0 {
        return SessionControl.markResult(next, event: "room clear")
    }
    next.enemyLane = nextShooterEnemyLane(after: next.shotsFired)
    return next
}""",
        """static func advanceShooterFrame(_ state: GameSessionState) -> GameSessionState {
    fireShooterWeapon(state)
}""",
        """static func startCustomRealityKitSession(sessionSeconds: Int) -> GameSessionState {
    if SystemFlags.hasRacing {
        return startRacingSession(sessionSeconds: sessionSeconds)
    }
    if SystemFlags.hasWeapon || SystemFlags.hasEnemies || SystemFlags.hasHealth || SystemFlags.hasCover {
        return startShooterSession(sessionSeconds: sessionSeconds)
    }
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.lastEvent = "started"
    return state
}""",
        """static func advanceCustomRealityKitSession(_ state: GameSessionState) -> GameSessionState {
    if SystemFlags.hasRacing {
        return advanceRacingFrame(state)
    }
    if SystemFlags.hasWeapon || SystemFlags.hasEnemies || SystemFlags.hasHealth || SystemFlags.hasCover {
        return advanceShooterFrame(state)
    }
    var next = state
    if next.phase != .playing {
        return startCustomRealityKitSession(sessionSeconds: next.sessionSeconds)
    }
    next.primaryActions += 1
    next.elapsedSeconds += 1
    next.score += scoreForHit(isPerfect: SystemFlags.has("lap_timer"))
    next.lastEvent = InputController.primaryActionLabel
    if SystemFlags.hasCollision && next.primaryActions >= 2 {
        next.isFailureProofVisible = true
        next = SessionControl.markResult(next, event: "collision proof")
    }
    return next
}""",
        """static func racingScreenshotSession(for screenshotState: ScreenshotState?, fallback: GameSessionState) -> GameSessionState {
    switch screenshotState?.rawValue {
    case "gameplay_start":
        return startRacingSession(sessionSeconds: fallback.sessionSeconds)
    case "mid_action":
        var state = startRacingSession(sessionSeconds: fallback.sessionSeconds)
        state = advanceRacingFrame(state)
        return state
    case "fail_or_hit":
        var state = startRacingSession(sessionSeconds: fallback.sessionSeconds)
        state = advanceRacingFrame(state)
        state = advanceRacingFrame(state)
        return state
    case "results":
        var state = startRacingSession(sessionSeconds: fallback.sessionSeconds)
        state = advanceRacingFrame(state)
        state = advanceRacingFrame(state)
        state = advanceRacingFrame(state)
        return SessionControl.markResult(state, event: "race results")
    default:
        return fallback
    }
}""",
        """static func shooterScreenshotSession(for screenshotState: ScreenshotState?, fallback: GameSessionState) -> GameSessionState {
    switch screenshotState?.rawValue {
    case "gameplay_start":
        return startShooterSession(sessionSeconds: fallback.sessionSeconds)
    case "mid_action":
        var state = startShooterSession(sessionSeconds: fallback.sessionSeconds)
        state = fireShooterWeapon(state)
        return state
    case "fail_or_hit":
        var state = startShooterSession(sessionSeconds: fallback.sessionSeconds)
        state.aimLane = 0
        state = fireShooterWeapon(state)
        state = fireShooterWeapon(state)
        return state
    case "results":
        var state = startShooterSession(sessionSeconds: fallback.sessionSeconds)
        state = fireShooterWeapon(state)
        state.aimLane = state.enemyLane
        state = fireShooterWeapon(state)
        state.aimLane = state.enemyLane
        state = fireShooterWeapon(state)
        return state
    default:
        return fallback
    }
}""",
        """static func customRealityKitScreenshotSession(for screenshotState: ScreenshotState?, fallback: GameSessionState) -> GameSessionState {
    if SystemFlags.hasRacing {
        return racingScreenshotSession(for: screenshotState, fallback: fallback)
    }
    if SystemFlags.hasWeapon || SystemFlags.hasEnemies || SystemFlags.hasHealth || SystemFlags.hasCover {
        return shooterScreenshotSession(for: screenshotState, fallback: fallback)
    }
    switch screenshotState?.rawValue {
    case "gameplay_start":
        return startCustomRealityKitSession(sessionSeconds: fallback.sessionSeconds)
    case "mid_action":
        var state = startCustomRealityKitSession(sessionSeconds: fallback.sessionSeconds)
        state = advanceCustomRealityKitSession(state)
        return state
    case "fail_or_hit":
        var state = startCustomRealityKitSession(sessionSeconds: fallback.sessionSeconds)
        state = advanceCustomRealityKitSession(state)
        state = advanceCustomRealityKitSession(state)
        return state
    case "results":
        var state = startCustomRealityKitSession(sessionSeconds: fallback.sessionSeconds)
        state = advanceCustomRealityKitSession(state)
        return SessionControl.markResult(state, event: "results proof")
    default:
        return fallback
    }
}""",
    ]


def custom_realitykit_adapter_content_sections() -> str:
    return """                if SystemFlags.hasRacing {
                    HStack(spacing: 12) {
                        Text("Lap \\(state.currentLap)")
                            .font(.caption.monospacedDigit())
                        Text("Distance \\(state.raceDistance)")
                            .font(.caption.monospacedDigit())
                        Text("Checkpoint \\(state.checkpointIndex + 1)/\\(GameRules.checkpointCount)")
                            .font(.caption.monospacedDigit())
                        Text("Lane \\(state.vehicleLane + 1)")
                            .font(.caption.monospacedDigit())
                        Spacer()
                    }

                    HStack {
                        Button("Left") {
                            state.vehicleLane = GameRules.laneAfterSteer(currentLane: state.vehicleLane, direction: -1)
                        }
                        .buttonStyle(.bordered)
                        Button("Right") {
                            state.vehicleLane = GameRules.laneAfterSteer(currentLane: state.vehicleLane, direction: 1)
                        }
                        .buttonStyle(.bordered)
                        Spacer()
                    }
                }

                if SystemFlags.hasWeapon || SystemFlags.hasEnemies || SystemFlags.hasHealth || SystemFlags.hasCover {
                    HStack(spacing: 12) {
                        Text("Health \\(state.shooterHealth)")
                            .font(.caption.monospacedDigit())
                        Text("Enemies \\(state.enemiesRemaining)")
                            .font(.caption.monospacedDigit())
                        Text("Shots \\(state.shotsFired)")
                            .font(.caption.monospacedDigit())
                        Text("Aim \\(state.aimLane + 1)")
                            .font(.caption.monospacedDigit())
                        Spacer()
                    }

                    HStack {
                        Button("Aim Left") {
                            state.aimLane = GameRules.aimLaneAfterMove(currentLane: state.aimLane, direction: -1)
                        }
                        .buttonStyle(.bordered)
                        Button("Aim Right") {
                            state.aimLane = GameRules.aimLaneAfterMove(currentLane: state.aimLane, direction: 1)
                        }
                        .buttonStyle(.bordered)
                        Button("Cover") {
                            state = GameRules.toggleShooterCover(state)
                        }
                        .buttonStyle(.bordered)
                        Spacer()
                    }
                }
"""


def custom_realitykit_game_scene_controller_swift(spec: Mapping[str, Any]) -> str:
    entity_lines = _scene_entity_setup_lines(
        spec,
        [
            ("vehicleEntity", {"player", "vehicle"}),
            ("playerEntity", {"player"}),
            ("trackEntity", {"arena", "environment", "track"}),
            ("obstacleEntity", {"obstacle", "hazard"}),
            ("checkpointEntity", {"ui_prop", "checkpoint", "target"}),
            ("weaponEntity", {"weapon"}),
            ("enemyEntity", {"enemy"}),
            ("coverEntity", {"cover"}),
        ],
    )
    return f"""import RealityKit

final class GameSceneController {{
    private let anchor = AnchorEntity(world: .zero)
    private var vehicleEntity: Entity?
    private var playerEntity: Entity?
    private var trackEntity: Entity?
    private var obstacleEntity: Entity?
    private var checkpointEntity: Entity?
    private var weaponEntity: Entity?
    private var enemyEntity: Entity?
    private var coverEntity: Entity?
    private var cameraRigEntity: Entity?

    func install(into view: ARView) {{
{entity_lines}

        let cameraRig = Entity()
        cameraRig.transform = CameraRig.transform
        cameraRigEntity = cameraRig
        anchor.addChild(cameraRig)
        view.scene.addAnchor(anchor)
    }}

    func update(state: GameSessionState) {{
        if SystemFlags.hasRacing {{
            updateRacing(state: state)
            return
        }}
        if SystemFlags.hasWeapon || SystemFlags.hasEnemies || SystemFlags.hasHealth || SystemFlags.hasCover {{
            updateShooter(state: state)
            return
        }}
        cameraRigEntity?.transform = CameraRig.transform
        anchor.position.z = 0
        anchor.scale = state.isFailureProofVisible ? [1.05, 1.05, 1.05] : [1, 1, 1]
    }}

    func updateRacing(state: GameSessionState) {{
        vehicleEntity?.position.x = xPosition(forRaceLane: state.vehicleLane)
        vehicleEntity?.position.z = -0.80
        vehicleEntity?.scale = state.isRaceCollision ? [0.90, 0.90, 0.90] : [1, 1, 1]

        trackEntity?.position.z = -Float(state.raceDistance % 6) * 0.04

        obstacleEntity?.isEnabled = SystemFlags.hasCollision
        obstacleEntity?.position.x = xPosition(forRaceLane: state.obstacleLane)
        obstacleEntity?.position.z = -1.10 - Float(state.raceDistance % 4) * 0.16

        checkpointEntity?.isEnabled = SystemFlags.hasLapTimer
        checkpointEntity?.position = [0, 0.18, -1.55 - Float(state.checkpointIndex) * 0.12]

        var cameraTransform = CameraRig.transform
        cameraTransform.translation.z -= Float(state.raceDistance) * 0.03
        cameraRigEntity?.transform = cameraTransform

        anchor.position.z = 0
        anchor.scale = state.isFailureProofVisible ? [1.05, 1.05, 1.05] : [1, 1, 1]
    }}

    private func xPosition(forRaceLane lane: Int) -> Float {{
        Float(GameRules.clampedRaceLane(lane) - 1) * 0.45
    }}

    func updateShooter(state: GameSessionState) {{
        playerEntity?.position = [0, state.isTakingCover ? -0.06 : 0, -0.72]
        playerEntity?.scale = state.isShooterDefeated ? [0.85, 0.85, 0.85] : [1, 1, 1]

        weaponEntity?.isEnabled = SystemFlags.hasWeapon
        weaponEntity?.position = [xPosition(forShooterLane: state.aimLane) * 0.35, 0.12, -0.66]
        weaponEntity?.scale = state.lastShotHit ? [1.16, 1.16, 1.16] : [1, 1, 1]

        enemyEntity?.isEnabled = SystemFlags.hasEnemies && state.enemiesRemaining > 0
        enemyEntity?.position.x = xPosition(forShooterLane: state.enemyLane)
        enemyEntity?.position.z = -1.15 - Float(state.shotsFired % 3) * 0.12
        enemyEntity?.scale = state.lastShotHit ? [0.88, 0.88, 0.88] : [1, 1, 1]

        coverEntity?.isEnabled = SystemFlags.hasCover
        coverEntity?.position = [state.isTakingCover ? 0 : -0.55, -0.05, -0.72]
        coverEntity?.scale = state.isTakingCover ? [1.12, 1.12, 1.12] : [1, 1, 1]

        cameraRigEntity?.transform = CameraRig.transform
        anchor.position.z = 0
        anchor.scale = state.isFailureProofVisible ? [1.05, 1.05, 1.05] : [1, 1, 1]
    }}

    private func xPosition(forShooterLane lane: Int) -> Float {{
        Float(GameRules.clampedShooterLane(lane) - 1) * 0.45
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


def _swift_string_literal(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=True)
