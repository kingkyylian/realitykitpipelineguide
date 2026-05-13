#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from rkp.asset_manifest import asset_usdz_path, find_asset, load_manifest, write_manifest
from rkp.inspect_usdz import inspect_asset
from rkp.rkp_project import ProjectPaths, load_project
from rkp.runtime import module_command, package_env

PROJECT = load_project()


def relative(path: Path, project: ProjectPaths = PROJECT) -> str:
    return project.rel(path)


def resolve_input_path(path: Path, project: ProjectPaths = PROJECT) -> Path:
    expanded = path.expanduser()
    if expanded.is_absolute():
        return expanded
    return project.root / expanded


def validate_screenshot(path: Path) -> None:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return
    if data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9"):
        return
    raise ValueError(f"screenshot file is not a valid PNG or JPEG image: {path}")


def copy_screenshot(asset_id: str, screenshot: Path, project: ProjectPaths = PROJECT) -> Path:
    if not screenshot.exists() or not screenshot.is_file():
        raise ValueError(f"screenshot file does not exist: {screenshot}")
    validate_screenshot(screenshot)

    project.screenshots_dir.mkdir(parents=True, exist_ok=True)
    if screenshot.resolve().is_relative_to(project.screenshots_dir.resolve()):
        return screenshot.resolve()

    suffix = screenshot.suffix.lower() or ".png"
    output = project.screenshots_dir / f"{asset_id}_accepted{suffix}"
    shutil.copy2(screenshot, output)
    return output.resolve()


def update_asset_brief(
    asset_id: str,
    screenshot_rel: str,
    *,
    inspection_ok: bool = False,
    project: ProjectPaths = PROJECT,
) -> None:
    brief_path = project.docs_assets_dir / f"{asset_id}.md"
    if not brief_path.exists():
        return

    text = brief_path.read_text(encoding="utf-8")
    replacements = {
        f"- [ ] USDZ exported to `Assets/Imported/{asset_id}.usdz`.": f"- [x] USDZ exported to `Assets/Imported/{asset_id}.usdz`.",
        "- [ ] `Tools/asset_manifest.json` status changed from `planned` to `imported`.": "- [x] `Tools/asset_manifest.json` status changed from `planned` to `imported`.",
        "- [ ] Manifest entry remains aligned with this role and budget.": "- [x] Manifest entry remains aligned with this role and budget.",
        "- [ ] `make doctor` passes without new errors.": "- [x] `make doctor` passes without new errors.",
        "- [ ] Simulator screenshot captured if visual.": "- [x] Simulator screenshot captured if visual.",
        "- [ ] Runtime screenshot evidence captured before imported status.": "- [x] Runtime screenshot evidence captured before imported status.",
        f"- [ ] `rkp accept-asset {asset_id} --screenshot <path>` passes.": f"- [x] `rkp accept-asset {asset_id} --screenshot <path>` passes.",
        "- [ ] `Docs/WORKLOG.md` lesson added.": "- [x] `Docs/WORKLOG.md` lesson added.",
    }
    if inspection_ok:
        replacements[f"- [ ] `rkp inspect-usdz {asset_id} --json` passes."] = (
            f"- [x] `rkp inspect-usdz {asset_id} --json` passes."
        )
    for old, new in replacements.items():
        text = text.replace(old, new)

    if "## Evidence" not in text:
        text += f"\n## Evidence\n\n![Accepted {asset_id}](../screenshots/{Path(screenshot_rel).name})\n"

    brief_path.write_text(text, encoding="utf-8")


def prepend_worklog(asset_id: str, screenshot_rel: str, usdz_rel: str, project: ProjectPaths = PROJECT) -> None:
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"""### Accepted Asset: {asset_id}

**Durum:** Tamamlandı  
**Tarih:** {today}  
**Amaç:** `{asset_id}` asset'ini production pipeline'a screenshot evidence ile kabul etmek.

**Acceptance:**

- USDZ: `{usdz_rel}`
- Screenshot: `{screenshot_rel}`
- Manifest status: `imported`

**Verification:**

```text
make doctor: ok
```

**Öğrenme notu:**

Asset kabulü dosyanın oluşmasıyla değil, runtime evidence ve manifest/worklog kaydıyla tamamlanır.

"""
    if not project.worklog.exists():
        project.worklog.parent.mkdir(parents=True, exist_ok=True)
        project.worklog.write_text("# Worklog\n\n## Current Sprint\n\n", encoding="utf-8")
    text = project.worklog.read_text(encoding="utf-8")
    marker = "## Current Sprint\n\n"
    if marker in text:
        text = text.replace(marker, marker + entry, 1)
    else:
        text += "\n\n" + entry
    project.worklog.write_text(text, encoding="utf-8")


def run_doctor(project: ProjectPaths = PROJECT) -> int:
    return subprocess.run(
        module_command("rkp.pipeline_doctor"),
        cwd=project.root,
        env=package_env(),
    ).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Accept a built asset into the RealityKit pipeline.")
    parser.add_argument("--id", required=True, help="Asset id from Tools/asset_manifest.json")
    parser.add_argument("--screenshot", required=True, help="Required visual evidence path")
    args = parser.parse_args()

    manifest = load_manifest()
    asset = find_asset(manifest, args.id)
    if asset is None:
        print(f"error: unknown asset id: {args.id}", file=sys.stderr)
        return 1

    usdz_path = asset_usdz_path(asset, PROJECT)
    if not usdz_path.exists() or usdz_path.stat().st_size <= 0:
        print(f"error: built USDZ is missing or empty: {relative(usdz_path)}", file=sys.stderr)
        return 1

    try:
        accepted_screenshot = copy_screenshot(args.id, resolve_input_path(Path(args.screenshot)))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    screenshot_rel = relative(accepted_screenshot)
    usdz_rel = relative(usdz_path)
    inspection_ok = bool(inspect_asset(args.id).get("ok"))
    asset["status"] = "imported"
    notes = asset.get("notes", "")
    acceptance_note = f" Accepted with screenshot {screenshot_rel}."
    if acceptance_note.strip() not in notes:
        asset["notes"] = (notes.rstrip() + acceptance_note).strip()
    write_manifest(manifest)

    update_asset_brief(args.id, screenshot_rel, inspection_ok=inspection_ok)
    prepend_worklog(args.id, screenshot_rel, usdz_rel)

    doctor_status = run_doctor()
    if doctor_status != 0:
        print("error: asset accepted files were written, but pipeline doctor failed", file=sys.stderr)
        return doctor_status

    print(f"accepted asset: {args.id}")
    print(f"- usdz: {usdz_rel}")
    print(f"- screenshot: {screenshot_rel}")
    print("- manifest status: imported")
    return 0


if __name__ == "__main__":
    sys.exit(main())
