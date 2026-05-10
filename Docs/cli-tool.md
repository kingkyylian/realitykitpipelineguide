# RealityKit Pipeline CLI

`Tools/rkp.py` and the installable `rkp` command are the primary interfaces for this repository. The guide explains the system, but the CLI runs the system.

Generated USDZ files are reusable asset outputs. Acceptance proves the asset can load in the RealityKit fixture or your own RealityKit app, but it does not mean the fixture should permanently use that asset as its default target.

This repository does not ship a standalone MCP server yet. Treat the JSON commands below as the current stable automation surface and the intended base for future MCP-style wrappers.

## Normal User Path

Use this path when the goal is a simple, comprehensive RealityKit asset pipeline:

```bash
rkp init --project-name MyGame
rkp make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
rkp inspect-usdz enemy_drone
rkp verify-asset enemy_drone --build
rkp release-check
```

Add screenshot acceptance only after the asset has been loaded in RealityKit:

```bash
rkp accept-asset enemy_drone --screenshot Docs/screenshots/enemy_drone_imported.jpg
```

Those commands are the core product. The remaining commands support diagnostics, advanced generation, release hygiene, or experimental workflows.

## Mental Model

RKP owns the asset pipeline contract:

```text
brief -> manifest -> Blender/USDZ draft -> inspect -> RealityKit screenshot evidence -> release check
```

The pipeline has three asset states:

1. `planned`: the asset exists in the manifest and has a brief.
2. `built`: a USDZ exists, but it has not been verified in RealityKit.
3. `imported`: the USDZ has screenshot evidence and is accepted for production use.

`built` is intentionally not a manifest status. It is a file-system fact: `Assets/Imported/<id>.usdz` exists. Production acceptance happens only through `accept-asset`.

v0.1 has a local Python package and portable project config. `rkp` discovers the project root by walking up from the current directory until it finds `rkp.json`.

Install from GitHub:

```bash
pipx install git+https://github.com/kingkyylian/realitykitpipelineguide.git
rkp --version
```

Bootstrap another RealityKit project from that project's root:

```bash
rkp init --project-name MyGame
```

This writes `rkp.json`, an empty `Tools/asset_manifest.json`, and the minimal asset/doc/source directories used by the pipeline. It refuses to overwrite an existing project unless `--force` is passed, and existing directories are left in place.

Generated default config:

```json
{
  "manifest": "Tools/asset_manifest.json",
  "assets_dir": "Assets/Imported",
  "docs_dir": "Docs",
  "blender_dir": "Tools/blender",
  "textures_dir": "Assets/Textures",
  "source_dir": "Assets/Source",
  "tests_dir": "Tests",
  "xcode_project": null,
  "xcode_scheme": null,
  "xcode_destination": "generic/platform=iOS Simulator",
  "derived_data_path": "Build/DerivedData"
}
```

Set `xcode_project` and `xcode_scheme` when the project should run the Xcode build gate during `release-check`.

## Daily RKP Commands

Show where the project stands:

```bash
rkp --version
rkp status
python3 Tools/rkp.py status
```

Check static pipeline health:

```bash
rkp doctor
python3 Tools/rkp.py doctor
```

Add Blender discovery diagnostics when troubleshooting build setup:

```bash
rkp doctor --blender
rkp doctor --blender --json
BLENDER=/custom/path/to/blender rkp doctor --blender
```

Initialize a project:

```bash
rkp init
rkp init --project-name MyGame
rkp init --force
python3 Tools/rkp.py init
python3 Tools/rkp.py init --project-name MyGame
python3 Tools/rkp.py init --force
```

For a fresh external project:

```bash
mkdir MyRealityKitGame
cd MyRealityKitGame
pipx install git+https://github.com/kingkyylian/realitykitpipelineguide.git
rkp --version
rkp init --project-name MyRealityKitGame
rkp doctor
rkp make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
rkp build-asset enemy_drone
rkp verify-asset enemy_drone
rkp status --json
rkp release-check
```

In a minimal external project, `doctor` should report zero errors. Missing `README.md`, `LICENSE`, and `Makefile` are recommendations, not pipeline blockers.

