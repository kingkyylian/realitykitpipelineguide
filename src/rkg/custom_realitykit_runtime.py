from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from rkg.plan import runtime_entities_for

SceneBinding = tuple[str, frozenset[str]]


@dataclass(frozen=True)
class CustomRealityKitRuntimeAdapter:
    id: str
    systems: tuple[str, ...]
    state_fields: tuple[str, ...]
    rule_members: tuple[str, ...]
    content_section: str
    scene_properties: tuple[str, ...]
    scene_bindings: tuple[SceneBinding, ...]
    system_flags_condition: str
    scene_update_call: str
    start_session_call: str
    advance_session_call: str
    screenshot_session_call: str
    scene_methods: str


_CORE_STATE_FIELDS = (
    "var primaryActions: Int = 0",
    "var isFailureProofVisible: Bool = false",
)


def custom_realitykit_runtime_adapters() -> tuple[CustomRealityKitRuntimeAdapter, ...]:
    return (
        _racing_runtime_adapter(),
        _projectile_runtime_adapter(),
        _shooter_runtime_adapter(),
        _collector_runtime_adapter(),
    )


def custom_realitykit_adapter_capabilities() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for adapter in custom_realitykit_runtime_adapters():
        records.append(
            {
                "id": adapter.id,
                "systems": list(adapter.systems),
                "state_fields": [_swift_member_name(field) for field in adapter.state_fields],
                "rule_members": [_swift_member_name(member) for member in adapter.rule_members],
                "scene_properties": list(adapter.scene_properties),
                "scene_roles": sorted({role for _, roles in adapter.scene_bindings for role in roles}),
            }
        )
    return records


def custom_realitykit_state_fields() -> list[str]:
    fields = list(_CORE_STATE_FIELDS)
    for adapter in custom_realitykit_runtime_adapters():
        fields.extend(adapter.state_fields)
    return fields


def custom_realitykit_rule_members() -> list[str]:
    adapters = custom_realitykit_runtime_adapters()
    members: list[str] = []
    for adapter in adapters:
        members.extend(adapter.rule_members)
    members.extend(_custom_realitykit_core_rule_members(adapters))
    return members


def custom_realitykit_adapter_content_sections() -> str:
    return "\n".join(adapter.content_section for adapter in custom_realitykit_runtime_adapters())


def custom_realitykit_game_scene_controller_swift(spec: Mapping[str, Any]) -> str:
    adapters = custom_realitykit_runtime_adapters()
    entity_lines = _scene_entity_setup_lines(
        spec,
        tuple(binding for adapter in adapters for binding in adapter.scene_bindings),
    )
    property_lines = "\n".join(
        f"    private var {property_name}: Entity?"
        for property_name in _ordered_unique(property_name for adapter in adapters for property_name in adapter.scene_properties)
    )
    update_dispatch = "\n".join(
        f"""        if {adapter.system_flags_condition} {{
            {adapter.scene_update_call}
            return
        }}"""
        for adapter in adapters
    )
    adapter_methods = "\n\n".join(adapter.scene_methods for adapter in adapters)
    return f"""import RealityKit

final class GameSceneController {{
    private let anchor = AnchorEntity(world: .zero)
{property_lines}
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
{update_dispatch}
        cameraRigEntity?.transform = CameraRig.transform
        anchor.position.z = 0
        anchor.scale = state.isFailureProofVisible ? [1.05, 1.05, 1.05] : [1, 1, 1]
    }}

{adapter_methods}
}}
"""


def _racing_runtime_adapter() -> CustomRealityKitRuntimeAdapter:
    return CustomRealityKitRuntimeAdapter(
        id="racing",
        systems=("racing", "lap_timer", "collision"),
        state_fields=(
            "var raceDistance: Int = 0",
            "var currentLap: Int = 0",
            "var checkpointIndex: Int = 0",
            "var vehicleLane: Int = 1",
            "var obstacleLane: Int = 0",
            "var isRaceCollision: Bool = false",
        ),
        rule_members=(
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
        ),
        content_section="""                if SystemFlags.hasRacing {
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
""",
        scene_properties=("vehicleEntity", "trackEntity", "obstacleEntity", "checkpointEntity"),
        scene_bindings=(
            ("vehicleEntity", frozenset({"player", "vehicle"})),
            ("trackEntity", frozenset({"arena", "environment", "track"})),
            ("obstacleEntity", frozenset({"obstacle", "hazard"})),
            ("checkpointEntity", frozenset({"ui_prop", "checkpoint", "target"})),
        ),
        system_flags_condition="SystemFlags.hasRacing",
        scene_update_call="updateRacing(state: state)",
        start_session_call="startRacingSession(sessionSeconds: sessionSeconds)",
        advance_session_call="advanceRacingFrame(state)",
        screenshot_session_call="racingScreenshotSession(for: screenshotState, fallback: fallback)",
        scene_methods="""    func updateRacing(state: GameSessionState) {
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
    }

    private func xPosition(forRaceLane lane: Int) -> Float {
        Float(GameRules.clampedRaceLane(lane) - 1) * 0.45
    }""",
    )


