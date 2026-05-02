# Learning Roadmap

## Principle

Kyylian and Mehmet both learn the whole asset/texture system. Work can be split during a session, but every handoff should end with a shared review of what changed, what broke, and how it was verified.

## Sprint 1: Running Sandbox

- Generate the Xcode project.
- Build and run on simulator.
- Understand `ContentView`, `RealityKitGameView`, and `GameARView`.
- Change spawn positions and projectile speed.

## Sprint 2: First Blender Asset

- Create `target_basic.blend`.
- Export `target_basic.usdz`.
- Add it to `Assets/Imported`.
- Replace the procedural sphere target.

## Sprint 3: First Textured Asset

- Understand what base color texture means.
- UV unwrap a simple target asset.
- Export `target_basic_textured.usdz`.
- Confirm RealityKit loads the textured asset before the fallback asset.
- Compare simulator screenshots against the untextured target.

## Sprint 4: Gameplay Loop

- Add target health.
- Add wave timer.
- Add miss penalty.
- Add simple hit VFX.

## Sprint 5: Mobile Polish

- Add sound.
- Add haptics.
- Profile with Instruments.
- Reduce asset cost until frame time is stable.

## Sprint 6: visionOS Branch

- Add a separate visionOS target.
- Move interaction from screen tap to spatial gesture.
- Test comfort, scale, and placement rules.
