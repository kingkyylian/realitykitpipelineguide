# RealityKit Pipeline Demo

Small learning project for building a mobile RealityKit game pipeline with AI-assisted production.

The demo starts with procedural RealityKit objects so the app can compile before any Blender assets exist. The asset pipeline is still present: export `.usdz` files from Blender into `Assets/Imported`, register them in `Tools/asset_manifest.json`, then load or replace procedural placeholders from code.

Start each session from `Docs/WORKLOG.md`. It tracks the current sprint, decisions, verification results, and the asset/code contracts we agree on.

For the teaching version of the pipeline, start from `Docs/guide.md`. It explains the full asset journey from gameplay need to USDZ export, Xcode resource import, RealityKit loading, simulator screenshot, and learning notes. A generated PDF lives at `Docs/pdf/realitykit-pipeline-guide.pdf`.

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

## First Learning Sprint

1. Run the procedural sandbox.
2. Make one Blender target asset with correct scale and origin.
3. Export it as `.usdz` to `Assets/Imported/target_basic.usdz`.
4. Add it to `Tools/asset_manifest.json`.
5. Run `rtk xcodegen generate` after adding new resource files.
6. Build the app. The loader searches `target_basic.usdz` in the app bundle and `Imported/`.
7. Profile frame time after adding real assets.

## Folder Map

- `Sources/RealityKitPipelineDemo`: SwiftUI and RealityKit code.
- `Assets/Imported`: USDZ files exported from Blender or Reality Composer Pro.
- `Assets/Textures`: source or exported texture files.
- `Docs`: pipeline, budgets, checklists.
- `Docs/guide.md`: public-facing learning guide for the asset and texture pipeline.
- `Docs/diagrams`: Mermaid source diagrams for the guide or PDF export.
- `Docs/screenshots`: selected visual evidence used by the guide.
- `Docs/pdf`: generated PDF guide for sharing.
- `Prompts`: reusable AI prompts for Codex/Claude.
- `Tools/asset_manifest.json`: source of truth for asset names and budgets.
