# New RealityKit Game Startup Checklist

Use this when starting a new RealityKit game from the lessons in this repo. It is intentionally practical: clone the patterns, rename the domain, and keep the verification discipline.

## Phase 0: Pick the Game Shape

Write one paragraph:

- Player fantasy:
- Core action:
- Camera style:
- Session length:
- Main asset classes:
- First playable goal:

Example:

```text
Player fantasy: A clean mobile target range.
Core action: Tap to shoot moving targets.
Camera style: Fixed non-AR RealityKit camera.
Session length: 60 seconds.
Main asset classes: target, projectile, arena floor, feedback VFX.
First playable goal: Spawn three targets, shoot them, score hits by ring.
```

## Phase 1: Establish Runtime Skeleton

Required before custom art:

- SwiftUI entry screen or direct game view.
- RealityKit scene root.
- Camera/framing contract.
- Procedural placeholder assets.
- Input path.
- GameSession state object.
- Reset path.
- Local build command.

Acceptance:

```bash
make release-check
```

## Phase 2: Define Asset Classes

Create a table before making assets:

| Asset class | Runtime role | Fallback | Budget | First id |
| --- | --- | --- | ---: | --- |
| Target | Score object | Procedural rings | 1,500 tris / 512 texture | `target_basic` |
| Floor | Spatial reference | Procedural grid | 800 tris / 512 texture | `arena_floor` |
| Projectile | Feedback object | Procedural sphere | 400 tris / procedural material | `projectile_basic` |

Rules:

- Do not start with hero art.
- Do not add normal/roughness maps until base color is proven.
- Do not remove procedural fallback until imported replacement is stable.

## Phase 3: First Asset Vertical Slice

The first imported asset should be small and gameplay-relevant.

Required steps:

1. Write asset brief.
2. Add manifest entry.
3. Author mesh with correct origin and scale.
4. Export USDZ.
5. Add to `Assets/Imported`.
6. Generate project.
7. Build.
8. Load through RealityKit.
9. Capture simulator screenshot.
10. Write worklog lesson.

Do not proceed to asset two until asset one reaches quality level 5 in `Docs/guide.md`.

## Phase 4: Gameplay Before Polish

Before adding more art, make sure the player can:

- start or reset the session
- perform the core action
- get clear hit/miss feedback
- understand score
- repeat the loop

The first playable should look simple but behave honestly.

## Phase 5: Production Hardening

Add these only after the vertical slice works:

- Wave state
- Result screen
- High score
- Settings
- Device profiling
- Audio/haptic settings
- Release notes

## Reusable Folder Map

```text
Sources/<GameName>/
Assets/Imported/
Assets/Source/
Assets/Textures/
Docs/screenshots/
Docs/WORKLOG.md
Docs/production-playbook.md
Tools/asset_manifest.json
Tools/blender/
Prompts/
```

## First Week Plan

| Day | Outcome |
| ---: | --- |
| 1 | Runtime skeleton builds and launches. |
| 2 | Procedural placeholder gameplay loop works. |
| 3 | First imported USDZ loads. |
| 4 | Scale/origin/orientation tuned with screenshot. |
| 5 | First texture works and is tied to gameplay readability. |
| 6 | CI and release checklist green. |
| 7 | README, worklog, and guide reflect the real project state. |

## Stop Conditions

Pause and fix the system if:

- The app only works on one machine.
- A new asset requires manual Xcode project editing.
- The README command path differs from CI.
- Screenshot evidence no longer matches current behavior.
- Only one person understands the asset pipeline.

