# Commands

Run from the repository root.

## Generate and Build

```bash
make generate
make build
```

## Primary Pipeline CLI

```bash
python3 Tools/rkp.py status
python3 Tools/rkp.py doctor
python3 Tools/rkp.py new-asset enemy_drone --type gameplay_target
python3 Tools/rkp.py build-asset enemy_drone
python3 Tools/rkp.py accept-asset enemy_drone --screenshot Docs/screenshots/enemy_drone_imported.jpg
python3 Tools/rkp.py release-check
```

Use this interface for agent automation, future MCP-style wrappers, and reusable tooling. The Makefile remains a local convenience wrapper around the same tool.

## Full Local Release Check

```bash
python3 Tools/rkp.py release-check
```

This runs the pipeline doctor, XcodeGen, manifest validation, and Xcode simulator build with workspace-local DerivedData.

## Pipeline Doctor

```bash
python3 Tools/rkp.py doctor
```

This runs `Tools/pipeline_doctor.py`, a fast static check for manifest/imported asset consistency, XcodeGen paths, Markdown evidence links, public local path leaks, CLI docs, CI basics, and skill packaging.

## New Asset Scaffolder

```bash
python3 Tools/rkp.py new-asset enemy_drone --type gameplay_target
```

Supported types:

- `gameplay_target`
- `environment`
- `prop`
- `projectile`

This creates a planned manifest entry, `Docs/assets/<id>.md`, and `Tools/blender/create_<id>.py`. It does not generate the final USDZ or mark the asset imported.

## Asset Build

```bash
python3 Tools/rkp.py build-asset enemy_drone
```

If Blender is not on `PATH`:

```bash
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender python3 Tools/rkp.py build-asset enemy_drone
```

This runs `Tools/blender/create_<id>.py` and verifies `Assets/Imported/<id>.usdz` exists and is non-empty. It intentionally leaves manifest status unchanged.

## Asset Acceptance

```bash
python3 Tools/rkp.py accept-asset enemy_drone --screenshot Docs/screenshots/enemy_drone_imported.jpg
```

Screenshot is required. The command marks the manifest entry imported, records screenshot evidence, updates `Docs/assets/<id>.md` when present, prepends a worklog acceptance entry, and runs `make doctor` through `Tools/pipeline_doctor.py`.

## Validate Manifest Only

```bash
make validate
```

## Regenerate Guide PDF

```bash
make guide
```

Use when `Docs/guide.md` changes materially.

## Install This Skill Into Codex

```bash
make install-skill
```

This copies `Skills/realitykit-pipeline-guide` into `${CODEX_HOME:-$HOME/.codex}/skills/realitykit-pipeline-guide`.

## Fast Repo Structure Check

```bash
python3 Skills/realitykit-pipeline-guide/scripts/check_repo.py
```
