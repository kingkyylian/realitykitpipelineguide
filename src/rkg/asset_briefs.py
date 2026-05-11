from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def asset_brief(asset_id: str, asset: Mapping[str, Any]) -> str:
    role = str(asset.get("role") or asset.get("type") or "prop")
    asset_type = str(asset.get("type") or "prop")
    budget = str(asset.get("budget") or "1500 tris / 512 texture")
    fallback = str(asset.get("fallback") or "procedural_fallback")
    return f"""# Asset Brief: {asset_id}

## Gameplay Need

Provide the `{role}` role for the generated RealityKit game while keeping the procedural fallback available until imported art is accepted.

## Contract

- Asset id: {asset_id}
- Type: {asset_type}
- Role: {role}
- Budget: {budget}
- Fallback: {fallback}
- Runtime file: `Assets/Imported/{asset_id}.usdz`
- Scale: 1 Blender unit = 1 meter
- Origin: centered for runtime placement unless this brief is updated
- Collision: match gameplay role, not raw mesh bounds

## Acceptance Checklist

- [ ] USDZ exported to `Assets/Imported/{asset_id}.usdz`.
- [ ] Manifest entry remains aligned with this role and budget.
- [ ] `rkp inspect-usdz {asset_id} --json` passes.
- [ ] Runtime screenshot evidence captured before imported status.
- [ ] `rkp accept-asset {asset_id} --screenshot <path>` passes.
"""
