# Product Focus Cleanup Implementation Plan

> **For agentic workers:** Execute this plan task-by-task. In Codex, use `executing-plans` inline unless the user explicitly asks for subagents or parallel agent work. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Make the repository read, build, and hand off as one simple product: `rkp`, a command-first RealityKit asset pipeline toolkit, with `rkg` clearly treated as experimental labs work.

**Architecture:** This is a product-boundary cleanup, not a rewrite. Keep all working RKG functionality, but move it out of the primary user journey. The public first path becomes `rkp init -> make-asset -> inspect/verify -> accept -> release-check`; RKG remains documented under an explicit experimental/labs boundary.

**Tech Stack:** Python CLI package under `src/rkp` and `src/rkg`, repo-local wrappers in `Tools/`, Markdown docs under `Docs/`, Python `unittest`, Ruff, XcodeGen/iOS simulator build gates.

---

## Current Repo State

- Branch: `main`.
- Existing uncommitted work belongs to the previous RKG screenshot evidence sprint.
- Current dirty files:
  - `CHANGELOG.md`
  - `Docs/WORKLOG.md`
  - `Docs/ai-handoff.md`
  - `Docs/game-factory.md`
  - `Docs/rkg-architecture.md`
  - `README.md`
  - `Tests/test_rkg_archetype_runtime.py`
  - `Tests/test_rkg_content_views.py`
  - `Tests/test_rkg_init_game.py`
  - `Tests/test_rkg_store_pack.py`
  - `Tests/test_rkg_screenshot_status.py`
  - `src/rkg/archetype_runtime.py`
  - `src/rkg/cli.py`
  - `src/rkg/content_views.py`
  - `src/rkg/scaffold.py`
  - `src/rkg/screenshot_status.py`
  - `src/rkg/store_pack.py`
- Baseline verification already observed: `rtk make verify-local` exits `0` with 137 tests, compileall, Ruff, and `rkp doctor` OK.

## Scope

In scope:

- Stabilize and commit the current RKG screenshot evidence batch before product cleanup.
- Reframe public docs so `rkp` is the obvious primary product.
- Move `rkg` language into an explicit experimental/labs lane.
- Add small doc-boundary tests so future edits do not put RKG back into the main product path accidentally.
- Update worklog, handoff, changelog, and verification evidence.

Out of scope:

- Deleting RKG.
- Renaming CLI entry points.
- Changing asset loader behavior.
- Changing the RealityKit fixture app behavior.
- Generating new assets or screenshots.
- Publishing, tagging, or pushing unless explicitly requested.

## File Structure

Modify:

- `README.md`
  - Public first impression.
  - Must show `rkp` as the product in the opening section and quick start.
  - Must move `rkg` to an experimental/labs subsection.

- `Docs/ai-handoff.md`
  - Agent orientation.
  - Must make the first decision rule unambiguous: default to RKP work unless user explicitly asks for RKG.

- `Docs/cli-tool.md`
  - Main CLI guide.
  - Must present the normal `rkp` happy path before advanced or experimental surfaces.

- `Docs/game-factory.md`
  - RKG overview.
  - Must begin with the labs/experimental boundary and point back to RKP as the stable product.

- `Docs/rkg-architecture.md`
  - RKG internals.
  - Must be framed as architecture for experimental RKG work, not product overview.

- `CHANGELOG.md`
  - Must separate RKP product-facing changes from RKG Labs changes.

- `Docs/WORKLOG.md`
  - Must record the Product Focus Cleanup sprint, commands, decisions, and verification.

- `Tests/test_product_boundary_docs.py`
  - New focused unittest file that checks the docs preserve the product boundary.

Do not modify:

- `Sources/RealityKitPipelineDemo/*`
- `Tools/asset_manifest.json`
- `Assets/Imported/*`
- `project.yml`
- `RealityKitPipelineDemo.xcodeproj/*`

---

### Task 1: Checkpoint Current RKG Screenshot Evidence Work

**Files:**
- Review only: current dirty RKG and docs files.
- Commit existing dirty batch before product cleanup.

- [x] **Step 1: Inspect the dirty tree**

Run:

```bash
git status --short
git diff --stat
```

Expected:

