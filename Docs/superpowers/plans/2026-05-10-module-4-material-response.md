# Module 4 Material Response Implementation Plan

> **For agentic workers:** Execute this plan task-by-task. In Codex, use `executing-plans` inline unless the user explicitly asks for subagents or parallel agent work. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Start Module 4 by proving a small roughness value vs roughness map workflow through RKP inspection, RealityKit fixture loading, screenshot evidence, and teaching docs.

**Architecture:** Keep `rkp` as the product surface and keep the existing target fallback order intact. Add material-map inspection to the CLI, then add one explicit material-response showcase asset and an opt-in fixture launch mode for visual comparison. Do not make the normal game loop depend on the new Module 4 asset.

**Tech Stack:** Python 3.10+, `unittest`, Ruff, RKP CLI, Blender/USDZ authoring scripts, SwiftUI + RealityKit fixture, XcodeGen, simulator screenshot evidence, Markdown docs/PDF.

---

## Current Repo State

- Branch: `main`.
- Latest published tag: `v0.2.1` at `4a11327`.
- Working tree should start clean.
- Current RKP status:
  - `target_basic`: `imported`
  - `target_basic_textured`: `imported`
  - `arena_floor`: `imported`
  - `enemy_drone`: `imported`
- `rkp doctor --json` is clean.
- `target_basic_textured` inspection passes with:
  - 284 triangles
  - 512x512 baseColor texture
  - `primvars:st` present
- Known doc drift:
  - `Docs/ai-handoff.md` still says to finish/publish `v0.2.1`.
  - `Docs/WORKLOG.md` Sprint 107 still describes `0.2.1` as a patch candidate in its decision text.

## Scope

In scope:

- Make handoff/worklog reflect that `v0.2.1` is already published.
- Optionally smoke test a clean install from the published `v0.2.1` tag.
- Extend `inspect-usdz` so configured material maps are visible in JSON/text output.
- Add one Module 4 showcase asset contract: `material_response_targets`.
- Add an opt-in fixture mode that displays the showcase asset without changing default target loading.
- Capture simulator evidence and accept the asset only after visual proof exists.
- Update the teaching guide, Blender checklist, worklog, handoff, manifest, and PDF.

Out of scope:

- Rewriting the target game loop.
- Changing `TargetFactory` fallback order.
- Adding automatic semantic screenshot analysis.
- Publishing a new release unless explicitly requested.
- Expanding `rkg`.
- Adding normal maps in this slice; normal maps stay a planned follow-up.

## File Structure

Create:

- `Tools/blender/create_material_response_targets.py`
  - Blender authoring script for the Module 4 comparison asset.
  - Creates baseColor and roughness textures.
  - Exports `Assets/Imported/material_response_targets.usdz`.

- `Docs/assets/material_response_targets.md`
  - Asset brief and acceptance checklist.

- `Sources/RealityKitPipelineDemo/MaterialResponseShowcase.swift`
  - Opt-in visual fixture for the material-response asset.
  - Loads `material_response_targets` if present.
  - Falls back to procedural comparison panels if the asset is missing.

Modify:

- `src/rkp/asset_manifest.py`
  - Add map-name to expected texture-name helpers.
  - Preserve `expected_basecolor_name` for existing callers.

- `src/rkp/inspect_usdz.py`
  - Report every configured `textureMaps` item.
  - Keep the existing `baseColorTexture` JSON key as a compatibility alias.

- `Tests/test_rkp_project.py`
  - Add tests for material-map inspection.

- `Tests/test_fixture_refactor.py`
  - Guard that the new showcase is opt-in and default target fallback order remains unchanged.

- `Tests/test_release_docs.py`
  - Guard that handoff knows `v0.2.1` is published and Module 4 is next.

- `Tools/asset_manifest.json`
  - Add `material_response_targets`.

- `Docs/guide.md`
  - Turn Planned Module 4 into a started/completed first exercise after evidence exists.

- `Docs/blender-usdz-checklist.md`
  - Add roughness-map rules after baseColor success.

- `Docs/WORKLOG.md`
  - Add Sprint 108 for Module 4.

- `Docs/ai-handoff.md`
  - Set next task to Module 4 or post-release demo, not `v0.2.1` publication.

- `Docs/pdf/realitykit-pipeline-guide.pdf`
  - Regenerate if `Docs/guide.md` changes.

Do not modify:

- `TargetFactory.swift` fallback order, except reading it in tests.
- Existing imported USDZ assets.
- Existing release tags.

---

### Task 1: Align Post-Release Handoff State

**Files:**
- Modify: `Tests/test_release_docs.py`
- Modify: `Docs/ai-handoff.md`
- Modify: `Docs/WORKLOG.md`