Makefile shortcuts for this toolkit checkout:

```bash
make bootstrap-dev
make verify-local
make status
make doctor
make doctor blender=1
make doctor blender=1 json=1
make test
make lint
```

Run `make bootstrap-dev` once in a cloned toolkit checkout before `make lint`; it creates `.venv`, installs the editable package, and installs the optional dev dependency group from `pyproject.toml` without mutating a Homebrew-managed Python environment.

## Asset Creation Commands

Create a new asset task:

```bash
rkp new-asset enemy_drone --type gameplay_target
make new-asset id=enemy_drone type=gameplay_target
```

Create a prompt-backed procedural Blender draft:

```bash
rkp prompt-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
```

`prompt-asset` is scaffold-first, not open-ended text-to-3D. The prompt is recorded in the manifest and brief, and it can select one of the built-in procedural archetypes: `drone`, `tower`, `crate`, `projectile`, or `target`. Unknown shapes use the asset type's default geometry template and require editing `Tools/blender/create_<asset_id>.py`.

Run the same loop through one command:

```bash
rkp make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
```

Add build, screenshot acceptance, and release gate as the asset moves forward:

```bash
rkp make-asset enemy_drone \
  --type gameplay_target \
  --prompt "red bullseye drone target" \
  --build \
  --screenshot Docs/screenshots/enemy_drone_imported.jpg \
  --release-check
```

Build the asset through Blender:

```bash
rkp build-asset enemy_drone
make build-asset id=enemy_drone
```

If Blender exits before export, `build-asset` reports the crash log and then tries `Tools/usdz_fallback_builder.py` when `usdzip` is available. This keeps prompt-backed procedural assets buildable on machines where Blender background mode is broken, while still leaving screenshot acceptance as a separate gate.

Skip Blender deliberately when you only need the direct USDZ draft:

```bash
rkp build-asset enemy_drone --fallback-only
make build-asset id=enemy_drone fallback=1
```

## Asset Verification Commands

Inspect the built USDZ before visual acceptance:

```bash
rkp inspect-usdz enemy_drone
rkp inspect-usdz enemy_drone --json
make inspect-usdz id=enemy_drone
make inspect-usdz id=enemy_drone json=1
```

`inspect-usdz` checks whether the package exists, whether the expected base color texture is inside the USDZ, whether PNG/JPEG texture dimensions stay under `maxTextureSize`, whether USD text exposes `primvars:st`, and whether parsed face counts stay under the manifest triangle budget. Binary `.usdc` packages are decoded through `usdcat` when that tool is available; otherwise geometry/UV status remains `unknown` instead of being invented.

Use `verify-asset` as the one-command asset quality gate:

```bash
rkp verify-asset enemy_drone
rkp verify-asset enemy_drone --build
rkp verify-asset enemy_drone \
  --build \
  --screenshot Docs/screenshots/enemy_drone_imported.jpg \
  --release-check
make verify-asset id=enemy_drone
make verify-asset id=enemy_drone build=1 screenshot=Docs/screenshots/enemy_drone_imported.jpg release=1
```

`verify-asset` runs optional build, `inspect-usdz`, optional screenshot acceptance, and optional release-check in that order. It stops at the first failed gate.

Accept the asset after simulator verification:

```bash
rkp accept-asset enemy_drone --screenshot Docs/screenshots/enemy_drone_imported.jpg
make accept-asset id=enemy_drone screenshot=Docs/screenshots/enemy_drone_imported.jpg
```

The fixture app is optional. The required contract is that accepted assets have manifest metadata, runtime USDZ files under `Assets/Imported`, Xcode resource bundle inclusion when applicable, RealityKit load verification, and screenshot evidence.

## Release and Cleanup Commands

Run the full release gate:

```bash
rkp release-check
rkp release-check --assets
python3 Tools/rkp.py release-check
make release-check
make release-check assets=1
```

Use `--assets` before release or handoff when imported USDZ files should be re-inspected as part of the release gate. It runs `inspect-usdz` for each manifest asset with `status: imported` before the optional Xcode build.

Clean ignored local scratch output explicitly:

