# Repo Release Checklist

Use this before pushing a public branch or creating a release.

Next release candidate: `v0.2.0`

Do not push, tag, or publish without explicit user approval.

## Keep

- `README.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `Makefile`
- `AGENTS.md`
- `.github/workflows/ci.yml`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE`
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
- `Docs/github-showcase.md`
- `Docs/releases/*.md`
- `Prompts`
- `Tools/blender`

## Ignore

- `Build/DerivedData`
- transient simulator screenshots under `Build/`
- local Xcode user data
- `.DS_Store`
- editor folders

## Before Push or Release

1. Run `xcodegen generate` or `make generate`.
2. Run the workspace-local build:

   ```bash
   xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination 'generic/platform=iOS Simulator' -derivedDataPath Build/DerivedData build
   ```

3. Validate the manifest:

   ```bash
   node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
   ```

4. Regenerate guide HTML/PDF if `Docs/guide.md` changed:

   ```bash
   make guide
   ```

5. Confirm selected evidence files exist:

   ```bash
   ls -lh Docs/screenshots Docs/pdf/realitykit-pipeline-guide.pdf
   ```

6. Review `Docs/WORKLOG.md` for stale active sprint status.
7. Review `Docs/ai-handoff.md` for stale current status or next-task guidance.
8. Set GitHub description and topics from `Docs/github-showcase.md`.
9. Review `CHANGELOG.md` and `Docs/releases/v0.2.0.md` for stale release notes.
10. Create `v0.2.0` release from `Docs/releases/v0.2.0.md` after push, CI, and explicit release approval.

## Current Evidence Set

| File | Purpose |
| --- | --- |
| `Docs/screenshots/target_basic_frontface.png` | First imported target, front-facing |
| `Docs/screenshots/target_basic_scale_slots.jpg` | Scale and deterministic spawn tuning |
| `Docs/screenshots/target_textured_sprint3_fresh.png` | Textured target loaded in RealityKit |
| `Docs/screenshots/ring_scoring_inner_hit.jpg` | Ring texture connected to gameplay scoring |
| `Docs/screenshots/arena_floor_fallback_ready.jpg` | Arena floor fallback works before imported floor asset exists |
| `Docs/screenshots/arena_floor_imported.jpg` | Imported arena floor is visible without hurting target readability |
| `Docs/pdf/realitykit-pipeline-guide.pdf` | Shareable guide snapshot |