def _projectile_runtime_adapter() -> CustomRealityKitRuntimeAdapter:
    return CustomRealityKitRuntimeAdapter(
        id="projectile",
        systems=("projectile", "shooting", "score"),
        state_fields=(
            "var projectileShots: Int = 0",
            "var projectileHits: Int = 0",
            "var projectileCharge: Int = 1",
            "var projectileLane: Int = 1",
            "var targetLane: Int = 1",
            "var projectileTravel: Int = 0",
            "var projectileInFlight: Bool = false",
            "var lastProjectileHit: Bool = false",
        ),
        rule_members=(
            "static let projectileLaneCount = 3",
            "static let maxProjectileCharge = 3",
            "static let projectileTravelFrames = 3",
            "static let projectileHitTarget = 3",
            "static let projectileShotLimit = 5",
            """static func clampedProjectileLane(_ lane: Int) -> Int {
    min(max(lane, 0), projectileLaneCount - 1)
}""",
            """static func projectileLaneAfterAim(currentLane: Int, direction: Int) -> Int {
    clampedProjectileLane(currentLane + direction)
}""",
            """static func clampedProjectileCharge(_ charge: Int) -> Int {
    min(max(charge, 1), maxProjectileCharge)
}""",
            """static func nextProjectileTargetLane(after shots: Int) -> Int {
    (shots + 1) % projectileLaneCount
}""",
            """static func startProjectileSession(sessionSeconds: Int) -> GameSessionState {
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.projectileShots = 0
    state.projectileHits = 0
    state.projectileCharge = 1
    state.projectileLane = 1
    state.targetLane = 1
    state.projectileTravel = 0
    state.projectileInFlight = false
    state.lastProjectileHit = false
    state.lastEvent = "projectile range ready"
    return state
}""",
            """static func chargeProjectile(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return startProjectileSession(sessionSeconds: next.sessionSeconds)
    }
    next.projectileCharge = clampedProjectileCharge(next.projectileCharge + 1)
    next.projectileInFlight = false
    next.projectileTravel = 0
    next.lastEvent = "charge \\(next.projectileCharge)"
    return next
}""",
            """static func launchProjectile(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return startProjectileSession(sessionSeconds: next.sessionSeconds)
    }
    next.primaryActions += 1
    next.elapsedSeconds += 1
    next.projectileShots += 1
    next.projectileTravel = projectileTravelFrames
    next.projectileInFlight = true
    let hit = SystemFlags.hasProjectile && next.projectileLane == next.targetLane
    next.lastProjectileHit = hit
    if hit {
        next.projectileHits += 1
        next.score += scoreForHit(isPerfect: next.projectileCharge >= maxProjectileCharge)
        next.lastEvent = "projectile hit"
    } else {
        next.lastEvent = "projectile miss"
    }
    next.targetLane = nextProjectileTargetLane(after: next.projectileShots)
    next.projectileCharge = 1
    if next.projectileHits >= projectileHitTarget {
        return SessionControl.markResult(next, event: "target clear")
    }
    if next.projectileShots >= projectileShotLimit {
        next.isFailureProofVisible = true
        return SessionControl.markResult(next, event: "shots spent")
    }
    return next
}""",
            """static func advanceProjectileFrame(_ state: GameSessionState) -> GameSessionState {
    launchProjectile(state)
}""",
            """static func projectileScreenshotSession(for screenshotState: ScreenshotState?, fallback: GameSessionState) -> GameSessionState {
    switch screenshotState?.rawValue {
    case "gameplay_start":
        return startProjectileSession(sessionSeconds: fallback.sessionSeconds)
    case "mid_action":
        var state = startProjectileSession(sessionSeconds: fallback.sessionSeconds)
        state = chargeProjectile(state)
        state = launchProjectile(state)
        return state
    case "fail_or_hit":
        var state = startProjectileSession(sessionSeconds: fallback.sessionSeconds)
        state.projectileLane = state.targetLane
        state = chargeProjectile(state)
        state = chargeProjectile(state)
        state = launchProjectile(state)
        return state
    case "results":
        var state = startProjectileSession(sessionSeconds: fallback.sessionSeconds)
        while state.projectileHits < projectileHitTarget {
            state.projectileLane = state.targetLane
            state = chargeProjectile(state)
            state = chargeProjectile(state)
            state = launchProjectile(state)
        }
        return state
    default:
        return fallback
    }
}""",
        ),
        content_section="""                if SystemFlags.hasProjectile || SystemFlags.hasShooting {
                    HStack(spacing: 12) {
                        Text("Shots \\(state.projectileShots)/\\(GameRules.projectileShotLimit)")
                            .font(.caption.monospacedDigit())
                        Text("Hits \\(state.projectileHits)")
                            .font(.caption.monospacedDigit())
                        Text("Charge \\(state.projectileCharge)")
                            .font(.caption.monospacedDigit())
                        Text("Aim \\(state.projectileLane + 1)")
                            .font(.caption.monospacedDigit())
                        Spacer()
                    }

                    HStack {
                        Button("Aim Left") {
                            state.projectileLane = GameRules.projectileLaneAfterAim(currentLane: state.projectileLane, direction: -1)
                        }
                        .buttonStyle(.bordered)
                        Button("Aim Right") {
                            state.projectileLane = GameRules.projectileLaneAfterAim(currentLane: state.projectileLane, direction: 1)
                        }
                        .buttonStyle(.bordered)
                        Button("Charge") {
                            state = GameRules.chargeProjectile(state)
                        }
                        .buttonStyle(.bordered)
                        Button("Launch") {
                            state = GameRules.launchProjectile(state)
                        }
                        .buttonStyle(.borderedProminent)
                        Spacer()
                    }
                }
""",
        scene_properties=("playerEntity", "arenaEntity", "weaponEntity", "projectileEntity", "targetEntity"),
        scene_bindings=(
            ("playerEntity", frozenset({"player"})),
            ("arenaEntity", frozenset({"arena", "environment"})),
            ("weaponEntity", frozenset({"weapon"})),
            ("projectileEntity", frozenset({"projectile"})),
            ("targetEntity", frozenset({"target"})),
        ),
        system_flags_condition="SystemFlags.hasProjectile || SystemFlags.hasShooting",
        scene_update_call="updateProjectile(state: state)",
        start_session_call="startProjectileSession(sessionSeconds: sessionSeconds)",
        advance_session_call="advanceProjectileFrame(state)",
        screenshot_session_call="projectileScreenshotSession(for: screenshotState, fallback: fallback)",
        scene_methods="""    func updateProjectile(state: GameSessionState) {
        playerEntity?.position = [0, 0, -0.78]
        playerEntity?.scale = state.isFailureProofVisible ? [0.92, 0.92, 0.92] : [1, 1, 1]

        arenaEntity?.position.z = -Float(state.projectileShots % 4) * 0.03

        weaponEntity?.isEnabled = SystemFlags.hasShooting
        weaponEntity?.position = [xPosition(forProjectileLane: state.projectileLane) * 0.35, 0.12, -0.70]
        weaponEntity?.scale = [1, 1, 1 + Float(state.projectileCharge - 1) * 0.10]

        projectileEntity?.isEnabled = SystemFlags.hasProjectile
        projectileEntity?.position = projectilePosition(state: state)
        projectileEntity?.scale = state.lastProjectileHit ? [1.22, 1.22, 1.22] : [1, 1, 1]

        targetEntity?.isEnabled = SystemFlags.hasProjectile || SystemFlags.hasShooting
        targetEntity?.position.x = xPosition(forProjectileLane: state.targetLane)
        targetEntity?.position.y = state.lastProjectileHit ? 0.16 : 0.08
        targetEntity?.position.z = -1.38
        targetEntity?.scale = state.lastProjectileHit ? [1.16, 1.16, 1.16] : [1, 1, 1]

        cameraRigEntity?.transform = CameraRig.transform
        anchor.position.z = 0
        anchor.scale = state.isFailureProofVisible ? [1.05, 1.05, 1.05] : [1, 1, 1]
    }

    private func projectilePosition(state: GameSessionState) -> SIMD3<Float> {
        let x = xPosition(forProjectileLane: state.projectileLane)
        if state.projectileInFlight {
            let travel = Float(min(state.projectileTravel, GameRules.projectileTravelFrames))
            return [x, 0.18 + Float(state.projectileCharge) * 0.03, -0.70 - travel * 0.22]
        }
        return [x, 0.16, -0.70]
    }

    private func xPosition(forProjectileLane lane: Int) -> Float {
        Float(GameRules.clampedProjectileLane(lane) - 1) * 0.45
    }""",
    )