```text
M CHANGELOG.md
M Docs/WORKLOG.md
M Docs/ai-handoff.md
M Docs/game-factory.md
M Docs/rkg-architecture.md
M README.md
M Tests/test_rkg_archetype_runtime.py
M Tests/test_rkg_content_views.py
M Tests/test_rkg_init_game.py
M Tests/test_rkg_store_pack.py
M src/rkg/archetype_runtime.py
M src/rkg/cli.py
M src/rkg/content_views.py
M src/rkg/scaffold.py
M src/rkg/store_pack.py
?? Tests/test_rkg_screenshot_status.py
?? src/rkg/screenshot_status.py
?? Docs/superpowers/plans/2026-05-10-product-focus-cleanup.md
```

- [x] **Step 2: Re-run the checkpoint verification**

Run:

```bash
rtk make verify-local
```

Expected:

```text
Ran 137 tests
OK
All checks passed!
pipeline doctor: ok
```

Negative-output lines from tests such as `release-check failed at step: assets` are acceptable only if the command exits `0`; those lines are expected test-fixture output.

- [x] **Step 3: Commit the previous sprint as its own unit**

Run:

```bash
git add CHANGELOG.md Docs/WORKLOG.md Docs/ai-handoff.md Docs/game-factory.md Docs/rkg-architecture.md README.md Tests/test_rkg_archetype_runtime.py Tests/test_rkg_content_views.py Tests/test_rkg_init_game.py Tests/test_rkg_store_pack.py Tests/test_rkg_screenshot_status.py src/rkg/archetype_runtime.py src/rkg/cli.py src/rkg/content_views.py src/rkg/scaffold.py src/rkg/screenshot_status.py src/rkg/store_pack.py
git commit -m "feat: add RKG screenshot evidence gate"
```

Expected:

```text
[main <sha>] feat: add RKG screenshot evidence gate
```

Rationale: Product cleanup should not be mixed with the previous RKG implementation batch.

Leave `Docs/superpowers/plans/2026-05-10-product-focus-cleanup.md` uncommitted in this step. It belongs to the product cleanup commit in Task 11.

---

### Task 2: Add Product Boundary Guard Tests

**Files:**
- Create: `Tests/test_product_boundary_docs.py`
- Test: `Tests/test_product_boundary_docs.py`

- [x] **Step 1: Write failing documentation boundary tests**

Create `Tests/test_product_boundary_docs.py`:

```python
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ProductBoundaryDocsTests(unittest.TestCase):
    def test_readme_opens_with_rkp_as_primary_product(self) -> None:
        readme = read("README.md")
        first_screen = readme[:1800]

        self.assertIn("command-first RealityKit asset pipeline toolkit", first_screen)
        self.assertIn("`rkp`", first_screen)
        self.assertIn("verification fixture", first_screen)
        self.assertLess(first_screen.index("`rkp`"), first_screen.index("`rkg`"))
        self.assertRegex(first_screen, r"rkg.*experimental|experimental.*rkg")

    def test_ai_handoff_defaults_future_agents_to_rkp(self) -> None:
        handoff = read("Docs/ai-handoff.md")
        first_section = handoff.split("## Completed Learning Modules", 1)[0]

        self.assertIn("default to `rkp`", first_section)
        self.assertIn("only work on `rkg`", first_section)
        self.assertIn("explicitly asks", first_section)

    def test_cli_doc_has_simple_rkp_happy_path_before_rkg(self) -> None:
        cli_doc = read("Docs/cli-tool.md")
        happy_path_match = re.search(
            r"rkp init[\s\S]+rkp make-asset[\s\S]+rkp inspect-usdz[\s\S]+rkp verify-asset[\s\S]+rkp release-check",
            cli_doc,
        )

        self.assertIsNotNone(happy_path_match)
        rkg_index = cli_doc.lower().find("rkg")
        if rkg_index != -1:
            self.assertLess(happy_path_match.start(), rkg_index)

    def test_rkg_docs_are_marked_as_labs(self) -> None:
        game_factory = read("Docs/game-factory.md")[:1200].lower()
        architecture = read("Docs/rkg-architecture.md")[:1200].lower()

        self.assertIn("experimental", game_factory)
        self.assertIn("labs", game_factory)
        self.assertIn("experimental", architecture)
        self.assertIn("labs", architecture)
```

- [x] **Step 2: Run the new tests and confirm they fail**

Run:

```bash
rtk .venv/bin/python -m unittest Tests/test_product_boundary_docs.py
```

Expected:

```text
FAILED
```

Expected failure reasons before implementation:

- `Docs/ai-handoff.md` does not yet contain the exact default-to-RKP rule.
- `Docs/cli-tool.md` may not include the concise happy path in the asserted order.
- RKG docs may not use the word `labs` in the first section.

