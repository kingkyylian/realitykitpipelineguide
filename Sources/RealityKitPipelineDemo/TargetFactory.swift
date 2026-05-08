import RealityKit
import UIKit

struct TargetFactory {
    struct SpawnedTarget {
        let assetName: String?
        let model: ModelEntity
    }

    private struct LoadedTargetAsset {
        let name: String
        let model: ModelEntity
    }

    private static let importedTargetOrientation = simd_quatf(angle: .pi / 2, axis: [1, 0, 0])
    private static let importedTargetScale: Float = 0.90
    private static let targetSpawnSlots: [SIMD3<Float>] = [
        [-0.32, 0.28, -1.92],
        [0.32, 0.28, -1.92],
        [0.0, 0.50, -2.05],
        [-0.62, 0.18, -2.02],
        [0.62, 0.18, -2.02]
    ]

    private var nextTargetSlot = 0

    var maxSpawnSlots: Int {
        Self.targetSpawnSlots.count
    }

    mutating func makeTarget(playerOrigin: SIMD3<Float>, relativeTo worldAnchor: Entity) -> SpawnedTarget {
        let importedTarget = loadTargetAsset()
        let target = importedTarget?.model ?? makeProceduralTarget()
        let targetPosition = nextSpawnPosition()

        target.name = "target"
        target.position = targetPosition

        if importedTarget != nil {
            applyImportedTargetOrientation(to: target)
            target.scale = SIMD3<Float>(repeating: Self.importedTargetScale)
            target.look(at: playerOrigin, from: targetPosition, relativeTo: worldAnchor)
            target.orientation *= simd_quatf(angle: .pi, axis: [0, 1, 0])
        }

        let shape = ShapeResource.generateSphere(radius: 0.32)
        target.components.set(CollisionComponent(shapes: [shape]))
        target.components.set(PhysicsBodyComponent(
            shapes: [shape],
            mass: 0,
            mode: .static
        ))

        return SpawnedTarget(assetName: importedTarget?.name, model: target)
    }

    mutating func resetSpawnSlots() {
        nextTargetSlot = 0
    }

    private func loadTargetAsset() -> LoadedTargetAsset? {
        for name in ["target_basic_textured", "target_basic"] {
            if let model = ImportedAssetLoader.loadModel(named: name) {
                return LoadedTargetAsset(name: name, model: model)
            }
        }
        return nil
    }

    private mutating func nextSpawnPosition() -> SIMD3<Float> {
        let position = Self.targetSpawnSlots[nextTargetSlot % Self.targetSpawnSlots.count]
        nextTargetSlot += 1
        return position
    }

    private func applyImportedTargetOrientation(to entity: Entity) {
        guard !entity.children.isEmpty else {
            entity.orientation = Self.importedTargetOrientation
            return
        }

        for child in entity.children {
            child.orientation *= Self.importedTargetOrientation
        }
    }

    private func makeProceduralTarget() -> ModelEntity {
        let material = RealityMaterials.pbr(
            color: UIColor(red: 0.95, green: 0.38, blue: 0.18, alpha: 1),
            roughness: 0.44,
            metallic: 0.0
        )
        return ModelEntity(mesh: .generateSphere(radius: 0.15), materials: [material])
    }
}
