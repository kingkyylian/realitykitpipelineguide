import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RkpCliTests(unittest.TestCase):
    def run_rkp(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "Tools/rkp.py", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def test_status_json_exposes_project_metadata_and_ready_assets(self) -> None:
        result = self.run_rkp("status", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["project"], "RealityKitPipelineDemo")
        self.assertEqual(payload["scale"], "1 Blender unit = 1 meter")
        self.assertGreaterEqual(len(payload["assets"]), 4)
        imported_assets = [asset for asset in payload["assets"] if asset["status"] == "imported"]
        self.assertTrue(imported_assets)
        self.assertTrue(all(asset["next"] == "ready" for asset in imported_assets))

    def test_doctor_json_reports_no_errors(self) -> None:
        result = self.run_rkp("doctor", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["errors"], 0)

    def test_make_asset_blocks_screenshot_acceptance_without_build(self) -> None:
        result = self.run_rkp(
            "make-asset",
            "test_no_build_accept",
            "--type",
            "gameplay_target",
            "--prompt",
            "red bullseye target",
            "--screenshot",
            "Docs/screenshots/missing.jpg",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("--screenshot requires --build", result.stderr)

    def test_build_asset_rejects_unknown_asset(self) -> None:
        result = self.run_rkp("build-asset", "does_not_exist")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown asset id", result.stderr)

    def test_inspect_usdz_rejects_unknown_asset(self) -> None:
        result = self.run_rkp("inspect-usdz", "does_not_exist")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown asset id", result.stdout)

    def test_verify_asset_runs_inspection_gate_for_ready_asset(self) -> None:
        result = self.run_rkp("verify-asset", "target_basic_textured")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("==> inspect-usdz", result.stdout)
        self.assertIn("verify-asset ok: target_basic_textured", result.stdout)

    def test_verify_asset_rejects_unknown_asset(self) -> None:
        result = self.run_rkp("verify-asset", "does_not_exist")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("verify-asset stopped at step: inspect-usdz", result.stderr)

    def test_version_flag_prints_package_version(self) -> None:
        result = self.run_rkp("--version")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "rkp 0.1.0")


if __name__ == "__main__":
    unittest.main()
