# RealityKit Pipeline Demo

Build a tiny iOS RealityKit game while learning the real Blender -> USDZ -> Xcode -> RealityKit asset pipeline.

Most RealityKit tutorials stop at code. This repo treats asset production as part of the game loop: each Blender/USDZ asset has a manifest entry, mobile budget, loader contract, simulator screenshot, and learning note.

![RealityKit pipeline gameplay demo](Docs/screenshots/demo.gif)

## What You Learn

- Build a SwiftUI + RealityKit game prototype.
- Generate and import Blender-authored USDZ assets.
- Keep asset scale, origin, UVs, materials, and texture budgets under control.
- Connect visual texture design to gameplay with ring-based scoring.
- Verify every asset with manifest checks, builds, screenshots, and worklog notes.

## Showcase

| Textured target scoring | Imported arena floor |
| --- | --- |
| ![Ring scoring inner hit](Docs/screenshots/ring_scoring_inner_hit.jpg) | ![Imported arena floor](Docs/screenshots/arena_floor_imported.jpg) |

The app starts with procedural RealityKit fallbacks so it can compile before any custom art exists. The asset pipeline then replaces placeholders with USDZ files exported from Blender into `Assets/Imported`.

## Quick Start

### Prerequisites

- macOS with Xcode installed.
- XcodeGen installed and available as `xcodegen`.
- Blender 4.x for authoring or regenerating art assets.
- Optional for guide PDF export: `pandoc` and `weasyprint`.

### Generate and Build

```bash
xcodegen generate
xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination 'generic/platform=iOS Simulator' -derivedDataPath Build/DerivedData build
```

To run visually, open `RealityKitPipelineDemo.xcodeproj` in Xcode and choose an iOS simulator.

### First Asset Loop

1. Read `Tools/asset_manifest.json` to pick an asset id and budget.
2. Author or regenerate an asset with Blender. A starter script lives at `Tools/blender/create_arena_floor.py`.
3. Export the final `.usdz` to `Assets/Imported/<asset_id>.usdz`.
4. Run `xcodegen generate`, build, and capture a simulator screenshot.
5. Record the result in `Docs/WORKLOG.md`.

### About `rtk`

Some internal docs and worklog entries use commands prefixed with `rtk`. That is this project's local agent wrapper, not a public dependency. If you cloned the repo normally, run the same command without `rtk`.

## Use as a Codex Skill

This repo includes a portable Codex skill at `Skills/realitykit-pipeline-guide`. Install it locally with:

```bash
make install-skill
```

After installing, ask Codex to use `realitykit-pipeline-guide` for RealityKit asset pipeline, gameplay, documentation, or release tasks. The skill points agents to the right workflow, contracts, commands, and repo gates without rereading the whole guide every time.

## Start Here

For the teaching version of the pipeline, start from `Docs/guide.md`. It explains the full asset journey from gameplay need to USDZ export, Xcode resource import, RealityKit loading, simulator screenshot, and learning notes. A generated PDF lives at `Docs/pdf/realitykit-pipeline-guide.pdf`.

For reusable production practice, use `Docs/production-playbook.md`. It defines the feature brief, asset/runtime contract, quality gates, review checklist, and definition of done for future RealityKit games.

For starting a new game from this repo's lessons, use `Docs/new-game-startup.md`.

Start each work session from `Docs/WORKLOG.md`. It tracks sprints, decisions, verification results, and asset/code contracts.

For AI agents or future handoff, start from `AGENTS.md` and `Docs/ai-handoff.md`.

## GitHub Metadata

Suggested repo description:

```text
Learn a complete Blender -> USDZ -> RealityKit asset pipeline through a tiny SwiftUI iOS game.
```

Suggested topics:

```text
realitykit, swift, swiftui, ios, ios-game, blender, usdz, game-development, 3d-pipeline, asset-pipeline
```

## Goals

- Learn SwiftUI + RealityKit app structure.
- Practice a simple gameplay loop: spawn targets, fire projectiles, score hits.
- Keep a clean path for Blender -> USDZ -> Xcode -> RealityKit.
- Teach the asset and texture pipeline as a shared system, not as isolated Blender/code roles.
- Use AI for repeatable planning, asset briefs, code tasks, and QA checklists.

