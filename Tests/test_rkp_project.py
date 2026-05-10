import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RkpProjectTests(unittest.TestCase):
    def png_bytes(self, width: int, height: int) -> bytes:
        def chunk(kind: bytes, data: bytes) -> bytes:
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

        raw = b"".join(b"\x00" + (b"\xff\x00\x00\xff" * width) for _ in range(height))
        return b"".join(
            [
                b"\x89PNG\r\n\x1a\n",
                chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
                chunk(b"IDAT", zlib.compress(raw, 9)),
                chunk(b"IEND", b""),
            ]
        )

    def make_external_project(self, root: Path) -> Path:
        tools = root / "Pipeline"
        assets = root / "GameAssets"
        nested = root / "Nested"
        tools.mkdir()
        assets.mkdir()
        nested.mkdir()
        (root / "rkp.json").write_text(
            json.dumps(
                {
                    "manifest": "Pipeline/manifest.json",
                    "assets_dir": "GameAssets",
                    "docs_dir": "Docs",
                    "blender_dir": "Pipeline/blender",
                    "textures_dir": "Textures",
                    "source_dir": "SourceArt",
                }
            ),
            encoding="utf-8",
        )
        (tools / "manifest.json").write_text(
            json.dumps(
                {
                    "project": "ExternalRealityKitGame",
                    "scale": "1 unit = 1 meter",
                    "assets": [],
                }
            ),
            encoding="utf-8",
        )
        return nested

    def add_built_asset(self, root: Path, asset_id: str) -> None:
        manifest_path = root / "Pipeline" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["assets"].append(
            {
                "id": asset_id,
                "file": f"{asset_id}.usdz",
                "type": "gameplay_target",
                "status": "planned",
                "maxTriangles": 100,
                "maxTextureSize": 512,
                "notes": "temporary built asset",
            }
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        asset_path = root / "GameAssets" / f"{asset_id}.usdz"
        asset_path.write_bytes(b"fake-usdz")
        brief_dir = root / "Docs" / "assets"
        brief_dir.mkdir(parents=True)
        (brief_dir / f"{asset_id}.md").write_text(
            f"""# Asset Brief: {asset_id}

- [ ] USDZ exported to `Assets/Imported/{asset_id}.usdz`.
- [ ] `Tools/asset_manifest.json` status changed from `planned` to `imported`.
- [ ] `make doctor` passes without new errors.
- [ ] Simulator screenshot captured if visual.
- [ ] `Docs/WORKLOG.md` lesson added.
""",
            encoding="utf-8",
        )
        (root / "Docs" / "WORKLOG.md").write_text("# Worklog\n\n## Current Sprint\n\n", encoding="utf-8")

    def add_buildable_asset(self, root: Path, asset_id: str) -> None:
        manifest_path = root / "Pipeline" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["assets"].append(
            {
                "id": asset_id,
                "file": f"{asset_id}.usdz",
                "type": "gameplay_target",
                "status": "planned",
                "maxTriangles": 100,
                "maxTextureSize": 512,
                "prompt": "red target",
                "archetype": "target",
                "notes": "temporary buildable asset",
            }
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        blender_dir = root / "Pipeline" / "blender"
        blender_dir.mkdir(parents=True)
        (blender_dir / f"create_{asset_id}.py").write_text("print('placeholder')\n", encoding="utf-8")

    def add_inspectable_usdz_asset(
        self,
        root: Path,
        asset_id: str,
        triangle_budget: int = 12,
        triangle_count: int = 2,
        texture_name: str | None = None,
        texture_size: tuple[int, int] | None = None,
        include_st_uv: bool = True,
    ) -> None:
        manifest_path = root / "Pipeline" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["assets"].append(
            {
                "id": asset_id,
                "file": f"{asset_id}.usdz",
                "type": "gameplay_target",
                "status": "planned",
                "maxTriangles": triangle_budget,
                "maxTextureSize": 512,
                "textureMaps": ["baseColor"],
                "notes": "inspectable test asset",
            }
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        faces = ", ".join("3" for _ in range(triangle_count))
        indices = ", ".join(str(index) for index in range(triangle_count * 3))
        uv_line = "    texCoord2f[] primvars:st = [(0, 0), (1, 0), (1, 1)]" if include_st_uv else ""
        usda = f"""#usda 1.0
def Mesh "Mesh"
{{
    int[] faceVertexCounts = [{faces}]
    int[] faceVertexIndices = [{indices}]
{uv_line}
}}
"""
        asset_path = root / "GameAssets" / f"{asset_id}.usdz"
        with zipfile.ZipFile(asset_path, "w") as archive:
            archive.writestr(f"{asset_id}.usda", usda)
            if texture_name:
                archive.writestr(
                    f"textures/{texture_name}",
                    self.png_bytes(*texture_size) if texture_size else b"png",
                )

    def test_find_project_root_walks_up_to_rkp_json(self) -> None:
        from Tools.rkp_project import find_project_root

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "a" / "b"
            nested.mkdir(parents=True)
            (root / "rkp.json").write_text("{}", encoding="utf-8")

            self.assertEqual(find_project_root(nested), root.resolve())

    def test_status_uses_cwd_project_config_not_script_location(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            manifest_path = root / "Pipeline" / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["assets"].append(
                {
                    "id": "external_target",
                    "file": "external_target.usdz",
                    "type": "gameplay_target",
                    "status": "planned",
                    "maxTriangles": 100,
                    "maxTextureSize": 512,
                    "notes": "temporary test asset",
                }
            )
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(ROOT / "Tools" / "rkp.py"), "status", "--json"],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["project"], "ExternalRealityKitGame")
            self.assertEqual(payload["assets"][0]["id"], "external_target")

    def test_new_asset_uses_external_project_config_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "new-asset",
                    "portable_target",
                    "--type",
                    "gameplay_target",
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root / "Pipeline" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["assets"][0]["id"], "portable_target")
            self.assertTrue((root / "Docs" / "assets" / "portable_target.md").exists())
            self.assertTrue((root / "Pipeline" / "blender" / "create_portable_target.py").exists())
            self.assertTrue((root / "GameAssets").is_dir())
            self.assertFalse((root / "Tools" / "asset_manifest.json").exists())

    def test_new_asset_blender_stub_matches_basecolor_export_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "new-asset",
                    "portable_texture",
                    "--type",
                    "gameplay_target",
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            script = (root / "Pipeline" / "blender" / "create_portable_texture.py").read_text(encoding="utf-8")
            self.assertIn('TEXTURE_PATH = TEXTURE_DIR / f"{ASSET_ID}_basecolor.png"', script)
            self.assertIn('image = bpy.data.images.new(f"{ASSET_ID}_basecolor", width=512, height=512)', script)
            self.assertIn("material.use_nodes = True", script)
            self.assertIn('nodes.new(type="ShaderNodeTexImage")', script)
            self.assertIn('uv_map.uv_map = "st"', script)
            self.assertIn('mesh.uv_layers.new(name="st")', script)
            self.assertIn('export_textures_mode="NEW"', script)
            self.assertIn("export_materials=True", script)
            self.assertIn("export_uvmaps=True", script)

    def test_prompt_asset_uses_external_project_config_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "prompt-asset",
                    "portable_drone",
                    "--type",
                    "gameplay_target",
                    "--prompt",
                    "red bullseye drone target",
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root / "Pipeline" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["assets"][0]["id"], "portable_drone")
            self.assertEqual(manifest["assets"][0]["archetype"], "drone")
            brief = (root / "Docs" / "assets" / "portable_drone.md").read_text(encoding="utf-8")
            self.assertIn("red bullseye drone target", brief)
            script = root / "Pipeline" / "blender" / "create_portable_drone.py"
            self.assertTrue(script.exists())
            self.assertIn("rkp.json", script.read_text(encoding="utf-8"))

    def test_prompt_asset_reports_unrecognized_archetype_without_internal_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "prompt-asset",
                    "portable_ship",
                    "--type",
                    "gameplay_target",
                    "--prompt",
                    "sleek spaceship fighter",
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                "archetype: unrecognized - using default (gameplay_target)",
                result.stdout,
            )
            self.assertIn(
                "geometry: default gameplay_target procedural template; edit the Blender script for prompt-specific shape",
                result.stdout,
            )
            self.assertNotIn("type-default", result.stdout)
            manifest = json.loads((root / "Pipeline" / "manifest.json").read_text(encoding="utf-8"))
            self.assertIsNone(manifest["assets"][0]["archetype"])
            self.assertNotIn("type-default", manifest["assets"][0]["notes"])
            self.assertIn("default geometry template", manifest["assets"][0]["notes"])

    def test_prompt_asset_claude_missing_key_fails_before_manifest_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            env = os.environ.copy()
            env.pop("ANTHROPIC_API_KEY", None)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "prompt-asset",
                    "portable_ai",
                    "--type",
                    "gameplay_target",
                    "--prompt",
                    "blue beacon tower target",
                    "--generator",
                    "claude",
                ],
                cwd=nested,
                env=env,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("ANTHROPIC_API_KEY not set", result.stderr)
            manifest = json.loads((root / "Pipeline" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["assets"], [])

    def test_accept_asset_uses_external_project_relative_screenshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_built_asset(root, "portable_accept")
            screenshot = root / "Docs" / "screenshots" / "portable_accept.jpg"
            screenshot.parent.mkdir(parents=True)
            screenshot.write_bytes(b"\xff\xd8portable screenshot evidence\xff\xd9")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "accept-asset",
                    "portable_accept",
                    "--screenshot",
                    "Docs/screenshots/portable_accept.jpg",
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root / "Pipeline" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["assets"][0]["status"], "imported")
            self.assertIn("Docs/screenshots/portable_accept.jpg", manifest["assets"][0]["notes"])
            brief = (root / "Docs" / "assets" / "portable_accept.md").read_text(encoding="utf-8")
            self.assertIn("- [x] Simulator screenshot captured if visual.", brief)
            worklog = (root / "Docs" / "WORKLOG.md").read_text(encoding="utf-8")
            self.assertIn("portable_accept", worklog)

    def test_accept_asset_copies_external_absolute_screenshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_built_asset(root, "portable_absolute")
            outside = root / "outside.jpg"
            outside.write_bytes(b"\xff\xd8portable screenshot evidence\xff\xd9")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "accept-asset",
                    "portable_absolute",
                    "--screenshot",
                    str(outside),
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            copied = root / "Docs" / "screenshots" / "portable_absolute_accepted.jpg"
            self.assertTrue(copied.exists())
            manifest = json.loads((root / "Pipeline" / "manifest.json").read_text(encoding="utf-8"))
            self.assertIn("Docs/screenshots/portable_absolute_accepted.jpg", manifest["assets"][0]["notes"])

    def test_accept_asset_rejects_non_image_screenshot_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_built_asset(root, "portable_invalid_screenshot")
            screenshot = root / "Docs" / "screenshots" / "not_an_image.jpg"
            screenshot.parent.mkdir(parents=True)
            screenshot.write_text('{"not": "an image"}', encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "accept-asset",
                    "portable_invalid_screenshot",
                    "--screenshot",
                    "Docs/screenshots/not_an_image.jpg",
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("not a valid PNG or JPEG image", result.stderr)
            manifest = json.loads((root / "Pipeline" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["assets"][0]["status"], "planned")

    def test_build_asset_uses_external_config_and_fails_gracefully_without_blender(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_buildable_asset(root, "portable_build")
            env = os.environ.copy()
            env["BLENDER"] = "/nonexistent/blender"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "build-asset",
                    "portable_build",
                ],
                cwd=nested,
                env=env,
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("GameAssets/portable_build.usdz", result.stderr)
            self.assertIn("Blender executable", result.stderr)
            self.assertFalse((root / "Tools" / "asset_manifest.json").exists())

    def test_build_asset_fallback_only_skips_blender_and_script_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_buildable_asset(root, "portable_fallback_only")
            (root / "Pipeline" / "blender" / "create_portable_fallback_only.py").unlink()
            fake_usdzip = root / "usdzip"
            fake_usdzip.write_text(
                f"""#!{sys.executable}
from pathlib import Path
import sys

output = Path(sys.argv[-1])
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(b"fallback-usdz")
""",
                encoding="utf-8",
            )
            fake_usdzip.chmod(0o755)
            env = os.environ.copy()
            env["BLENDER"] = "/nonexistent/blender"
            env["PATH"] = str(root)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "build-asset",
                    "portable_fallback_only",
                    "--fallback-only",
                ],
                cwd=nested,
                env=env,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / "GameAssets" / "portable_fallback_only.usdz").exists())
            self.assertIn("fallback asset built: GameAssets/portable_fallback_only.usdz", result.stdout)
            self.assertIn("next: rkp inspect-usdz portable_fallback_only", result.stdout)
            self.assertIn("manifest status is unchanged", result.stdout)
            self.assertNotIn("Blender executable", result.stderr)

    def test_build_asset_reports_missing_texture_as_info_after_successful_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_buildable_asset(root, "portable_textureless")
            fake_blender = root / "fake_blender.py"
            fake_blender.write_text(
                f"""#!{sys.executable}
from pathlib import Path
path = Path("GameAssets/portable_textureless.usdz")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_bytes(b"fake-usdz")
""",
                encoding="utf-8",
            )
            fake_blender.chmod(0o755)
            env = os.environ.copy()
            env["BLENDER"] = str(fake_blender)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "build-asset",
                    "portable_textureless",
                ],
                cwd=nested,
                env=env,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                "info: no texture file found - USDZ built without texture",
                result.stdout,
            )

    def test_build_asset_reports_when_texture_exists_but_is_not_packaged_in_usdz(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_buildable_asset(root, "portable_unpacked_texture")
            fake_blender = root / "fake_blender.py"
            fake_blender.write_text(
                f"""#!{sys.executable}
from pathlib import Path
import zipfile
texture = Path("Textures/portable_unpacked_texture_basecolor.png")
texture.parent.mkdir(parents=True, exist_ok=True)
texture.write_bytes(b"png")
output = Path("GameAssets/portable_unpacked_texture.usdz")
output.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(output, "w") as zf:
    zf.writestr("portable_unpacked_texture.usda", "#usda 1.0")
""",
                encoding="utf-8",
            )
            fake_blender.chmod(0o755)
            env = os.environ.copy()
            env["BLENDER"] = str(fake_blender)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "build-asset",
                    "portable_unpacked_texture",
                ],
                cwd=nested,
                env=env,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                "info: no texture file found - USDZ built without texture",
                result.stdout,
            )

    def test_build_asset_does_not_report_texture_info_when_usdz_contains_texture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_buildable_asset(root, "portable_packaged_texture")
            fake_blender = root / "fake_blender.py"
            fake_blender.write_text(
                f"""#!{sys.executable}
from pathlib import Path
import zipfile
texture = Path("Textures/portable_packaged_texture_basecolor.png")
texture.parent.mkdir(parents=True, exist_ok=True)
texture.write_bytes(b"png")
output = Path("GameAssets/portable_packaged_texture.usdz")
output.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(output, "w") as zf:
    zf.writestr("portable_packaged_texture.usda", "#usda 1.0")
    zf.write(texture, "textures/portable_packaged_texture_basecolor.png")
""",
                encoding="utf-8",
            )
            fake_blender.chmod(0o755)
            env = os.environ.copy()
            env["BLENDER"] = str(fake_blender)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "build-asset",
                    "portable_packaged_texture",
                ],
                cwd=nested,
                env=env,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("USDZ built without texture", result.stdout)

    def test_inspect_usdz_json_reports_texture_and_budget_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_inspectable_usdz_asset(
                root,
                "portable_inspect",
                triangle_budget=4,
                triangle_count=2,
                texture_name="portable_inspect_basecolor.png",
                texture_size=(256, 256),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "inspect-usdz",
                    "portable_inspect",
                    "--json",
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["asset"], "portable_inspect")
            self.assertEqual(payload["path"], "GameAssets/portable_inspect.usdz")
            self.assertEqual(payload["triangles"], 2)
            self.assertEqual(payload["maxTriangles"], 4)
            self.assertEqual(payload["triangleStatus"], "ok")
            self.assertTrue(payload["baseColorTexture"]["present"])
            self.assertEqual(payload["baseColorTexture"]["width"], 256)
            self.assertEqual(payload["baseColorTexture"]["height"], 256)
            self.assertEqual(payload["baseColorTexture"]["sizeStatus"], "ok")
            self.assertTrue(payload["uv"]["st"])
            self.assertEqual(payload["uv"]["status"], "present")

    def test_inspect_usdz_fails_when_budget_or_texture_gate_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_inspectable_usdz_asset(root, "portable_over_budget", triangle_budget=1, triangle_count=2)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "inspect-usdz",
                    "portable_over_budget",
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("triangle budget: over", result.stdout)
            self.assertIn("baseColor texture: missing", result.stdout)

    def test_inspect_usdz_fails_when_text_usd_lacks_st_uv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_inspectable_usdz_asset(
                root,
                "portable_missing_uv",
                texture_name="portable_missing_uv_basecolor.png",
                include_st_uv=False,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "inspect-usdz",
                    "portable_missing_uv",
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("uv st: missing", result.stdout)

    def test_inspect_usdz_fails_when_basecolor_texture_exceeds_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_inspectable_usdz_asset(
                root,
                "portable_large_texture",
                texture_name="portable_large_texture_basecolor.png",
                texture_size=(1024, 512),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "inspect-usdz",
                    "portable_large_texture",
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("baseColor size: 1024x512 / 512 (over)", result.stdout)

    def test_fallback_builder_uses_external_config_and_reports_missing_usdzip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_buildable_asset(root, "portable_fallback")
            env = os.environ.copy()
            env["PATH"] = ""

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "usdz_fallback_builder.py"),
                    "--id",
                    "portable_fallback",
                ],
                cwd=nested,
                env=env,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 127)
            self.assertIn("usdzip not found", result.stderr)
            self.assertFalse((root / "GameAssets" / "portable_fallback.usdz").exists())

    def test_release_check_uses_external_manifest_and_skips_missing_optional_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_buildable_asset(root, "portable_release")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "Tools" / "rkp.py"),
                    "release-check",
                ],
                cwd=nested,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("manifest ok", result.stdout)
            self.assertIn("skip tests", result.stdout)
            self.assertIn("skip xcode", result.stdout)


if __name__ == "__main__":
    unittest.main()
