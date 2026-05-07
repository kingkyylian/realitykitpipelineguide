from __future__ import annotations


def archetype_state_fields(archetype_id: str) -> list[str]:
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
    return []


def archetype_rule_members(archetype_id: str) -> list[str]:
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
        next.phase = .result
        next.isDefeated = true
        next.lastEvent = "hit obstacle"
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
        next.phase = .result
        next.lastEvent = "landed"
    } else if next.attemptsRemaining == 0 {
        next.phase = .result
        next.lastEvent = "attempts spent"
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
        next.phase = .result
        next.isDefeated = true
        next.lastEvent = "base breached"
    } else {
        next.lastEvent = "took damage"
    }
    return next
}""",
        ]
    return []


def indent_swift_block(text: str, *, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line else line for line in text.splitlines())
