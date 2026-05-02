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

            reticle
        }
    }

    private var hud: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 3) {
                    Text("REALITYKIT RANGE")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(.white.opacity(0.62))
                    Text(session.status)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(statusColor)
                        .lineLimit(1)
                        .minimumScaleFactor(0.75)
                }

                Spacer()

                Text("\(session.score)")
                    .font(.system(size: 34, weight: .bold, design: .rounded).monospacedDigit())
                    .foregroundStyle(.white)
            }

            HStack(spacing: 10) {
                metric("Shots", "\(session.shots)")
                metric("Hits", "\(session.hits)")
                metric("Accuracy", session.accuracyText)
                metric("Wave", "\(session.wave)")
                metric("Cleared", session.waveProgressText)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 16)
        .padding(.vertical, 14)
        .background(.black.opacity(0.62), in: RoundedRectangle(cornerRadius: 8))
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(.white.opacity(0.10), lineWidth: 1)
        )
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

    private var reticle: some View {
        ZStack {
            Circle()
                .stroke(.white.opacity(0.28), lineWidth: 1)
                .frame(width: 34, height: 34)
            Circle()
                .fill(.white.opacity(0.70))
                .frame(width: 4, height: 4)
            Rectangle()
                .fill(.white.opacity(0.40))
                .frame(width: 1, height: 12)
                .offset(y: -27)
            Rectangle()
                .fill(.white.opacity(0.40))
                .frame(width: 1, height: 12)
                .offset(y: 27)
            Rectangle()
                .fill(.white.opacity(0.40))
                .frame(width: 12, height: 1)
                .offset(x: -27)
            Rectangle()
                .fill(.white.opacity(0.40))
                .frame(width: 12, height: 1)
                .offset(x: 27)
        }
        .allowsHitTesting(false)
    }

    private var statusColor: Color {
        if session.status.contains("Bullseye") {
            return Color(red: 0.38, green: 0.95, blue: 1.0)
        }

        if session.status.contains("Inner") {
            return Color(red: 1.0, green: 0.82, blue: 0.26)
        }

        if session.status.contains("Outer") {
            return Color(red: 1.0, green: 0.48, blue: 0.36)
        }

        return .white.opacity(0.88)
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
        .frame(minWidth: 58, alignment: .leading)
    }
}
