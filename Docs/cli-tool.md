# RealityKit Pipeline CLI

`Tools/rkp.py` is the primary interface for this repository. The guide explains the system, but the CLI runs the system.

## Mental Model

The pipeline has three asset states:

1. `planned`: the asset exists in the manifest and has a brief.
2. `built`: a USDZ exists, but it has not been verified in RealityKit.
3. `imported`: the USDZ has simulator screenshot evidence and is accepted for production use.

`built` is intentionally not a manifest status. It is a file-system fact: `Assets/Imported/<id>.usdz` exists. Production acceptance happens only through `accept-asset`.

## Daily Commands

Show where the project stands:

```bash
python3 Tools/rkp.py status
```

Check static pipeline health:

```bash
python3 Tools/rkp.py doctor
```

Use JSON output for CI, scripts, agents, or future MCP-style wrappers:

```bash
python3 Tools/rkp.py status --json
python3 Tools/rkp.py doctor --json
```

Create a new asset task:

```bash
python3 Tools/rkp.py new-asset enemy_drone --type gameplay_target
```

Create a prompt-backed procedural Blender draft:

```bash
python3 Tools/rkp.py prompt-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
```

Build immediately when Blender is available:

```bash
python3 Tools/rkp.py prompt-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target" --build
```

Build the asset through Blender:

```bash
python3 Tools/rkp.py build-asset enemy_drone
```

Accept the asset after simulator verification:

```bash
python3 Tools/rkp.py accept-asset enemy_drone --screenshot Docs/screenshots/enemy_drone_imported.jpg
```

Run the full release gate:

```bash
python3 Tools/rkp.py release-check
```

## Makefile Compatibility

The Makefile is a convenience wrapper around the CLI:

```bash
make status
make doctor
make new-asset id=enemy_drone type=gameplay_target
make build-asset id=enemy_drone
make accept-asset id=enemy_drone screenshot=Docs/screenshots/enemy_drone_imported.jpg
make release-check
```

Prefer direct CLI commands when building automation, agents, or future MCP-style integrations. Prefer `make` for short local terminal usage.

## Tool Contract

- `new-asset` may create manifest entries, asset briefs, and Blender starter scripts.
- `prompt-asset` may create the same asset contract plus a prompt-backed procedural Blender generator and optional USDZ build.
- `build-asset` may create or replace USDZ/source files through Blender, but it does not mark the asset imported.
- `accept-asset` requires screenshot evidence and records production acceptance.
- `doctor` reads project state and should not mutate files.
- `status --json` and `doctor --json` are the stable machine-readable surface for automation.
- `release-check` runs the same gates expected before push or release.