- [ ] **Step 1: Write a failing handoff freshness test**

Append this test to `Tests/test_release_docs.py`:

```python
    def test_handoff_knows_v021_is_published_and_module4_is_next(self) -> None:
        handoff = read("Docs/ai-handoff.md")
        current_task = handoff.split("## Current Recommended Next Task", 1)[1].split("## Key Files", 1)[0]

        self.assertIn("`v0.2.1` is published", current_task)
        self.assertIn("Module 4", current_task)
        self.assertNotIn("finish and publish `v0.2.1`", current_task)
```

- [ ] **Step 2: Run the targeted test and confirm failure**

Run:

```bash
rtk .venv/bin/python -m unittest Tests.test_release_docs.ReleaseDocsTests.test_handoff_knows_v021_is_published_and_module4_is_next
```

Expected:

```text
FAIL
'`v0.2.1` is published' not found
```

- [ ] **Step 3: Update the handoff next-task block**

Replace the `## Current Recommended Next Task` section in `Docs/ai-handoff.md` with:

```markdown
## Current Recommended Next Task

Post-release state: `v0.2.1` is published and GitHub Actions passed on the release commit. Do not rewrite `v0.2.0` or `v0.2.1`; use a future patch release for corrections.

Recommended next path:

1. Optionally run one final clean install smoke test from the published `v0.2.1` tag.
2. Start Module 4: Texture Maps and Material Response.
3. Keep the first Module 4 slice small: roughness value vs roughness map comparison, simulator screenshot evidence, manifest/worklog/guide update.
4. Use `Docs/blender-support.md` when answering Blender/fallback setup questions.
5. Use `Docs/first-good-issues.md` when creating learner-friendly issue candidates.
```

- [ ] **Step 4: Update Sprint 107 decision text**

In `Docs/WORKLOG.md`, change the Sprint 107 `**Karar:**` paragraph from patch-candidate wording to:

```markdown
**Karar:**

`v0.2.0` release geri yazılmayacak. Düzeltmeler `v0.2.1` patch release olarak yayınlandı; sonraki düzeltmeler yeni patch release ile yapılacak. Module 4'e geçmeden önce istenirse son bir temiz tag-install smoke test çalıştırılabilir.
```

- [ ] **Step 5: Re-run release docs tests**

Run:

```bash
rtk .venv/bin/python -m unittest Tests/test_release_docs.py
```

Expected:

```text
OK
```

Commit checkpoint:

```bash
rtk git add Tests/test_release_docs.py Docs/ai-handoff.md Docs/WORKLOG.md
rtk git commit -m "docs: align v0.2.1 handoff state"
```

Skip the commit if the user wants one combined Module 4 commit.

---

### Task 2: Smoke Test Published v0.2.1 Tag

**Files:**
- No repo file changes unless documenting the result in Task 7.

- [ ] **Step 1: Install from the published tag in a disposable pipx environment**

Run:

```bash
pipx install --force git+https://github.com/kingkyylian/realitykitpipelineguide.git@v0.2.1
```

Expected:

```text
installed package rkp 0.2.1
```

Network access may require approval in Codex. If network is blocked, do not work around it silently; record the smoke test as not run.

- [ ] **Step 2: Confirm release identity**

Run:

```bash
rkp --version
```

Expected:

```text
rkp 0.2.1
```

- [ ] **Step 3: Bootstrap a clean external project**

Run:

```bash
rm -rf /private/tmp/rkp-v021-smoke
mkdir -p /private/tmp/rkp-v021-smoke
cd /private/tmp/rkp-v021-smoke
rkp init --project-name SmokeGame
rkp doctor --json
```

Expected:

```json
{
  "errors": 0,
  "ok": true
}
```

- [ ] **Step 4: Build and inspect one fallback draft**

Run:

```bash
rkp make-asset smoke_drone --type gameplay_target --prompt "red bullseye drone target"
rkp build-asset smoke_drone --fallback-only
rkp inspect-usdz smoke_drone --json
```

Expected:

```text
"ok": true
"baseColorTexture": { ... "present": true ... }
```

Record the smoke-test result in `Docs/WORKLOG.md` during Task 7.

---

### Task 3: Add Material Map Inspection Contract

**Files:**
- Modify: `src/rkp/asset_manifest.py`
- Modify: `src/rkp/inspect_usdz.py`
- Modify: `Tests/test_rkp_project.py`

- [ ] **Step 1: Write failing material-map inspection tests**

Add this helper parameter to `add_inspectable_usdz_asset` in `Tests/test_rkp_project.py`:

