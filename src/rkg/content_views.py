from __future__ import annotations

import json
from typing import Any, Mapping


def content_view_swift(display_name: str, spec: Mapping[str, Any]) -> str:
    game = spec["game"]
    loop = spec["loop"]
    title = _swift_string_literal(display_name)
    subtitle = _swift_string_literal(f"{game['archetype']} / {game['session_seconds']}s")
    player_action = _swift_string_literal(loop["player_action"])
    if str(game["archetype"]) == "lane_dodger":
        return _lane_dodger_content_view_swift(title, subtitle, player_action)
    if str(game["archetype"]) == "wave_defense_lite":
        return _wave_defense_content_view_swift(title, subtitle, player_action)
    if str(game["archetype"]) == "toss_physics":
        return _toss_physics_content_view_swift(title, subtitle, player_action)
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
                    Button(isPlaying ? "Reset" : "Start") {{
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


def _toss_physics_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var state = GameSessionState()
    @State private var throwPower = 0.5

    private var isPlaying: Bool {{
        state.phase == .playing
    }}

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
                    Text(state.lastEvent.capitalized)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }}

                HStack {{
                    Text({player_action})
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button(isPlaying ? "Throw" : "Start") {{
                        throwToss()
                    }}
                    .buttonStyle(.borderedProminent)
                    Button("Reset") {{
                        state = GameSessionState()
                        throwPower = 0.5
                    }}
                    .buttonStyle(.bordered)
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


def _wave_defense_content_view_swift(title: str, subtitle: str, player_action: str) -> str:
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var state = GameSessionState()

    private var isPlaying: Bool {{
        state.phase == .playing
    }}

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
                    Text(state.lastEvent.capitalized)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }}

                HStack {{
                    Text({player_action})
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button(isPlaying ? "Fire" : "Start") {{
                        fireWaveDefense()
                    }}
                    .buttonStyle(.borderedProminent)
                    Button("Damage") {{
                        state = GameRules.applyThreatDamage(state)
                    }}
                    .buttonStyle(.bordered)
                    Button("Reset") {{
                        state = GameSessionState()
                    }}
                    .buttonStyle(.bordered)
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
        state.phase == .playing
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
                    Text(state.lastEvent.capitalized)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }}

                HStack {{
                    Text({player_action})
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button(isPlaying ? "Dodge" : "Start") {{
                        advanceLaneDodger()
                    }}
                    .buttonStyle(.borderedProminent)
                    Button("Reset") {{
                        state = GameSessionState()
                    }}
                    .buttonStyle(.bordered)
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
