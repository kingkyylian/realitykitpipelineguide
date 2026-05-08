import RealityKit
import UIKit

enum ArenaBuilder {
    static func addShowcaseBackdrop(to worldAnchor: Entity) {
        let backdropMaterial = RealityMaterials.pbr(
            color: UIColor(red: 0.08, green: 0.10, blue: 0.12, alpha: 1),
            roughness: 0.82,
            metallic: 0.0
        )
        let backdrop = ModelEntity(mesh: .generateBox(size: [3.8, 1.6, 0.06]), materials: [backdropMaterial])
        backdrop.name = "showcase_backdrop"
        backdrop.position = [0, 0.18, -2.85]
        worldAnchor.addChild(backdrop)
    }

    static func addArena(to worldAnchor: Entity) {
        if let importedArena = ImportedAssetLoader.loadModel(named: "arena_floor") {
            importedArena.name = "arena_floor"
            importedArena.position = [0, -0.42, -1.6]
            worldAnchor.addChild(importedArena)
            return
        }

        let floorMaterial = RealityMaterials.pbr(
            color: UIColor(red: 0.14, green: 0.18, blue: 0.20, alpha: 1),
            roughness: 0.9,
            metallic: 0.0
        )
        let floor = ModelEntity(mesh: .generateBox(size: [3.2, 0.04, 3.2]), materials: [floorMaterial])
        floor.name = "arena_floor"
        floor.position = [0, -0.42, -1.6]
        worldAnchor.addChild(floor)

        let laneMaterial = RealityMaterials.pbr(
            color: UIColor(red: 0.20, green: 0.30, blue: 0.34, alpha: 1),
            roughness: 0.74,
            metallic: 0.0
        )
        for x in stride(from: -1.2, through: 1.2, by: 0.6) {
            let lane = ModelEntity(mesh: .generateBox(size: [0.018, 0.012, 2.9]), materials: [laneMaterial])
            lane.position = [Float(x), -0.38, -1.6]
            worldAnchor.addChild(lane)
        }
    }
}