```python
        texture_maps: list[str] | None = None,
        extra_textures: dict[str, tuple[int, int]] | None = None,
```

Inside the manifest asset, replace the fixed texture maps with:

```python
                "textureMaps": texture_maps or ["baseColor"],
```

Inside the archive-writing block, after the existing base texture write, add:

```python
            for extra_name, extra_size in (extra_textures or {}).items():
                archive.writestr(f"textures/{extra_name}", self.png_bytes(*extra_size))
```

Then add these tests:

```python
    def test_inspect_usdz_reports_configured_material_maps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_inspectable_usdz_asset(
                root,
                "material_maps",
                texture_name="material_maps_basecolor.png",
                texture_size=(512, 512),
                texture_maps=["baseColor", "roughness"],
                extra_textures={"material_maps_roughness.png": (512, 512)},
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "Tools" / "rkp.py"), "inspect-usdz", "material_maps", "--json"],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["textureMaps"]["baseColor"]["present"])
            self.assertTrue(payload["textureMaps"]["roughness"]["present"])
            self.assertEqual(payload["textureMaps"]["roughness"]["width"], 512)
            self.assertEqual(payload["textureMaps"]["roughness"]["height"], 512)
            self.assertEqual(payload["textureMaps"]["roughness"]["sizeStatus"], "ok")
            self.assertEqual(payload["baseColorTexture"], payload["textureMaps"]["baseColor"])

    def test_inspect_usdz_rejects_missing_roughness_map_when_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_inspectable_usdz_asset(
                root,
                "missing_roughness",
                texture_name="missing_roughness_basecolor.png",
                texture_size=(512, 512),
                texture_maps=["baseColor", "roughness"],
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "Tools" / "rkp.py"), "inspect-usdz", "missing_roughness", "--json"],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["textureMaps"]["roughness"]["present"])
            self.assertIn("roughness texture missing from USDZ", payload["errors"])
```

- [ ] **Step 2: Run the tests and confirm failure**

Run:

```bash
rtk .venv/bin/python -m unittest Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_reports_configured_material_maps Tests.test_rkp_project.RkpProjectTests.test_inspect_usdz_rejects_missing_roughness_map_when_configured
```

Expected:

```text
ERROR or FAIL
KeyError: 'textureMaps'
```

- [ ] **Step 3: Add texture map helpers**

In `src/rkp/asset_manifest.py`, add:

```python
TEXTURE_MAP_SUFFIXES = {
    "baseColor": "basecolor",
    "roughness": "roughness",
    "metallic": "metallic",
    "normal": "normal",
}
```

Add:

```python
def texture_map_names(asset: Asset) -> list[str]:
    texture_maps = asset.get("textureMaps")
    if isinstance(texture_maps, list):
        return [str(name) for name in texture_maps]
    return ["baseColor"]


def expected_texture_name(asset: Asset, map_name: str) -> str | None:
    suffix = TEXTURE_MAP_SUFFIXES.get(map_name)
    if suffix is None:
        return None
    if map_name not in texture_map_names(asset):
        return None
    return f"{asset['id']}_{suffix}.png"
```

Update `expected_basecolor_name`:

```python
def expected_basecolor_name(asset: Asset) -> str | None:
    return expected_texture_name(asset, "baseColor")
```

- [ ] **Step 4: Report all configured maps from inspect-usdz**

In `src/rkp/inspect_usdz.py`, update imports:

```python
from rkp.asset_manifest import asset_usdz_path, expected_basecolor_name, expected_texture_name, load_asset, texture_map_names
```

Initialize the payload with both keys:

```python
        "textureMaps": {},
        "baseColorTexture": {},
```

Before scanning the zip, populate map records:

```python
    for map_name in texture_map_names(asset):
        expected_name = expected_texture_name(asset, map_name)
        if expected_name is None:
            continue
        payload["textureMaps"][map_name] = {
            "expected": expected_name,
            "present": False,
            "width": None,
            "height": None,
            "maxSize": asset.get("maxTextureSize"),
            "sizeStatus": "unknown",
        }
    payload["baseColorTexture"] = payload["textureMaps"].get("baseColor", {
        "expected": expected_basecolor_name(asset),
        "present": None,
        "width": None,
        "height": None,
        "maxSize": asset.get("maxTextureSize"),
        "sizeStatus": "not_required",
    })
```

Inside the archive block, replace the single baseColor scan with:

```python
            for map_name, record in payload["textureMaps"].items():
                texture_member = next((name for name in entries if Path(name).name == record["expected"]), None)
                record["present"] = texture_member is not None
                if texture_member:
                    dimensions = image_dimensions(archive.read(texture_member))
                    if dimensions:
                        width, height = dimensions
                        record["width"] = width
                        record["height"] = height
                        max_size = record["maxSize"]
                        if max_size is not None:
                            record["sizeStatus"] = "ok" if max(width, height) <= max_size else "over"
            payload["baseColorTexture"] = payload["textureMaps"].get("baseColor", payload["baseColorTexture"])
```

