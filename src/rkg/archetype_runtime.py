from __future__ import annotations


def archetype_state_fields(archetype_id: str) -> list[str]:
    if archetype_id == "target_shooter":
        return [
            "var targetsHit: Int = 0",
            "var perfectHits: Int = 0",
        ]
    if archetype_id == "lane_dodger":
        return [
            "var currentLane: Int = 1",
            "var obstacleLane: Int = 0",
            "var isDefeated: Bool = false",
            "var nearMisses: Int = 0",
            "var distance: Int = 0",
        ]
    if archetype_id == "toss_physics":
        return [
            "var attemptsRemaining: Int = GameRules.maxAttempts",
            "var lastThrowPower: Double = 0",
            "var landedInZone: Bool = false",
        ]
    if archetype_id == "stack_puzzle":
        return [
            "var piecesPlaced: Int = 0",
            "var stablePieces: Int = 0",
            "var collapsed: Bool = false",
        ]
    if archetype_id == "wave_defense_lite":
        return [
            "var health: Int = GameRules.startingHealth",
            "var wave: Int = 1",
            "var threatsRemaining: Int = 0",
            "var clearedThreats: Int = 0",
            "var isDefeated: Bool = false",
        ]
    if archetype_id == "fighter_2_5d":
        return [
            "var playerHealth: Int = GameRules.fighterMaxHealth",
            "var opponentHealth: Int = GameRules.fighterMaxHealth",
            "var comboCount: Int = 0",
            "var guardMeter: Int = GameRules.startingGuardMeter",
            "var isDodging: Bool = false",
            "var isKnockout: Bool = false",
        ]
    if archetype_id == "custom_realitykit":
        return [
            "var primaryActions: Int = 0",
            "var isFailureProofVisible: Bool = false",
        ]
    return []


