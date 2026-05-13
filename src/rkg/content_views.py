from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from rkg.custom_realitykit_runtime import custom_realitykit_adapter_content_sections


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
    if str(game["archetype"]) == "flappy_side_scroller":
        return _flappy_content_view_swift(title, subtitle, player_action)
    if str(game["archetype"]) == "custom_realitykit":
        return _custom_realitykit_content_view_swift(title, subtitle, player_action)
    return _generic_content_view_swift(title, subtitle, player_action)


def _custom_realitykit_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    adapter_sections = custom_realitykit_adapter_content_sections()
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var state = GameRules.customRealityKitScreenshotSession(
        for: ScreenshotState.requested,
        fallback: GameSessionState()
    )
    @State private var hasStarted = ScreenshotState.requested != nil

    private var isPlaying: Bool {{
        SessionControl.isPlaying(state)
    }}

    private var isInterfaceVisible: Bool {{
        hasStarted || isPlaying || SessionControl.isResult(state)
    }}

    private var showsStartOverlay: Bool {{
        !isInterfaceVisible
    }}

    var body: some View {{
        ZStack(alignment: .bottom) {{
            GameView(state: state)
                .ignoresSafeArea()

            if showsStartOverlay {{
                StartOverlay(
                    title: {title},
                    subtitle: {subtitle},
                    playerAction: {player_action},
                    onStart: startSession
                )
            }}

            if isInterfaceVisible && !SessionControl.isResult(state) {{
                PrimaryInputLayer(
                    isPlaying: isPlaying,
                    playerAction: {player_action},
                    onPrimary: advanceSkeleton,
                    onReset: resetSession
                ) {{
{adapter_sections}
                }}
                .controlSize(.small)
                .padding(.horizontal, 12)
                .padding(.bottom, 12)
            }}

            if SessionControl.isResult(state) {{
                ResultView(state: state, onReset: resetSession)
                    .padding(.horizontal, 16)
                    .padding(.bottom, 28)
            }}
        }}
        .safeAreaInset(edge: .top) {{
            if isInterfaceVisible {{
                GameHUD(state: state)
                    .padding(.horizontal, 14)
                    .padding(.top, 8)
                    .padding(.bottom, 6)
            }}
        }}
        .statusBarHidden(true)
        .persistentSystemOverlays(.hidden)
    }}

    private func advanceSkeleton() {{
        if !isPlaying {{
            startSession()
            return
        }}
        state = GameRules.advanceCustomRealityKitSession(state)
    }}

    private func startSession() {{
        hasStarted = true
        state = GameRules.startCustomRealityKitSession(sessionSeconds: state.sessionSeconds)
    }}

    private func resetSession() {{
        state = SessionControl.reset()
        hasStarted = ScreenshotState.requested != nil
    }}
}}

private struct GameHUD: View {{
    let state: GameSessionState

    var body: some View {{
        HStack(alignment: .top, spacing: 12) {{
            VStack(alignment: .leading, spacing: 3) {{
                Text(InputController.controlSummary)
                    .font(.caption.weight(.semibold))
                    .lineLimit(1)
                Text(FeedbackState.message(for: state))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }}

            Spacer(minLength: 10)

            VStack(alignment: .trailing, spacing: 3) {{
                Text("Score \\(state.score)")
                    .font(.headline.monospacedDigit())
                    .lineLimit(1)
                Text(SystemFlags.summary)
                    .font(.caption2.monospaced())
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }}
        }}
        .foregroundStyle(.white)
        .shadow(color: .black.opacity(0.45), radius: 8, y: 2)
    }}
}}

private struct StartOverlay: View {{
    let title: String
    let subtitle: String
    let playerAction: String
    let onStart: () -> Void