Replace baseColor-only error checks with:

```python
    for map_name, record in payload["textureMaps"].items():
        if not record["present"]:
            payload["errors"].append(f"{map_name} texture missing from USDZ")
        if record["sizeStatus"] == "over":
            payload["errors"].append(f"{map_name} texture exceeds manifest maxTextureSize")
```

Keep `print_text` backward-readable by printing baseColor first, then additional maps:

```python
    for map_name, record in payload.get("textureMaps", {}).items():
        if map_name == "baseColor":
            continue
        status = "present" if record.get("present") else "missing"
        width = record.get("width")
        height = record.get("height")
        size = "unknown" if width is None or height is None else f"{width}x{height}"
        print(f"{map_name} texture: {status}, size: {size}")
```

- [ ] **Step 5: Run targeted and full Python tests**

Run:

```bash
rtk .venv/bin/python -m unittest Tests/test_rkp_project.py
rtk .venv/bin/python -m unittest discover -s Tests
```

Expected:

```text
OK
```

Commit checkpoint:

```bash
rtk git add src/rkp/asset_manifest.py src/rkp/inspect_usdz.py Tests/test_rkp_project.py
rtk git commit -m "feat: inspect configured material maps"
```

---

### Task 4: Add Module 4 Asset Contract and Authoring Script

**Files:**
- Create: `Tools/blender/create_material_response_targets.py`
- Create: `Docs/assets/material_response_targets.md`
- Modify: `Tools/asset_manifest.json`

- [ ] **Step 1: Add manifest entry**

Add this object to `Tools/asset_manifest.json`:

```json
{
  "id": "material_response_targets",
  "file": "material_response_targets.usdz",
  "type": "material_response_showcase",
  "status": "planned",
  "maxTriangles": 1800,
  "maxTextureSize": 1024,
  "textureMaps": [
    "baseColor",
    "roughness"
  ],
  "notes": "Module 4 comparison asset for roughness value versus roughness map behavior. Three small target panels should show matte value, glossy value, and roughness-map variation under the same RealityKit lighting. Accept only after simulator screenshot evidence is captured."
}
```

- [ ] **Step 2: Add the asset brief**

Create `Docs/assets/material_response_targets.md`:

```markdown
# Asset Brief: material_response_targets

## Gameplay Need

Teach Module 4 material response with one compact comparison asset that can be loaded in the RealityKit fixture without changing the normal target fallback path.

## Visual Contract

- Three target-like panels are visible side by side.
- Left panel: high roughness material value, matte response.
- Center panel: low roughness material value, glossier response.
- Right panel: roughness map variation, visibly mixed matte/gloss bands.
- All panels use the same readable base color ring language as `target_basic_textured`.
- Texture size starts at 512x512.

## Technical Contract

- Asset id: `material_response_targets`
- Runtime file: `Assets/Imported/material_response_targets.usdz`
- Source script: `Tools/blender/create_material_response_targets.py`
- Base color texture: `material_response_targets_basecolor.png`
- Roughness texture: `material_response_targets_roughness.png`
- UV primvar: `st`
- Max triangles: 1800
- Max texture size: 1024

## Acceptance Checklist

- [ ] USDZ exported to `Assets/Imported/material_response_targets.usdz`.
- [ ] `rkp inspect-usdz material_response_targets --json` passes.
- [ ] RealityKit fixture launched with `--material-response-mode`.
- [ ] Simulator screenshot captured at `Docs/screenshots/material_response_targets.jpg`.
- [ ] `rkp accept-asset material_response_targets --screenshot Docs/screenshots/material_response_targets.jpg` passes.
- [ ] `Docs/WORKLOG.md` records what was visually readable and what was not.
```

- [ ] **Step 3: Add the Blender script**

Create `Tools/blender/create_material_response_targets.py` using the existing generated-script style. The script should:

- Create three circular target panels.
- Use one 512x512 base color texture.
- Use one 512x512 roughness map texture.
- Assign roughness values to two panels and the roughness map to the third.
- Export USDZ with materials, textures, and UV maps.

Use this complete starting script:

```python
from __future__ import annotations

import math
from pathlib import Path

import bpy

ASSET_ID = "material_response_targets"
ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "Assets" / "Imported"
TEXTURE_DIR = ROOT / "Assets" / "Textures"
OUTPUT_PATH = ASSET_DIR / f"{ASSET_ID}.usdz"
BASECOLOR_PATH = TEXTURE_DIR / f"{ASSET_ID}_basecolor.png"
ROUGHNESS_PATH = TEXTURE_DIR / f"{ASSET_ID}_roughness.png"


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def write_texture(path: Path, roughness: bool = False) -> bpy.types.Image:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = bpy.data.images.new(path.stem, width=512, height=512)
    pixels: list[float] = []
    for y in range(512):
        for x in range(512):
            u = (x + 0.5) / 512
            v = (y + 0.5) / 512
            dx = u - 0.5
            dy = v - 0.5
            radius = math.sqrt(dx * dx + dy * dy)
            if roughness:
                value = 0.18 if int(u * 8) % 2 == 0 else 0.86
                pixels.extend([value, value, value, 1.0])
            elif radius < 0.14:
                pixels.extend([0.92, 0.08, 0.05, 1.0])
            elif radius < 0.28:
                pixels.extend([0.96, 0.94, 0.88, 1.0])
            elif radius < 0.42:
                pixels.extend([0.74, 0.05, 0.04, 1.0])
            else:
                pixels.extend([0.05, 0.055, 0.06, 1.0])
    image.pixels[:] = pixels
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    image.save()
    return image


def make_material(name: str, base_image: bpy.types.Image, roughness_value: float, roughness_image: bpy.types.Image | None) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    base = nodes.new(type="ShaderNodeTexImage")
    base.image = base_image
    base.extension = "CLIP"
    base_uv = nodes.new(type="ShaderNodeUVMap")
    base_uv.uv_map = "st"
    material.node_tree.links.new(base_uv.outputs["UV"], base.inputs["Vector"])
    material.node_tree.links.new(base.outputs["Color"], principled.inputs["Base Color"])
    principled.inputs["Roughness"].default_value = roughness_value
    principled.inputs["Metallic"].default_value = 0.0
    if roughness_image is not None:
        rough = nodes.new(type="ShaderNodeTexImage")
        rough.image = roughness_image
        rough.extension = "CLIP"
        rough_uv = nodes.new(type="ShaderNodeUVMap")
        rough_uv.uv_map = "st"
        material.node_tree.links.new(rough_uv.outputs["UV"], rough.inputs["Vector"])
        material.node_tree.links.new(rough.outputs["Color"], principled.inputs["Roughness"])
    return material


def create_panel(name: str, x_offset: float, material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.32, depth=0.035, location=(x_offset, 0.36, -1.75), rotation=(math.pi / 2, 0, 0))
    panel = bpy.context.object
    panel.name = name
    panel.data.name = f"{name}_mesh"
    panel.data.materials.append(material)
    uv_layer = panel.data.uv_layers.new(name="st") if not panel.data.uv_layers else panel.data.uv_layers[0]
    uv_layer.name = "st"
    for polygon in panel.data.polygons:
        for loop_index in polygon.loop_indices:
            vertex = panel.data.vertices[panel.data.loops[loop_index].vertex_index].co
            uv_layer.data[loop_index].uv = ((vertex.x / 0.64) + 0.5, (vertex.y / 0.64) + 0.5)
    return panel


def main() -> None:
    reset_scene()
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    base = write_texture(BASECOLOR_PATH)
    roughness = write_texture(ROUGHNESS_PATH, roughness=True)
    matte = make_material("matte_value_roughness_086", base, 0.86, None)
    glossy = make_material("glossy_value_roughness_018", base, 0.18, None)
    mapped = make_material("mapped_roughness_bands", base, 0.5, roughness)
    create_panel("matte_value_panel", -0.46, matte)
    create_panel("glossy_value_panel", 0.0, glossy)
    create_panel("roughness_map_panel", 0.46, mapped)
    bpy.ops.wm.usd_export(
        filepath=str(OUTPUT_PATH),
        selected_objects_only=False,
        export_materials=True,
        export_textures=True,
        export_textures_mode="NEW",
        export_uvmaps=True,
    )
    print(f"exported {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Validate manifest JSON**

Run:

```bash
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
```

Expected:

```text
manifest ok
```

---

### Task 5: Add Opt-In RealityKit Showcase Mode

**Files:**
- Create: `Sources/RealityKitPipelineDemo/MaterialResponseShowcase.swift`
- Modify: `Sources/RealityKitPipelineDemo/GameARView.swift`
- Modify: `Tests/test_fixture_refactor.py`

- [ ] **Step 1: Write failing fixture guard tests**

Append to `Tests/test_fixture_refactor.py`:

```python
    def test_material_response_showcase_is_opt_in(self) -> None:
        showcase = SOURCE_DIR / "MaterialResponseShowcase.swift"
        game_ar_view = (SOURCE_DIR / "GameARView.swift").read_text(encoding="utf-8")
        target_factory = (SOURCE_DIR / "TargetFactory.swift").read_text(encoding="utf-8")

        self.assertTrue(showcase.exists())
        text = showcase.read_text(encoding="utf-8")
        self.assertIn('"material_response_targets"', text)
        self.assertIn("ImportedAssetLoader.loadModel", text)
        self.assertIn('"--material-response-mode"', game_ar_view)
        self.assertIn("MaterialResponseShowcase.add", game_ar_view)
        self.assertNotIn('"material_response_targets"', target_factory)
