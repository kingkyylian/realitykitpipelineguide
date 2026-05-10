# Blender Support and Fallback Matrix

RKP is built around Blender-authored USDZ assets, but the CLI must remain useful on machines where Blender background export is missing or unstable. Treat Blender as the preferred authoring path and the direct USDZ fallback as a draft-generation safety net.

## Support Policy

| Environment | Status | Use it for | Required follow-up |
| --- | --- | --- | --- |
| Blender 4.x with working USD export | Preferred authoring path | Generated Blender scripts, UV/material iteration, source asset edits. | Run `rkp inspect-usdz` and accept with screenshot evidence. |
| Blender 4.5 LTS | Reference diagnostic target | Stable local authoring when background mode works on the machine. | Confirm with `rkp doctor --blender` before relying on it. |
| Newer Blender previews or 5.x builds | Not the public baseline yet | Local experiments and compatibility checks. | Record failures in `Docs/WORKLOG.md`; keep fallback path available. |
| No working Blender, but `usdzip` exists | Draft fallback path | Prompt-backed procedural USDZ drafts through automatic recovery or explicit `rkp build-asset --fallback-only`. | Do not mark imported until RealityKit screenshot evidence exists. |
| No Blender and no `usdzip` | Planning-only path | Manifest entries, asset briefs, and generator scripts. | Install a working authoring tool before build/acceptance. |

## Known Reference-Machine Behavior

On the current reference machine, Blender 4.5.8 LTS, 5.1.0, and 5.1.1 were observed crashing during background startup before the generated Python asset script ran. RKP recovered by using the direct USDZ fallback through `/usr/bin/usdzip` for prompt-backed procedural assets.

That fallback creates a real `.usdz`, but it does not replace visual acceptance. The asset should remain a draft until it is loaded in RealityKit and accepted with screenshot evidence.

Use `--fallback-only` when you want to skip Blender entirely and produce the direct USDZ draft on purpose:

```bash
rkp build-asset enemy_drone --fallback-only
make build-asset id=enemy_drone fallback=1
```

## Diagnostic Commands

Check discovery:

```bash
rkp doctor --blender
rkp doctor --blender --json
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender rkp doctor --blender
```

Build and inspect a draft:

```bash
rkp build-asset enemy_drone
rkp inspect-usdz enemy_drone
rkp verify-asset enemy_drone --build
```

Accept only after RealityKit evidence:

```bash
rkp accept-asset enemy_drone --screenshot Docs/screenshots/enemy_drone_imported.jpg
```

## Documentation Rule

When a Blender version or fallback behavior changes, update this file, `Docs/WORKLOG.md`, and any user-facing command examples that would otherwise mislead a fresh contributor.