    var body: some View {{
        VStack(alignment: .leading, spacing: 16) {{
            Spacer()

            VStack(alignment: .leading, spacing: 5) {{
                Text(title)
                    .font(.system(size: 38, weight: .bold, design: .rounded))
                    .lineLimit(2)
                    .minimumScaleFactor(0.72)
                Text(subtitle)
                    .font(.subheadline.monospaced())
                    .foregroundStyle(.white.opacity(0.68))
                    .lineLimit(1)
                Text(playerAction)
                    .font(.callout)
                    .foregroundStyle(.white.opacity(0.78))
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
            }}

            Button(action: onStart) {{
                HStack(spacing: 8) {{
                    Image(systemName: "play.fill")
                    Text(InputIntent.startTitle)
                }}
                .font(.headline)
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
            }}
            .buttonStyle(.borderedProminent)
            .tint(.white)
            .foregroundStyle(.black)

            Spacer()
                .frame(maxHeight: 160)
        }}
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 24)
        .foregroundStyle(.white)
        .shadow(color: .black.opacity(0.55), radius: 12, y: 4)
    }}
}}

private struct PrimaryInputLayer<AdapterControls: View>: View {{
    let isPlaying: Bool
    let playerAction: String
    let onPrimary: () -> Void
    let onReset: () -> Void
    let adapterControls: AdapterControls

    init(
        isPlaying: Bool,
        playerAction: String,
        onPrimary: @escaping () -> Void,
        onReset: @escaping () -> Void,
        @ViewBuilder adapterControls: () -> AdapterControls
    ) {{
        self.isPlaying = isPlaying
        self.playerAction = playerAction
        self.onPrimary = onPrimary
        self.onReset = onReset
        self.adapterControls = adapterControls()
    }}

    var body: some View {{
        VStack(alignment: .leading, spacing: 10) {{
            HStack(spacing: 10) {{
                Image(systemName: "scope")
                    .imageScale(.medium)
                    .foregroundStyle(.white.opacity(0.82))
                Text(playerAction)
                    .font(.caption)
                    .foregroundStyle(.white.opacity(0.72))
                    .lineLimit(2)
                Spacer(minLength: 8)
                Button(action: onPrimary) {{
                    HStack(spacing: 6) {{
                        Image(systemName: "bolt.fill")
                        Text(isPlaying ? InputController.primaryActionLabel : InputIntent.startTitle)
                    }}
                }}
                .buttonStyle(.borderedProminent)
                Button(action: onReset) {{
                    Image(systemName: "arrow.counterclockwise")
                }}
                .buttonStyle(.bordered)
                .accessibilityLabel(InputIntent.resetTitle)
            }}

            adapterControls.foregroundStyle(.white)
        }}
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.black.opacity(0.58))
        .overlay(
            RoundedRectangle(cornerRadius: 8, style: .continuous)
                .stroke(Color.white.opacity(0.14), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
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


def _flappy_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var state = GameRules.flappyScreenshotSession(
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
                        Text("Height \\(Int(state.birdY * 100))")
                            .font(.caption.monospacedDigit())
                    }}
                }}

                HStack(spacing: 12) {{
                    Text("Pipes \\(state.pipesPassed)")
                        .font(.caption.monospacedDigit())
                    Text("Gap \\(Int(state.gapY * 100))")
                        .font(.caption.monospacedDigit())
                    Text("Velocity \\(Int(state.birdVelocity * 100))")
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
                            flapFlappy()
                        }}
                        .buttonStyle(.borderedProminent)
                        .controlSize(.small)
                        Button("Tick") {{
                            tickFlappy()
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
                TapGesture().onEnded {{
                    flapFlappy()
                }}
            )
        }}
    }}

    private func flapFlappy() {{
        if !isPlaying {{
            state = GameRules.startFlappySession(sessionSeconds: state.sessionSeconds)
            return
        }}
        state = GameRules.flapBird(state)
    }}

    private func tickFlappy() {{
        if !isPlaying {{
            state = GameRules.startFlappySession(sessionSeconds: state.sessionSeconds)
            return
        }}
        state = GameRules.advanceFlappyFrame(state)
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
