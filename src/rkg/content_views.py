from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def content_view_swift(display_name: str, spec: Mapping[str, Any]) -> str:
    game = spec["game"]
    loop = spec["loop"]
    title = _swift_string_literal(display_name)
    subtitle = _swift_string_literal(f"{game['archetype']} / {game['session_seconds']}s")
    player_action = _swift_string_literal(loop["player_action"])
    if str(game["archetype"]) == "target_shooter":
        return _target_shooter_content_view_swift(title, subtitle, player_action)
    if str(game["archetype"]) == "lane_dodger":
        return _lane_dodger_content_view_swift(title, subtitle, player_action)
    if str(game["archetype"]) == "wave_defense_lite":
        return _wave_defense_content_view_swift(title, subtitle, player_action)
    if str(game["archetype"]) == "toss_physics":
        return _toss_physics_content_view_swift(title, subtitle, player_action)
    if str(game["archetype"]) == "stack_puzzle":
        return _stack_puzzle_content_view_swift(title, subtitle, player_action)
    if str(game["archetype"]) == "fighter_2_5d":
        return _fighter_content_view_swift(title, subtitle, player_action)
    if str(game["archetype"]) == "custom_realitykit":
        return _custom_realitykit_content_view_swift(title, subtitle, player_action)
    return _generic_content_view_swift(title, subtitle, player_action)


def _custom_realitykit_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var state = GameRules.customRealityKitScreenshotSession(
        for: ScreenshotState.requested,
        fallback: GameSessionState()
    )

    private var isPlaying: Bool {{
        SessionControl.isPlaying(state)
    }}

    var body: some View {{
        ZStack(alignment: .top) {{
            GameView(state: state)
                .ignoresSafeArea()

            VStack(spacing: 8) {{
                HStack {{
                    VStack(alignment: .leading, spacing: 2) {{
                        Text({title})
                            .font(.headline)
                        Text({subtitle})
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }}
                    Spacer()
                    Text("Score \\(state.score)")
                        .font(.headline.monospacedDigit())
                }}

                HStack(spacing: 12) {{
                    Text(InputController.controlSummary)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Text(SystemFlags.summary)
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                    Spacer()
                }}

                HStack {{
                    Text({player_action})
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button(isPlaying ? InputController.primaryActionLabel : InputIntent.startTitle) {{
                        advanceSkeleton()
                    }}
                    .buttonStyle(.borderedProminent)
                    Button(InputIntent.resetTitle) {{
                        state = SessionControl.reset()
                    }}
                    .buttonStyle(.bordered)
                }}

                if SystemFlags.hasRacing {{
                    HStack(spacing: 12) {{
                        Text("Lap \\(state.currentLap)")
                            .font(.caption.monospacedDigit())
                        Text("Distance \\(state.raceDistance)")
                            .font(.caption.monospacedDigit())
                        Text("Checkpoint \\(state.checkpointIndex + 1)/\\(GameRules.checkpointCount)")
                            .font(.caption.monospacedDigit())
                        Text("Lane \\(state.vehicleLane + 1)")
                            .font(.caption.monospacedDigit())
                        Spacer()
                    }}

                    HStack {{
                        Button("Left") {{
                            state.vehicleLane = GameRules.laneAfterSteer(currentLane: state.vehicleLane, direction: -1)
                        }}
                        .buttonStyle(.bordered)
                        Button("Right") {{
                            state.vehicleLane = GameRules.laneAfterSteer(currentLane: state.vehicleLane, direction: 1)
                        }}
                        .buttonStyle(.bordered)
                        Spacer()
                    }}
                }}

                if SystemFlags.hasWeapon || SystemFlags.hasEnemies || SystemFlags.hasHealth || SystemFlags.hasCover {{
                    HStack(spacing: 12) {{
                        Text("Health \\(state.shooterHealth)")
                            .font(.caption.monospacedDigit())
                        Text("Enemies \\(state.enemiesRemaining)")
                            .font(.caption.monospacedDigit())
                        Text("Shots \\(state.shotsFired)")
                            .font(.caption.monospacedDigit())
                        Text("Aim \\(state.aimLane + 1)")
                            .font(.caption.monospacedDigit())
                        Spacer()
                    }}

                    HStack {{
                        Button("Aim Left") {{
                            state.aimLane = GameRules.aimLaneAfterMove(currentLane: state.aimLane, direction: -1)
                        }}
                        .buttonStyle(.bordered)
                        Button("Aim Right") {{
                            state.aimLane = GameRules.aimLaneAfterMove(currentLane: state.aimLane, direction: 1)
                        }}
                        .buttonStyle(.bordered)
                        Button("Cover") {{
                            state = GameRules.toggleShooterCover(state)
                        }}
                        .buttonStyle(.bordered)
                        Spacer()
                    }}
                }}

                if SessionControl.isResult(state) {{
                    ResultView(state: state) {{
                        state = SessionControl.reset()
                    }}
                }}
            }}
            .padding()
            .background(.thinMaterial)
        }}
    }}

    private func advanceSkeleton() {{
        if !isPlaying {{
            state = GameRules.startCustomRealityKitSession(sessionSeconds: state.sessionSeconds)
            return
        }}
        state = GameRules.advanceCustomRealityKitSession(state)
    }}
}}
"""


def _generic_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var score = 0
    @State private var isPlaying = false

    var body: some View {{
        ZStack(alignment: .top) {{
            GameView()
                .ignoresSafeArea()

            VStack(spacing: 8) {{
                HStack {{
                    VStack(alignment: .leading, spacing: 2) {{
                        Text({title})
                            .font(.headline)
                        Text({subtitle})
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }}
                    Spacer()
                    Text("Score \\(score)")
                        .font(.headline.monospacedDigit())
                }}

                HStack {{
                    Text({player_action})
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button(isPlaying ? InputIntent.resetTitle : InputIntent.startTitle) {{
                        isPlaying.toggle()
                        if !isPlaying {{
                            score = 0
                        }}
                    }}
                    .buttonStyle(.borderedProminent)
                }}
            }}
            .padding()
            .background(.thinMaterial)
        }}
    }}
}}
"""