---

### Task 3: Reframe README Around the RKP Happy Path

**Files:**
- Modify: `README.md`
- Test: `Tests/test_product_boundary_docs.py`

- [x] **Step 1: Replace the opening product framing**

In `README.md`, keep the title and screenshot, but make the first section say:

```markdown
# RealityKit Pipeline Toolkit

A command-first RealityKit asset pipeline toolkit for taking a gameplay asset from brief to Blender/USDZ output, RealityKit verification, simulator evidence, and release checks.

`rkp` is the product. The included SwiftUI + RealityKit target-shooting app is a verification fixture used to prove that generated or imported assets actually load in RealityKit. `rkg` is experimental labs work on top of the same pipeline; it is not the main user path.

Most RealityKit tutorials stop at code. This repo treats asset production as part of the game loop: each Blender/USDZ asset has a manifest entry, mobile budget, loader contract, screenshot, and learning note.
```

- [x] **Step 2: Replace `What This Is` with primary and labs lanes**

Use this structure near the top of `README.md`:

```markdown
## What This Is

Primary product:

- `rkp`: the installable CLI for asset status, validation, scaffolding, Blender builds, USDZ inspection, screenshot-based acceptance, tests, and release checks.
- `Skills/realitykit-pipeline-guide`: an installable Codex skill that points agents at the same asset, build, and documentation contracts.
- `.claude/commands`: slash commands such as `/rkp`, `/rkp-asset`, and `/rkp-status` for agent-style usage.
- `Sources/RealityKitPipelineDemo`: a small playable RealityKit verification fixture that proves pipeline output inside an iOS app.
- `Docs`: the teaching, production, and AI-agent handoff layer around the same pipeline.

Experimental labs:

- `rkg`: a game-factory research CLI for scoring ideas, validating specs, scaffolding small RealityKit projects, and generating QA/store-pack docs. Treat it as active research on top of RKP, not as a finished commercial game generator.
```

- [x] **Step 3: Add a short happy path before broader Quick Start text**

Add this under `## Quick Start` or directly before it:

```markdown
## The Normal RKP Path

```bash
rkp init --project-name MyGame
rkp make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
rkp inspect-usdz enemy_drone
rkp verify-asset enemy_drone --build
rkp release-check
```

When simulator evidence is available, accept the asset:

```bash
rkp accept-asset enemy_drone --screenshot Docs/screenshots/enemy_drone_imported.jpg
```

This is the product loop. Everything else in the repository exists to teach, verify, or extend that loop.
```

- [x] **Step 4: Keep the product boundary table but simplify wording**

Ensure the table still contains these rows in this order:

```markdown
| Surface | Maturity | Use it for | Do not assume |
| --- | --- | --- | --- |
| `rkp` asset pipeline | Preview, actively usable | Asset contracts, Blender/USDZ drafts, manifest health, screenshot acceptance, and release gates. | Fully automatic text-to-3D, automatic Xcode project edits, or asset acceptance without screenshot evidence. |
| RealityKit fixture app | Verification harness | Proving imported USDZ files load and behave inside RealityKit. | A production game architecture or the default destination for every generated asset. |
| Codex skill and docs | Teaching/handoff layer | Keeping agents and contributors on the same commands, contracts, and verification gates. | A standalone MCP server; JSON CLI output is the current automation surface. |
| `rkg` game factory | Experimental labs | GameSpec validation, small generated project scaffolds, archetype exploration, QA/store-pack planning. | A finished commercial game factory or automated App Store submission system. |
```

- [x] **Step 5: Run the README-focused test**

Run:

```bash
rtk .venv/bin/python -m unittest Tests.test_product_boundary_docs.ProductBoundaryDocsTests.test_readme_opens_with_rkp_as_primary_product
```

Expected:

```text
OK
```

---

### Task 4: Make AI Handoff Default to RKP

**Files:**
- Modify: `Docs/ai-handoff.md`
- Test: `Tests/test_product_boundary_docs.py`

- [x] **Step 1: Add an explicit default decision rule near the top**

After the first project-status paragraph in `Docs/ai-handoff.md`, add:

```markdown
Default decision rule: default to `rkp` asset-pipeline work unless the user explicitly asks for `rkg`, game factory, generated games, archetypes, store packs, or screenshot QA for generated projects. Only work on `rkg` when that experimental labs route is explicitly requested or when maintaining existing RKG tests/docs.
```

- [x] **Step 2: Split completed modules into product and labs groups**

