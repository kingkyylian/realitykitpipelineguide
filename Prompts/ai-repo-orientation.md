# AI Repo Orientation Prompt

Use this prompt when asking a new AI agent to continue work on this repository.

```text
You are working in RealityKitPipelineDemo.

First read:
- AGENTS.md
- Docs/ai-handoff.md
- README.md
- Docs/guide.md
- Docs/WORKLOG.md
- Tools/asset_manifest.json

Project goal:
This is both a small iOS RealityKit game prototype and a teaching project for the full asset/texture pipeline. Do not treat it as code-only. Any asset or pipeline change must improve the educational material.

Current completed modules:
- first USDZ import
- target scale/orientation tuning
- first base color textured USDZ
- UV primvar lesson (`st`)
- professional guide PDF

Before claiming success:
- validate manifest
- run workspace-local xcodebuild
- update docs/worklog if behavior or learning content changed
- regenerate guide PDF if Docs/guide.md changed

Do not commit or include Build/, DerivedData, .DS_Store, or local caches.
Ask before pushing to remote.
```
