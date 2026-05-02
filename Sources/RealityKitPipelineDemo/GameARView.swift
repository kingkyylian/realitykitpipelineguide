import Combine
import RealityKit
import UIKit

final class GameARView: ARView {
    private struct LoadedTargetAsset {
        let name: String
        let model: ModelEntity
    }

    private struct Projectile {
        let entity: ModelEntity
        let velocity: SIMD3<Float>
        var canScore: Bool
        var age: TimeInterval
    }

    private let gameSession: GameSession
    private let worldAnchor = AnchorEntity(world: .zero)
    private var subscriptions: [Cancellable] = []
    private var projectiles: [Projectile] = []
    private var targets: [ModelEntity] = []
    private var lastSpawnToken = 0
    private var lastResetToken = 0
    private var nextTargetSlot = 0
    private var hasConfiguredScene = false
    private let importedTargetOrientation = simd_quatf(angle: .pi / 2, axis: [1, 0, 0])
    private let importedTargetScale: Float = 0.48
    private let playerOrigin = SIMD3<Float>(0, 0.08, 0.2)
    private let targetSpawnSlots: [SIMD3<Float>] = [
        [-0.58, 0.18, -2.25],
        [0.58, 0.30, -2.35],
        [0.0, 0.48, -2.55],
        [-0.82, 0.42, -2.65],
        [0.82, 0.12, -2.15]
    ]

    init(frame: CGRect, session: GameSession) {
        self.gameSession = session
        super.init(frame: frame, cameraMode: .nonAR, automaticallyConfigureSession: false)
    }

    required init(frame frameRect: CGRect) {
        self.gameSession = GameSession()
        super.init(frame: frameRect, cameraMode: .nonAR, automaticallyConfigureSession: false)
    }

