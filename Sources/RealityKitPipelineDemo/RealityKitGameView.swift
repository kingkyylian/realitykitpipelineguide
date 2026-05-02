import RealityKit
import SwiftUI

struct RealityKitGameView: UIViewRepresentable {
    let session: GameSession
    let spawnToken: Int
    let resetToken: Int

    func makeUIView(context: Context) -> GameARView {
        let view = GameARView(frame: .zero, session: session)
        view.configureScene()
        return view
    }

    func updateUIView(_ uiView: GameARView, context: Context) {
        uiView.apply(spawnToken: spawnToken, resetToken: resetToken)
    }
}