Keep the current table content, but change the headings around it to this shape:

```markdown
## Product Surface

The stable product surface is the RKP pipeline:

- `Tools/rkp.py`
- `src/rkp`
- `Tools/asset_manifest.json`
- `Assets/Imported`
- `Docs/cli-tool.md`
- `Docs/guide.md`
- `Skills/realitykit-pipeline-guide`

## Experimental Labs Surface

RKG is useful but secondary:

- `Tools/rkg.py`
- `src/rkg`
- `Docs/game-factory.md`
- `Docs/rkg-architecture.md`
- `Tests/test_rkg_*.py`

Do not expand RKG while doing product-focus cleanup unless a test or doc boundary requires it.
```

- [x] **Step 3: Shorten the long portability paragraph**

Replace the long paragraph beginning with `Portability status:` with this shorter version:

```markdown
Portability status: `rkp` is installable, config-aware, and usable from external RealityKit projects. `rkp.json` marks the project root and configures manifest/assets/docs/blender/textures/source/tests/Xcode paths. The stable machine-readable surfaces are `rkp status --json` and `rkp doctor --json`. `rkg` also ships as an entry point, but it remains experimental labs work.
```

- [x] **Step 4: Update recommended next task**

Replace the current recommended task section with:

```markdown
## Current Recommended Next Task

Product focus cleanup:

1. Keep `rkp` as the first-screen product in README and docs.
2. Keep `rkg` under explicit experimental labs framing.
3. Preserve all current verification gates.
4. Avoid changing fixture app behavior.
5. After cleanup, run `rtk make verify-local`, manifest validation, and `rtk .venv/bin/python Tools/rkp.py release-check`.
```

- [x] **Step 5: Run the handoff-focused test**

Run:

```bash
rtk .venv/bin/python -m unittest Tests.test_product_boundary_docs.ProductBoundaryDocsTests.test_ai_handoff_defaults_future_agents_to_rkp
```

Expected:

```text
OK
```

---

### Task 5: Simplify the CLI Guide Around Five Normal Commands

**Files:**
- Modify: `Docs/cli-tool.md`
- Test: `Tests/test_product_boundary_docs.py`

- [x] **Step 1: Add a short primary path after the intro**

Insert this after the opening paragraphs:

```markdown
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
```

- [x] **Step 2: Rename broad sections to reduce cognitive load**

Use these section names in order:

```markdown
## Normal User Path
## Mental Model
## Daily RKP Commands
## Asset Creation Commands
## Asset Verification Commands
## Release and Cleanup Commands
## Automation JSON
## Advanced Backends
## v0.1 Limits
```

Do not remove command examples; move them under these headings if needed.

- [x] **Step 3: Keep RKG out of the normal CLI page**

If `Docs/cli-tool.md` mentions `rkg`, keep it below the RKP command sections and use this wording:

```markdown
`rkg` is documented separately in `Docs/game-factory.md` because it is experimental labs work, not the normal RKP asset pipeline.
```

- [x] **Step 4: Run the CLI-doc test**

Run:

```bash
rtk .venv/bin/python -m unittest Tests.test_product_boundary_docs.ProductBoundaryDocsTests.test_cli_doc_has_simple_rkp_happy_path_before_rkg
```

Expected:

```text
OK
```

---

### Task 6: Mark RKG Docs as Experimental Labs

**Files:**
- Modify: `Docs/game-factory.md`
- Modify: `Docs/rkg-architecture.md`
- Test: `Tests/test_product_boundary_docs.py`

- [x] **Step 1: Add labs banner to `Docs/game-factory.md`**

At the top, after the title, add:

```markdown
> **Experimental labs:** RKG explores game-factory workflows on top of the RKP asset pipeline. It is not the main product, not a finished app factory, and not the default path for contributors. Use RKP first unless the task explicitly asks for generated games, archetypes, store packs, or RKG screenshot QA.
```

- [x] **Step 2: Update the principle section**

Ensure `Docs/game-factory.md` says:

```markdown
RKP remains the stable RealityKit asset pipeline. RKG is the experimental labs layer above it.
```

- [x] **Step 3: Add labs banner to `Docs/rkg-architecture.md`**

At the top, after the title, add:

```markdown
> **Experimental labs architecture:** This document is for maintaining RKG internals. It should not be used as the main product overview. The main product overview is the RKP path in `README.md` and `Docs/cli-tool.md`.
```

- [x] **Step 4: Keep RKG ownership boundaries intact**

