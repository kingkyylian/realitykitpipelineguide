# Slash Commands

This repo includes Claude-style slash commands for the RealityKit pipeline. They are thin command prompts around `Tools/rkp.py`.

## Commands

Create or continue a prompt-backed asset:

```text
/rkp-asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target"
```

Build when Blender is available:

```text
/rkp-asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target" build=true
```

Accept with screenshot evidence and run the final gate:

```text
/rkp-asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target" build=true screenshot=Docs/screenshots/enemy_drone_imported.jpg release=true
```

Check the pipeline:

```text
/rkp-status
/rkp-status json
```

## Contract

- Slash commands do not replace the pipeline rules.
- `build=true` still requires Blender.
- `screenshot=<path>` still requires a real simulator screenshot.
- Production acceptance still goes through `accept-asset`.
- The implementation surface remains `python3 Tools/rkp.py ...`.
