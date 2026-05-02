---
name: realitykit-pipeline-guide
description: Build, review, or extend RealityKit iOS game projects that use a Blender -> USDZ -> Xcode -> RealityKit asset pipeline. Use when working on imported USDZ assets, asset manifests, mobile 3D budgets, RealityKit loaders/fallbacks, gameplay features tied to assets, simulator screenshot evidence, production playbooks, or teaching/handoff docs for this repository style.
---

# RealityKit Pipeline Guide

Use this skill to keep RealityKit game work tied to an asset pipeline contract, not just code changes.

## Quick Workflow

1. Identify the task type:
   - Asset import or texture work
   - Gameplay feature
   - Visual/game-feel polish
   - Documentation or release polish
   - New game startup
2. Confirm the working directory is an RKP repo before editing:
   - `Tools/rkp.py` must exist.
   - `Tools/asset_manifest.json` must exist.
   - If either is missing, do not create a fake/minimal pipeline. Tell the user this directory is not an RKP repo and ask them to `cd` into the repo, clone the template, or explicitly request a bootstrap.
3. Read only the needed reference:
   - `references/workflows.md` for task routing and implementation flow.
   - `references/contracts.md` for asset/gameplay/release acceptance gates.
   - `references/commands.md` for build, validation, PDF, and install commands.
   - `references/slash-commands.md` for `/rkp` slash command usage and Codex equivalents.
4. Preserve the repo contract:
   - Prefer `python3 Tools/rkp.py status` for first orientation.
   - Imported assets live in `Assets/Imported`.
   - Asset metadata lives in `Tools/asset_manifest.json`.
   - Public evidence lives in `Docs/screenshots`.
   - Lessons and decisions go in `Docs/WORKLOG.md`.
   - Future-agent context goes in `Docs/ai-handoff.md` when project state changes.
5. Verify before claiming completion.

## Default Rules

- Keep procedural fallbacks unless the task explicitly removes them.
- Keep XcodeGen as the project generation source of truth.
- Never scaffold ad hoc `Tools/`, `Assets/`, or `Docs/` folders in an empty directory as a substitute for the RKP repo.
- Prefer `python3 Tools/rkp.py release-check` for local verification.
- For visual changes, run the simulator and capture or reference screenshot evidence.
- Do not use a latest Apple API if the public CI Xcode baseline cannot compile it.
- Keep docs canonical: update `Docs/guide.md` for teaching, `Docs/production-playbook.md` for production gates, and `Docs/new-game-startup.md` for future-game startup guidance.

## Useful Script

Run this from the repo root for a fast structure check:

```bash
make doctor
```

For a smaller skill-package-only check, run:

```bash
python3 Skills/realitykit-pipeline-guide/scripts/check_repo.py
```

These checks do not replace Xcode build verification.
