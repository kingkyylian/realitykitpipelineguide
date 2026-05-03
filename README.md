# RealityKit Pipeline Toolkit

A command-first RealityKit asset pipeline toolkit: CLI, installable Codex skill, agent slash commands, and reusable contracts for Blender-authored USDZ assets.

This is a developer tool first. The included target-shooting app is a verification fixture used to prove the workflow: scaffold an asset, build it with Blender, accept it with simulator evidence, and ship it through Xcode.

Most RealityKit tutorials stop at code. This repo treats asset production as part of the game loop: each Blender/USDZ asset has a manifest entry, mobile budget, loader contract, screenshot, and learning note.

![RealityKit pipeline gameplay demo](Docs/screenshots/demo.gif)

## What This Is

- `rkp`: the installable CLI for asset status, validation, scaffolding, Blender builds, screenshot-based acceptance, tests, and release checks.
- `Skills/realitykit-pipeline-guide`: an installable Codex skill that points agents at the same asset, build, and documentation contracts.
- `.claude/commands`: slash commands such as `/rkp`, `/rkp-asset`, and `/rkp-status` for agent-style usage.
- `Sources/RealityKitPipelineDemo`: a small playable RealityKit verification fixture that proves pipeline output inside an iOS app.
- `Docs`: the teaching, production, and AI-agent handoff layer around the same pipeline.

Generated assets are tool outputs first. Keep them in `Assets/Imported` and copy or load them in your own RealityKit game when needed; the fixture app is only a verification harness and does not automatically switch its default gameplay target to every newly generated asset.

## What You Learn

- Build a SwiftUI + RealityKit game prototype.
- Generate and import Blender-authored USDZ assets.
- Keep asset scale, origin, UVs, materials, and texture budgets under control.
- Connect visual texture design to gameplay with ring-based scoring.
- Verify every asset with CLI checks, builds, screenshots, and worklog notes.

## Verification Fixture

| Textured target scoring | Imported arena floor |
| --- | --- |
| ![Ring scoring inner hit](Docs/screenshots/ring_scoring_inner_hit.jpg) | ![Imported arena floor](Docs/screenshots/arena_floor_imported.jpg) |

The fixture app starts with procedural RealityKit fallbacks so it can compile before any custom art exists. The asset pipeline then replaces placeholders with USDZ files exported from Blender into `Assets/Imported`.

## Quick Start

### Prerequisites

- Python 3.10+ and `pipx`.
- Blender 4.x if you want to build generated Blender assets locally.
- macOS with Xcode and XcodeGen only if you want to run the included iOS verification fixture.

### Use The Pipeline CLI

Install the toolkit directly from GitHub. You do not need to clone this repo for normal CLI usage.

```bash
pipx install git+https://github.com/kingkyylian/realitykitpipelineguide.git
rkp --version
```

Bootstrap any RealityKit project from that project's root:

```bash
rkp init --project-name MyGame
rkp doctor
rkp make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
rkp release-check
```

Machine-readable status and doctor output are available for scripts and agents:

```bash
rkp status --json
rkp doctor --json
```

### First Asset In Your Own Project

This is the shortest "I do not know this repo, I just need a RealityKit asset" path:

```bash
mkdir MyRealityKitGame
cd MyRealityKitGame
pipx install git+https://github.com/kingkyylian/realitykitpipelineguide.git
rkp init --project-name MyRealityKitGame
rkp doctor
rkp make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
rkp build-asset enemy_drone
rkp status
rkp release-check
```

Expected first doctor result in a new project is `0 error(s)` with only recommended project hygiene warnings such as `README.md`, `LICENSE`, or `Makefile`.

`build-asset` first tries Blender. If Blender is unavailable or crashes in background mode, RKP tries the direct USDZ fallback when `usdzip` exists. A fallback-built USDZ is still only a draft; keep the asset `planned` until you load it in your app or the fixture and accept it with a real screenshot:

```bash
rkp accept-asset enemy_drone --screenshot Docs/screenshots/enemy_drone_imported.jpg
```

`accept-asset` expects simulator or device screenshot evidence. If you do not have Xcode or a simulator on this machine, skip that step; the USDZ can still stay as a `planned` draft without blocking the rest of the pipeline.

If you are developing this toolkit repo itself, clone it and use the repo-local wrapper or Makefile:

