from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ReleaseDocsTests(unittest.TestCase):
    def test_changelog_has_v020_release_above_v010_history(self) -> None:
        changelog = read("CHANGELOG.md")

        self.assertIn("## Unreleased", changelog)
        self.assertIn("## v0.2.0 - RKP product path and RKG labs preview (2026-05-10)", changelog)
        self.assertIn("## v0.1.0 - Public pipeline toolkit preview", changelog)
        self.assertLess(changelog.index("## Unreleased"), changelog.index("## v0.2.0"))
        self.assertLess(changelog.index("## v0.2.0"), changelog.index("## v0.1.0"))

        unreleased = changelog.split("## Unreleased", 1)[1].split("## v0.2.0", 1)[0]
        self.assertIn("No unreleased changes yet", unreleased)

        v020 = changelog.split("## v0.2.0", 1)[1].split("## v0.1.0", 1)[0]
        for expected in (
            "RKP Product Surface",
            "RKG Experimental Labs",
            "rkp build-asset --fallback-only",
            "rkg verify-screenshots",
            "rtk make verify-local",
            "rtk .venv/bin/python Tools/rkp.py release-check",
        ):
            self.assertIn(expected, v020)

    def test_release_notes_are_ready_for_publication(self) -> None:
        release = read("Docs/releases/v0.2.0.md")

        self.assertIn("Status: Final release notes for `v0.2.0`.", release)
        self.assertIn("Target tag: `v0.2.0`", release)
        self.assertIn("Compare range after tag: `v0.1.0..v0.2.0`", release)
        self.assertIn("RKP-first product boundary", release)
        self.assertIn("RKG remains experimental labs", release)
        self.assertNotIn("Draft release notes", release)
        self.assertNotIn("Publish Checklist", release)

    def test_showcase_uses_v020_release_copy_not_old_first_release(self) -> None:
        showcase = read("Docs/github-showcase.md")

        self.assertIn("## v0.2.0 Release Copy", showcase)
        self.assertIn("git tag v0.2.0", showcase)
        self.assertIn("Docs/releases/v0.2.0.md", showcase)
        self.assertIn("Existing baseline tag", showcase)
        self.assertIn("Post-Release Outreach Gaps", showcase)
        self.assertNotIn("git tag v0.1.0", showcase)
        self.assertNotIn("`v0.1.0` tag and GitHub Release", showcase)

    def test_release_checklist_points_to_prepared_release_notes(self) -> None:
        checklist = read("Docs/repo-release-checklist.md")

        self.assertIn("Latest prepared release notes: `Docs/releases/v0.2.0.md`", checklist)
        self.assertIn("Docs/releases/*.md", checklist)
        self.assertIn("Do not push, tag, or publish without explicit user approval", checklist)
        self.assertIn("Create the release from the matching `Docs/releases/<version>.md` file", checklist)
        self.assertNotIn("Create `v0.1.0` release", checklist)
