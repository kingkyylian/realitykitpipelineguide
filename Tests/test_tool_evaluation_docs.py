from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ToolEvaluationDocsTests(unittest.TestCase):
    def test_tool_evaluation_records_release_findings_and_patch_candidate(self) -> None:
        report = read("Docs/tool-evaluation-v0.2.0.md")

        self.assertIn("Published `v0.2.0` Reports Package Version `0.1.0`", report)
        self.assertIn("Accepts Non-Image Screenshot Evidence", report)
        self.assertIn("Status: fixed locally for the patch candidate", report)
        self.assertIn("rkp 0.2.1", report)
        self.assertIn("Do not start Module 4 from the published `v0.2.0` state", report)
        self.assertIn("release-check` returns success for minimal external projects", report)
