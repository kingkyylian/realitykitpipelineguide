import CoreGraphics
import Foundation

enum WaveRules {
    static func targetCountForCurrentWave(wave: Int, maxTargets: Int) -> Int {
        min(2 + max(wave - 1, 0), maxTargets)
    }

    static func targetCountForNextWave(wave: Int, maxTargets: Int) -> Int {
        min(2 + wave, maxTargets)
    }
}

enum TargetScoring {
    static func screenHit(distance: CGFloat, boundsWidth: CGFloat) -> (points: Int, zone: String) {
        let bullseyeRadius = boundsWidth * 0.022
        let innerRingRadius = boundsWidth * 0.048

        if distance < bullseyeRadius {
            return (5, "Bullseye")
        }

        if distance < innerRingRadius {
            return (3, "Inner ring")
        }

        return (1, "Outer ring")
    }

    static func spatialHit(radialDistance: Float) -> (points: Int, zone: String) {
        if radialDistance < 0.104 {
            return (5, "Bullseye")
        }

        if radialDistance < 0.215 {
            return (3, "Inner ring")
        }

        return (1, "Outer ring")
    }
}
