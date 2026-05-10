import RealityKit
import UIKit

enum MaterialResponseShowcase {
    private static let showcasePosition = SIMD3<Float>(0, 0.72, -1.55)
    private static let playerOrigin = SIMD3<Float>(0, 0.08, 0.2)
    private static let importedOrientation = simd_quatf(angle: .pi / 2, axis: [1, 0, 0])

    static func add(to worldAnchor: Entity) {
        addComparisonLight(to: worldAnchor)

        if let model = ImportedAssetLoader.loadModel(named: "material_response_targets") {
            model.name = "material_response_targets"
            model.position = showcasePosition
            model.scale = SIMD3<Float>(repeating: 1.0)
            applyImportedOrientation(to: model)
            model.look(at: playerOrigin, from: showcasePosition, relativeTo: worldAnchor)
            model.orientation *= simd_quatf(angle: .pi, axis: [0, 1, 0])
            worldAnchor.addChild(model)
            return
        }

        addProceduralFallback(to: worldAnchor)
    }

    private static func addComparisonLight(to worldAnchor: Entity) {
        let light = PointLight()
        light.light.intensity = 2800
        light.position = [0.35, 0.95, -0.95]
        worldAnchor.addChild(light)
    }

    private static func addProceduralFallback(to worldAnchor: Entity) {
        let panels: [(Float, Float, UIColor)] = [
            (-0.62, 0.88, UIColor(red: 0.72, green: 0.08, blue: 0.06, alpha: 1)),
            (0.0, 0.18, UIColor(red: 0.88, green: 0.10, blue: 0.07, alpha: 1)),
            (0.62, 0.52, UIColor(red: 0.78, green: 0.18, blue: 0.12, alpha: 1))
        ]

        for (x, roughness, color) in panels {
            let material = RealityMaterials.pbr(color: color, roughness: roughness, metallic: 0.0)
            let panel = ModelEntity(mesh: .generateBox(size: [0.34, 0.34, 0.035]), materials: [material])
            panel.position = showcasePosition + SIMD3<Float>(x, 0, 0)
            worldAnchor.addChild(panel)
        }
    }

    private static func applyImportedOrientation(to entity: Entity) {
        guard !entity.children.isEmpty else {
            entity.orientation = importedOrientation
            return
        }

        for child in entity.children {
            child.orientation *= importedOrientation
        }
    }
}