def _swift_string_literal(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=True)


def _target_shooter_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var state = GameSessionState()

    private var isPlaying: Bool {{
        SessionControl.isPlaying(state)
    }}

    var body: some View {{
        ZStack(alignment: .top) {{
            GameView(state: state)
                .ignoresSafeArea()

            VStack(spacing: 8) {{
                HStack {{
                    VStack(alignment: .leading, spacing: 2) {{
                        Text({title})
                            .font(.headline)
                        Text({subtitle})
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }}
                    Spacer()
                    VStack(alignment: .trailing, spacing: 2) {{
                        Text("Score \\(state.score)")
                            .font(.headline.monospacedDigit())
                        Text("Hits \\(state.targetsHit)")
                            .font(.caption.monospacedDigit())
                    }}
                }}

                HStack(spacing: 12) {{
                    Text("Perfect \\(state.perfectHits)")
                        .font(.caption.monospacedDigit())
                    Text(FeedbackState.message(for: state))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                }}

                HStack {{
                    Text({player_action})
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button(InputIntent.primaryButtonTitle(isPlaying: isPlaying)) {{
                        hitTarget()
                    }}
                    .buttonStyle(.borderedProminent)
                    Button("Finish") {{
                        state = GameRules.finishTargetShooterSession(state)
                    }}
                    .buttonStyle(.bordered)
                    Button(InputIntent.resetTitle) {{
                        state = SessionControl.reset()
                    }}
                    .buttonStyle(.bordered)
                }}

                if SessionControl.isResult(state) {{
                    ResultView(state: state) {{
                        state = SessionControl.reset()
                    }}
                }}
            }}
            .padding()
            .background(.thinMaterial)
        }}
    }}

    private func hitTarget() {{
        if !isPlaying {{
            state = GameRules.startTargetShooterSession(sessionSeconds: state.sessionSeconds)
            return
        }}
        state = GameRules.recordTargetHit(state)
    }}
}}
"""


def _stack_puzzle_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var state = GameSessionState()
    @State private var stablePlacement = true

    private var isPlaying: Bool {{
        SessionControl.isPlaying(state)
    }}

    var body: some View {{
        ZStack(alignment: .top) {{
            GameView(state: state)
                .ignoresSafeArea()

            VStack(spacing: 8) {{
                HStack {{
                    VStack(alignment: .leading, spacing: 2) {{
                        Text({title})
                            .font(.headline)
                        Text({subtitle})
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }}
                    Spacer()
                    VStack(alignment: .trailing, spacing: 2) {{
                        Text("Score \\(state.score)")
                            .font(.headline.monospacedDigit())
                        Text("Pieces \\(state.piecesPlaced)/\\(GameRules.maxPieces)")
                            .font(.caption.monospacedDigit())
                    }}
                }}

                HStack(spacing: 12) {{
                    Text("Stable \\(state.stablePieces)")
                        .font(.caption.monospacedDigit())
                    Text(FeedbackState.message(for: state))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Toggle("Stable", isOn: $stablePlacement)
                        .font(.caption)
                        .fixedSize()
                }}

                HStack {{
                    Text({player_action})
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button(InputIntent.primaryButtonTitle(isPlaying: isPlaying)) {{
                        placeStackPuzzlePiece()
                    }}
                    .buttonStyle(.borderedProminent)
                    Button("Collapse") {{
                        state = GameRules.collapseStack(state)
                    }}
                    .buttonStyle(.bordered)
                    Button(InputIntent.resetTitle) {{
                        state = SessionControl.reset()
                        stablePlacement = true
                    }}
                    .buttonStyle(.bordered)
                }}

                if SessionControl.isResult(state) {{
                    ResultView(state: state) {{
                        state = SessionControl.reset()
                        stablePlacement = true
                    }}
                }}
            }}
            .padding()
            .background(.thinMaterial)
        }}
    }}

    private func placeStackPuzzlePiece() {{
        if !isPlaying {{
            state = GameRules.startStackPuzzleSession(sessionSeconds: state.sessionSeconds)
            return
        }}
        state = GameRules.placeStackPiece(state, stable: stablePlacement)
    }}
}}
"""


