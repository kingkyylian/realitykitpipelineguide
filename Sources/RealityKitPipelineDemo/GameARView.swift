import AudioToolbox
import Combine
import RealityKit
import SwiftUI
import UIKit

final class GameARView: ARView {
    private struct Projectile {
        let entity: ModelEntity
        let velocity: SIMD3<Float>
        let intendedTargetID: ObjectIdentifier?
        let scoreOverride: (points: Int, zone: String)?
        var age: TimeInterval
    }

    private let gameSession: GameSession
    private let worldAnchor = AnchorEntity(world: .zero)
    private var targetFactory = TargetFactory()
    private var hitEffectSystem = HitEffectSystem()
    private var subscriptions: [Cancellable] = []
    private var projectiles: [Projectile] = []
    private var targets: [ModelEntity] = []
    private var lastSpawnToken = 0
    private var lastResetToken = 0
    private var hasConfiguredScene = false
    private let playerOrigin = SIMD3<Float>(0, 0.08, 0.2)

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
        ArenaBuilder.addShowcaseBackdrop(to: worldAnchor)
        ArenaBuilder.addArena(to: worldAnchor)
        gameSession.startRun(targetCount: targetCountForCurrentWave())
        spawnWaveTargets()

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

        if ProcessInfo.processInfo.arguments.contains("--demo-mode") {
            scheduleDemoPlayback()
        }
    }

    func apply(spawnToken: Int, resetToken: Int) {
        if resetToken != lastResetToken {
            lastResetToken = resetToken
            resetScene()
        }

        if spawnToken != lastSpawnToken {
            lastSpawnToken = spawnToken
            spawnTarget()
            gameSession.addTargetToCurrentWave()
        }
    }

    private func addLighting() {
        let light = DirectionalLight()
        light.light.intensity = 2600
        light.orientation = simd_quatf(angle: -.pi / 4, axis: [1, 0, 0])
        worldAnchor.addChild(light)
    }

    private func spawnTarget() {
        let spawnedTarget = targetFactory.makeTarget(playerOrigin: playerOrigin, relativeTo: worldAnchor)
        let target = spawnedTarget.model
        if let assetName = spawnedTarget.assetName {
            gameSession.status = "\(assetName) ready"
        }

        targets.append(target)
        worldAnchor.addChild(target)
        animateTargetSpawn(target)
        gameSession.activeTargets = targets.count
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
        let material = RealityMaterials.pbr(
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

        worldAnchor.addChild(projectile)
        projectiles.append(Projectile(
            entity: projectile,
            velocity: direction * 9.0,
            intendedTargetID: intendedTargetID,
            scoreOverride: scoreOverride,
            age: 0
        ))
        gameSession.recordShot()
    }

    private func scheduleDemoPlayback() {
        let steps: [(delay: TimeInterval, targetIndex: Int)] = [
            (1.60, 0),
            (3.20, 1),
            (4.80, 0),
        ]

        for step in steps {
            DispatchQueue.main.asyncAfter(deadline: .now() + step.delay) { [weak self] in
                self?.fireDemoProjectile(atTargetIndex: step.targetIndex)
            }
        }
    }

    private func fireDemoProjectile(atTargetIndex index: Int) {
        guard targets.indices.contains(index) else { return }

        let target = targets[index]
        let direction = simd_normalize(target.position - playerOrigin)
        fireProjectile(
            from: playerOrigin,
            direction: direction,
            intendedTargetID: ObjectIdentifier(target),
            scoreOverride: (points: 5, zone: "Bullseye")
        )
    }

    private func updateProjectiles(deltaTime: TimeInterval) {
        if !projectiles.isEmpty {
            for index in projectiles.indices {
                projectiles[index].age += deltaTime
                projectiles[index].entity.position += projectiles[index].velocity * Float(deltaTime)
            }

            resolveHits()
            removeExpiredProjectiles()
        }

        hitEffectSystem.update(deltaTime: deltaTime)
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
            hitEffectSystem.add(at: target.position, points: score.points, playerOrigin: playerOrigin, worldAnchor: worldAnchor)
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

        gameSession.recordTargetsDestroyed(hitTargets.count)
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
        hitEffectSystem.add(at: target.position, points: score.points, playerOrigin: playerOrigin, worldAnchor: worldAnchor)
        playHitSound(points: score.points)

        projectile.entity.removeFromParent()
        target.removeFromParent()

        projectiles.removeAll { ObjectIdentifier($0.entity) == projectileID }
        targets.removeAll { ObjectIdentifier($0) == targetID }
        gameSession.recordTargetsDestroyed(1)
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
        TargetScoring.screenHit(distance: distance, boundsWidth: bounds.width)
    }

    private func spawnNextWaveIfNeeded() {
        if targets.isEmpty {
            gameSession.advanceWave(targetCount: targetCountForNextWave())
            spawnWaveTargets()
        }
    }

    private func targetCountForCurrentWave() -> Int {
        WaveRules.targetCountForCurrentWave(wave: gameSession.wave, maxTargets: targetFactory.maxSpawnSlots)
    }

    private func targetCountForNextWave() -> Int {
        WaveRules.targetCountForNextWave(wave: gameSession.wave, maxTargets: targetFactory.maxSpawnSlots)
    }

    private func spawnWaveTargets() {
        for _ in 0..<targetCountForCurrentWave() {
            spawnTarget()
        }
    }

    private func scoreForHit(projectilePosition: SIMD3<Float>, target: ModelEntity) -> (points: Int, zone: String) {
        let cameraDirection = simd_normalize(playerOrigin - target.position)
        let offset = projectilePosition - target.position
        let faceOffset = offset - simd_dot(offset, cameraDirection) * cameraDirection
        let radialDistance = simd_length(faceOffset)

        return TargetScoring.spatialHit(radialDistance: radialDistance)
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

    private func animateTargetSpawn(_ target: Entity) {
        let originalScale = target.scale
        let finalTransform = target.transform
        target.scale = originalScale * 0.18
        target.move(to: finalTransform, relativeTo: target.parent, duration: 0.24)
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

    private func resetScene() {
        projectiles.forEach { $0.entity.removeFromParent() }
        targets.forEach { $0.removeFromParent() }
        projectiles.removeAll()
        targets.removeAll()
        hitEffectSystem.removeAll()
        targetFactory.resetSpawnSlots()
        gameSession.reset()
        spawnWaveTargets()
    }
}
