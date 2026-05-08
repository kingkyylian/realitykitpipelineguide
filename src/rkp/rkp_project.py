from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CONFIG_FILE = "rkp.json"
DEFAULT_CONFIG = {
    "manifest": "Tools/asset_manifest.json",
    "assets_dir": "Assets/Imported",
    "docs_dir": "Docs",
    "blender_dir": "Tools/blender",
    "textures_dir": "Assets/Textures",
    "source_dir": "Assets/Source",
    "tests_dir": "Tests",
    "xcode_project": None,
    "xcode_scheme": None,
    "xcode_destination": "generic/platform=iOS Simulator",
    "derived_data_path": "Build/DerivedData",
}


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    config: dict

    @property
    def manifest(self) -> Path:
        return self.root / self.config["manifest"]

    @property
    def assets_dir(self) -> Path:
        return self.root / self.config["assets_dir"]

    @property
    def docs_dir(self) -> Path:
        return self.root / self.config["docs_dir"]

    @property
    def screenshots_dir(self) -> Path:
        return self.docs_dir / "screenshots"

    @property
    def docs_assets_dir(self) -> Path:
        return self.docs_dir / "assets"

    @property
    def worklog(self) -> Path:
        return self.docs_dir / "WORKLOG.md"

    @property
    def blender_dir(self) -> Path:
        return self.root / self.config["blender_dir"]

    @property
    def textures_dir(self) -> Path:
        return self.root / self.config["textures_dir"]

    @property
    def source_dir(self) -> Path:
        return self.root / self.config["source_dir"]

    @property
    def tests_dir(self) -> Path:
        return self.root / self.config["tests_dir"]

    @property
    def xcode_project(self) -> Path | None:
        value = self.config.get("xcode_project")
        if not value:
            return None
        return self.root / value

    @property
    def xcode_scheme(self) -> str | None:
        return self.config.get("xcode_scheme")

    @property
    def xcode_destination(self) -> str:
        return self.config["xcode_destination"]

    @property
    def derived_data_path(self) -> Path:
        return self.root / self.config["derived_data_path"]

    def rel(self, path: Path) -> str:
        return str(path.relative_to(self.root))


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (candidate / CONFIG_FILE).exists():
            return candidate

    raise FileNotFoundError(f"could not find {CONFIG_FILE} from {current}")


def load_config(root: Path) -> dict:
    config_path = root / CONFIG_FILE
    config = dict(DEFAULT_CONFIG)
    if config_path.exists():
        loaded = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError(f"{CONFIG_FILE} must contain a JSON object")
        config.update({key: value for key, value in loaded.items() if value is not None})
    return config


def load_project(start: Path | None = None) -> ProjectPaths:
    root = find_project_root(start)
    return ProjectPaths(root=root, config=load_config(root))
