import json
import sys
import tempfile
import unittest
import zipfile
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class RkpPackageTests(unittest.TestCase):
    def test_runtime_helpers_expose_package_subprocess_contract(self) -> None:
        from rkp import runtime

        command = runtime.module_command("rkp.inspect_usdz", "target_basic")
        env = runtime.package_env()

        self.assertEqual(command, [sys.executable, "-m", "rkp.inspect_usdz", "target_basic"])
        self.assertEqual(env["PYTHONPATH"].split(":")[0], str(SRC))

    def test_asset_manifest_helpers_expose_shared_contract(self) -> None:
        from rkp import asset_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "Pipeline" / "manifest.json"
            manifest_path.parent.mkdir()
            project = SimpleNamespace(
                manifest=manifest_path,
                assets_dir=root / "Assets",
                textures_dir=root / "Textures",
            )
            manifest = {
                "assets": [
                    {"id": "plain", "file": "plain.usdz", "status": "imported", "textureMaps": []},
                    {"id": "textured", "file": "textured.usdz", "status": "imported"},
                    {"id": "draft", "file": "draft.usdz", "status": "planned"},
                ]
            }
            asset_manifest.write_manifest(manifest, project)

            loaded = asset_manifest.load_manifest(project)
            plain = asset_manifest.load_asset("plain", project)
            textured = asset_manifest.load_asset("textured", project)

        self.assertEqual(loaded["assets"][0]["id"], "plain")
        self.assertEqual(asset_manifest.imported_asset_ids(loaded), ["plain", "textured"])
        self.assertEqual(asset_manifest.asset_file_name("new_target"), "new_target.usdz")
        self.assertIsNone(asset_manifest.expected_basecolor_name(plain))
        self.assertEqual(asset_manifest.expected_basecolor_name(textured), "textured_basecolor.png")
        self.assertEqual(asset_manifest.asset_usdz_path(textured, project), root / "Assets" / "textured.usdz")
        self.assertEqual(
            asset_manifest.expected_basecolor_texture(textured, project),
            root / "Textures" / "textured_basecolor.png",
        )

    def test_tool_discovery_reports_invalid_blender_override(self) -> None:
        from rkp import tool_discovery

        with patch.dict("os.environ", {"BLENDER": "/nonexistent/blender"}):
            result = tool_discovery.resolve_blender()

        self.assertEqual(result.source, "BLENDER")
        self.assertEqual(result.path, Path("/nonexistent/blender"))
        self.assertFalse(result.is_executable)
        self.assertEqual(result.error, "Blender executable is not available: /nonexistent/blender")

    def test_inspect_usdz_uses_usdcat_for_binary_geometry_when_available(self) -> None:
        from rkp import inspect_usdz

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "manifest.json"
            assets_dir = root / "Assets"
            assets_dir.mkdir()
            project = SimpleNamespace(
                manifest=manifest_path,
                assets_dir=assets_dir,
                rel=lambda path: str(Path(path).relative_to(root)),
            )
            manifest_path.write_text(
                json.dumps(
                    {
                        "assets": [
                            {
                                "id": "binary_target",
                                "file": "binary_target.usdz",
                                "status": "imported",
                                "maxTriangles": 4,
                                "textureMaps": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with zipfile.ZipFile(assets_dir / "binary_target.usdz", "w") as archive:
                archive.writestr("binary_target.usdc", b"binary")
            usdcat_text = "#usda 1.0\nint[] faceVertexCounts = [3, 3]\ntexCoord2f[] primvars:st = [(0, 0)]\n"

            with patch.object(inspect_usdz.shutil, "which", return_value="/usr/bin/usdcat"), patch.object(
                inspect_usdz.subprocess,
                "run",
                return_value=SimpleNamespace(returncode=0, stdout=usdcat_text),
            ):
                payload = inspect_usdz.inspect_asset("binary_target", project)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["triangles"], 2)
        self.assertEqual(payload["triangleStatus"], "ok")
        self.assertEqual(payload["uv"]["status"], "present")

    def test_cleanup_dry_run_reports_candidates_without_removing(self) -> None:
        from rkp import cleanup

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "rkp.json").write_text("{}", encoding="utf-8")
            build = root / "Build"
            pycache = root / "src" / "__pycache__"
            egg_info = root / "src" / "rkp.egg-info"
            usdzip_scratch = root / "Assets" / "Imported" / "(A Document Being Saved By usdzip)"
            ds_store = root / ".DS_Store"
            for path in (build, pycache, egg_info, usdzip_scratch):
                path.mkdir(parents=True)
            ds_store.write_text("local", encoding="utf-8")
            project = SimpleNamespace(root=root, rel=lambda path: str(Path(path).relative_to(root)))

            candidates = cleanup.collect_candidates(project)

        self.assertEqual(
            [candidate.rel_path for candidate in candidates],
            [
                ".DS_Store",
                "Assets/Imported/(A Document Being Saved By usdzip)",
                "Build",
                "src/__pycache__",
                "src/rkp.egg-info",
            ],
        )

    def test_doctor_ignores_local_checkpoint_markdown(self) -> None:
        from rkp.pipeline_doctor import Doctor

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkpoints = root / "Docs" / "checkpoints"
            checkpoints.mkdir(parents=True)
            local_path = "/Us" "ers/kyylian/Developer/RealityKitPipelineDemo"
            (checkpoints / "LATEST.md").write_text(
                f"Root: {local_path}\n",
                encoding="utf-8",
            )

            doctor = Doctor(root)
            doctor.check_public_text()

        self.assertEqual(doctor.findings, [])

    def test_doctor_ignores_local_virtualenv_metadata(self) -> None:
        from rkp.pipeline_doctor import Doctor

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / ".venv" / "lib" / "python3.13" / "site-packages" / "rkp.dist-info"
            metadata.mkdir(parents=True)
            local_path = "/Us" "ers/kyylian/Developer/RealityKitPipelineDemo"
            (metadata / "direct_url.json").write_text(f'{{"url":"file://{local_path}"}}', encoding="utf-8")

            doctor = Doctor(root)
            doctor.check_public_text()

        self.assertEqual(doctor.findings, [])

    def test_make_asset_subprocesses_use_package_modules(self) -> None:
        from rkp import cli

        commands: list[list[str]] = []

        def capture(command: list[str], active_project=None) -> int:
            commands.append(command)
            return 0

        args = Namespace(
            id="portable_module",
            prompt="red target",
            type="gameplay_target",
            build=True,
            screenshot="Docs/screenshots/portable_module.jpg",
            release_check=True,
            force=False,
        )

        with patch.object(cli, "run", side_effect=capture):
            result = cli.run_make_asset(args)

        self.assertEqual(result, 0)
        self.assertEqual(
            commands,
            [
                [
                    sys.executable,
                    "-m",
                    "rkp.prompt_asset",
                    "portable_module",
                    "--prompt",
                    "red target",
                    "--type",
                    "gameplay_target",
                ],
                [sys.executable, "-m", "rkp.build_asset", "--id", "portable_module"],
                [
                    sys.executable,
                    "-m",
                    "rkp.accept_asset",
                    "--id",
                    "portable_module",
                    "--screenshot",
                    "Docs/screenshots/portable_module.jpg",
                ],
                [sys.executable, "-m", "rkp.cli", "release-check"],
            ],
        )

    def test_verify_asset_runs_build_inspect_accept_and_release_check(self) -> None:
        from rkp import cli

        commands: list[list[str]] = []

        def capture(command: list[str], active_project=None) -> int:
            commands.append(command)
            return 0

        args = Namespace(
            id="portable_module",
            build=True,
            screenshot="Docs/screenshots/portable_module.jpg",
            release_check=True,
        )

        with patch.object(cli, "run", side_effect=capture):
            result = cli.run_verify_asset(args)

        self.assertEqual(result, 0)
        self.assertEqual(
            commands,
            [
                [sys.executable, "-m", "rkp.build_asset", "--id", "portable_module"],
                [sys.executable, "-m", "rkp.inspect_usdz", "portable_module"],
                [
                    sys.executable,
                    "-m",
                    "rkp.accept_asset",
                    "--id",
                    "portable_module",
                    "--screenshot",
                    "Docs/screenshots/portable_module.jpg",
                ],
                [sys.executable, "-m", "rkp.cli", "release-check"],
            ],
        )

    def test_verify_asset_stops_when_inspection_fails(self) -> None:
        from rkp import cli

        commands: list[list[str]] = []

        def fail_inspect(command: list[str], active_project=None) -> int:
            commands.append(command)
            return 1 if command[:3] == [sys.executable, "-m", "rkp.inspect_usdz"] else 0

        args = Namespace(
            id="portable_module",
            build=False,
            screenshot="Docs/screenshots/portable_module.jpg",
            release_check=True,
        )

        with patch.object(cli, "run", side_effect=fail_inspect):
            result = cli.run_verify_asset(args)

        self.assertEqual(result, 1)
        self.assertEqual(commands, [[sys.executable, "-m", "rkp.inspect_usdz", "portable_module"]])

    def test_release_check_assets_inspects_imported_assets_before_xcode(self) -> None:
        from rkp import cli

        commands: list[list[str]] = []
        fake_project = SimpleNamespace(
            root=ROOT,
            tests_dir=ROOT / "MissingTestsForPackageUnit",
            rel=lambda path: str(Path(path).relative_to(ROOT)),
            xcode_project=ROOT / "RealityKitPipelineDemo.xcodeproj",
            xcode_scheme="RealityKitPipelineDemo",
            xcode_destination="generic/platform=iOS Simulator",
            derived_data_path=ROOT / "Build" / "DerivedData",
        )
        manifest = {
            "assets": [
                {"id": "ready_target", "status": "imported"},
                {"id": "draft_target", "status": "planned"},
            ]
        }

        def capture(command: list[str], active_project=None) -> int:
            commands.append(command)
            return 1 if command[:3] == [sys.executable, "-m", "rkp.inspect_usdz"] else 0

        with patch.object(cli, "project", return_value=fake_project), patch.object(
            cli.Doctor, "run", return_value=0
        ), patch.object(cli, "load_manifest", return_value=manifest), patch.object(
            cli, "run", side_effect=capture
        ):
            result = cli.run_release_check(include_assets=True)

        self.assertEqual(result, 1)
        self.assertEqual(commands, [[sys.executable, "-m", "rkp.inspect_usdz", "ready_target"]])

    def test_claude_generation_wraps_geometry_with_export_boilerplate(self) -> None:
        from rkp import prompt_asset

        class FakeMessages:
            def create(self, **kwargs):
                return SimpleNamespace(
                    content=[
                        SimpleNamespace(
                            text="```python\n"
                            "def main():\n"
                            "    obj = object()\n"
                            "    export_usdz(obj)\n"
                            "\n"
                            "if __name__ == '__main__':\n"
                            "    main()\n"
                            "```"
                        )
                    ]
                )

        class FakeAnthropic:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key
                self.messages = FakeMessages()

        fake_module = SimpleNamespace(Anthropic=FakeAnthropic)

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}), patch.dict(
            sys.modules, {"anthropic": fake_module}
        ):
            script = prompt_asset._generate_with_claude(
                "ai_tower",
                "gameplay_target",
                "blue beacon tower target",
            )

        self.assertIsNotNone(script)
        self.assertIn('ASSET_ID = "ai_tower"', script)
        self.assertIn('USDZ_PATH = IMPORTED_DIR / f"{ASSET_ID}.usdz"', script)
        self.assertIn("def export_usdz(obj):", script)
        self.assertIn("export_usdz(obj)", script)
        self.assertNotIn("```", script)

    def test_template_generator_does_not_call_claude_when_api_key_exists(self) -> None:
        from rkp import prompt_asset

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_project = SimpleNamespace(
                blender_dir=root / "blender",
                rel=lambda path: str(Path(path).relative_to(root)),
            )

            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}), patch.object(
                prompt_asset,
                "_generate_with_claude",
                side_effect=AssertionError("Claude should be opt-in"),
            ):
                script_path, ai_generated = prompt_asset.write_blender_script(
                    "template_target",
                    "gameplay_target",
                    "red bullseye target",
                    "target",
                    force=True,
                    generator="template",
                    project=fake_project,
                )
            script = script_path.read_text(encoding="utf-8")

        self.assertFalse(ai_generated)
        self.assertIn('ASSET_ID = "template_target"', script)
        self.assertIn("ARCHETYPE = 'target'", script)

    def test_make_asset_meshy_uses_configured_asset_path_and_refine_quality(self) -> None:
        from rkp import cli
        from rkp import meshy_asset

        commands: list[list[str]] = []
        calls: list[tuple[str, str, Path, str, bool]] = []

        def capture(command: list[str], active_project=None) -> int:
            commands.append(command)
            return 0

        def fake_generate_usdz(
            prompt: str,
            asset_id: str,
            output_path: Path,
            api_key: str | None = None,
            refine: bool = False,
        ) -> Path:
            assert api_key is not None
            calls.append((prompt, asset_id, output_path, api_key, refine))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"fake-usdz")
            return output_path

        args = Namespace(
            id="meshy_drone",
            prompt="red drone target",
            type="gameplay_target",
            quality="refine",
            screenshot="Docs/screenshots/meshy_drone.jpg",
            release_check=True,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_project = SimpleNamespace(
                root=root,
                assets_dir=root / "Imported",
                rel=lambda path: str(Path(path).relative_to(root)),
            )

            with patch.dict("os.environ", {"MESHY_API_KEY": "test-meshy-key"}), patch.object(
                cli, "project", return_value=fake_project
            ), patch.object(cli, "run", side_effect=capture), patch.object(
                meshy_asset, "generate_usdz", side_effect=fake_generate_usdz
            ):
                result = cli.run_make_asset_meshy(args)

        self.assertEqual(result, 0)
        self.assertEqual(
            commands,
            [
                [sys.executable, "-m", "rkp.new_asset", "--id", "meshy_drone", "--type", "gameplay_target"],
                [
                    sys.executable,
                    "-m",
                    "rkp.accept_asset",
                    "--id",
                    "meshy_drone",
                    "--screenshot",
                    "Docs/screenshots/meshy_drone.jpg",
                ],
                [sys.executable, "-m", "rkp.cli", "release-check"],
            ],
        )
        self.assertEqual(
            calls,
            [
                (
                    "red drone target",
                    "meshy_drone",
                    root / "Imported" / "meshy_drone.usdz",
                    "test-meshy-key",
                    True,
                )
            ],
        )

    def test_meshy_preview_task_uses_mobile_budget_payload(self) -> None:
        from rkp import meshy_asset

        captured: list[tuple[str, str, dict | None]] = []

        def fake_request(url: str, api_key: str, body: dict | None = None) -> dict:
            captured.append((url, api_key, body))
            return {"result": "task_123"}

        with patch.object(meshy_asset, "_request", side_effect=fake_request):
            task_id = meshy_asset._create_task("red drone target", "test-key")

        self.assertEqual(task_id, "task_123")
        self.assertEqual(captured[0][1], "test-key")
        self.assertEqual(captured[0][2]["target_formats"], ["usdz"])
        self.assertEqual(captured[0][2]["target_polycount"], 1500)


if __name__ == "__main__":
    unittest.main()
