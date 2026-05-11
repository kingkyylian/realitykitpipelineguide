import RealityKit
import UIKit

enum MaterialResponseShowcase {
    private static let showcasePosition = SIMD3<Float>(0, 0.72, -1.55)
    private static let playerOrigin = SIMD3<Float>(0, 0.08, 0.2)
    private static let importedOrientation = simd_quatf(angle: .pi / 2, axis: [1, 0, 0])

    static func add(to worldAnchor: Entity) {
        addComparisonLights(to: worldAnchor)

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

    private static func addComparisonLights(to worldAnchor: Entity) {
        let grazingLight = PointLight()
        grazingLight.light.intensity = 9200
        grazingLight.position = [-0.72, 1.06, -0.78]
        worldAnchor.addChild(grazingLight)

        let rimLight = PointLight()
        rimLight.light.intensity = 5200
        rimLight.position = [0.84, 0.92, -1.02]
        worldAnchor.addChild(rimLight)
    }

    private static func addProceduralFallback(to worldAnchor: Entity) {
        let panels: [(Float, Float, Float, UIColor)] = [
            (-0.72, 0.98, 0.0, UIColor(red: 0.72, green: 0.08, blue: 0.06, alpha: 1)),
            (-0.24, 0.04, 0.0, UIColor(red: 0.88, green: 0.10, blue: 0.07, alpha: 1)),
            (0.24, 0.52, 0.0, UIColor(red: 0.78, green: 0.18, blue: 0.12, alpha: 1)),
            (0.72, 0.18, 1.0, UIColor(red: 0.78, green: 0.18, blue: 0.12, alpha: 1))
        ]

        for (x, roughness, metallic, color) in panels {
            let material = RealityMaterials.pbr(color: color, roughness: roughness, metallic: metallic)
            let panel = ModelEntity(mesh: .generateBox(size: [0.34, 0.34, 0.035]), materials: [material])
            let witness = ModelEntity(mesh: .generateSphere(radius: 0.045), materials: [material])
            witness.position = [0.09, 0.09, 0.045]
            panel.addChild(witness)
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