def _toss_physics_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var state = GameSessionState()
    @State private var throwPower = 0.5

    private var isPlaying: Bool {{
        SessionControl.isPlaying(state)
    }}

    var body: some View {{
        ZStack(alignment: .top) {{
            GameView(state: state)
                .ignoresSafeArea()

            VStack(spacing: 8) {{
                HStack {{
                    VStack(alignment: .leading, spacing: 2) {{
                        Text({title})
                            .font(.headline)
                        Text({subtitle})
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }}
                    Spacer()
                    VStack(alignment: .trailing, spacing: 2) {{
                        Text("Score \\(state.score)")
                            .font(.headline.monospacedDigit())
                        Text("Attempts \\(state.attemptsRemaining)")
                            .font(.caption.monospacedDigit())
                    }}
                }}

                HStack(spacing: 12) {{
                    Text("Power \\(Int(throwPower * 100))%")
                        .font(.caption.monospacedDigit())
                    Slider(value: $throwPower, in: 0...1)
                        .frame(maxWidth: 180)
                    Text(FeedbackState.message(for: state))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }}

                HStack {{
                    Text({player_action})
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button(InputIntent.primaryButtonTitle(isPlaying: isPlaying)) {{
                        throwToss()
                    }}
                    .buttonStyle(.borderedProminent)
                    Button(InputIntent.resetTitle) {{
                        state = SessionControl.reset()
                        throwPower = 0.5
                    }}
                    .buttonStyle(.bordered)
                }}

                if SessionControl.isResult(state) {{
                    ResultView(state: state) {{
                        state = SessionControl.reset()
                        throwPower = 0.5
                    }}
                }}
            }}
            .padding()
            .background(.thinMaterial)
        }}
    }}

    private func throwToss() {{
        if !isPlaying {{
            state = GameRules.startTossSession(sessionSeconds: state.sessionSeconds)
            return
        }}
        state = GameRules.resolveToss(state, power: throwPower)
    }}
}}
"""


def _fighter_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var state = GameRules.fighterScreenshotSession(
        for: ScreenshotState.requested,
        fallback: GameSessionState()
    )

    private var isPlaying: Bool {{
        SessionControl.isPlaying(state)
    }}

    var body: some View {{
        ZStack(alignment: .top) {{
            GameView(state: state)
                .ignoresSafeArea()

            VStack(spacing: 8) {{
                HStack {{
                    VStack(alignment: .leading, spacing: 2) {{
                        Text({title})
                            .font(.headline)
                        Text({subtitle})
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }}
                    Spacer()
                    VStack(alignment: .trailing, spacing: 2) {{
                        Text("Score \\(state.score)")
                            .font(.headline.monospacedDigit())
                        Text("HP \\(state.playerHealth)")
                            .font(.caption.monospacedDigit())
                    }}
                }}

                HStack(spacing: 12) {{
                    Text("Opponent \\(state.opponentHealth)")
                        .font(.caption.monospacedDigit())
                    Text("Combo \\(state.comboCount)")
                        .font(.caption.monospacedDigit())
                    Text("Guard \\(state.guardMeter)")
                        .font(.caption.monospacedDigit())
                    Spacer()
                    Text(FeedbackState.message(for: state))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }}

                if !SessionControl.isResult(state) {{
                    HStack(spacing: 8) {{
                        Spacer()
                        Button(InputIntent.primaryButtonTitle(isPlaying: isPlaying)) {{
                            attackFighter()
                        }}
                        .buttonStyle(.borderedProminent)
                        .controlSize(.small)
                        Button("Dodge") {{
                            dodgeFighter()
                        }}
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                        Button("Damage") {{
                            state = GameRules.applyFighterDamage(state)
                        }}
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                        Button(InputIntent.resetTitle) {{
                            state = SessionControl.reset()
                        }}
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                    }}
                    .font(.caption.weight(.semibold))
                    .lineLimit(1)
                    .minimumScaleFactor(0.85)
                }}

                if SessionControl.isResult(state) {{
                    ResultView(state: state) {{
                        state = SessionControl.reset()
                    }}
                }}
            }}
            .padding()
            .background(.thinMaterial)
            .gesture(
                DragGesture(minimumDistance: 20).onEnded {{ _ in
                    dodgeFighter()
                }}
            )
        }}
    }}

    private func attackFighter() {{
        if !isPlaying {{
            state = GameRules.startFighterDuelSession(sessionSeconds: state.sessionSeconds)
            return
        }}
        state = GameRules.recordFighterAttack(state)
    }}

    private func dodgeFighter() {{
        if !isPlaying {{
            state = GameRules.startFighterDuelSession(sessionSeconds: state.sessionSeconds)
            return
        }}
        state = GameRules.performPerfectDodge(state)
    }}
}}
"""