```bash
git clone https://github.com/kingkyylian/realitykitpipelineguide.git
cd realitykitpipelineguide
python3 Tools/rkp.py status
python3 -m unittest discover -s Tests
python3 Tools/rkp.py release-check
make status
make test
```

### Prompt To Asset

`make-asset` is the one-command asset loop. It turns a short prompt into an asset contract and Blender generator script, then can optionally build, accept, and run the release gate.

This is not full text-to-3D generation. The prompt is used for the brief, palette, and a small keyword-based archetype set: `drone`, `tower`, `crate`, `projectile`, and `target`. If no archetype is recognized, RKP writes the default procedural template for the asset type and tells you to edit the generated Blender script for prompt-specific geometry.

If you are using a slash-command agent CLI, use:

```text
/rkp asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target"
```

The longer direct slash command is also available:

```text
/rkp-asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target"
```

For terminal usage, run the same pipeline directly:

```bash
rkp make-asset enemy_drone \
  --type gameplay_target \
  --prompt "red bullseye drone target"
```

For this prompt the tool infers `drone`, then writes a procedural Blender draft with a central body, four arms, rotor discs, Smart UV projection, and an `st` UV layer for USDZ export.

For prompts like `katana` or `spaceship`, the current v0.1 behavior is scaffold-first: RKP records the prompt and produces a default template, but it does not invent new geometry. Open `Tools/blender/create_<asset_id>.py` and replace the default geometry with the shape you want.

If Blender is available, add `--build`:

```bash
rkp make-asset enemy_drone \
  --type gameplay_target \
  --prompt "red bullseye drone target" \
  --build
```

If Blender crashes or is unavailable but `usdzip` exists, RKP falls back to a direct USDZ builder for prompt-backed procedural assets. The fallback still creates a real `.usdz`; the asset remains `planned` until simulator screenshot acceptance.

After verifying the result in the simulator and saving a screenshot, run the same command with acceptance:

```bash
rkp make-asset enemy_drone \
  --type gameplay_target \
  --prompt "red bullseye drone target" \
  --build \
  --screenshot Docs/screenshots/enemy_drone_imported.jpg \
  --release-check
```

Use status JSON when an agent or script needs to inspect the inferred archetype:

```bash
rkp status --json
```

### Generate and Build

```bash
xcodegen generate
xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination 'generic/platform=iOS Simulator' -derivedDataPath Build/DerivedData build
```

To run visually, open `RealityKitPipelineDemo.xcodeproj` in Xcode and choose an iOS simulator.

### First Asset Loop

1. Start the asset loop:

   ```bash
   rkp make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
   ```

2. If Blender is available, build the USDZ in the same command:

   ```bash
   rkp make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target" --build
   ```

3. Verify the asset in the simulator and capture a screenshot.
4. Accept it and run the release gate:

   ```bash
   rkp make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target" --build --screenshot Docs/screenshots/enemy_drone_imported.jpg --release-check
   ```

### About `rtk`

Some internal docs and worklog entries use commands prefixed with `rtk`. That is this project's local agent wrapper, not a public dependency. If you cloned the repo normally, run the same command without `rtk`.

## Use In Your Own Project

v0.1 includes a Python package. Install it from GitHub:

```bash
pipx install git+https://github.com/kingkyylian/realitykitpipelineguide.git
rkp --version
```

Then bootstrap from your RealityKit project root:

```bash
rkp init --project-name MyGame
```

This creates a minimal RKP workspace:

```text
rkp.json
Tools/asset_manifest.json
Assets/Imported/
Assets/Textures/
Assets/Source/
Docs/assets/
Docs/screenshots/
Tools/blender/
```

`rkp init` does not overwrite an existing `rkp.json` or manifest unless you pass `--force`, and it preserves existing directories such as `Assets/Imported`.

After bootstrap, `rkp` discovers the project root by walking up from the current directory until it finds `rkp.json`.

Generated default `rkp.json`:

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

Set `xcode_project` and `xcode_scheme` when you want `release-check` to include the Xcode build gate.

Manual integration path:

1. Fork this repo or copy the toolkit folders into your RealityKit project:

   ```text
   Tools/
   Skills/realitykit-pipeline-guide/
   Prompts/
   Docs/cli-tool.md
   Docs/blender-usdz-checklist.md
   Docs/production-playbook.md
   Tools/asset_manifest.json
   ```

