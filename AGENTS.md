# AGENTS.md

This repository is a teaching-oriented RealityKit asset and texture pipeline toolkit.

## Primary Goal

Build and document a command-first RealityKit pipeline toolkit that teaches contributors the full asset journey:

```text
gameplay need -> asset brief -> mesh/origin/scale -> UV/material/texture -> USDZ export -> Xcode resource bundle -> RealityKit loader -> simulator screenshot -> worklog/checklist
```

Do not treat this as a game-first app. The SwiftUI + RealityKit target shooter is a verification fixture for the CLI, skill, command, and documentation workflow. Every asset change should improve the teaching material.

## Communication

- Be concise and concrete.
- Report verification evidence, not assumptions.
- Do not say work is complete without running the relevant verification command.

## Shell Rules

- `rtk` is a project-internal CLI wrapper used by the original authors. External contributors can omit it and run the same commands directly (e.g. `xcodebuild` instead of `rtk xcodebuild`).
- Prefer `rtk` prefix if available, otherwise run commands directly.
- Use workspace-local DerivedData:

  ```bash
  rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build
  ```

- `Build/` is scratch output and is ignored.
- Public evidence belongs under `Docs/screenshots`.
- Shareable PDF belongs under `Docs/pdf`.

## Repo Map

| Path | Purpose |
| --- | --- |
| `Sources/RealityKitPipelineDemo` | SwiftUI + RealityKit app code |
| `Assets/Imported` | App-bundled USDZ assets |
| `Assets/Textures` | Texture source/export area |
| `Tools/asset_manifest.json` | Source of truth for asset status and budget |
| `Docs/guide.md` | Main teaching guide |
| `Docs/WORKLOG.md` | Sprint history, decisions, verification |
| `Docs/blender-usdz-checklist.md` | USDZ export checklist |
| `Docs/repo-release-checklist.md` | GitHub release hygiene |
| `Docs/ai-handoff.md` | Current state and next tasks for AI agents |
| `Prompts` | Reusable task prompts |

## Current Asset Loader Behavior

`GameARView` tries target assets in this order:

1. `target_basic_textured`
2. `target_basic`
3. procedural sphere fallback

If adding a new target asset, keep fallback behavior intact unless the user explicitly asks to change it.

## Asset Rules

- Asset ids use `snake_case`.
- USDZ file name should match asset id: `<asset_id>.usdz`.
- Add or update the asset in `Tools/asset_manifest.json`.
- First texture pass should use one base color texture unless the current sprint is explicitly about material maps.
- Use 512x512 texture first; move to 1024x1024 only if screenshot/device comparison proves value.
- RealityKit visual acceptance requires a simulator screenshot.

## Documentation Rules

After meaningful work, update the relevant docs:

- `Docs/WORKLOG.md` for sprint result, commands, decisions, and learning notes.
- `Docs/guide.md` when the teaching path changes.
- `Docs/blender-usdz-checklist.md` when export/UV/material lessons change.
- `Tools/asset_manifest.json` when an asset changes status or budget.
- `Docs/ai-handoff.md` when next task/current status changes.

Regenerate the guide PDF after editing `Docs/guide.md`:

```bash
rtk pandoc Docs/guide.md --standalone --embed-resources --resource-path=Docs --css Docs/guide-style.css --metadata title="RealityKit Asset and Texture Pipeline Guide" -o Build/realitykit-pipeline-guide.html
rtk weasyprint Build/realitykit-pipeline-guide.html Build/realitykit-pipeline-guide.pdf
rtk cp Build/realitykit-pipeline-guide.pdf Docs/pdf/realitykit-pipeline-guide.pdf
```

## Verification Checklist

Before claiming success:

1. Validate manifest:

   ```bash
   rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
   ```

2. Build:

   ```bash
   rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build
   ```

3. For visual/asset work, run on simulator and capture or reference a screenshot.

CoreSimulator warnings often appear in this sandbox; they are acceptable only if `xcodebuild: ok` is present.

## Do Not

- Do not commit `Build/`, DerivedData, `.DS_Store`, or local tool caches.
- Do not remove fallback behavior without explicit request.
- Do not add advanced material maps before base color behavior is verified.
- Do not change unrelated Swift/UI code while doing doc-only work.
- Do not claim a module is complete just because docs were edited.

## Recommended Next Tasks

See `Docs/ai-handoff.md`.
