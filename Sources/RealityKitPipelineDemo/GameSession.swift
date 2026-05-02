import Combine
import Foundation

final class GameSession: ObservableObject {
    @Published var score = 0
    @Published var shots = 0
    @Published var hits = 0
    @Published var activeTargets = 0
    @Published var wave = 1
    @Published var targetsThisWave = 2
    @Published var clearedTargets = 0
    @Published var status = "Procedural sandbox ready"

    var accuracyText: String {
        guard shots > 0 else { return "0%" }
        return "\(Int((Double(hits) / Double(shots)) * 100))%"
    }

    var waveProgressText: String {
        "\(clearedTargets)/\(targetsThisWave)"
    }

    func startRun(targetCount: Int) {
        score = 0
        shots = 0
        hits = 0
        activeTargets = 0
        wave = 1
        targetsThisWave = targetCount
        clearedTargets = 0
        status = "Wave 1 ready"
    }

    func reset() {
        startRun(targetCount: 2)
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

    func recordTargetsDestroyed(_ count: Int) {
        clearedTargets = min(targetsThisWave, clearedTargets + count)
    }

    func addTargetToCurrentWave() {
        targetsThisWave += 1
        status = "Target added"
    }

    func advanceWave(targetCount: Int) {
        wave += 1
        targetsThisWave = targetCount
        clearedTargets = 0
        status = "Wave \(wave) ready"
    }
}
