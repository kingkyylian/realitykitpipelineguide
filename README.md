# RealityKit Pipeline Demo

Small learning project for building a mobile RealityKit game pipeline with AI-assisted production.

![Ring scoring gameplay screenshot](Docs/screenshots/ring_scoring_inner_hit.jpg)

The demo starts with procedural RealityKit objects so the app can compile before any Blender assets exist. The asset pipeline is still present: export `.usdz` files from Blender into `Assets/Imported`, register them in `Tools/asset_manifest.json`, then load or replace procedural placeholders from code.

Start each session from `Docs/WORKLOG.md`. It tracks the current sprint, decisions, verification results, and the asset/code contracts we agree on.

For the teaching version of the pipeline, start from `Docs/guide.md`. It explains the full asset journey from gameplay need to USDZ export, Xcode resource import, RealityKit loading, simulator screenshot, and learning notes. A generated PDF lives at `Docs/pdf/realitykit-pipeline-guide.pdf`.

For AI agents or future handoff, start from `AGENTS.md` and `Docs/ai-handoff.md`.

## Goals

- Learn SwiftUI + RealityKit app structure.
- Practice a simple gameplay loop: spawn targets, fire projectiles, score hits.
- Keep a clean path for Blender -> USDZ -> Reality Composer Pro/Xcode.
- Teach the asset and texture pipeline as a shared system, not as isolated Blender/code roles.
- Use AI for repeatable planning, asset briefs, code tasks, and QA checklists.

## Commands

Generate the Xcode project:

```bash
rtk xcodegen generate
```

Build for iOS simulator:

```bash
rtk xcodebuild -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination 'platform=iOS Simulator,name=iPhone 16' build
```

Build with workspace-local DerivedData, which avoids writing into the default Xcode cache:

```bash
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build
```

## Current Learning State

Completed:

- Procedural RealityKit sandbox.
- First imported USDZ target: `target_basic.usdz`.
- Scale/orientation tuning with deterministic spawn slots.
- First base color textured target: `target_basic_textured.usdz`.
- UV primvar lesson: source USDZ uses `st`.
- Ring-based scoring: bullseye `+5`, inner ring `+3`, outer ring `+1`.
- Arena floor loader fallback prepared.

Active:

- Sprint 5: `arena_floor.usdz` environment asset pipeline.

Canonical course material:

- `Docs/guide.md`
- `Docs/pdf/realitykit-pipeline-guide.pdf`

## Folder Map

- `Sources/RealityKitPipelineDemo`: SwiftUI and RealityKit code.
- `Assets/Imported`: USDZ files exported from Blender or Reality Composer Pro.
- `Assets/Textures`: source or exported texture files.
- `Docs`: pipeline, budgets, checklists.
- `Docs/guide.md`: public-facing learning guide for the asset and texture pipeline.
- `Docs/ai-handoff.md`: fast orientation page for AI agents and future sessions.
- `Docs/diagrams`: Mermaid source diagrams for the guide or PDF export.
- `Docs/screenshots`: selected visual evidence used by the guide.
- `Docs/pdf`: generated PDF guide for sharing.
- `Prompts`: reusable AI prompts for Codex/Claude.
- `Tools/asset_manifest.json`: source of truth for asset names and budgets.