def _wave_defense_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var state = GameSessionState()

    private var isPlaying: Bool {{
        SessionControl.isPlaying(state)
    }}

    var body: some View {{
        ZStack(alignment: .top) {{
            GameView(state: state)
                .ignoresSafeArea()

            VStack(spacing: 8) {{
                HStack {{
                    VStack(alignment: .leading, spacing: 2) {{
                        Text({title})
                            .font(.headline)
                        Text({subtitle})
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }}
                    Spacer()
                    VStack(alignment: .trailing, spacing: 2) {{
                        Text("Score \\(state.score)")
                            .font(.headline.monospacedDigit())
                        Text("Health \\(state.health)")
                            .font(.caption.monospacedDigit())
                    }}
                }}

                HStack(spacing: 12) {{
                    Text("Wave \\(state.wave)")
                        .font(.caption.monospacedDigit())
                    Text("Threats \\(state.threatsRemaining)")
                        .font(.caption.monospacedDigit())
                    Text("Cleared \\(state.clearedThreats)")
                        .font(.caption.monospacedDigit())
                    Spacer()
                    Text(FeedbackState.message(for: state))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }}

                HStack {{
                    Text({player_action})
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button(InputIntent.primaryButtonTitle(isPlaying: isPlaying)) {{
                        fireWaveDefense()
                    }}
                    .buttonStyle(.borderedProminent)
                    Button("Damage") {{
                        state = GameRules.applyThreatDamage(state)
                    }}
                    .buttonStyle(.bordered)
                    Button(InputIntent.resetTitle) {{
                        state = SessionControl.reset()
                    }}
                    .buttonStyle(.bordered)
                }}

                if SessionControl.isResult(state) {{
                    ResultView(state: state) {{
                        state = SessionControl.reset()
                    }}
                }}
            }}
            .padding()
            .background(.thinMaterial)
        }}
    }}

    private func fireWaveDefense() {{
        if !isPlaying {{
            state = GameRules.startWaveDefenseSession(sessionSeconds: state.sessionSeconds)
            return
        }}
        state = GameRules.clearThreat(state)
    }}
}}
"""


def _lane_dodger_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var state = GameSessionState()

    private var isPlaying: Bool {{
        SessionControl.isPlaying(state)
    }}

    var body: some View {{
        ZStack(alignment: .top) {{
            GameView(state: state)
                .ignoresSafeArea()

            VStack(spacing: 8) {{
                HStack {{
                    VStack(alignment: .leading, spacing: 2) {{
                        Text({title})
                            .font(.headline)
                        Text({subtitle})
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }}
                    Spacer()
                    VStack(alignment: .trailing, spacing: 2) {{
                        Text("Score \\(state.score)")
                            .font(.headline.monospacedDigit())
                        Text("Distance \\(state.distance)")
                            .font(.caption.monospacedDigit())
                    }}
                }}

                HStack(spacing: 12) {{
                    Text("Lane \\(state.currentLane + 1)/\\(GameRules.laneCount)")
                        .font(.caption.monospacedDigit())
                    Text("Obstacle \\(state.obstacleLane + 1)")
                        .font(.caption.monospacedDigit())
                    Text("Near \\(state.nearMisses)")
                        .font(.caption.monospacedDigit())
                    Spacer()
                    Text(FeedbackState.message(for: state))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }}

                HStack {{
                    Text({player_action})
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button(InputIntent.primaryButtonTitle(isPlaying: isPlaying)) {{
                        advanceLaneDodger()
                    }}
                    .buttonStyle(.borderedProminent)
                    Button(InputIntent.resetTitle) {{
                        state = SessionControl.reset()
                    }}
                    .buttonStyle(.bordered)
                }}

                if SessionControl.isResult(state) {{
                    ResultView(state: state) {{
                        state = SessionControl.reset()
                    }}
                }}
            }}
            .padding()
            .background(.thinMaterial)
            .gesture(
                DragGesture(minimumDistance: 20).onEnded {{ value in
                    moveLane(value.translation.width > 0 ? 1 : -1)
                }}
            )
        }}
    }}

    private func moveLane(_ direction: Int) {{
        state.currentLane = GameRules.laneAfterMove(currentLane: state.currentLane, direction: direction)
        state.lastEvent = "lane changed"
    }}

    private func advanceLaneDodger() {{
        if !isPlaying {{
            state = GameRules.startLaneDodgerSession(sessionSeconds: state.sessionSeconds)
            return
        }}
        state = GameRules.advanceLaneDodgerFrame(state)
    }}
}}
"""
