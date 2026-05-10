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
