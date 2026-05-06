# Codebase Audit and Cleanup Route

Date: 2026-05-06

Scope: whole repository scan for dead code, hygiene gaps, optimization candidates, and next implementation route.

## Evidence Collected

```text
Repo vitals: 54 commits, 2026-05-02..2026-05-06, 2 branches, 1 contributor
Hotspots: Docs/WORKLOG.md, README.md, Docs/ai-handoff.md, Sources/RealityKitPipelineDemo/GameARView.swift, Docs/cli-tool.md, Docs/guide.md
Bug-magnet overlap: Sources/RealityKitPipelineDemo/GameARView.swift appears in both hotspot and fix/bug commit scans
python3 -m compileall -q src Tools Tests: ok
python3 -m unittest discover -s Tests: ok, 41 tests
python3 Tools/rkp.py doctor --json: ok, 0 errors, 1 warning
python3 Tools/rkp.py doctor --blender --json: ok, Blender discovery passes, same CI warning
python3 Tools/rkp.py inspect-usdz target_basic_textured --json: ok, baseColor 512x512 / 1024, geometry/uv unknown because binary .usdc
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: xcodebuild ok, CoreSimulator sandbox warnings only
python3 Tools/rkp.py release-check: ok; doctor warning only, tests ok, xcodegen ok, xcodebuild ok
```

## Current Health

The project is release-gate clean. There is no confirmed tracked dead code block that can be safely deleted immediately. The Python AST scan did not find public top-level functions/classes that appear only at their definition site. Swift false positives were protocol methods `makeUIView` and `updateUIView`, so they are not dead code.

Ignored local output exists and is not tracked: `Build/`, `__pycache__/`, `src/rkp.egg-info/`, `.DS_Store`, and two empty `Assets/Imported/(A Document Being Saved By usdzip...)` directories. These are cleanup candidates, not release blockers.

The main risks are maintainability and quality-gate coverage rather than broken behavior.

## Findings

### P1 - Release Check Does Not Verify Imported Assets

Status: implemented in Sprint 51 as `rkp release-check --assets`.

`release-check` validates doctor/tests/manifest/Xcode, but it does not run `inspect-usdz` or `verify-asset` across imported manifest assets. A broken imported USDZ could pass release-check if the manifest and build still pass.

Route:

1. Add `rkp verify-all-assets` or `rkp release-check --assets`.
2. Iterate manifest assets with `status == "imported"`.
3. Run `inspect-usdz <id>` for each.
4. Treat binary `.usdc` triangle/UV unknown as non-blocking at first, but keep texture presence/size blocking.
5. Add tests with one passing asset and one missing/oversized texture fixture.

Acceptance:

```text
python3 Tools/rkp.py release-check --assets
python3 -m unittest discover -s Tests
```

### P1 - Bootstrap Blender Stub Is Older Than Prompt Template

Status: implemented in Sprint 51. `new-asset` now writes a baseColor texture stub with `st` UVs and modern USD texture export flags.

`src/rkp/new_asset.py` generates a basic Blender stub with `export_textures=True`, while the newer prompt template and worklog moved to `export_textures_mode="NEW"`. Also, `new-asset` adds `textureMaps: ["baseColor"]`, but the basic stub does not create a base color texture. This can make a plain `new-asset -> build-asset -> inspect-usdz` path fail the texture gate unless the user manually fills the stub.

Route:

1. Decide the contract:
   - Option A: plain `new-asset` creates no `textureMaps` until a texture is generated.
   - Option B: plain stub generates a 512x512 baseColor texture like `prompt-asset`.
2. Prefer Option B for teaching consistency.
3. Update the stub exporter to the same USD export contract as the prompt template.
4. Add an external-project test that asserts the generated stub includes `export_textures_mode="NEW"` and baseColor texture path.

Acceptance:

```text
python3 -m unittest Tests.test_rkp_project
python3 Tools/rkp.py doctor --json
```

### P1 - CLI Runtime Helpers Create Coupling Back Into `cli.py`

Status: implemented in Sprint 52. Runtime subprocess helpers now live in `src/rkp/runtime.py`.

`accept_asset.py`, `build_asset.py`, and `prompt_asset.py` import `module_command` and `package_env` from `rkp.cli`. This works, but it makes `cli.py` both the command entrypoint and a shared runtime helper module. As the CLI grows, this increases circular-import risk and makes unit tests patch the wrong layer.

Route:

1. Create `src/rkp/runtime.py`.
2. Move `package_env`, `module_command`, and `run_module` style helpers there.
3. Update CLI and subcommands to import runtime helpers from `rkp.runtime`.
4. Keep behavior identical and test subprocess vectors.

Acceptance:

```text
python3 -m unittest Tests.test_rkp_package Tests.test_rkp_cli
python3 Tools/rkp.py make-asset smoke_runtime --type gameplay_target --prompt "red target" --force
```