def _shooter_runtime_adapter() -> CustomRealityKitRuntimeAdapter:
    return CustomRealityKitRuntimeAdapter(
        id="shooter",
        systems=("weapon", "hitscan", "enemies", "health", "cover"),
        state_fields=(
            "var shooterHealth: Int = GameRules.shooterMaxHealth",
            "var enemiesRemaining: Int = GameRules.startingEnemyCount",
            "var shotsFired: Int = 0",
            "var aimLane: Int = 1",
            "var enemyLane: Int = 1",
            "var isTakingCover: Bool = false",
            "var isShooterDefeated: Bool = false",
            "var lastShotHit: Bool = false",
        ),
        rule_members=(
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
        ),
        content_section="""                if SystemFlags.hasWeapon || SystemFlags.hasEnemies || SystemFlags.hasHealth || SystemFlags.hasCover {
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
""",
        scene_properties=("playerEntity", "weaponEntity", "enemyEntity", "coverEntity"),
        scene_bindings=(
            ("playerEntity", frozenset({"player"})),
            ("weaponEntity", frozenset({"weapon"})),
            ("enemyEntity", frozenset({"enemy"})),
            ("coverEntity", frozenset({"cover"})),
        ),
        system_flags_condition="SystemFlags.hasWeapon || SystemFlags.hasEnemies || SystemFlags.hasHealth || SystemFlags.hasCover",
        scene_update_call="updateShooter(state: state)",
        start_session_call="startShooterSession(sessionSeconds: sessionSeconds)",
        advance_session_call="advanceShooterFrame(state)",
        screenshot_session_call="shooterScreenshotSession(for: screenshotState, fallback: fallback)",
        scene_methods="""    func updateShooter(state: GameSessionState) {
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
    }

    private func xPosition(forShooterLane lane: Int) -> Float {
        Float(GameRules.clampedShooterLane(lane) - 1) * 0.45
    }""",
    )


