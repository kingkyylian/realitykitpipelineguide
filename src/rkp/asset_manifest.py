from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rkp.rkp_project import ProjectPaths, load_project

JsonDict = dict[str, Any]
Asset = dict[str, Any]


def _project(project: ProjectPaths | None = None) -> ProjectPaths:
    return project or load_project()


def load_manifest(project: ProjectPaths | None = None) -> JsonDict:
    active_project = _project(project)
    return json.loads(active_project.manifest.read_text(encoding="utf-8"))


def write_manifest(manifest: JsonDict, project: ProjectPaths | None = None) -> None:
    active_project = _project(project)
    active_project.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def assets(manifest: JsonDict) -> list[Asset]:
    value = manifest.get("assets", [])
    return value if isinstance(value, list) else []


def ensure_assets(manifest: JsonDict) -> list[Asset]:
    value = manifest.setdefault("assets", [])
    if not isinstance(value, list):
        raise TypeError("manifest assets must be a list")
    return value


def find_asset(manifest: JsonDict, asset_id: str) -> Asset | None:
    for asset in assets(manifest):
        if isinstance(asset, dict) and asset.get("id") == asset_id:
            return asset
    return None


def load_asset(asset_id: str, project: ProjectPaths | None = None) -> Asset | None:
    return find_asset(load_manifest(project), asset_id)


def imported_asset_ids(manifest: JsonDict) -> list[str]:
    return [
        asset["id"]
        for asset in assets(manifest)
        if isinstance(asset, dict) and isinstance(asset.get("id"), str) and asset.get("status") == "imported"
    ]


def asset_file_name(asset_id: str) -> str:
    return f"{asset_id}.usdz"


def asset_usdz_path(asset: Asset, project: ProjectPaths | None = None) -> Path:
    active_project = _project(project)
    return active_project.assets_dir / str(asset["file"])


def basecolor_texture_name(asset_id: str) -> str:
    return f"{asset_id}_basecolor.png"


def expected_basecolor_name(asset: Asset) -> str | None:
    texture_maps = asset.get("textureMaps")
    if texture_maps is not None and "baseColor" not in texture_maps:
        return None
    return basecolor_texture_name(str(asset["id"]))


def expected_basecolor_texture(asset: Asset, project: ProjectPaths | None = None) -> Path | None:
    expected = expected_basecolor_name(asset)
    if expected is None:
        return None
    active_project = _project(project)
    return active_project.textures_dir / expected
