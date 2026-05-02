import AudioToolbox
import Combine
import RealityKit
import SwiftUI
import UIKit

final class GameARView: ARView {
    private struct LoadedTargetAsset {
        let name: String
        let model: ModelEntity
    }

    private struct Projectile {
        let entity: ModelEntity
        let intendedTargetID: ObjectIdentifier?
        let scoreOverride: (points: Int, zone: String)?
        var age: TimeInterval
    }

    private struct HitEffect {
        let root: Entity
        let flash: ModelEntity
        var sparks: [(entity: ModelEntity, velocity: SIMD3<Float>)]
        var age: TimeInterval
        let duration: TimeInterval
    }

    private let gameSession: GameSession
    private let worldAnchor = AnchorEntity(world: .zero)
    private var subscriptions: [Cancellable] = []
    private var projectiles: [Projectile] = []
    private var targets: [ModelEntity] = []
    private var hitEffects: [HitEffect] = []
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
        addShowcaseBackdrop()
        addArena()
        spawnTarget()
        spawnTarget()

        let tap = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        addGestureRecognizer(tap)

        let update = scene.subscribe(to: SceneEvents.Update.self) { [weak self] event in
            self?.updateProjectiles(deltaTime: event.deltaTime)
        }
        subscriptions.append(update)

        let collision = scene.subscribe(to: CollisionEvents.Began.self) { [weak self] event in
            self?.handleCollision(event)
        }
        subscriptions.append(collision)
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
        light.light.intensity = 2600
        light.orientation = simd_quatf(angle: -.pi / 4, axis: [1, 0, 0])
        worldAnchor.addChild(light)
    }

    private func addShowcaseBackdrop() {
        let backdropMaterial = makePBRMaterial(
            color: UIColor(red: 0.08, green: 0.10, blue: 0.12, alpha: 1),
            roughness: 0.82,
            metallic: 0.0
        )
        let backdrop = ModelEntity(mesh: .generateBox(size: [3.8, 1.6, 0.06]), materials: [backdropMaterial])
        backdrop.name = "showcase_backdrop"
        backdrop.position = [0, 0.18, -2.85]
        worldAnchor.addChild(backdrop)
    }

    private func addArena() {
        if let importedArena = ImportedAssetLoader.loadModel(named: "arena_floor") {
            importedArena.name = "arena_floor"
            importedArena.position = [0, -0.42, -1.6]
            worldAnchor.addChild(importedArena)
            return
        }

        let floorMaterial = makePBRMaterial(
            color: UIColor(red: 0.14, green: 0.18, blue: 0.20, alpha: 1),
            roughness: 0.9,
            metallic: 0.0
        )
        let floor = ModelEntity(mesh: .generateBox(size: [3.2, 0.04, 3.2]), materials: [floorMaterial])
        floor.name = "arena_floor"
        floor.position = [0, -0.42, -1.6]
        worldAnchor.addChild(floor)

        let laneMaterial = makePBRMaterial(
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
        target.components.set(PhysicsBodyComponent(
            shapes: [.generateSphere(radius: 0.17)],
            mass: 0,
            mode: .static
        ))
        targets.append(target)
        worldAnchor.addChild(target)
        animateTargetSpawn(target)
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
        let material = makePBRMaterial(
            color: UIColor(red: 0.95, green: 0.38, blue: 0.18, alpha: 1),
            roughness: 0.44,
            metallic: 0.0
        )
        return ModelEntity(mesh: .generateSphere(radius: 0.15), materials: [material])
    }

    @objc private func handleTap(_ recognizer: UITapGestureRecognizer) {
        let point = recognizer.location(in: self)
        guard isGameplayTap(point) else { return }

        let aim = screenAim(for: point)
        let direction: SIMD3<Float>
        let intendedTargetID: ObjectIdentifier?
        let scoreOverride: (points: Int, zone: String)?

        if let aim {
            direction = simd_normalize(aim.targetPosition - playerOrigin)
            intendedTargetID = aim.targetID
            scoreOverride = aim.score
        } else if let ray = ray(through: point) {
            direction = simd_normalize(ray.direction)
            intendedTargetID = nil
            scoreOverride = nil
        } else {
            direction = [0, 0, -1]
            intendedTargetID = nil
            scoreOverride = nil
        }

        fireProjectile(
            from: playerOrigin,
            direction: direction,
            intendedTargetID: intendedTargetID,
            scoreOverride: scoreOverride
        )
    }

    private func isGameplayTap(_ point: CGPoint) -> Bool {
        let hudBottom: CGFloat = 205
        let controlsTop = bounds.height - 170
        return point.y > hudBottom && point.y < controlsTop
    }

    private func fireProjectile(
        from origin: SIMD3<Float>,
        direction: SIMD3<Float>,
        intendedTargetID: ObjectIdentifier?,
        scoreOverride: (points: Int, zone: String)?
    ) {
        let material = makePBRMaterial(
            color: UIColor(red: 0.30, green: 0.72, blue: 1.0, alpha: 1),
            roughness: 0.26,
            metallic: 0.0
        )
        let projectile = ModelEntity(mesh: .generateSphere(radius: 0.045), materials: [material])
        projectile.name = "projectile"
        projectile.position = origin
        let shape = ShapeResource.generateSphere(radius: 0.05)
        projectile.components.set(CollisionComponent(shapes: [shape]))
        projectile.components.set(PhysicsBodyComponent(
            shapes: [shape],
            mass: 0.04,
            mode: .kinematic
        ))
        projectile.components.set(PhysicsMotionComponent(
            linearVelocity: direction * 9.0,
            angularVelocity: .zero
        ))

        worldAnchor.addChild(projectile)
        projectiles.append(Projectile(
            entity: projectile,
            intendedTargetID: intendedTargetID,
            scoreOverride: scoreOverride,
            age: 0
        ))
        gameSession.recordShot()
    }

    private func updateProjectiles(deltaTime: TimeInterval) {
        guard !projectiles.isEmpty else { return }

        for index in projectiles.indices {
            projectiles[index].age += deltaTime
        }

        resolveHits()
        updateHitEffects(deltaTime: deltaTime)
        removeExpiredProjectiles()
    }

    private func handleCollision(_ event: CollisionEvents.Began) {
        let first = ObjectIdentifier(event.entityA)
        let second = ObjectIdentifier(event.entityB)

        guard let projectile = projectiles.first(where: {
            let id = ObjectIdentifier($0.entity)
            return id == first || id == second
        }) else {
            return
        }

        let projectileID = ObjectIdentifier(projectile.entity)
        let otherID = projectileID == first ? second : first

        guard let target = targets.first(where: { ObjectIdentifier($0) == otherID }) else {
            return
        }

        if let intendedTargetID = projectile.intendedTargetID, intendedTargetID != ObjectIdentifier(target) {
            return
        }

        resolveHit(projectile: projectile, target: target)
    }

    private func resolveHits() {
        var hitProjectiles = Set<ObjectIdentifier>()
        var hitTargets = Set<ObjectIdentifier>()
        var hitScores: [ObjectIdentifier: (points: Int, zone: String)] = [:]

        for projectile in projectiles {
            for target in targets {
                let distance = simd_distance(projectile.entity.position, target.position)
                if distance < 0.22 {
                    let targetID = ObjectIdentifier(target)
                    if let intendedTargetID = projectile.intendedTargetID, intendedTargetID != targetID {
                        continue
                    }

                    hitProjectiles.insert(ObjectIdentifier(projectile.entity))
                    hitTargets.insert(targetID)

                    let score = projectile.scoreOverride ?? scoreForHit(projectilePosition: projectile.entity.position, target: target)
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

        for target in targets where hitTargets.contains(ObjectIdentifier(target)) {
            let score = hitScores[ObjectIdentifier(target)] ?? (points: 1, zone: "Outer ring")
            addHitEffect(at: target.position, points: score.points)
            playHitSound(points: score.points)
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

    private func resolveHit(projectile: Projectile, target: ModelEntity) {
        let projectileID = ObjectIdentifier(projectile.entity)
        let targetID = ObjectIdentifier(target)

        guard projectiles.contains(where: { ObjectIdentifier($0.entity) == projectileID }),
              targets.contains(where: { ObjectIdentifier($0) == targetID }) else {
            return
        }

        let score = projectile.scoreOverride ?? scoreForHit(projectilePosition: projectile.entity.position, target: target)

        gameSession.recordHit(points: score.points, zone: score.zone)
        addHitEffect(at: target.position, points: score.points)
        playHitSound(points: score.points)

        projectile.entity.removeFromParent()
        target.removeFromParent()

        projectiles.removeAll { ObjectIdentifier($0.entity) == projectileID }
        targets.removeAll { ObjectIdentifier($0) == targetID }
        gameSession.activeTargets = targets.count

        spawnNextWaveIfNeeded()
    }

    private func screenAim(for point: CGPoint) -> (
        targetID: ObjectIdentifier,
        targetPosition: SIMD3<Float>,
        score: (points: Int, zone: String)
    )? {
        var bestTarget: ModelEntity?
        var bestDistance = CGFloat.greatestFiniteMagnitude

        for target in targets {
            let targetPoint = estimatedScreenPoint(for: target.position)
            let distance = hypot(point.x - targetPoint.x, point.y - targetPoint.y)
            let targetRadius = bounds.width * 0.10
            if distance < targetRadius, distance < bestDistance {
                bestDistance = distance
                bestTarget = target
            }
        }

        guard let bestTarget else { return nil }

        return (ObjectIdentifier(bestTarget), bestTarget.position, scoreForScreenHit(distance: bestDistance))
    }

    private func estimatedScreenPoint(for position: SIMD3<Float>) -> CGPoint {
        CGPoint(
            x: bounds.midX + CGFloat(position.x) * bounds.width * 0.32,
            y: bounds.height * 0.416 - CGFloat(position.y - 0.30) * bounds.height * 0.18
        )
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

    private func removeExpiredProjectiles() {
        projectiles.removeAll { projectile in
            let shouldRemove = projectile.age > 2.8 || projectile.entity.position.z < -4.5
            if shouldRemove {
                projectile.entity.removeFromParent()
            }
            return shouldRemove
        }
    }

    private func addHitEffect(at position: SIMD3<Float>, points: Int) {
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

    private func animateTargetSpawn(_ target: Entity) {
        guard #available(iOS 26.0, *) else {
            return
        }

        let originalScale = target.scale
        target.scale = originalScale * 0.18
        Entity.animate(.spring(response: 0.34, dampingFraction: 0.72)) {
            target.scale = originalScale
        }
    }

    private func playHitSound(points: Int) {
        switch points {
        case 5:
            AudioServicesPlaySystemSound(1521)  // haptic pop — bullseye
        case 3:
            AudioServicesPlaySystemSound(1520)  // haptic peek — inner ring
        default:
            AudioServicesPlaySystemSound(1104)  // tock — outer ring
        }
    }

    private func makePBRMaterial(color: UIColor, roughness: Float, metallic: Float) -> PhysicallyBasedMaterial {
        var material = PhysicallyBasedMaterial()
        material.baseColor = .init(tint: color)
        material.roughness = .init(floatLiteral: roughness)
        material.metallic = .init(floatLiteral: metallic)
        return material
    }

    private func updateHitEffects(deltaTime: TimeInterval) {
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

    private func resetScene() {
        projectiles.forEach { $0.entity.removeFromParent() }
        targets.forEach { $0.removeFromParent() }
        hitEffects.forEach { $0.root.removeFromParent() }
        projectiles.removeAll()
        targets.removeAll()
        hitEffects.removeAll()
        nextTargetSlot = 0
        gameSession.reset()
        spawnTarget()
        spawnTarget()
    }
}
