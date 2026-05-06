#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from rkp.rkp_project import DEFAULT_CONFIG, ProjectPaths, load_project


TEXT_EXTENSIONS = {
    ".md",
    ".yml",
    ".yaml",
    ".json",
    ".swift",
    ".py",
    ".txt",
}
MACOS_BLENDER_APP = Path("/Applications/Blender.app/Contents/MacOS/Blender")


@dataclass
class Finding:
    level: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict:
        return {"level": self.level, "message": self.message, "path": self.path}

    def render(self) -> str:
        prefix = {"error": "ERROR", "warning": "WARN", "info": "INFO"}[self.level]
        if self.path:
            return f"[{prefix}] {self.path}: {self.message}"
        return f"[{prefix}] {self.message}"


class Doctor:
    def __init__(self, project: ProjectPaths | Path) -> None:
        if isinstance(project, ProjectPaths):
            self.project = project
        else:
            self.project = ProjectPaths(root=project, config=dict(DEFAULT_CONFIG))
        self.root = self.project.root
        self.findings: list[Finding] = []

    def error(self, message: str, path: str | None = None) -> None:
        self.findings.append(Finding("error", message, path))

    def warning(self, message: str, path: str | None = None) -> None:
        self.findings.append(Finding("warning", message, path))

    def is_toolkit_repo(self) -> bool:
        return (self.root / "pyproject.toml").exists() and (self.root / "src" / "rkp" / "cli.py").exists()

    def check_required_paths(self) -> None:
        required = [
            self.project.config.get("manifest", "Tools/asset_manifest.json"),
            self.project.config.get("assets_dir", "Assets/Imported"),
        ]
        recommended = [
            "README.md",
            "LICENSE",
            "Makefile",
        ]
        toolkit_recommended = [
            "pyproject.toml",
            "rkp.json",
            "project.yml",
            ".github/workflows/ci.yml",
            self.project.config.get("textures_dir", "Assets/Textures"),
            "Docs/guide.md",
            "Docs/cli-tool.md",
            "Docs/slash-commands.md",
            "Docs/production-playbook.md",
            "Docs/new-game-startup.md",
            "Docs/WORKLOG.md",
            "Docs/ai-handoff.md",
            "Tools/rkp.py",
            "Tools/prompt_asset.py",
            "src/rkp/cli.py",
            "src/rkp/prompt_asset.py",
            "Tests/test_rkp_cli.py",
            "Tests/test_rkp_package.py",
            ".claude/commands/rkp.md",
            ".claude/commands/rkp-asset.md",
            ".claude/commands/rkp-status.md",
            "Skills/realitykit-pipeline-guide/SKILL.md",
        ]
        if self.is_toolkit_repo():
            recommended.extend(toolkit_recommended)
        for rel in required:
            if not (self.root / rel).exists():
                self.error("required path is missing", rel)
        for rel in recommended:
            if not (self.root / rel).exists():
                self.warning("recommended path is missing", rel)

    def check_manifest(self) -> None:
        manifest_path = self.project.manifest
        if not manifest_path.exists():
            return

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.error(f"invalid JSON: {exc}", self._rel(manifest_path))
            return

        assets = manifest.get("assets")
        if not isinstance(assets, list):
            self.error("assets must be a list", self._rel(manifest_path))
            return
        if not assets:
            return

        seen_ids: set[str] = set()
        seen_files: set[str] = set()
        for index, asset in enumerate(assets):
            label = f"{self._rel(manifest_path)} assets[{index}]"
            if not isinstance(asset, dict):
                self.error("asset entry must be an object", label)
                continue

            asset_id = asset.get("id")
            file_name = asset.get("file")
            status = asset.get("status")
            if not isinstance(asset_id, str) or not re.fullmatch(r"[a-z0-9_]+", asset_id):
                self.error("id must be snake_case", label)
            elif asset_id in seen_ids:
                self.error(f"duplicate asset id: {asset_id}", label)
            else:
                seen_ids.add(asset_id)

            if not isinstance(file_name, str) or not file_name.endswith(".usdz"):
                self.error("file must be a .usdz filename", label)
            elif file_name in seen_files:
                self.error(f"duplicate asset file: {file_name}", label)
            else:
                seen_files.add(file_name)

            for numeric_key in ("maxTriangles", "maxTextureSize"):
                value = asset.get(numeric_key)
                if not isinstance(value, int) or value <= 0:
                    self.error(f"{numeric_key} must be a positive integer", label)

            if status == "imported" and isinstance(file_name, str):
                imported_path = self.project.assets_dir / file_name
                if not imported_path.exists():
                    self.error(f"imported asset file missing: {file_name}", self._rel(self.project.assets_dir))
                elif imported_path.stat().st_size == 0:
                    self.error(f"imported asset file is empty: {file_name}", self._rel(self.project.assets_dir))

        imported_files = {path.name for path in self.project.assets_dir.glob("*.usdz")}
        untracked_assets = sorted(imported_files - seen_files)
        for file_name in untracked_assets:
            self.warning("USDZ exists without manifest entry", self._rel(self.project.assets_dir / file_name))

    def check_project_paths(self) -> None:
        project_path = self.root / "project.yml"
        if not project_path.exists():
            return

        for line in project_path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"\s*-\s+path:\s+(.+)\s*$", line)
            if not match:
                continue
            rel = match.group(1).strip().strip("\"'")
            if not (self.root / rel).exists():
                self.error("XcodeGen source/resource path does not exist", rel)

    def check_markdown_links(self) -> None:
        for md_path in self.root.glob("**/*.md"):
            if self._is_ignored(md_path):
                continue
            text = md_path.read_text(encoding="utf-8")
            for target in self._extract_markdown_targets(text):
                if self._is_external_target(target):
                    continue
                clean = target.split("#", 1)[0]
                if not clean:
                    continue
                linked = (md_path.parent / clean).resolve()
                try:
                    linked.relative_to(self.root)
                except ValueError:
                    self.warning(f"link points outside repo: {target}", self._rel(md_path))
                    continue
                if not linked.exists():
                    self.error(f"broken markdown link/image: {target}", self._rel(md_path))

    def check_public_text(self) -> None:
        local_path_pattern = re.compile(r"/Users/[^\\s)`]+")
        for path in self._text_files():
            rel = self._rel(path)
            if rel.startswith("Docs/WORKLOG.md") or rel in {"Tools/pipeline_doctor.py", "src/rkp/pipeline_doctor.py"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for match in local_path_pattern.finditer(text):
                self.warning(f"local absolute path appears in public text: {match.group(0)}", rel)

            if rel == "README.md" and "rtk" in text and "not a public dependency" not in text:
                self.error("README mentions rtk without explaining it is not a public dependency", rel)

    def check_skill_pack(self) -> None:
        skill = self.root / "Skills/realitykit-pipeline-guide"
        if not skill.exists():
            return
        required = [
            "SKILL.md",
            "agents/openai.yaml",
            "references/workflows.md",
            "references/contracts.md",
            "references/commands.md",
            "references/slash-commands.md",
            "scripts/check_repo.py",
        ]
        for rel in required:
            if not (skill / rel).exists():
                self.error("skill file is missing", f"Skills/realitykit-pipeline-guide/{rel}")

        skill_md = skill / "SKILL.md"
        if skill_md.exists():
            text = skill_md.read_text(encoding="utf-8")
            if "[TODO" in text or "TODO:" in text:
                self.error("skill still contains TODO placeholder", self._rel(skill_md))
            if "name: realitykit-pipeline-guide" not in text:
                self.error("skill frontmatter name is missing or wrong", self._rel(skill_md))

    def check_ci(self) -> None:
        ci = self.root / ".github/workflows/ci.yml"
        if not ci.exists():
            return
        text = ci.read_text(encoding="utf-8")
        for required in ("xcodegen generate", "Tools/asset_manifest.json", "python3 -m unittest discover -s Tests", "xcodebuild"):
            if required not in text:
                self.error(f"CI is missing required step content: {required}", ".github/workflows/ci.yml")
        if "actions/checkout@v4" in text:
            self.warning("actions/checkout@v4 currently emits Node 20 deprecation warnings", ".github/workflows/ci.yml")

    def check_blender(self) -> None:
        override = os.environ.get("BLENDER")
        if override:
            blender = Path(override)
            if not blender.exists() or not os.access(blender, os.X_OK):
                self.error(f"Blender executable is not available: {override}", "BLENDER")
            return

        executable = shutil.which("blender")
        if executable:
            return

        if MACOS_BLENDER_APP.exists() and os.access(MACOS_BLENDER_APP, os.X_OK):
            return

        self.error(
            "Blender executable not found. Install Blender or set BLENDER=/path/to/blender.",
            "BLENDER",
        )

    def collect(self, include_blender: bool = False) -> list[Finding]:
        self.check_required_paths()
        self.check_manifest()
        self.check_project_paths()
        self.check_markdown_links()
        self.check_public_text()
        self.check_skill_pack()
        self.check_ci()
        if include_blender:
            self.check_blender()
        return self.findings

    def summary(self) -> dict:
        errors = [finding for finding in self.findings if finding.level == "error"]
        warnings = [finding for finding in self.findings if finding.level == "warning"]
        return {
            "ok": len(errors) == 0,
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": [finding.to_dict() for finding in self.findings],
        }

    def run(self, include_blender: bool = False) -> int:
        self.collect(include_blender=include_blender)
        summary = self.summary()

        if not self.findings:
            print("pipeline doctor: ok")
            return 0

        for finding in self.findings:
            print(finding.render())

        print(f"pipeline doctor: {summary['errors']} error(s), {summary['warnings']} warning(s)")
        return 1 if summary["errors"] else 0

    def _extract_markdown_targets(self, text: str) -> Iterable[str]:
        image_or_link = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
        for match in image_or_link.finditer(text):
            target = match.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            yield target

    def _is_external_target(self, target: str) -> bool:
        return (
            "://" in target
            or target.startswith("mailto:")
            or target.startswith("#")
            or target.startswith("app://")
            or target.startswith("plugin://")
        )

    def _text_files(self) -> Iterable[Path]:
        for path in self.root.glob("**/*"):
            if self._is_ignored(path) or not path.is_file():
                continue
            if path.suffix in TEXT_EXTENSIONS:
                yield path

    def _is_ignored(self, path: Path) -> bool:
        parts = path.relative_to(self.root).parts
        return parts[0] in {".git", "Build", ".claude", "RealityKitPipelineDemo.xcodeproj"}

    def _rel(self, path: Path) -> str:
        return str(path.relative_to(self.root))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the RealityKit pipeline repo structure.")
    parser.add_argument("--blender", action="store_true", help="Also verify Blender executable discovery")
    args = parser.parse_args()
    return Doctor(load_project()).run(include_blender=args.blender)


if __name__ == "__main__":
    sys.exit(main())