### P2 - Manifest and Asset Lookup Logic Is Duplicated

Status: implemented in Sprint 53. Shared manifest/asset helpers now live in `src/rkp/asset_manifest.py`.

`load_asset` and related manifest reads are duplicated in `build_asset.py`, `inspect_usdz.py`, and `usdz_fallback_builder.py`. `load_manifest`/`write_manifest` also exist in multiple modules.

Route:

1. Add `src/rkp/asset_manifest.py`.
2. Centralize `load_manifest`, `write_manifest`, `find_asset`, `expected_basecolor_name`, and `asset_usdz_path`.
3. Replace duplicated helpers module by module.
4. Keep `Tools/*.py` wrappers unchanged for compatibility.

Acceptance:

```text
python3 -m unittest discover -s Tests
python3 Tools/rkp.py verify-asset target_basic_textured
```

### P2 - Blender Discovery Logic Is Duplicated

Status: implemented in Sprint 54. Blender discovery now lives in `src/rkp/tool_discovery.py`.

`MACOS_BLENDER_APP` and executable discovery exist in both `build_asset.py` and `pipeline_doctor.py`. They are currently aligned, but this will drift when version diagnostics are added.

Route:

1. Add `src/rkp/tool_discovery.py`.
2. Move Blender executable resolution and validation there.
3. Return structured result: source, path, executable, version if available.
4. Make `doctor --blender` and `build-asset` consume the same resolver.

Acceptance:

```text
python3 Tools/rkp.py doctor --blender --json
BLENDER=/nonexistent/blender python3 Tools/rkp.py doctor --blender --json
python3 -m unittest Tests.test_rkp_cli
```

### P2 - `GameARView.swift` Has Too Many Responsibilities

`GameARView.swift` is 641 lines and owns scene setup, asset loading, target spawning, projectile simulation, scoring, collision handling, hit effects, haptics, demo playback, and reset behavior. It is the highest-risk app file by git-history overlap.

Route:

1. Extract pure scoring and wave math first:
   - `TargetScoring`
   - `WaveRules`
2. Then extract visual builders:
   - `ArenaBuilder`
   - `TargetFactory`
   - `HitEffectSystem`
3. Keep `GameARView` as orchestration only.
4. Add lightweight Swift unit tests for pure scoring/wave math if the project adds a test target.

Acceptance:

```text
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build
manual screenshot check for target load and hit feedback
```

### P2 - USDZ Inspection Has a Binary Geometry Blind Spot

`inspect-usdz` can inspect text `.usda`/`.usd` members, but binary `.usdc` packages report triangle and UV status as unknown. This is honest, but it weakens acceptance for Blender-built binary packages.

Route:

1. Detect `usdcat` availability.
2. For `.usdc` members, optionally run `usdcat` into temp text and parse the result.
3. Keep the current pure-Python path as fallback when USD tools are unavailable.
4. Add tests with mocked `usdcat`.

Acceptance:

```text
python3 Tools/rkp.py inspect-usdz target_basic_textured --json
python3 -m unittest Tests.test_rkp_project
```

### P3 - Local Cleanup Command Is Too Narrow

`make clean` only removes `Build/DerivedData`. The scan found ignored local outputs that accumulate during tests/builds: `Build/`, `__pycache__/`, `src/rkp.egg-info/`, and empty usdzip temp directories under `Assets/Imported`.

Route:

1. Add `rkp clean --dry-run` first, not a blind `rm`.
2. Show ignored cleanup candidates.
3. Add `rkp clean --apply` for Build/pycache/egg-info and known empty usdzip scratch dirs.
4. Wire `make clean` to the CLI command after tests.

Acceptance:

```text
python3 Tools/rkp.py clean --dry-run
python3 -m unittest Tests.test_rkp_cli
```

### P3 - Tooling Lacks First-Class Lint

`ruff` and `pyflakes` are not installed in the current environment, and `pyproject.toml` has no lint configuration. Current quality relies on tests, compileall, doctor, and Xcode build.

Route:

1. Add optional dev dependency group if package policy allows it.
2. Configure `ruff` for `src`, `Tests`, and `Tools`.
3. Keep generated Blender script strings excluded or explicitly ignored where needed.
4. Add CI lint only after local false positives are resolved.

Acceptance:

```text
python3 -m ruff check src Tests Tools
python3 -m unittest discover -s Tests
```

## Suggested Execution Order

1. Asset gate hardening: `release-check --assets`.
2. Bootstrap stub contract fix.
3. Runtime helper extraction from `cli.py`.
4. Manifest helper extraction.
5. Shared Blender discovery/version resolver.
6. USDZ binary inspection via `usdcat`.
7. `GameARView.swift` responsibility split.
8. Safe clean command and lint setup.

This order protects release correctness before maintainability refactors. The project is currently usable; these tasks make it harder for future asset work to regress silently.