Confirm both docs still preserve this rule:

```markdown
RKG can call RKP commands. It cannot mark assets accepted without RKP screenshot evidence.
```

- [x] **Step 5: Run the RKG-doc test**

Run:

```bash
rtk .venv/bin/python -m unittest Tests.test_product_boundary_docs.ProductBoundaryDocsTests.test_rkg_docs_are_marked_as_labs
```

Expected:

```text
OK
```

---

### Task 7: Reorganize Changelog Without Hiding RKG

**Files:**
- Modify: `CHANGELOG.md`

- [x] **Step 1: Split `Unreleased` into product-facing groups**

Change `## Unreleased` to this shape:

```markdown
## Unreleased

### RKP Product Surface

- Clarified the public product boundary: RKP is the active toolkit surface, RKG is experimental labs, and the included app is a verification fixture.
- Added Makefile `bootstrap-dev` and `verify-local` targets for local contributor setup and lint/test/doctor verification.
- Hardened RKP release and asset verification gates with USDZ inspection, direct USDZ fallback handling, Blender diagnostics, and safer cleanup support.

### RKG Experimental Labs

- `rkg` RealityKit game-factory CLI surface for idea scoring, archetype discovery, spec validation, game planning, screenshot QA planning, project scaffolding, generated game verification, and store-pack checklist generation.
- Archetype registry for `target_shooter`, `lane_dodger`, `toss_physics`, `stack_puzzle`, and `wave_defense_lite`.
- `rkg qa-plan` command for machine-readable and text screenshot capture plans.
- `rkg verify-screenshots` command for checking generated screenshot evidence files against a `qa-plan --json` payload or generated project `GameSpec.json`.
- Minimal playable generated loops and RealityKit state-to-scene binding for the five seed archetypes.

### Fixture and Teaching

- Split the RealityKit fixture view into focused arena, target factory, hit-effect, and material helpers while preserving target fallback order.
- Clarified the multi-archetype RKG scope so target shooter remains one fixture, not the whole product.

### Verified

- `rtk make verify-local`
- `rtk .venv/bin/python Tools/rkp.py release-check`
- manifest validation
- XcodeGen project generation
- iOS simulator generic build
```

- [x] **Step 2: Preserve specific details when moving bullets**

Keep detailed RKG bullets if useful, but keep them under `### RKG Experimental Labs`. Do not let RKG bullets appear before RKP product bullets.

- [x] **Step 3: Run a changelog sanity check**

Run:

```bash
rtk rg -n "RKG Experimental Labs|RKP Product Surface|Verified" CHANGELOG.md
```

Expected:

```text
CHANGELOG.md:<line>:### RKP Product Surface
CHANGELOG.md:<line>:### RKG Experimental Labs
CHANGELOG.md:<line>:### Verified
```

---

### Task 8: Record the Product Focus Sprint

**Files:**
- Modify: `Docs/WORKLOG.md`

- [x] **Step 1: Add new sprint above Sprint 99**

Add:

```markdown
### Sprint 100: Product Focus Cleanup

**Durum:** Devam ediyor
**Tarih:** 2026-05-10
**Amaç:** Projeyi tek ana ürün omurgasına geri oturtmak: `rkp` aktif RealityKit asset pipeline tool'u, `rkg` ise açıkça experimental labs katmanı.

**Plan:**

- Mevcut RKG screenshot evidence işini ayrı checkpoint olarak kapat.
- README ilk ekranını `rkp` happy path'e indir.
- `Docs/ai-handoff.md` içine default-to-RKP karar kuralı ekle.
- `Docs/cli-tool.md` içinde normal kullanıcı yolunu beş komutluk RKP akışına sadeleştir.
- `Docs/game-factory.md` ve `Docs/rkg-architecture.md` dosyalarını experimental labs olarak işaretle.
- `CHANGELOG.md` içinde RKP product surface ve RKG experimental labs ayrımını görünür yap.
- Product boundary doc testleri ekle.

**Verification:**

```text
Bekleniyor: rtk .venv/bin/python -m unittest Tests/test_product_boundary_docs.py
Bekleniyor: rtk make verify-local
Bekleniyor: rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
Bekleniyor: rtk .venv/bin/python Tools/rkp.py release-check
Bekleniyor: rtk git diff --check
```

**Karar:**

Ürün vitrini `rkp` olacak. `rkg` korunacak, test edilecek ve dokümante edilecek; ancak README/CLI/handoff ana akışında experimental labs olarak kalacak.
```

