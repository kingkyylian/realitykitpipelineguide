import Combine
import Foundation

final class GameSession: ObservableObject {
    @Published var score = 0
    @Published var shots = 0
    @Published var hits = 0
    @Published var activeTargets = 0
    @Published var status = "Procedural sandbox ready"

    var accuracyText: String {
        guard shots > 0 else { return "0%" }
        return "\(Int((Double(hits) / Double(shots)) * 100))%"
    }

    func reset() {
        score = 0
        shots = 0
        hits = 0
        activeTargets = 0
        status = "Scene reset"
    }

    func recordShot() {
        shots += 1
        status = "Projectile fired"
    }

    func recordHit(points: Int, zone: String) {
        hits += 1
        score += points
        status = "\(zone) +\(points)"
    }
}