def _collector_runtime_adapter() -> CustomRealityKitRuntimeAdapter:
    return CustomRealityKitRuntimeAdapter(
        id="collector",
        systems=("collect", "score", "timer"),
        state_fields=(
            "var collectedItems: Int = 0",
            "var collectiblesRemaining: Int = GameRules.startingCollectibleCount",
            "var collectionTimer: Int = GameRules.collectionTimerSeconds",
            "var comboStreak: Int = 0",
            "var collectorLane: Int = 1",
            "var pickupLane: Int = 1",
            "var isCollectionTimedOut: Bool = false",
        ),
        rule_members=(
            "static let collectorLaneCount = 3",
            "static let startingCollectibleCount = 5",
            "static let collectionTimerSeconds = 20",
            """static func clampedCollectorLane(_ lane: Int) -> Int {
    min(max(lane, 0), collectorLaneCount - 1)
}""",
            """static func collectorLaneAfterMove(currentLane: Int, direction: Int) -> Int {
    clampedCollectorLane(currentLane + direction)
}""",
            """static func nextPickupLane(after collectedItems: Int) -> Int {
    (collectedItems + 1) % collectorLaneCount
}""",
            """static func scoreForCollection(collectedItems: Int, comboStreak: Int) -> Int {
    collectedItems * hitScore + comboStreak * 5
}""",
            """static func startCollectorSession(sessionSeconds: Int) -> GameSessionState {
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.collectedItems = 0
    state.collectiblesRemaining = startingCollectibleCount
    state.collectionTimer = min(sessionSeconds, collectionTimerSeconds)
    state.comboStreak = 0
    state.collectorLane = 1
    state.pickupLane = 1
    state.lastEvent = "collection started"
    return state
}""",
            """static func collectPickup(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return startCollectorSession(sessionSeconds: next.sessionSeconds)
    }
    next.primaryActions += 1
    next.elapsedSeconds += 1
    if SystemFlags.hasTimer {
        next.collectionTimer = max(0, next.collectionTimer - 1)
    }
    let didCollect = next.collectiblesRemaining > 0 && next.collectorLane == next.pickupLane
    if didCollect {
        next.collectedItems += 1
        next.collectiblesRemaining = max(0, next.collectiblesRemaining - 1)
        next.comboStreak += 1
        next.score = scoreForCollection(collectedItems: next.collectedItems, comboStreak: next.comboStreak)
        next.pickupLane = nextPickupLane(after: next.collectedItems)
        next.lastEvent = "pickup collected"
    } else {
        next.comboStreak = 0
        next.lastEvent = "pickup missed"
    }
    if next.collectiblesRemaining <= 0 {
        return SessionControl.markResult(next, event: "collection complete")
    }
    if SystemFlags.hasTimer && next.collectionTimer <= 0 {
        next.isCollectionTimedOut = true
        next.isFailureProofVisible = true
        return SessionControl.markResult(next, event: "timer expired")
    }
    return next
}""",
            """static func advanceCollectorFrame(_ state: GameSessionState) -> GameSessionState {
    collectPickup(state)
}""",
            """static func collectorScreenshotSession(for screenshotState: ScreenshotState?, fallback: GameSessionState) -> GameSessionState {
    switch screenshotState?.rawValue {
    case "gameplay_start":
        return startCollectorSession(sessionSeconds: fallback.sessionSeconds)
    case "mid_action":
        var state = startCollectorSession(sessionSeconds: fallback.sessionSeconds)
        state = collectPickup(state)
        return state
    case "fail_or_hit":
        var state = startCollectorSession(sessionSeconds: fallback.sessionSeconds)
        state.collectionTimer = 1
        state.collectorLane = 0
        state.pickupLane = 2
        state = collectPickup(state)
        return state
    case "results":
        var state = startCollectorSession(sessionSeconds: fallback.sessionSeconds)
        for _ in 0..<startingCollectibleCount {
            state.collectorLane = state.pickupLane
            state = collectPickup(state)
        }
        return state
    default:
        return fallback
    }
}""",
        ),
        content_section="""                if SystemFlags.hasCollect || SystemFlags.hasScore || SystemFlags.hasTimer {
                    HStack(spacing: 12) {
                        Text("Items \\(state.collectedItems)/\\(GameRules.startingCollectibleCount)")
                            .font(.caption.monospacedDigit())
                        Text("Timer \\(state.collectionTimer)")
                            .font(.caption.monospacedDigit())
                        Text("Combo \\(state.comboStreak)")
                            .font(.caption.monospacedDigit())
                        Text("Lane \\(state.collectorLane + 1)")
                            .font(.caption.monospacedDigit())
                        Spacer()
                    }

                    HStack {
                        Button("Move Left") {
                            state.collectorLane = GameRules.collectorLaneAfterMove(currentLane: state.collectorLane, direction: -1)
                        }
                        .buttonStyle(.bordered)
                        Button("Move Right") {
                            state.collectorLane = GameRules.collectorLaneAfterMove(currentLane: state.collectorLane, direction: 1)
                        }
                        .buttonStyle(.bordered)
                        Button("Collect") {
                            state = GameRules.collectPickup(state)
                        }
                        .buttonStyle(.bordered)
                        Spacer()
                    }
                }
""",
        scene_properties=("playerEntity", "arenaEntity", "pickupEntity", "timerEntity"),
        scene_bindings=(
            ("playerEntity", frozenset({"player"})),
            ("arenaEntity", frozenset({"arena", "environment"})),
            ("pickupEntity", frozenset({"pickup"})),
            ("timerEntity", frozenset({"ui_prop", "timer"})),
        ),
        system_flags_condition="SystemFlags.hasCollect || SystemFlags.hasScore || SystemFlags.hasTimer",
        scene_update_call="updateCollector(state: state)",
        start_session_call="startCollectorSession(sessionSeconds: sessionSeconds)",
        advance_session_call="advanceCollectorFrame(state)",
        screenshot_session_call="collectorScreenshotSession(for: screenshotState, fallback: fallback)",
        scene_methods="""    func updateCollector(state: GameSessionState) {
        playerEntity?.position.x = xPosition(forCollectorLane: state.collectorLane)
        playerEntity?.position.z = -0.76
        playerEntity?.scale = state.isCollectionTimedOut ? [0.88, 0.88, 0.88] : [1, 1, 1]

        arenaEntity?.position.z = -Float(state.collectedItems % 4) * 0.04

        pickupEntity?.isEnabled = SystemFlags.hasCollect && state.collectiblesRemaining > 0
        pickupEntity?.position.x = xPosition(forCollectorLane: state.pickupLane)
        pickupEntity?.position.y = 0.12 + Float(state.comboStreak % 2) * 0.04
        pickupEntity?.position.z = -1.04
        pickupEntity?.scale = state.comboStreak > 0 ? [1.18, 1.18, 1.18] : [1, 1, 1]

        timerEntity?.isEnabled = SystemFlags.hasTimer
        timerEntity?.position = [0, 0.22, -1.38]
        timerEntity?.scale = state.collectionTimer <= 5 ? [1.18, 1.18, 1.18] : [1, 1, 1]

        cameraRigEntity?.transform = CameraRig.transform
        anchor.position.z = 0
        anchor.scale = state.isFailureProofVisible ? [1.05, 1.05, 1.05] : [1, 1, 1]
    }

    private func xPosition(forCollectorLane lane: Int) -> Float {
        Float(GameRules.clampedCollectorLane(lane) - 1) * 0.45
    }""",
    )


