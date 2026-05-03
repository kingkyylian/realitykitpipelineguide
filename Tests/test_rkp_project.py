import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RkpProjectTests(unittest.TestCase):
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

    def test_accept_asset_uses_external_project_relative_screenshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = self.make_external_project(root)
            self.add_built_asset(root, "portable_accept")
            screenshot = root / "Docs" / "screenshots" / "portable_accept.jpg"
            screenshot.parent.mkdir(parents=True)
            screenshot.write_bytes(b"jpg")

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
            outside.write_bytes(b"jpg")

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