```bash
python3 Tools/rkp.py clean --dry-run
python3 Tools/rkp.py clean --apply
```

Run the CLI smoke tests:

```bash
python3 -m unittest discover -s Tests
```

Claude-style slash commands live in `.claude/commands`:

```text
/rkp status
/rkp asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target"
/rkp-asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target"
/rkp-status
```

They are agent-facing wrappers around `python3 Tools/rkp.py`. See `Docs/slash-commands.md`.

## Automation JSON

Use JSON output for CI, scripts, agents, or future MCP-style wrappers:

```bash
rkp status --json
rkp doctor --json
python3 Tools/rkp.py status --json
python3 Tools/rkp.py doctor --json
```

`status --json` includes inferred prompt archetypes when available, so agents can distinguish a `drone` draft from a generic `gameplay_target`.

`doctor --json`, `doctor --blender --json`, `inspect-usdz --json`, and the normal non-mutating command output are the current automation surface. No standalone MCP server ships yet.

## Advanced Backends

The default generator is deterministic and does not call external APIs just because an API key exists. To ask Claude for a custom Blender script, install the optional AI dependency and opt in:

```bash
pipx inject rkp anthropic
export ANTHROPIC_API_KEY=...
rkp prompt-asset enemy_tower \
  --type gameplay_target \
  --prompt "blue beacon tower target" \
  --generator claude
```

Use Meshy when the desired output is an external text-to-3D USDZ draft instead of a Blender script:

```bash
export MESHY_API_KEY=...
rkp make-asset enemy_drone \
  --type gameplay_target \
  --prompt "red drone target with four rotors" \
  --backend meshy \
  --quality preview
```

`--quality refine` runs Meshy's refine/PBR pass. Meshy output still needs simulator screenshot acceptance before the asset is considered imported, and the same `--screenshot` and `--release-check` flags can be added to this command after visual verification.

## v0.1 Limits

- RKP generates asset contracts, Blender scripts, USDZ drafts, manifest status, and release checks; it does not automatically wire arbitrary Xcode project resources.
- `release-check` skips Xcode unless `xcode_project` and `xcode_scheme` are configured in `rkp.json`.
- Blender background export can fail on some machines. The USDZ fallback keeps the procedural prompt loop alive when `usdzip` exists, and `rkp build-asset --fallback-only` can run that path explicitly, but it does not replace visual acceptance.
- No standalone MCP server ships yet. Use `status --json` and `doctor --json` as the current automation surface.
- The published package version is `0.2.1`; pin to a tag for reproducible tool behavior.

`rkg` is documented separately in `Docs/game-factory.md` because it is experimental labs work, not the normal RKP asset pipeline.

## Tool Contract

- `new-asset` may create manifest entries, asset briefs, and Blender starter scripts.
- `init` may create `rkp.json`, an empty manifest, and minimal pipeline directories. It refuses to overwrite without `--force`.
- `prompt-asset` may create the same asset contract plus a prompt-backed procedural Blender generator and optional USDZ build.
- `make-asset` orchestrates prompt scaffolding, optional USDZ build, optional screenshot acceptance, and optional release check.
- `build-asset` may create or replace USDZ/source files through Blender or explicit direct fallback, but it does not mark the asset imported.
- `inspect-usdz` reads a built USDZ package and reports texture presence, texture dimensions, UV, and known triangle budget gates without mutating files.
- `verify-asset` orchestrates optional build, USDZ inspection, optional screenshot acceptance, and optional release check, stopping at the first failed gate.
- `accept-asset` requires screenshot evidence and records production acceptance.
- `doctor` reads project state and should not mutate files. Core pipeline paths are errors; public showcase paths are warnings so minimal external projects can still use portable commands. `--blender` adds an explicit Blender executable diagnostic.
- `status --json` and `doctor --json` are the stable machine-readable surface for automation.
- `release-check` runs doctor, CLI tests when configured, manifest validation, optional imported-asset inspection with `--assets`, and the optional Xcode build expected before push or release.
- `clean --dry-run` lists ignored local scratch output; `clean --apply` removes those candidates explicitly.
