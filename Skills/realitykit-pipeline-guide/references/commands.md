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
python3 Tools/rkp.py prompt-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
python3 Tools/rkp.py make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
python3 Tools/rkp.py build-asset enemy_drone
python3 Tools/rkp.py accept-asset enemy_drone --screenshot Docs/screenshots/enemy_drone_imported.jpg
python3 Tools/rkp.py release-check
```

Use this interface for agent automation, future MCP-style wrappers, and reusable tooling. The Makefile remains a local convenience wrapper around the same tool.

Machine-readable commands:

```bash
python3 Tools/rkp.py status --json
python3 Tools/rkp.py doctor --json
```

Use JSON output for scripts, CI assertions, and agent planning. Keep side-effect commands such as `build-asset` and `accept-asset` text-first unless a concrete integration needs structured output.

`status --json` includes `archetype` for prompt-backed assets when it is available from the manifest or generated Blender script.

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

## Prompt Asset Draft

```bash
python3 Tools/rkp.py prompt-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
```

With Blender available:

```bash
python3 Tools/rkp.py prompt-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target" --build
```

This creates the asset contract, writes a prompt-backed procedural Blender generator, records the prompt in the asset brief, and can optionally run the USDZ build. It does not mark the asset imported; visual acceptance still requires `accept-asset`.

## One-Command Asset Loop

```bash
python3 Tools/rkp.py make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
```

With Blender, screenshot evidence, and final gate:

```bash
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender python3 Tools/rkp.py make-asset enemy_drone \
  --type gameplay_target \
  --prompt "red bullseye drone target" \
  --build \
  --screenshot Docs/screenshots/enemy_drone_imported.jpg \
  --release-check
```

This command orchestrates `prompt-asset`, optional `build-asset`, optional `accept-asset`, and optional `release-check`. Screenshot acceptance remains explicit.

## Slash Commands

For agent CLIs that support repository slash commands:

```text
/rkp-asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target"
/rkp-status
```

The slash commands live in `.claude/commands` and wrap the same `Tools/rkp.py` pipeline. They do not bypass screenshot acceptance.

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
