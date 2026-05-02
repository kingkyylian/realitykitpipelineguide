# Repo Release Checklist

Use this before creating the public repository or pushing a first clean branch.

## Keep

- `README.md`
- `AGENTS.md`
- `project.yml`
- `Sources/RealityKitPipelineDemo`
- `Assets/Imported/*.usdz` that are part of the lesson
- `Tools/asset_manifest.json`
- `Docs/guide.md`
- `Docs/ai-handoff.md`
- `Docs/diagrams`
- `Docs/screenshots`
- `Docs/pdf/realitykit-pipeline-guide.pdf`
- `Docs/*checklist*.md`, `Docs/asset-budget.md`, `Docs/learning-roadmap.md`, `Docs/pipeline.md`
- `Prompts`

## Ignore

- `Build/DerivedData`
- transient simulator screenshots under `Build/`
- local Xcode user data
- `.DS_Store`
- editor folders

## Before Push

1. Run `rtk xcodegen generate`.
2. Run the workspace-local build:

   ```bash
   rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build
   ```

3. Validate the manifest:

   ```bash
   rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
   ```

4. Regenerate guide HTML/PDF if `Docs/guide.md` changed:

   ```bash
   rtk pandoc Docs/guide.md --standalone --embed-resources --resource-path=Docs --css Docs/guide-style.css --metadata title="RealityKit Asset and Texture Pipeline Guide" -o Build/realitykit-pipeline-guide.html
   rtk weasyprint Build/realitykit-pipeline-guide.html Build/realitykit-pipeline-guide.pdf
   rtk cp Build/realitykit-pipeline-guide.pdf Docs/pdf/realitykit-pipeline-guide.pdf
   ```

5. Confirm selected evidence files exist:

   ```bash
   rtk ls -lh Docs/screenshots Docs/pdf/realitykit-pipeline-guide.pdf
   ```

6. Review `Docs/WORKLOG.md` for stale active sprint status.
7. Review `Docs/ai-handoff.md` for stale current status or next-task guidance.

## Current Evidence Set

| File | Purpose |
| --- | --- |
| `Docs/screenshots/target_basic_frontface.png` | First imported target, front-facing |
| `Docs/screenshots/target_basic_scale_slots.jpg` | Scale and deterministic spawn tuning |
| `Docs/screenshots/target_textured_sprint3_fresh.png` | Textured target loaded in RealityKit |
| `Docs/pdf/realitykit-pipeline-guide.pdf` | Shareable guide snapshot |
