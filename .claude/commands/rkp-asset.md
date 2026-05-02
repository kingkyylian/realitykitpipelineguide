# RealityKit Pipeline Asset

Use this command when the user wants to create or continue a RealityKit pipeline asset from a short prompt.

Invocation examples:

```text
/rkp-asset enemy_drone gameplay_target red bullseye drone target
/rkp-asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target"
/rkp-asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target" build=true
/rkp-asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target" build=true screenshot=Docs/screenshots/enemy_drone_imported.jpg release=true
```

User arguments:

```text
$ARGUMENTS
```

## Behavior

1. Parse `$ARGUMENTS`.
2. Prefer explicit `key=value` arguments:
   - `id=<asset_id>`
   - `type=<asset_type>`
   - `prompt="<asset prompt>"`
   - `build=true`
   - `screenshot=<path>`
   - `release=true`
   - `force=true`
3. If the user uses positional arguments, interpret them as:
   - first token: asset id
   - second token: asset type
   - remaining tokens: prompt
4. Default `type` to `gameplay_target` only if the user omitted it.
5. Run the command from the repository root:

```bash
python3 Tools/rkp.py make-asset <id> --type <type> --prompt "<prompt>"
```

6. Add flags only when requested:
   - `build=true` -> `--build`
   - `screenshot=<path>` -> `--screenshot <path>`
   - `release=true` -> `--release-check`
   - `force=true` -> `--force`

## Guardrails

- Do not mark the asset complete unless `accept-asset` succeeds through screenshot evidence.
- If `--build` fails because Blender is not on PATH, explain the exact retry command:

```bash
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender python3 Tools/rkp.py make-asset <id> --type <type> --prompt "<prompt>" --build
```

- If the user provides `screenshot` without `build=true`, tell them the pipeline requires build before acceptance and rerun with `build=true` only if they confirm.
- After a successful command, run:

```bash
python3 Tools/rkp.py status
```

- For substantial changes, update `Docs/WORKLOG.md`.

## Response Style

Report:

- the asset id
- inferred archetype if visible in command output or `status --json`
- generated files
- next command the user should run
- whether Blender build or screenshot acceptance happened
