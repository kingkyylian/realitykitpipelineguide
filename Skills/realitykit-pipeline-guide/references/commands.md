# Commands

Run from the repository root.

## Generate and Build

```bash
make generate
make build
```

## Full Local Release Check

```bash
make release-check
```

This runs the pipeline doctor, XcodeGen, manifest validation, and Xcode simulator build with workspace-local DerivedData.

## Pipeline Doctor

```bash
make doctor
```

This runs `Tools/pipeline_doctor.py`, a fast static check for manifest/imported asset consistency, XcodeGen paths, Markdown evidence links, public local path leaks, CI basics, and skill packaging.

## New Asset Scaffolder

```bash
make new-asset id=enemy_drone type=gameplay_target
```

Supported types:

- `gameplay_target`
- `environment`
- `prop`
- `projectile`

This creates a planned manifest entry, `Docs/assets/<id>.md`, and `Tools/blender/create_<id>.py`. It does not generate the final USDZ or mark the asset imported.

## Asset Build

```bash
make build-asset id=enemy_drone
```

If Blender is not on `PATH`:

```bash
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender make build-asset id=enemy_drone
```

This runs `Tools/blender/create_<id>.py` and verifies `Assets/Imported/<id>.usdz` exists and is non-empty. It intentionally leaves manifest status unchanged.

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
