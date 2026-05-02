# RealityKit Pipeline

Use this command as the short slash-command entrypoint for the RealityKit pipeline.

Invocation examples:

```text
/rkp status
/rkp status json
/rkp asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target"
/rkp asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target" build=true
/rkp asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target" build=true screenshot=Docs/screenshots/enemy_drone_imported.jpg release=true
```

User arguments:

```text
$ARGUMENTS
```

## Behavior

1. Parse the first word of `$ARGUMENTS` as the subcommand.
2. Supported subcommands:
   - `status`
   - `asset`
   - `doctor`
   - `release`
3. If no subcommand is provided, run:

```bash
python3 Tools/rkp.py status
python3 Tools/rkp.py doctor
```

## Subcommands

### status

Run:

```bash
python3 Tools/rkp.py status
python3 Tools/rkp.py doctor
```

If arguments contain `json`, also run:

```bash
python3 Tools/rkp.py status --json
python3 Tools/rkp.py doctor --json
```

### asset

Parse the remaining arguments after `asset`.

Prefer explicit key-value arguments:

- `id=<asset_id>`
- `type=<asset_type>`
- `prompt="<asset prompt>"`
- `build=true`
- `screenshot=<path>`
- `release=true`
- `force=true`

Then run:

```bash
python3 Tools/rkp.py make-asset <id> --type <type> --prompt "<prompt>"
```

Add flags only when requested:

- `build=true` -> `--build`
- `screenshot=<path>` -> `--screenshot <path>`
- `release=true` -> `--release-check`
- `force=true` -> `--force`

### doctor

Run:

```bash
python3 Tools/rkp.py doctor
```

### release

Run:

```bash
python3 Tools/rkp.py release-check
```

## Guardrails

- Do not bypass screenshot acceptance.
- If `screenshot=<path>` is provided without `build=true`, explain that acceptance requires build first.
- If Blender is not on PATH, show this retry form:

```bash
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender python3 Tools/rkp.py make-asset <id> --type <type> --prompt "<prompt>" --build
```

## Response Style

Keep the answer short:

- what ran
- what changed
- inferred archetype if relevant
- next command