```

- [ ] **Step 2: Run the test and confirm failure**

Run:

```bash
rtk .venv/bin/python -m unittest Tests.test_fixture_refactor.FixtureRefactorTests.test_material_response_showcase_is_opt_in
```

Expected:

```text
FAIL
MaterialResponseShowcase.swift does not exist
```

- [ ] **Step 3: Create MaterialResponseShowcase.swift**

Create `Sources/RealityKitPipelineDemo/MaterialResponseShowcase.swift`:

```swift
import RealityKit
import UIKit

enum MaterialResponseShowcase {
    static func add(to worldAnchor: Entity) {
        if let model = ImportedAssetLoader.loadModel(named: "material_response_targets") {
            model.name = "material_response_targets"
            model.position = [0, 0.0, 0]
            model.scale = SIMD3<Float>(repeating: 1.0)
            worldAnchor.addChild(model)
            return
        }

        addProceduralFallback(to: worldAnchor)
    }

    private static func addProceduralFallback(to worldAnchor: Entity) {
        let panels: [(Float, Float, UIColor)] = [
            (-0.46, 0.86, UIColor(red: 0.72, green: 0.08, blue: 0.06, alpha: 1)),
            (0.0, 0.18, UIColor(red: 0.88, green: 0.10, blue: 0.07, alpha: 1)),
            (0.46, 0.52, UIColor(red: 0.78, green: 0.18, blue: 0.12, alpha: 1))
        ]

        for (x, roughness, color) in panels {
            let material = RealityMaterials.pbr(color: color, roughness: roughness, metallic: 0.0)
            let panel = ModelEntity(mesh: .generateBox(size: [0.34, 0.34, 0.035]), materials: [material])
            panel.position = [x, 0.36, -1.75]
            worldAnchor.addChild(panel)
        }
    }
}
```

- [ ] **Step 4: Call showcase only for launch arg**

In `GameARView.configureScene()`, after `ArenaBuilder.addArena(to: worldAnchor)`, add:

```swift
        if ProcessInfo.processInfo.arguments.contains("--material-response-mode") {
            MaterialResponseShowcase.add(to: worldAnchor)
        }
```

Do not remove or alter:

```swift
        spawnWaveTargets()
```

Do not edit `TargetFactory.swift`.

- [ ] **Step 5: Run fixture tests**

Run:

```bash
rtk .venv/bin/python -m unittest Tests/test_fixture_refactor.py
```

Expected:

```text
OK
```

---

### Task 6: Build, Inspect, Capture, and Accept the Asset

**Files:**
- Generated/modify: `Assets/Imported/material_response_targets.usdz`
- Generated/modify: `Assets/Textures/material_response_targets_basecolor.png`
- Generated/modify: `Assets/Textures/material_response_targets_roughness.png`
- Create: `Docs/screenshots/material_response_targets.jpg`
- Modify: `Tools/asset_manifest.json`

- [ ] **Step 1: Build the USDZ through RKP**

Run:

```bash
rtk .venv/bin/python Tools/rkp.py build-asset material_response_targets
```

Expected:

```text
asset built: Assets/Imported/material_response_targets.usdz
```

If Blender crashes before export on the reference machine, stop this task and record the blocker in `Docs/WORKLOG.md`. Do not mark the asset `imported` and do not fake screenshot evidence.

- [ ] **Step 2: Inspect material maps**

Run:

```bash
rtk .venv/bin/python Tools/rkp.py inspect-usdz material_response_targets --json
```

Expected:

```text
"ok": true
"textureMaps": {
  "baseColor": { "present": true, "sizeStatus": "ok" },
  "roughness": { "present": true, "sizeStatus": "ok" }
}
```

- [ ] **Step 3: Generate and build the Xcode project**

Run:

```bash
rtk xcodegen generate
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build
```

Expected:

```text
xcodebuild ok
```

CoreSimulator sandbox warnings are acceptable only if the command exits `0`.

- [ ] **Step 4: Capture simulator screenshot**

Launch the app with:

```text
--material-response-mode
```

Capture the screenshot to:

```text
Docs/screenshots/material_response_targets.jpg
```

Acceptance criteria:

- The normal target game still appears.
- Three material-response panels are visible.
- The roughness-map panel has visibly different bands or response variation.
- HUD/controls do not block the comparison panels.
- The existing default target asset remains `target_basic_textured`.

- [ ] **Step 5: Accept the asset**

Run:

```bash
rtk .venv/bin/python Tools/rkp.py accept-asset material_response_targets --screenshot Docs/screenshots/material_response_targets.jpg
```

Expected:

```text
accepted asset: material_response_targets
```

- [ ] **Step 6: Re-inspect all imported assets**

Run:

```bash
rtk .venv/bin/python Tools/rkp.py release-check --assets
```

Expected:

```text
release-check ok
```

---

### Task 7: Update Teaching Docs

**Files:**
- Modify: `Docs/guide.md`
- Modify: `Docs/blender-usdz-checklist.md`
- Modify: `Docs/WORKLOG.md`
- Modify: `Docs/ai-handoff.md`
- Modify: `Docs/pdf/realitykit-pipeline-guide.pdf`

- [ ] **Step 1: Update the guide coverage matrix**

In `Docs/guide.md`, change:

```markdown
| Roughness / metallic maps | Planned | yok | Material response dersi eklenecek. |
```

to:

```markdown
| Roughness maps | Started | `material_response_targets`, `Docs/screenshots/material_response_targets.jpg` | Roughness value vs roughness map comparison began in Module 4. |
```

Keep metallic maps planned unless a metallic map was actually tested.

- [ ] **Step 2: Update Planned Module 4 section**

Replace the first exercise checklist with evidence-based text:

```markdown
İlk egzersiz sonucu:

1. `material_response_targets` asset'i üç panelle roughness value ve roughness map davranışını karşılaştırır.
2. `rkp inspect-usdz material_response_targets --json` baseColor ve roughness texture varlığını doğrular.
3. Simulator screenshot `Docs/screenshots/material_response_targets.jpg` olarak saklanır.
4. Eğer screenshot farkı yeterince okunur göstermediyse bir sonraki adım ışık açısını veya panel yüzeyini değiştirmek olmalı; map sayısını artırmak değil.
```

- [ ] **Step 3: Update Blender checklist**

Add under `## UV and Materials`:

```markdown
- Roughness map'e yalnızca base color import doğrulandıktan sonra geç.
- Roughness value ile roughness map'i aynı ışık ve aynı kamera altında karşılaştır.
- Roughness map dosya adı asset prefix'i taşımalı: `<asset_id>_roughness.png`.
- Roughness farkı simulator screenshot'ta okunmuyorsa önce ışık/surface açısını düzelt; normal/metallic map ekleme.
```

- [ ] **Step 4: Add Sprint 108 worklog entry**

Insert a new current sprint above Sprint 107:

```markdown
### Sprint 108: Module 4 Material Response First Slice

**Durum:** Tamamlandı
**Tarih:** 2026-05-10
**Amaç:** Base color sonrası ilk material response dersini roughness value ve roughness map karşılaştırmasıyla doğrulamak.

**Yapılanlar:**

- `inspect-usdz` configured material maps raporlayacak şekilde genişletildi.
- `material_response_targets` asset kontratı, Blender script'i, manifest kaydı ve brief'i eklendi.
- RealityKit fixture'a sadece `--material-response-mode` ile çalışan opt-in showcase eklendi.
- Simulator screenshot ile asset kabul edildi.

**Verification:**

```text
rtk .venv/bin/python -m unittest discover -s Tests: ok
rtk .venv/bin/python Tools/rkp.py inspect-usdz material_response_targets --json: ok
rtk xcodebuild -quiet -project RealityKitPipelineDemo.xcodeproj -scheme RealityKitPipelineDemo -destination generic/platform=iOS\ Simulator -derivedDataPath Build/DerivedData build: ok
rtk .venv/bin/python Tools/rkp.py accept-asset material_response_targets --screenshot Docs/screenshots/material_response_targets.jpg: ok
rtk .venv/bin/python Tools/rkp.py release-check --assets: ok
```

**Karar:**

Module 4'te normal map'e geçmeden önce roughness farkının screenshot'ta okunur olması gerekiyor. Görsel fark zayıfsa map sayısını artırmak yerine ışık, panel açısı veya yüzey formu ayarlanacak.
```

If any verification command was not run or failed, replace `ok` with the exact observed result.

- [ ] **Step 5: Update AI handoff**

In `Docs/ai-handoff.md`, add `material_response_targets` to the completed/started module evidence only after screenshot acceptance.