## Common Commands

Generate the Xcode project:

```bash
xcodegen generate
```

Build for iOS simulator:

```bash
xcodebuild -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination 'platform=iOS Simulator,name=iPhone 16' build
```

Build with workspace-local DerivedData, which avoids writing into the default Xcode cache:

```bash
xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination 'generic/platform=iOS Simulator' -derivedDataPath Build/DerivedData build
```

Validate the asset manifest:

```bash
node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
```

Run the pipeline doctor:

```bash
make doctor
```

Scaffold a new asset:

```bash
make new-asset id=enemy_drone type=gameplay_target
```

Run the Blender build script for an asset:

```bash
make build-asset id=enemy_drone
```

If Blender is not on `PATH`, provide it explicitly:

```bash
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender make build-asset id=enemy_drone
```

Accept a built asset with required visual evidence:

```bash
make accept-asset id=enemy_drone screenshot=Docs/screenshots/enemy_drone_imported.jpg
```

Regenerate the guide PDF:

```bash
pandoc Docs/guide.md --standalone --embed-resources --resource-path=Docs --css Docs/guide-style.css --metadata title="RealityKit Asset and Texture Pipeline Guide" -o Build/realitykit-pipeline-guide.html
weasyprint Build/realitykit-pipeline-guide.html Build/realitykit-pipeline-guide.pdf
cp Build/realitykit-pipeline-guide.pdf Docs/pdf/realitykit-pipeline-guide.pdf
```

## Current Learning State

Completed:

- Procedural RealityKit sandbox.
- First imported USDZ target: `target_basic.usdz`.
- Scale/orientation tuning with deterministic spawn slots.
- First base color textured target: `target_basic_textured.usdz`.
- UV primvar lesson: source USDZ uses `st`.
- Ring-based scoring: bullseye `+5`, inner ring `+3`, outer ring `+1`.
- Arena floor import: `arena_floor.usdz`.
- Wave loop: HUD shows current wave and cleared target progress.

Canonical course material:

- `Docs/guide.md`
- `Docs/pdf/realitykit-pipeline-guide.pdf`
- `Docs/production-playbook.md`
- `Docs/new-game-startup.md`

Reusable templates:

- `Prompts/asset-brief.md`
- `Prompts/game-feature-brief.md`
- `Prompts/codex-task.md`
- `Prompts/qa-checklist.md`
- `Skills/realitykit-pipeline-guide`

## Folder Map

- `Sources/RealityKitPipelineDemo`: SwiftUI and RealityKit code.
- `Assets/Imported`: USDZ files exported from Blender or Reality Composer Pro.
- `Assets/Source`: optional source-art handoff area; app target does not depend on it.
- `Assets/Textures`: source or exported texture files.
- `Docs`: pipeline, budgets, checklists.
- `Docs/guide.md`: public-facing learning guide for the asset and texture pipeline.
- `Docs/production-playbook.md`: reusable production gates and team workflow.
- `Docs/new-game-startup.md`: checklist for starting a future RealityKit game.
- `Docs/features`: feature briefs and acceptance contracts.
- `Docs/ai-handoff.md`: fast orientation page for AI agents and future sessions.
- `Docs/diagrams`: Mermaid source diagrams for the guide or PDF export.
- `Docs/screenshots`: selected visual evidence used by the guide.
- `Docs/pdf`: generated PDF guide for sharing.
- `Prompts`: reusable AI prompts for Codex/Claude.
- `Skills/realitykit-pipeline-guide`: installable Codex skill for this pipeline.
- `Tools/blender`: Blender-side starter scripts and authoring notes.
- `Tools/accept_asset.py`: marks a built asset imported only when screenshot evidence is provided.
- `Tools/asset_manifest.json`: source of truth for asset names and budgets.
- `Tools/build_asset.py`: runs `Tools/blender/create_<id>.py` and verifies the expected USDZ exists.
- `Tools/new_asset.py`: creates a manifest entry, asset brief, and Blender starter script for a new asset.
- `Tools/pipeline_doctor.py`: static pipeline consistency checker for manifests, docs, links, CI paths, and skill packaging.
