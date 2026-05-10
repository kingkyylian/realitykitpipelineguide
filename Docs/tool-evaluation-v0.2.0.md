# RKP Tool Evaluation: v0.2.0 Release and v0.2.1 Patch Candidate

Date: 2026-05-10

Purpose: test the published tool like an external user before moving to Module 4 texture/material work.

## Scope

This pass tested:

- GitHub tag install from `v0.2.0`.
- Clean external project bootstrap.
- Prompt-backed asset creation.
- Direct USDZ fallback build.
- USDZ inspection.
- Asset verification.
- Screenshot acceptance.
- Release checks with and without imported assets.
- Common failure paths and error messages.
- Local fixes prepared for a `0.2.1` patch candidate.

## Environments

| Environment | Install Source | Project Path | Result |
| --- | --- | --- | --- |
| Published release | `git+https://github.com/kingkyylian/realitykitpipelineguide.git@v0.2.0` | `/private/tmp/rkp-eval-v020-a` | Install and CLI worked, but package version reported `0.1.0`. |
| Local patch candidate | local checkout after fixes | `/private/tmp/rkp-eval-local-021-a` | Install built `rkp-0.2.1`; external project flow worked. |

## Positive Findings

- `rkp init --project-name EvalGame` creates a minimal external project without pulling in repository-specific files.
- `rkp doctor --json` reports zero errors in a minimal external project and correctly treats missing `README.md`, `LICENSE`, and `Makefile` as warnings.
- `rkp status --json` is clean enough for automation and works from nested directories.
- `rkp make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"` records the prompt, creates a brief, writes a Blender generator, and selects the expected `drone` archetype.
- `rkp build-asset enemy_drone --fallback-only` produces a compact USDZ draft without Blender.
- `rkp inspect-usdz enemy_drone --json` verified the fallback USDZ with texture, UV, and budget data: 804 triangles, 512x512 base color texture, `primvars:st` present.
- `rkp verify-asset enemy_drone` runs the inspect gate and points to the next screenshot acceptance command.
- `rkp accept-asset` rejects missing screenshot paths.
- `rkp release-check --assets` inspects imported assets and skips Xcode only when `xcode_project` is not configured.
- Error messages for unknown assets, non-snake-case ids, duplicate init, invalid `BLENDER`, and missing generated project files are direct enough to act on.

## Critical Findings

### 1. Published `v0.2.0` Reports Package Version `0.1.0`

Observed from a clean GitHub tag install:

```text
Successfully installed PyYAML-6.0.3 rkp-0.1.0
rkp --version -> rkp 0.1.0
```

Impact: users cannot trust `rkp --version` to identify the release they installed from `v0.2.0`.

Status: fixed locally for the patch candidate by setting `pyproject.toml`, `src/rkp/__init__.py`, and `src/rkg/__init__.py` to `0.2.1`.

### 2. Published `v0.2.0` Accepts Non-Image Screenshot Evidence

Observed in the external `v0.2.0` install:

```text
file Docs/screenshots/not_an_image.jpg -> JSON data
rkp accept-asset fake_screenshot_asset --screenshot Docs/screenshots/not_an_image.jpg
accepted asset: fake_screenshot_asset
manifest status: imported
```

Impact: a user can accidentally mark an asset as `imported` with a non-image file.

Status: fixed locally for the patch candidate. `accept-asset` now rejects files that are not PNG or JPEG by header.

## Realistic Limitations

- Screenshot acceptance still proves image-file validity, not semantic visual correctness. A valid JPEG of the wrong scene can still pass; human visual QA or simulator automation is still required.
- `release-check` returns success for minimal external projects when tests and Xcode are not configured. This is useful for portability, but the output must be read carefully because it means "pipeline checks passed with skipped gates", not "production app release is fully proven".
- `make-asset --build` does not expose `--fallback-only`; Blender-free users need the two-step path: `make-asset`, then `build-asset --fallback-only`.
- The fallback builder depends on `usdzip`. It worked locally, but machines without `usdzip` still need setup guidance.
- The package still installs both `rkp` and experimental `rkg`; docs mark `rkg` as labs, but the entry point is visible to users.

## Patch Candidate Verification

Local `0.2.1` candidate checks:

```text
/private/tmp/rkp-install-local-021-a/bin/rkp --version: rkp 0.2.1
rkp init --project-name EvalGamePatch: ok
rkp make-asset patch_drone --type gameplay_target --prompt "red bullseye drone target": ok
rkp build-asset patch_drone --fallback-only: ok, 16068-byte USDZ
rkp inspect-usdz patch_drone --json: ok, 804 triangles, 512x512 base color, UV present
rkp accept-asset patch_drone --screenshot Docs/screenshots/not_an_image.jpg: rejected, not a valid PNG or JPEG image
rkp accept-asset patch_drone --screenshot Docs/screenshots/patch_drone_imported.jpg: ok
rkp release-check --assets: ok
```

Repository verification after fixes:

```text
rtk .venv/bin/python -m unittest Tests/test_release_docs.py Tests/test_rkp_cli.py Tests/test_rkp_package.py Tests/test_rkp_project.py: ok, 50 tests
rtk git diff --check: ok
```

## Recommendation

Do not start Module 4 from the published `v0.2.0` state. First finish the `0.2.1` patch candidate, run full local verification, push, wait for CI, and publish `v0.2.1`.

After `v0.2.1`, the tool is strong enough for Module 4 authoring, with one caveat: visual proof is still human-reviewed screenshot evidence unless a future simulator capture checker is added.