Set the next task to:

```markdown
Next recommended task: continue Module 4 with either metallic value comparison or normal-map export behavior. Do not add both in the same sprint.
```

- [ ] **Step 6: Regenerate guide PDF**

Run:

```bash
rtk pandoc Docs/guide.md --standalone --embed-resources --resource-path=Docs --css Docs/guide-style.css --metadata title="RealityKit Asset and Texture Pipeline Guide" -o Build/realitykit-pipeline-guide.html
rtk weasyprint Build/realitykit-pipeline-guide.html Build/realitykit-pipeline-guide.pdf
rtk cp Build/realitykit-pipeline-guide.pdf Docs/pdf/realitykit-pipeline-guide.pdf
```

Expected:

```text
Docs/pdf/realitykit-pipeline-guide.pdf updated
```

---

### Task 8: Final Verification and Review

**Files:**
- Review all changed files.
- Do not push or tag unless explicitly requested.

- [ ] **Step 1: Run full local verification**

Run:

```bash
rtk .venv/bin/python -m unittest discover -s Tests
rtk make verify-local
rtk node -e "JSON.parse(require('fs').readFileSync('Tools/asset_manifest.json','utf8')); console.log('manifest ok')"
rtk .venv/bin/python Tools/rkp.py release-check --assets
rtk git diff --check
```

Expected:

```text
OK
All checks passed!
manifest ok
release-check ok
```

- [ ] **Step 2: Confirm default loader behavior did not regress**

Run:

```bash
rtk .venv/bin/python -m unittest Tests/test_fixture_refactor.py
```

Expected:

```text
OK
```

Manually confirm `TargetFactory.swift` still tries:

```text
target_basic_textured -> target_basic -> procedural fallback
```

- [ ] **Step 3: Self-review the diff**

Run:

```bash
rtk git status --short
rtk git diff --stat
rtk git diff -- Tools/asset_manifest.json src/rkp/inspect_usdz.py Sources/RealityKitPipelineDemo/GameARView.swift Sources/RealityKitPipelineDemo/MaterialResponseShowcase.swift Docs/guide.md Docs/WORKLOG.md Docs/ai-handoff.md
```

Review for:

- Asset marked `imported` without valid screenshot evidence.
- Default target loader changed accidentally.
- `baseColorTexture` JSON compatibility broken.
- Roughness map required for assets that do not declare it.
- Guide claiming Module 4 complete before screenshot evidence exists.
- Build output or DerivedData accidentally tracked.

- [ ] **Step 4: Commit Module 4 slice**

Run:

```bash
rtk git add src/rkp/asset_manifest.py src/rkp/inspect_usdz.py Tests/test_rkp_project.py Tests/test_fixture_refactor.py Tests/test_release_docs.py Tools/asset_manifest.json Tools/blender/create_material_response_targets.py Docs/assets/material_response_targets.md Sources/RealityKitPipelineDemo/MaterialResponseShowcase.swift Sources/RealityKitPipelineDemo/GameARView.swift Docs/guide.md Docs/blender-usdz-checklist.md Docs/WORKLOG.md Docs/ai-handoff.md Docs/pdf/realitykit-pipeline-guide.pdf Docs/screenshots/material_response_targets.jpg Assets/Imported/material_response_targets.usdz Assets/Textures/material_response_targets_basecolor.png Assets/Textures/material_response_targets_roughness.png
rtk git commit -m "feat: add material response module slice"
```

Expected:

```text
[main <sha>] feat: add material response module slice
```

Do not push unless the user explicitly asks.

---

## Acceptance Criteria

The Module 4 first slice is done only when all of these are true:

- `v0.2.1` handoff drift is corrected.
- `inspect-usdz` reports configured `textureMaps` and preserves `baseColorTexture`.
- `material_response_targets` exists in manifest and has a brief.
- The USDZ contains both baseColor and roughness textures.
- RealityKit fixture can show the comparison through `--material-response-mode`.
- Default target fallback order is unchanged.
- Screenshot evidence exists under `Docs/screenshots`.
- `accept-asset` marks the asset imported only after screenshot evidence.
- `Docs/guide.md`, `Docs/blender-usdz-checklist.md`, `Docs/WORKLOG.md`, `Docs/ai-handoff.md`, and the guide PDF are updated.
- Full local verification and `release-check --assets` pass.

## Recommended Follow-Up

After this slice, choose exactly one next Module 4 step:

1. Metallic value comparison only.
2. Normal-map export/import behavior only.
3. 512 vs 1024 texture resolution comparison only.

Do not combine these into one sprint. Each needs its own screenshot evidence and worklog decision.
