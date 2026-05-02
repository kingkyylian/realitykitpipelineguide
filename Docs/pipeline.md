# RealityKit Learning Pipeline

This project uses a small loop that can be repeated for every feature or asset.

## 1. Design Brief

Write one page before building:

- Player action
- Win/fail condition
- Required entities
- Required animations
- Sound needs
- Performance risk

Keep the first version playable in one day.

## 2. Learning Split

Kyylian and Mehmet should learn the whole path, not separate into permanent Blender/code roles. Split work only to move faster, then review each handoff together.

Useful stations:

- Design station: gameplay intent, visual target, asset brief, QA checklist.
- Asset station: mesh, origin, UV, material, texture, USDZ export.
- RealityKit station: bundle import, loader behavior, scale, orientation, collision, material verification.
- Documentation station: checklist updates, screenshots, decisions, budget notes.

Every AI output or manual experiment must become one of these:

- Code change
- Asset brief
- Test checklist
- Design decision
- Learning note

## 3. Blender Asset Pass

Create the simplest asset that proves the pipeline. The tool can be Blender, Blender MCP, or another generator, but the learning target is the same:

1. Model in meters.
2. Apply transforms.
3. Set origin intentionally.
4. UV unwrap.
5. Assign one or two materials.
6. Add the minimum texture set needed for the current lesson.
7. Export `.usdz`.
8. Drop into `Assets/Imported`.
9. Register in `Tools/asset_manifest.json`.
10. Run `rtk xcodegen generate` so Xcode sees the new resource.
11. Load in RealityKit or Reality Composer Pro.

## 4. RealityKit Integration

Start with procedural placeholders. Replace one object at a time with imported assets.

Recommended order:

1. Target mesh
2. Arena floor
3. Projectile
4. UI sound effects
5. Hit animation
6. Spawn animation

## 5. Verification

For every vertical slice:

- App builds in Xcode.
- Scene loads without missing resources.
- Tap input works.
- Hit detection works.
- Reset returns to clean state.
- No obvious frame drops on target device.

## 6. Production Rule

Do not add more art detail until the asset can travel from Blender to the running app cleanly.