    @available(*, unavailable)
    dynamic required init?(coder decoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    func configureScene() {
        guard !hasConfiguredScene else { return }
        hasConfiguredScene = true

        environment.background = .color(.init(red: 0.06, green: 0.07, blue: 0.08, alpha: 1.0))
        scene.anchors.append(worldAnchor)

        addLighting()
        addArena()
        spawnTarget()
        spawnTarget()

        let tap = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        addGestureRecognizer(tap)

        let update = scene.subscribe(to: SceneEvents.Update.self) { [weak self] event in
            self?.updateProjectiles(deltaTime: event.deltaTime)
        }
        subscriptions.append(update)
    }

    func apply(spawnToken: Int, resetToken: Int) {
        if resetToken != lastResetToken {
            lastResetToken = resetToken
            resetScene()
        }

        if spawnToken != lastSpawnToken {
            lastSpawnToken = spawnToken
            spawnTarget()
        }
    }

    private func addLighting() {
        let light = DirectionalLight()
        light.light.intensity = 1800
        light.orientation = simd_quatf(angle: -.pi / 4, axis: [1, 0, 0])
        worldAnchor.addChild(light)
    }

    private func addArena() {
        if let importedArena = ImportedAssetLoader.loadModel(named: "arena_floor") {
            importedArena.name = "arena_floor"
            importedArena.position = [0, -0.42, -1.6]
            worldAnchor.addChild(importedArena)
            return
        }

        let floorMaterial = SimpleMaterial(color: UIColor(red: 0.14, green: 0.18, blue: 0.20, alpha: 1), isMetallic: false)
        let floor = ModelEntity(mesh: .generateBox(size: [3.2, 0.04, 3.2]), materials: [floorMaterial])
        floor.name = "arena_floor"
        floor.position = [0, -0.42, -1.6]
        worldAnchor.addChild(floor)

        let laneMaterial = SimpleMaterial(color: UIColor(red: 0.20, green: 0.30, blue: 0.34, alpha: 1), isMetallic: false)
        for x in stride(from: -1.2, through: 1.2, by: 0.6) {
            let lane = ModelEntity(mesh: .generateBox(size: [0.018, 0.012, 2.9]), materials: [laneMaterial])
            lane.position = [Float(x), -0.38, -1.6]
            worldAnchor.addChild(lane)
        }
    }

    private func spawnTarget() {
        let importedTarget = loadTargetAsset()
        let target = importedTarget?.model ?? makeProceduralTarget()
        if let importedTarget {
            applyImportedTargetOrientation(to: target)
            target.scale = SIMD3<Float>(repeating: importedTargetScale)
            gameSession.status = "\(importedTarget.name) ready"
        }

        let targetPosition = nextSpawnPosition()

        target.name = "target"
        target.position = targetPosition
        if importedTarget != nil {
            target.look(at: playerOrigin, from: targetPosition, relativeTo: worldAnchor)
            target.orientation *= simd_quatf(angle: .pi, axis: [0, 1, 0])
        }

        target.components.set(CollisionComponent(shapes: [.generateSphere(radius: 0.17)]))
        targets.append(target)
        worldAnchor.addChild(target)
        gameSession.activeTargets = targets.count
    }

    private func loadTargetAsset() -> LoadedTargetAsset? {
        for name in ["target_basic_textured", "target_basic"] {
            if let model = ImportedAssetLoader.loadModel(named: name) {
                return LoadedTargetAsset(name: name, model: model)
            }
        }
        return nil
    }

    private func nextSpawnPosition() -> SIMD3<Float> {
        let position = targetSpawnSlots[nextTargetSlot % targetSpawnSlots.count]
        nextTargetSlot += 1
        return position
    }

    private func applyImportedTargetOrientation(to entity: Entity) {
        guard !entity.children.isEmpty else {
            entity.orientation = importedTargetOrientation
            return
        }

        for child in entity.children {
            child.orientation *= importedTargetOrientation
        }
    }

    private func makeProceduralTarget() -> ModelEntity {
        let material = SimpleMaterial(color: UIColor(red: 0.95, green: 0.38, blue: 0.18, alpha: 1), isMetallic: false)
        return ModelEntity(mesh: .generateSphere(radius: 0.15), materials: [material])
    }

    @objc private func handleTap(_ recognizer: UITapGestureRecognizer) {
        let point = recognizer.location(in: self)
        let direction: SIMD3<Float>

        if let ray = ray(through: point) {
            direction = simd_normalize(ray.direction)
        } else {
            direction = [0, 0, -1]
        }

        fireProjectile(from: playerOrigin, direction: direction)
        if resolveScreenHit(point: point), let lastProjectile = projectiles.indices.last {
            projectiles[lastProjectile].canScore = false
        }
    }

    private func fireProjectile(from origin: SIMD3<Float>, direction: SIMD3<Float>) {
        let material = SimpleMaterial(color: UIColor(red: 0.30, green: 0.72, blue: 1.0, alpha: 1), isMetallic: false)
        let projectile = ModelEntity(mesh: .generateSphere(radius: 0.045), materials: [material])
        projectile.name = "projectile"
        projectile.position = origin
        projectile.components.set(CollisionComponent(shapes: [.generateSphere(radius: 0.05)]))

        worldAnchor.addChild(projectile)
        projectiles.append(Projectile(entity: projectile, velocity: direction * 3.4, canScore: true, age: 0))
        gameSession.recordShot()
    }

    private func updateProjectiles(deltaTime: TimeInterval) {
        guard !projectiles.isEmpty else { return }

        for index in projectiles.indices {
            projectiles[index].age += deltaTime
            projectiles[index].entity.position += projectiles[index].velocity * Float(deltaTime)
        }

        resolveHits()
        removeExpiredProjectiles()
    }

    private func resolveHits() {
        var hitProjectiles = Set<ObjectIdentifier>()
        var hitTargets = Set<ObjectIdentifier>()
        var hitScores: [ObjectIdentifier: (points: Int, zone: String)] = [:]

        for projectile in projectiles {
            guard projectile.canScore else { continue }

            for target in targets {
                let distance = simd_distance(projectile.entity.position, target.position)
                if distance < 0.22 {
                    hitProjectiles.insert(ObjectIdentifier(projectile.entity))
                    let targetID = ObjectIdentifier(target)
                    hitTargets.insert(targetID)

                    let score = scoreForHit(projectilePosition: projectile.entity.position, target: target)
                    if score.points > (hitScores[targetID]?.points ?? 0) {
                        hitScores[targetID] = score
                    }
                }
            }
        }

        guard !hitTargets.isEmpty else { return }

        for score in hitScores.values {
            gameSession.recordHit(points: score.points, zone: score.zone)
        }

        projectiles.removeAll { projectile in
            if hitProjectiles.contains(ObjectIdentifier(projectile.entity)) {
                projectile.entity.removeFromParent()
                return true
            }
            return false
        }

        targets.removeAll { target in
            if hitTargets.contains(ObjectIdentifier(target)) {
                target.removeFromParent()
                return true
            }
            return false
        }

        gameSession.activeTargets = targets.count

        spawnNextWaveIfNeeded()
    }

    private func resolveScreenHit(point: CGPoint) -> Bool {
        var bestTarget: ModelEntity?
        var bestDistance = CGFloat.greatestFiniteMagnitude

        for target in targets {
            let targetPoint = estimatedScreenPoint(for: target.position)
            let distance = hypot(point.x - targetPoint.x, point.y - targetPoint.y)
            let targetRadius = bounds.width * 0.09
            if distance < targetRadius, distance < bestDistance {
                bestDistance = distance
                bestTarget = target
            }
        }

        guard let bestTarget else { return false }

        let score = scoreForScreenHit(distance: bestDistance)
        bestTarget.removeFromParent()
        targets.removeAll { ObjectIdentifier($0) == ObjectIdentifier(bestTarget) }
        gameSession.recordHit(points: score.points, zone: score.zone)
        gameSession.activeTargets = targets.count
        spawnNextWaveIfNeeded()
        return true
    }

    private func estimatedScreenPoint(for position: SIMD3<Float>) -> CGPoint {
        CGPoint(
            x: bounds.midX + CGFloat(position.x) * bounds.width * 0.32,
            y: bounds.height * 0.416 - CGFloat(position.y - 0.30) * bounds.height * 0.18
        )
    }

    private func spawnNextWaveIfNeeded() {
        if targets.isEmpty {
            gameSession.status = "Wave cleared"
            spawnTarget()
            spawnTarget()
            spawnTarget()
        }
    }

    private func scoreForHit(projectilePosition: SIMD3<Float>, target: ModelEntity) -> (points: Int, zone: String) {
        let cameraDirection = simd_normalize(playerOrigin - target.position)
        let offset = projectilePosition - target.position
        let faceOffset = offset - simd_dot(offset, cameraDirection) * cameraDirection
        let radialDistance = simd_length(faceOffset)

        if radialDistance < 0.055 {
            return (5, "Bullseye")
        }

        if radialDistance < 0.115 {
            return (3, "Inner ring")
        }

        return (1, "Outer ring")
    }

    private func scoreForScreenHit(distance: CGFloat) -> (points: Int, zone: String) {
        let bullseyeRadius = bounds.width * 0.022
        let innerRingRadius = bounds.width * 0.048

        if distance < bullseyeRadius {
            return (5, "Bullseye")
        }

        if distance < innerRingRadius {
            return (3, "Inner ring")
        }

        return (1, "Outer ring")
    }

    private func removeExpiredProjectiles() {
        projectiles.removeAll { projectile in
            let shouldRemove = projectile.age > 2.8 || projectile.entity.position.z < -4.5
            if shouldRemove {
                projectile.entity.removeFromParent()
            }
            return shouldRemove
        }
    }

    private func resetScene() {
        projectiles.forEach { $0.entity.removeFromParent() }
        targets.forEach { $0.removeFromParent() }
        projectiles.removeAll()
        targets.removeAll()
        nextTargetSlot = 0
        gameSession.reset()
        spawnTarget()
        spawnTarget()
    }
}
