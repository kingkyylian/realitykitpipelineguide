from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class PublicPolishDocsTests(unittest.TestCase):
    def test_readme_has_public_badges_and_polish_links(self) -> None:
        readme = read("README.md")
        first_screen = readme[:900]

        self.assertIn("actions/workflows/ci.yml/badge.svg", first_screen)
        self.assertIn("python-3.10%2B", first_screen)
        self.assertIn("license-MIT", first_screen)
        self.assertIn("RealityKit-iOS%20fixture", first_screen)
        self.assertIn("Docs/blender-support.md", readme)
        self.assertIn("Docs/first-good-issues.md", readme)

    def test_blender_support_documents_fallback_without_acceptance_shortcut(self) -> None:
        blender_support = read("Docs/blender-support.md")

        self.assertIn("Blender 4.x", blender_support)
        self.assertIn("usdzip", blender_support)
        self.assertIn("rkp build-asset enemy_drone --fallback-only", blender_support)
        self.assertIn("rkp doctor --blender", blender_support)
        self.assertIn("screenshot evidence", blender_support)
        self.assertIn("does not replace visual acceptance", blender_support)

    def test_first_good_issues_are_rkp_first_and_verifiable(self) -> None:
        issues = read("Docs/first-good-issues.md")

        self.assertIn("`rkp` is the stable asset pipeline", issues)
        self.assertIn("Docs/blender-support.md", issues)
        self.assertIn("Verification", issues)
        self.assertIn("rtk make verify-local", issues)
        self.assertIn("Do not expand RKG unless", issues)

    def test_ai_handoff_next_task_is_not_stale_product_cleanup(self) -> None:
        handoff = read("Docs/ai-handoff.md")
        next_task = handoff.split("## Current Recommended Next Task", 1)[1].split("## Key Files", 1)[0]

        self.assertNotIn("Product focus cleanup", next_task)
        self.assertIn("Public polish follow-up", next_task)
        self.assertIn("Docs/blender-support.md", next_task)
        self.assertIn("Docs/first-good-issues.md", next_task)
