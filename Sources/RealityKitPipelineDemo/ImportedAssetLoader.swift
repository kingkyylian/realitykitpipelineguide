import Foundation
import RealityKit

enum ImportedAssetLoader {
    static func loadModel(named name: String) -> ModelEntity? {
        guard let url = url(for: name) else {
            return nil
        }

        do {
            let model = try ModelEntity.loadModel(contentsOf: url)
            model.name = name
            return model
        } catch {
            return nil
        }
    }

    private static func url(for name: String) -> URL? {
        Bundle.main.url(forResource: name, withExtension: "usdz")
            ?? Bundle.main.url(forResource: name, withExtension: "usdz", subdirectory: "Imported")
            ?? Bundle.main.url(forResource: name, withExtension: "usdz", subdirectory: "Assets/Imported")
    }
}