def archetype_rule_members(archetype_id: str) -> list[str]:
    if archetype_id == "target_shooter":
        return [
            """static func startTargetShooterSession(sessionSeconds: Int) -> GameSessionState {
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.lastEvent = "started"
    return state
}""",
            """static func recordTargetHit(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return startTargetShooterSession(sessionSeconds: next.sessionSeconds)
    }
    next.targetsHit += 1
    let perfect = next.targetsHit % 3 == 0
    if perfect {
        next.perfectHits += 1
    }
    next.score += scoreForHit(isPerfect: perfect)
    next.lastEvent = perfect ? "perfect hit" : "hit"
    return next
}""",
            """static func finishTargetShooterSession(_ state: GameSessionState) -> GameSessionState {
    let next = state
    if next.phase == .result {
        return next
    }
    return SessionControl.markResult(next, event: "session complete")
}""",
        ]
    if archetype_id == "lane_dodger":
        return [
            "static let laneCount = 3",
            "static let nearMissBonus = 5",
            """static func laneAfterMove(currentLane: Int, direction: Int) -> Int {
    clampedLane(currentLane + direction)
}""",
            """static func clampedLane(_ lane: Int) -> Int {
    min(max(lane, 0), laneCount - 1)
}""",
            """static func isCollision(playerLane: Int, obstacleLane: Int) -> Bool {
    playerLane == obstacleLane
}""",
            """static func isNearMiss(playerLane: Int, obstacleLane: Int) -> Bool {
    abs(playerLane - obstacleLane) == 1
}""",
            """static func nextObstacleLane(after distance: Int) -> Int {
    (distance + 1) % laneCount
}""",
            """static func scoreForDistance(_ distance: Int, nearMisses: Int) -> Int {
    distance + nearMisses * nearMissBonus
}""",
            """static func startLaneDodgerSession(sessionSeconds: Int) -> GameSessionState {
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.obstacleLane = nextObstacleLane(after: 0)
    state.lastEvent = "started"
    return state
}""",
            """static func advanceLaneDodgerFrame(_ state: GameSessionState) -> GameSessionState {
    var next = state
    next.distance += 1
    next.obstacleLane = nextObstacleLane(after: next.distance)
    if isCollision(playerLane: next.currentLane, obstacleLane: next.obstacleLane) {
        next.isDefeated = true
        next = SessionControl.markResult(next, event: "hit obstacle")
    } else if isNearMiss(playerLane: next.currentLane, obstacleLane: next.obstacleLane) {
        next.nearMisses += 1
        next.lastEvent = "near miss"
    } else {
        next.lastEvent = "clear"
    }
    next.score = scoreForDistance(next.distance, nearMisses: next.nearMisses)
    return next
}""",
        ]
    if archetype_id == "toss_physics":
        return [
            "static let maxAttempts = 3",
            """static func clampedThrowPower(_ power: Double) -> Double {
    min(max(power, 0), 1)
}""",
            """static func consumeAttempt(_ attemptsRemaining: Int) -> Int {
    max(0, attemptsRemaining - 1)
}""",
            """static func scoreForLanding(inZone: Bool, power: Double) -> Int {
    inZone ? Int(clampedThrowPower(power) * 100) : 0
}""",
            """static func landedInScoringZone(power: Double) -> Bool {
    power >= 0.45 && power <= 0.75
}""",
            """static func startTossSession(sessionSeconds: Int) -> GameSessionState {
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.attemptsRemaining = maxAttempts
    state.lastEvent = "aiming"
    return state
}""",
            """static func resolveToss(_ state: GameSessionState, power: Double) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return startTossSession(sessionSeconds: next.sessionSeconds)
    }
    let clampedPower = clampedThrowPower(power)
    let landed = landedInScoringZone(power: clampedPower)
    next.lastThrowPower = clampedPower
    next.landedInZone = landed
    next.attemptsRemaining = consumeAttempt(next.attemptsRemaining)
    next.score += scoreForLanding(inZone: landed, power: clampedPower)
    if landed {
        next = SessionControl.markResult(next, event: "landed")
    } else if next.attemptsRemaining == 0 {
        next = SessionControl.markResult(next, event: "attempts spent")
    } else {
        next.lastEvent = "missed"
    }
    return next
}""",
        ]
    if archetype_id == "stack_puzzle":
        return [
            "static let maxPieces = 8",
            """static func nextPieceIndex(after piecesPlaced: Int) -> Int {
    min(piecesPlaced + 1, maxPieces)
}""",
            """static func isStable(stablePieces: Int, piecesPlaced: Int) -> Bool {
    stablePieces >= piecesPlaced
}""",
            """static func scoreForStack(piecesPlaced: Int, stablePieces: Int) -> Int {
    piecesPlaced * 10 + stablePieces * 5
}""",
            """static func startStackPuzzleSession(sessionSeconds: Int) -> GameSessionState {
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.lastEvent = "started"
    return state
}""",
            """static func placeStackPiece(_ state: GameSessionState, stable: Bool) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return startStackPuzzleSession(sessionSeconds: next.sessionSeconds)
    }
    if next.piecesPlaced >= maxPieces {
        next = SessionControl.markResult(next, event: "tower complete")
        return next
    }
    next.piecesPlaced = nextPieceIndex(after: next.piecesPlaced)
    if stable {
        next.stablePieces = min(next.stablePieces + 1, next.piecesPlaced)
        next.lastEvent = "stable piece"
    } else {
        next.collapsed = true
        next = SessionControl.markResult(next, event: "collapsed")
    }
    next.score = scoreForStack(piecesPlaced: next.piecesPlaced, stablePieces: next.stablePieces)
    if next.piecesPlaced >= maxPieces && !next.collapsed {
        next = SessionControl.markResult(next, event: "tower complete")
    }
    return next
}""",
            """static func collapseStack(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return next
    }
    next.collapsed = true
    next.score = scoreForStack(piecesPlaced: next.piecesPlaced, stablePieces: next.stablePieces)
    next = SessionControl.markResult(next, event: "collapsed")
    return next
}""",
        ]
    if archetype_id == "wave_defense_lite":
        return [
            "static let startingHealth = 3",
            """static func threatsForWave(_ wave: Int) -> Int {
    max(1, wave + 1)
}""",
            """static func healthAfterDamage(_ health: Int, damage: Int = 1) -> Int {
    max(0, health - damage)
}""",
            """static func isDefeated(health: Int) -> Bool {
    health <= 0
}""",
            """static func nextWave(after wave: Int) -> Int {
    wave + 1
}""",
            """static func startWaveDefenseSession(sessionSeconds: Int) -> GameSessionState {
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.health = startingHealth
    state.wave = 1
    state.threatsRemaining = threatsForWave(state.wave)
    state.lastEvent = "wave started"
    return state
}""",
            """static func clearThreat(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return startWaveDefenseSession(sessionSeconds: next.sessionSeconds)
    }
    next.threatsRemaining = max(0, next.threatsRemaining - 1)
    next.clearedThreats += 1
    if next.threatsRemaining == 0 {
        next.wave = nextWave(after: next.wave)
        next.threatsRemaining = threatsForWave(next.wave)
        next.lastEvent = "wave cleared"
    } else {
        next.lastEvent = "threat cleared"
    }
    next.score = next.clearedThreats * hitScore + (next.wave - 1) * perfectScore
    return next
}""",
            """static func applyThreatDamage(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return next
    }
    next.health = healthAfterDamage(next.health)
    if isDefeated(health: next.health) {
        next.isDefeated = true
        next = SessionControl.markResult(next, event: "base breached")
    } else {
        next.lastEvent = "took damage"
    }
    return next
}""",
        ]
    if archetype_id == "fighter_2_5d":
        return [
            "static let fighterMaxHealth = 5",
            "static let startingGuardMeter = 1",
            "static let maxGuardMeter = 3",
            "static let comboBonus = 3",
            """static func fighterHealthAfterHit(_ health: Int) -> Int {
    max(0, health - 1)
}""",
            """static func scoreForFighterHit(comboCount: Int) -> Int {
    hitScore + comboCount * comboBonus
}""",
            """static func startFighterDuelSession(sessionSeconds: Int) -> GameSessionState {
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.playerHealth = fighterMaxHealth
    state.opponentHealth = fighterMaxHealth
    state.guardMeter = startingGuardMeter
    state.lastEvent = "round started"
    return state
}""",
            """static func recordFighterAttack(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return startFighterDuelSession(sessionSeconds: next.sessionSeconds)
    }
    next.isDodging = false
    next.comboCount += 1
    next.opponentHealth = fighterHealthAfterHit(next.opponentHealth)
    next.score += scoreForFighterHit(comboCount: next.comboCount)
    if next.opponentHealth <= 0 {
        next.isKnockout = true
        next = SessionControl.markResult(next, event: "knockout")
    } else {
        next.lastEvent = "hit landed"
    }
    return next
}""",
            """static func performPerfectDodge(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return startFighterDuelSession(sessionSeconds: next.sessionSeconds)
    }
    next.isDodging = true
    next.guardMeter = min(maxGuardMeter, next.guardMeter + 1)
    next.score += perfectScore
    next.lastEvent = "perfect dodge"
    return next
}""",
            """static func applyFighterDamage(_ state: GameSessionState) -> GameSessionState {
    var next = state
    if next.phase != .playing {
        return next
    }
    if next.isDodging {
        return performPerfectDodge(next)
    }
    next.playerHealth = fighterHealthAfterHit(next.playerHealth)
    next.comboCount = 0
    next.guardMeter = max(0, next.guardMeter - 1)
    if next.playerHealth <= 0 {
        next = SessionControl.markResult(next, event: "defeated")
    } else {
        next.lastEvent = "took hit"
    }
    return next
}""",
            """static func fighterScreenshotSession(for screenshotState: ScreenshotState?, fallback: GameSessionState) -> GameSessionState {
    switch screenshotState?.rawValue {
    case "round_start":
        return startFighterDuelSession(sessionSeconds: fallback.sessionSeconds)
    case "mid_combo":
        var state = startFighterDuelSession(sessionSeconds: fallback.sessionSeconds)
        state = recordFighterAttack(state)
        state = recordFighterAttack(state)
        return state
    case "perfect_dodge":
        let state = startFighterDuelSession(sessionSeconds: fallback.sessionSeconds)
        return performPerfectDodge(state)
    case "knockout":
        var state = startFighterDuelSession(sessionSeconds: fallback.sessionSeconds)
        while state.opponentHealth > 0 {
            state = recordFighterAttack(state)
        }
        return state
    default:
        return fallback
    }
}""",
        ]
    if archetype_id == "custom_realitykit":
        return [
            """static func startCustomRealityKitSession(sessionSeconds: Int) -> GameSessionState {
    var state = GameSessionState()
    state.phase = .playing
    state.sessionSeconds = sessionSeconds
    state.lastEvent = "started"
    return state
}""",
            """static func advanceCustomRealityKitSession(_ state: GameSessionState) -> GameSessionState {
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
            """static func customRealityKitScreenshotSession(for screenshotState: ScreenshotState?, fallback: GameSessionState) -> GameSessionState {
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
    return []


def indent_swift_block(text: str, *, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line else line for line in text.splitlines())
