# AI Handoff

This file is the fast orientation page for any AI agent opening the repository.

## Project Status

Current state: local Git repo on `main`. Use `git log --oneline --decorate -6` for the latest commit list instead of relying on a fixed count in this document.

No remote is configured yet.

## What This Project Is

RealityKitPipelineDemo is a small iOS RealityKit learning project. It teaches a complete asset and texture pipeline:

```text
Blender / asset generation -> USDZ -> XcodeGen resource bundle -> RealityKit import -> simulator screenshot -> documented learning note
```

It is not only a game prototype. It is also a teaching artifact for Kyylian and Mehmet.

## Completed Learning Modules

| Module | Status | Evidence |
| --- | --- | --- |
| First USDZ import | Complete | `Assets/Imported/target_basic.usdz`, `Docs/screenshots/target_basic_frontface.png` |
| Scale/orientation tuning | Complete | `Docs/screenshots/target_basic_scale_slots.jpg` |
| Base color textured asset | Complete | `Assets/Imported/target_basic_textured.usdz`, `Docs/screenshots/target_textured_sprint3_fresh.png` |
| UV primvar lesson | Complete | `Docs/blender-usdz-checklist.md`, `Docs/WORKLOG.md` |
| Ring-based scoring | Complete | `Docs/screenshots/ring_scoring_inner_hit.jpg` |
| Arena floor fallback | Complete | `Docs/screenshots/arena_floor_fallback_ready.jpg` |
| Arena floor import | Complete | `Assets/Imported/arena_floor.usdz`, `Docs/screenshots/arena_floor_imported.jpg` |
| Teaching guide | Strong first version | `Docs/guide.md`, `Docs/pdf/realitykit-pipeline-guide.pdf` |

## Planned Learning Modules

Recommended order:

1. GitHub repo polish: README, LICENSE, CI, issue/PR templates. Basic public onboarding exists; next polish should refine examples and source-art coverage.
2. Module 4: Texture Maps and Material Response.
3. Module 5: Performance and Mobile Asset Budget.
4. Module 6: Collision, VFX, and Gameplay Feel. Ring scoring is started; VFX/audio remain.
5. Module 7: Environment Asset and Texture Atlas. Arena floor import is complete; future work can expand atlas/tiling variants.
6. Module 8: Repo and Authoring Workflow.

## Current Recommended Next Task

If the user asks to make the repository look professional on GitHub, do this next:

1. Add a real source `.blend` for one teaching asset or confirm script-generated sources are enough.
2. Add README badges after the GitHub remote exists.
3. Add a short demo GIF or hosted video link.
4. Set GitHub repo description/topics from `Docs/github-showcase.md`.
5. Create the `v0.1.0` tag/release from `CHANGELOG.md`.
6. Expand `Tools/blender` with target asset generation/export scripts.
7. Add a first-good-issue list for learners.

If the user asks to continue education content, do this next:

1. Start Module 4: Texture Maps and Material Response.
2. Define a roughness/material value comparison asset.
3. Keep base color pipeline intact.
4. Add screenshot-based comparison.

## Key Files to Read First

1. `AGENTS.md`
2. `README.md`
3. `Docs/guide.md`
4. `Docs/WORKLOG.md`
5. `Tools/asset_manifest.json`
6. `Sources/RealityKitPipelineDemo/GameARView.swift`

## Known Implementation Details

- `GameARView` uses non-AR RealityKit mode.
- `GameARView` loads `target_basic_textured` first, then `target_basic`, then procedural fallback.
- Imported target scale is normalized with `0.48`.
- Spawn positions are deterministic slots for teaching/debugging.
- Ring scoring is deterministic screen-space scoring: bullseye `+5`, inner ring `+3`, outer ring `+1`.
- `GameARView.addArena()` tries `arena_floor` first, then falls back to procedural floor + lane markers.
- `arena_floor.usdz` is imported and manifest status is `imported`.
- Showcase polish exists: darker backdrop, readable HUD, reticle overlay, projectile-delayed scoring, and hit spark VFX.
- Modern RealityKit pass exists: physics bodies, collision events, PBR helper materials, and SDK-stable target spawn animation with `move(to:relativeTo:duration:)`.
- Public onboarding includes `README.md`, `LICENSE`, `CONTRIBUTING.md`, `Makefile`, GitHub Actions, issue templates, and `Tools/blender`.
- `Build/` is ignored scratch output.
- Public screenshots are copied to `Docs/screenshots`.

## Verification Commands

Manifest:

```bash
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
```

Build:

```bash
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build
```

Guide PDF:

```bash
rtk pandoc Docs/guide.md --standalone --embed-resources --resource-path=Docs --css Docs/guide-style.css --metadata title="RealityKit Asset and Texture Pipeline Guide" -o Build/realitykit-pipeline-guide.html
rtk weasyprint Build/realitykit-pipeline-guide.html Build/realitykit-pipeline-guide.pdf
rtk cp Build/realitykit-pipeline-guide.pdf Docs/pdf/realitykit-pipeline-guide.pdf
```

## Documentation Contract

If you change code, assets, or teaching flow:

- update `Docs/WORKLOG.md`
- update `Tools/asset_manifest.json` if assets changed
- update `Docs/guide.md` if the learning path changed
- regenerate `Docs/pdf/realitykit-pipeline-guide.pdf` if guide changed
- update this file if the next task changes

## Git Notes

- Current branch: `main`
- Keep commits focused.
- Do not push unless the user explicitly asks.
- Do not commit ignored scratch output.
