import Foundation
import RealityKit
import UIKit

struct HitEffectSystem {
    private struct HitEffect {
        let root: Entity
        let flash: ModelEntity
        var sparks: [(entity: ModelEntity, velocity: SIMD3<Float>)]
        var age: TimeInterval
        let duration: TimeInterval
    }

    private var hitEffects: [HitEffect] = []

    mutating func add(
        at position: SIMD3<Float>,
        points: Int,
        playerOrigin: SIMD3<Float>,
        worldAnchor: Entity
    ) {
        let root = Entity()
        root.name = "hit_effect"
        root.position = position

        let color: UIColor
        switch points {
        case 5:
            color = UIColor(red: 0.20, green: 0.92, blue: 1.0, alpha: 1.0)
        case 3:
            color = UIColor(red: 1.0, green: 0.82, blue: 0.22, alpha: 1.0)
        default:
            color = UIColor(red: 0.98, green: 0.34, blue: 0.24, alpha: 1.0)
        }

        let material = SimpleMaterial(color: color, roughness: 0.35, isMetallic: false)
        var sparks: [(entity: ModelEntity, velocity: SIMD3<Float>)] = []

        for index in 0..<18 {
            let angle = (Float(index) / 18.0) * 2.0 * .pi
            let vertical = sin(Float(index) * 1.7) * 0.07
            let spark = ModelEntity(mesh: .generateSphere(radius: 0.014), materials: [material])
            spark.position = [0, 0, 0.03]
            root.addChild(spark)
            sparks.append((
                entity: spark,
                velocity: [cos(angle) * 0.62, sin(angle) * 0.62, vertical + 0.16]
            ))
        }

        let flash = ModelEntity(mesh: .generateSphere(radius: 0.045), materials: [material])
        flash.position = [0, 0, 0.04]
        root.addChild(flash)

        root.look(at: playerOrigin, from: position, relativeTo: worldAnchor)
        worldAnchor.addChild(root)
        hitEffects.append(HitEffect(root: root, flash: flash, sparks: sparks, age: 0, duration: 0.36))
    }

    mutating func update(deltaTime: TimeInterval) {
        guard !hitEffects.isEmpty else { return }

        for index in hitEffects.indices {
            hitEffects[index].age += deltaTime
            let progress = min(Float(hitEffects[index].age / hitEffects[index].duration), 1.0)
            let dt = Float(deltaTime)

            for i in hitEffects[index].sparks.indices {
                hitEffects[index].sparks[i].velocity.y -= 3.2 * dt
                hitEffects[index].sparks[i].entity.position += hitEffects[index].sparks[i].velocity * dt
                let fadeScale = max(0, 1.0 - progress * 1.1)
                hitEffects[index].sparks[i].entity.scale = SIMD3<Float>(repeating: fadeScale)
            }

            let flashScale = sin(progress * .pi) * 1.8
            hitEffects[index].flash.scale = SIMD3<Float>(repeating: max(0, flashScale))
        }

        hitEffects.removeAll { effect in
            let shouldRemove = effect.age >= effect.duration
            if shouldRemove {
                effect.root.removeFromParent()
            }
            return shouldRemove
        }
    }

    mutating func removeAll() {
        hitEffects.forEach { $0.root.removeFromParent() }
        hitEffects.removeAll()
    }
}
