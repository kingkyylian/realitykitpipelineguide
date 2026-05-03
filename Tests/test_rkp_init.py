import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RkpInitTests(unittest.TestCase):
    def run_rkp(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "Tools" / "rkp.py"), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def test_init_creates_minimal_pipeline_files_and_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = self.run_rkp(root, "init")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / "rkp.json").exists())
            self.assertTrue((root / "Tools" / "asset_manifest.json").exists())
            for rel in [
                "Assets/Imported",
                "Assets/Textures",
                "Assets/Source",
                "Docs/assets",
                "Docs/screenshots",
                "Tools/blender",
            ]:
                self.assertTrue((root / rel).is_dir(), rel)
            manifest = json.loads((root / "Tools" / "asset_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["project"], root.name)
            self.assertEqual(manifest["assets"], [])

    def test_init_refuses_to_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.run_rkp(root, "init").returncode, 0)
            config = root / "rkp.json"
            config.write_text('{"manifest":"custom.json"}\n', encoding="utf-8")

            result = self.run_rkp(root, "init")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("already initialized", result.stderr)
            self.assertEqual(config.read_text(encoding="utf-8"), '{"manifest":"custom.json"}\n')

    def test_init_force_overwrites_existing_config_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.run_rkp(root, "init").returncode, 0)
            (root / "rkp.json").write_text('{"manifest":"custom.json"}\n', encoding="utf-8")
            (root / "Tools" / "asset_manifest.json").write_text('{"project":"Old","assets":[{"id":"old"}]}\n', encoding="utf-8")

            result = self.run_rkp(root, "init", "--force", "--project-name", "ForcedGame")

            self.assertEqual(result.returncode, 0, result.stderr)
            config = json.loads((root / "rkp.json").read_text(encoding="utf-8"))
            self.assertEqual(config["manifest"], "Tools/asset_manifest.json")
            manifest = json.loads((root / "Tools" / "asset_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["project"], "ForcedGame")
            self.assertEqual(manifest["assets"], [])

    def test_init_project_name_sets_manifest_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = self.run_rkp(root, "init", "--project-name", "MyGame")

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root / "Tools" / "asset_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["project"], "MyGame")

    def test_init_keeps_existing_asset_directory_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "Assets" / "Imported"
            existing.mkdir(parents=True)
            marker = existing / "keep.usdz"
            marker.write_bytes(b"keep")

            result = self.run_rkp(root, "init")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(marker.read_bytes(), b"keep")

    def test_init_project_passes_doctor_with_empty_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.run_rkp(root, "init").returncode, 0)

            result = self.run_rkp(root, "doctor", "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["errors"], 0)

    def test_init_project_doctor_does_not_warn_for_toolkit_repo_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.run_rkp(root, "init").returncode, 0)

            result = self.run_rkp(root, "doctor", "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            warning_paths = {
                finding["path"]
                for finding in payload["findings"]
                if finding["level"] == "warning"
            }
            self.assertEqual(warning_paths, {"README.md", "LICENSE", "Makefile"})


if __name__ == "__main__":
    unittest.main()