- [x] **Step 2: After final verification, update status**

After Task 10 passes, change:

```markdown
**Durum:** Devam ediyor
```

to:

```markdown
**Durum:** Tamamlandı
```

Replace `Bekleniyor:` lines with actual results.

---

### Task 9: Run Focused Tests and Fix Drift

**Files:**
- Modify as needed only in files from previous tasks.
- Test: `Tests/test_product_boundary_docs.py`

- [x] **Step 1: Run the new boundary test file**

Run:

```bash
rtk .venv/bin/python -m unittest Tests/test_product_boundary_docs.py
```

Expected:

```text
Ran 4 tests
OK
```

- [x] **Step 2: If a test fails, fix the doc text rather than weakening the test**

Acceptable fixes:

- Move the RKP happy path earlier in `README.md` or `Docs/cli-tool.md`.
- Add the exact `default to \`rkp\`` wording to `Docs/ai-handoff.md`.
- Add `experimental labs` wording to RKG docs.

Do not:

- Delete RKG references.
- Change tests to allow RKG to appear before RKP in the first-screen docs.
- Add vague wording like "may be experimental" instead of the direct labs boundary.

- [x] **Step 3: Run all Python tests**

Run:

```bash
rtk .venv/bin/python -m unittest discover -s Tests
```

Expected:

```text
OK
```

Test count should be at least 141 after adding the 4 boundary tests.

---

### Task 10: Full Verification Gate

**Files:**
- No new edits unless verification reveals a real issue.

- [x] **Step 1: Run local verification**

Run:

```bash
rtk make verify-local
```

Expected:

```text
compileall ok
Ruff ok
unittest OK
pipeline doctor: ok
```

- [x] **Step 2: Validate manifest**

Run:

```bash
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
```

Expected:

```text
manifest ok
```

- [x] **Step 3: Run release check**

Run:

```bash
rtk .venv/bin/python Tools/rkp.py release-check
```

Expected:

```text
release-check ok
```

CoreSimulator sandbox warnings are acceptable only if the command exits `0`.

- [x] **Step 4: Check whitespace**

Run:

```bash
rtk git diff --check
```

Expected: no output and exit `0`.

- [x] **Step 5: Inspect final diff**

Run:

```bash
git diff --stat
git diff -- README.md Docs/ai-handoff.md Docs/cli-tool.md Docs/game-factory.md Docs/rkg-architecture.md CHANGELOG.md Docs/WORKLOG.md Tests/test_product_boundary_docs.py
```

Expected:

- Only docs and the new boundary test changed.
- No source code under `src/rkp`, `src/rkg`, or `Sources/RealityKitPipelineDemo` changed during product cleanup.
- No asset files changed.

---

### Task 11: Commit Product Focus Cleanup

**Files:**
- Commit product cleanup batch.

- [x] **Step 1: Stage the cleanup files**

Run:

```bash
git add README.md Docs/ai-handoff.md Docs/cli-tool.md Docs/game-factory.md Docs/rkg-architecture.md CHANGELOG.md Docs/WORKLOG.md Tests/test_product_boundary_docs.py Docs/superpowers/plans/2026-05-10-product-focus-cleanup.md
```

- [x] **Step 2: Commit**

Run:

```bash
git commit -m "docs: refocus repository around RKP product path"
```

Expected:

```text
[main <sha>] docs: refocus repository around RKP product path
```

- [x] **Step 3: Confirm clean working tree**

Run:

```bash
git status --short
```

Expected:

```text
```

No output.

---

## Self-Review Checklist

- [x] README first screen says `rkp` is the product.
- [x] README still mentions `rkg`, but only as experimental labs.
- [x] `Docs/ai-handoff.md` tells future agents to default to RKP unless RKG is explicitly requested.
- [x] `Docs/cli-tool.md` starts with the normal five-command RKP path.
- [x] RKG docs preserve useful architecture while clearly marking labs status.
- [x] Changelog separates RKP product surface from RKG experimental labs.
- [x] No asset, fixture app, or CLI behavior changed.
- [x] `rtk make verify-local` passed.
- [x] `rtk .venv/bin/python Tools/rkp.py release-check` passed.
- [x] Product-boundary tests passed.

## Execution Notes

Recommended execution mode: inline execution in this session using `executing-plans`, with a checkpoint after Task 1 and another after Task 6.

Do not use subagents unless explicitly requested; the work is mostly docs plus one small test file, and parallel edits would add merge risk without much benefit.