def _custom_realitykit_core_rule_members(adapters: Sequence[CustomRealityKitRuntimeAdapter]) -> tuple[str, ...]:
    return (
        f"""static func startCustomRealityKitSession(sessionSeconds: Int) -> GameSessionState {{
{_rule_dispatch_lines(adapters, "start_session_call")}
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.lastEvent = "started"
    return state
}}""",
        f"""static func advanceCustomRealityKitSession(_ state: GameSessionState) -> GameSessionState {{
{_rule_dispatch_lines(adapters, "advance_session_call")}
    var next = state
    if next.phase != .playing {{
        return startCustomRealityKitSession(sessionSeconds: next.sessionSeconds)
    }}
    next.primaryActions += 1
    next.elapsedSeconds += 1
    next.score += scoreForHit(isPerfect: SystemFlags.has("lap_timer"))
    next.lastEvent = InputController.primaryActionLabel
    if SystemFlags.hasCollision && next.primaryActions >= 2 {{
        next.isFailureProofVisible = true
        next = SessionControl.markResult(next, event: "collision proof")
    }}
    return next
}}""",
        f"""static func customRealityKitScreenshotSession(for screenshotState: ScreenshotState?, fallback: GameSessionState) -> GameSessionState {{
{_rule_dispatch_lines(adapters, "screenshot_session_call")}
    switch screenshotState?.rawValue {{
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
    }}
}}""",
    )


