# RealityKit Pipeline Demo

Small learning project for building a mobile RealityKit game pipeline with Blender-authored USDZ assets and AI-assisted production.

![Ring scoring gameplay screenshot](Docs/screenshots/ring_scoring_inner_hit.jpg)

The demo starts with procedural RealityKit objects so the app can compile before any Blender assets exist. The asset pipeline is still present: export `.usdz` files from Blender into `Assets/Imported`, register them in `Tools/asset_manifest.json`, then load or replace procedural placeholders from code.

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

## Start Here

For the teaching version of the pipeline, start from `Docs/guide.md`. It explains the full asset journey from gameplay need to USDZ export, Xcode resource import, RealityKit loading, simulator screenshot, and learning notes. A generated PDF lives at `Docs/pdf/realitykit-pipeline-guide.pdf`.

Start each work session from `Docs/WORKLOG.md`. It tracks sprints, decisions, verification results, and asset/code contracts.

For AI agents or future handoff, start from `AGENTS.md` and `Docs/ai-handoff.md`.

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

Canonical course material:

- `Docs/guide.md`
- `Docs/pdf/realitykit-pipeline-guide.pdf`

## Folder Map

- `Sources/RealityKitPipelineDemo`: SwiftUI and RealityKit code.
- `Assets/Imported`: USDZ files exported from Blender or Reality Composer Pro.
- `Assets/Source`: optional source-art handoff area; app target does not depend on it.
- `Assets/Textures`: source or exported texture files.
- `Docs`: pipeline, budgets, checklists.
- `Docs/guide.md`: public-facing learning guide for the asset and texture pipeline.
- `Docs/ai-handoff.md`: fast orientation page for AI agents and future sessions.
- `Docs/diagrams`: Mermaid source diagrams for the guide or PDF export.
- `Docs/screenshots`: selected visual evidence used by the guide.
- `Docs/pdf`: generated PDF guide for sharing.
- `Prompts`: reusable AI prompts for Codex/Claude.
- `Tools/blender`: Blender-side starter scripts and authoring notes.
- `Tools/asset_manifest.json`: source of truth for asset names and budgets.
