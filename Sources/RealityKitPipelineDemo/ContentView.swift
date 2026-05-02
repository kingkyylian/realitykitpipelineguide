import SwiftUI

struct ContentView: View {
    @StateObject private var session = GameSession()
    @State private var spawnToken = 0
    @State private var resetToken = 0

    var body: some View {
        ZStack {
            RealityKitGameView(
                session: session,
                spawnToken: spawnToken,
                resetToken: resetToken
            )
            .ignoresSafeArea()

            VStack(spacing: 0) {
                hud
                Spacer()
                controls
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 14)
        }
    }

    private var hud: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 12) {
                metric("Score", "\(session.score)")
                metric("Shots", "\(session.shots)")
                metric("Hits", "\(session.hits)")
                metric("Accuracy", session.accuracyText)
            }

            Text(session.status)
                .font(.subheadline.weight(.medium))
                .foregroundStyle(.white.opacity(0.86))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(.black.opacity(0.52), in: RoundedRectangle(cornerRadius: 8))
    }

    private var controls: some View {
        HStack(spacing: 12) {
            Button {
                spawnToken += 1
            } label: {
                Label("Spawn", systemImage: "scope")
            }

            Button(role: .destructive) {
                resetToken += 1
            } label: {
                Label("Reset", systemImage: "arrow.counterclockwise")
            }
        }
        .buttonStyle(.borderedProminent)
        .controlSize(.large)
        .labelStyle(.titleAndIcon)
        .frame(maxWidth: .infinity, alignment: .trailing)
    }

    private func metric(_ title: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title.uppercased())
                .font(.caption2.weight(.bold))
                .foregroundStyle(.white.opacity(0.62))
            Text(value)
                .font(.headline.monospacedDigit())
                .foregroundStyle(.white)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
        }
        .frame(minWidth: 64, alignment: .leading)
    }
}