def _rule_dispatch_lines(adapters: Sequence[CustomRealityKitRuntimeAdapter], call_attribute: str) -> str:
    return "\n".join(
        f"""    if {adapter.system_flags_condition} {{
        return {getattr(adapter, call_attribute)}
    }}"""
        for adapter in adapters
    )


def _runtime_entity_swift(entity: Mapping[str, str]) -> str:
    variable = entity["variable"]
    asset_id = _swift_string_literal(entity["asset_id"])
    role = _swift_string_literal(entity["role"])
    fallback = _swift_string_literal(entity["fallback"])
    position = entity["position"]
    return f"""        let {variable} = AssetLoader.loadPrimaryEntity(assetId: {asset_id}, role: {role}, fallback: {fallback})
        {variable}.position = {position}
        anchor.addChild({variable})"""


def _scene_entity_setup_lines(spec: Mapping[str, Any], bindings: Sequence[SceneBinding]) -> str:
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


def _ordered_unique(values: Iterable[str]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        result.append(value)
        seen.add(value)
    return tuple(result)


def _swift_member_name(declaration: str) -> str:
    first_line = declaration.strip().splitlines()[0]
    for prefix in ("var ", "static let ", "static var ", "static func "):
        if first_line.startswith(prefix):
            remainder = first_line[len(prefix) :]
            return remainder.split("(", 1)[0].split(":", 1)[0].split("=", 1)[0].strip()
    return first_line


def _swift_string_literal(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=True)
