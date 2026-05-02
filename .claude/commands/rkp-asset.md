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
2. Before running anything, confirm the current directory is an RKP repo:
   - `Tools/rkp.py` must exist.
   - `Tools/asset_manifest.json` must exist.
   - If either file is missing, stop. Do not create a minimal replacement pipeline in the current directory.
3. Prefer explicit `key=value` arguments:
   - `id=<asset_id>`
   - `type=<asset_type>`
   - `prompt="<asset prompt>"`
   - `build=true`
   - `build=false`
   - `screenshot=<path>`
   - `release=true`
   - `force=true`
4. If the user uses positional arguments, interpret them as:
   - first token: asset id
   - second token: asset type
   - remaining tokens: prompt
5. Default `type` to `gameplay_target` only if the user omitted it.
6. Run the command from the repository root. Default to a real build unless the user explicitly passes `build=false`:

```bash
python3 Tools/rkp.py make-asset <id> --type <type> --prompt "<prompt>" --build
```

7. Add or remove flags based on user arguments:
   - `build=false` -> omit `--build`
   - `screenshot=<path>` -> `--screenshot <path>`
   - `release=true` -> `--release-check`
   - `force=true` -> `--force`

## Guardrails

- Do not mark the asset complete unless `accept-asset` succeeds through screenshot evidence.
- If `--build` fails because Blender is missing, explain that Blender must be installed or passed through `BLENDER=/path/to/blender`.
- If `--build` fails with a Blender crash log, report that path and do not pretend the USDZ was created.
- The CLI auto-detects `/Applications/Blender.app/Contents/MacOS/Blender` on macOS, so this retry form is only needed for non-standard installs:

```bash
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender python3 Tools/rkp.py make-asset <id> --type <type> --prompt "<prompt>" --build
```

- If the user provides `screenshot` with `build=false`, tell them the pipeline requires build before acceptance and rerun with build only if they confirm.
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