2. Keep or replace `Sources/RealityKitPipelineDemo`. It is only the verification fixture. Your app can use its own RealityKit loader as long as accepted assets still prove the same path:

   ```text
   manifest -> Assets/Imported/<asset_id>.usdz -> Xcode resource bundle -> RealityKit load -> screenshot evidence
   ```

3. Update `project.yml` or your Xcode project so `Assets/Imported` is copied into the app bundle.
4. Run `rkp doctor`, then adapt any missing path findings intentionally.
5. Use `status --json` and `doctor --json` if you want to wrap this toolkit from another agent, script, or future MCP server.

The manifest format is intentionally simple JSON and can travel to another repo. `init`, `status`, `doctor`, `new-asset`, `prompt-asset`, `build-asset`, `accept-asset`, and `release-check` are config-aware. If `xcode_project` is omitted, `release-check` runs doctor/tests/manifest validation and skips the Xcode gate with a warning-style message.

## Known Limits In v0.1

- Blender background USDZ export is still machine-sensitive. On the current reference machine, Blender 4.5.8 crashed during the fresh-project walkthrough, and RKP recovered by building a fallback USDZ through `/usr/bin/usdzip`.
- The fallback builder is for prompt-backed procedural drafts. It is enough to keep the asset loop moving, but visual acceptance still requires loading the USDZ in RealityKit and providing screenshot evidence.
- RKP does not automatically edit arbitrary Xcode projects. Add `Assets/Imported` to your app bundle yourself, or set `xcode_project` and `xcode_scheme` in `rkp.json` when you want `release-check` to run the Xcode build gate.
- There is no standalone MCP server yet. `status --json` and `doctor --json` are the stable machine-readable surfaces for agents and future MCP wrappers.
- The package version is currently `0.1.0`. Until release tags are cut, GitHub installs track the default branch.

## Use as a Codex Skill

This repo includes a portable Codex skill at `Skills/realitykit-pipeline-guide`. Install it locally with:

```bash
make install-skill
```

After installing, ask Codex to use `realitykit-pipeline-guide` for RealityKit asset pipeline, fixture, documentation, or release tasks. The skill points agents to the right workflow, contracts, commands, and repo gates without rereading the whole guide every time.

This repo does not ship a standalone MCP server yet. `status --json` and `doctor --json` are the stable machine-readable surfaces intended for future MCP-style wrappers and current agent automation.

## Start Here

For the command-first version of the pipeline, start from `Docs/cli-tool.md`.

For slash-command usage, start from `Docs/slash-commands.md`.

For the teaching version of the pipeline, use `Docs/guide.md`. It explains the full asset journey from gameplay need to USDZ export, Xcode resource import, RealityKit loading, simulator screenshot, and learning notes. A generated PDF lives at `Docs/pdf/realitykit-pipeline-guide.pdf`.

For reusable production practice, use `Docs/production-playbook.md`. It defines the feature brief, asset/runtime contract, quality gates, review checklist, and definition of done for future RealityKit games.

For starting a new game from this repo's lessons, use `Docs/new-game-startup.md`.

Start each work session from `Docs/WORKLOG.md`. It tracks sprints, decisions, verification results, and asset/code contracts.

For AI agents or future handoff, start from `AGENTS.md` and `Docs/ai-handoff.md`.

## GitHub Metadata

Suggested repo description:

```text
Command-first Blender -> USDZ -> RealityKit asset pipeline toolkit with CLI, Codex skill, slash commands, and an iOS verification fixture.
```

Suggested topics:

```text
realitykit, swift, swiftui, ios, blender, usdz, codex-skill, developer-tools, 3d-pipeline, asset-pipeline
```

## Goals

- Learn SwiftUI + RealityKit app structure.
- Use a small fixture loop to prove imported assets under RealityKit.
- Keep a CLI-driven path for Blender -> USDZ -> Xcode -> RealityKit.
- Teach the asset and texture pipeline as a shared system, not as isolated Blender/code roles.
- Use AI for repeatable planning, asset briefs, code tasks, and QA checklists.

## Common Commands

These commands assume `rkp` was installed with `pipx install git+https://github.com/kingkyylian/realitykitpipelineguide.git`.

Show pipeline health:

```bash
rkp status
rkp doctor
```

Initialize a project:

```bash
rkp init --project-name MyGame
```

Generate the Xcode project for the included fixture app:

```bash
xcodegen generate
```

Build for iOS simulator:

```bash
xcodebuild -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination 'platform=iOS Simulator,name=iPhone 16' build
```

Build with workspace-local DerivedData, which avoids writing into the default Xcode cache:

```bash
xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination 'generic/platform=iOS Simulator' -derivedDataPath Build/DerivedData build
```

Validate the asset manifest:

```bash
node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
```

Run the pipeline doctor:

```bash
rkp doctor
```

Scaffold a new asset:

```bash
rkp new-asset enemy_drone --type gameplay_target
```

Create a prompt-backed procedural Blender draft:

```bash
rkp prompt-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
```

Run the one-command asset loop:

```bash
rkp make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
```

Run the Blender build script for an asset:

```bash
rkp build-asset enemy_drone
```

If Blender is not on `PATH`, provide it explicitly:

```bash
BLENDER=/custom/path/to/blender rkp build-asset enemy_drone
```

Accept a built asset with required visual evidence:

```bash
rkp accept-asset enemy_drone --screenshot Docs/screenshots/enemy_drone_imported.jpg
```

Regenerate the guide PDF:

```bash
pandoc Docs/guide.md --standalone --embed-resources --resource-path=Docs --css Docs/guide-style.css --metadata title="RealityKit Asset and Texture Pipeline Guide" -o Build/realitykit-pipeline-guide.html
weasyprint Build/realitykit-pipeline-guide.html Build/realitykit-pipeline-guide.pdf
cp Build/realitykit-pipeline-guide.pdf Docs/pdf/realitykit-pipeline-guide.pdf
```

## Current Learning State

Completed:

- Procedural RealityKit sandbox.
- First imported USDZ target: `target_basic.usdz`.
- Scale/orientation tuning with deterministic spawn slots.
- First base color textured target: `target_basic_textured.usdz`.
- UV primvar lesson: source USDZ uses `st`.
- Ring-based scoring: bullseye `+5`, inner ring `+3`, outer ring `+1`.
- Arena floor import: `arena_floor.usdz`.
- Wave loop: HUD shows current wave and cleared target progress.

Canonical course material:

- `Docs/guide.md`
- `Docs/pdf/realitykit-pipeline-guide.pdf`
- `Docs/production-playbook.md`
- `Docs/new-game-startup.md`

Reusable templates:

- `Prompts/asset-brief.md`
- `Prompts/game-feature-brief.md`
- `Prompts/codex-task.md`
- `Prompts/qa-checklist.md`
- `Skills/realitykit-pipeline-guide`

## Folder Map

- `Sources/RealityKitPipelineDemo`: SwiftUI and RealityKit code.
- `Assets/Imported`: USDZ files exported from Blender or Reality Composer Pro.
- `Assets/Source`: optional source-art handoff area; app target does not depend on it.
- `Assets/Textures`: source or exported texture files.
- `Docs`: pipeline, budgets, checklists.
- `Docs/cli-tool.md`: command-first usage contract for the pipeline CLI.
- `Docs/slash-commands.md`: slash command usage for agent CLIs.
- `Docs/guide.md`: public-facing learning guide for the asset and texture pipeline.
- `Docs/production-playbook.md`: reusable production gates and team workflow.
- `Docs/new-game-startup.md`: checklist for starting a future RealityKit game.
- `Docs/features`: feature briefs and acceptance contracts.
- `Docs/ai-handoff.md`: fast orientation page for AI agents and future sessions.
- `Docs/diagrams`: Mermaid source diagrams for the guide or PDF export.
- `Docs/screenshots`: selected visual evidence used by the guide.
- `Docs/pdf`: generated PDF guide for sharing.
- `Prompts`: reusable AI prompts for Codex/Claude.
- `Skills/realitykit-pipeline-guide`: installable Codex skill for this pipeline.
- `Tools/blender`: Blender-side starter scripts and authoring notes.
- `Tools/rkp.py`: primary CLI entrypoint for status, doctor, asset scaffolding, build, accept, tests, and release checks.
- `Tools/accept_asset.py`: marks a built asset imported only when screenshot evidence is provided.
- `Tools/asset_manifest.json`: source of truth for asset names and budgets.
- `Tools/build_asset.py`: runs `Tools/blender/create_<id>.py` and verifies the expected USDZ exists.
- `Tools/new_asset.py`: creates a manifest entry, asset brief, and Blender starter script for a new asset.
- `Tools/prompt_asset.py`: creates a prompt-backed Blender generator script and asset brief notes.
- `Tools/pipeline_doctor.py`: static pipeline consistency checker for manifests, docs, links, CI paths, and skill packaging.
