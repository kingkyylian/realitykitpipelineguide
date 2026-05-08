import RealityKit
import UIKit

enum RealityMaterials {
    static func pbr(color: UIColor, roughness: Float, metallic: Float) -> PhysicallyBasedMaterial {
        var material = PhysicallyBasedMaterial()
        material.baseColor = .init(tint: color)
        material.roughness = .init(floatLiteral: roughness)
        material.metallic = .init(floatLiteral: metallic)
        return material
    }
}
