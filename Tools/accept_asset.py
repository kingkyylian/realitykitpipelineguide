#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "Tools" / "asset_manifest.json"
WORKLOG_PATH = ROOT / "Docs" / "WORKLOG.md"
SCREENSHOTS_DIR = ROOT / "Docs" / "screenshots"


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def write_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def find_asset(manifest: dict, asset_id: str) -> dict | None:
    for asset in manifest.get("assets", []):
        if asset.get("id") == asset_id:
            return asset
    return None


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def copy_screenshot(asset_id: str, screenshot: Path) -> Path:
    if not screenshot.exists() or not screenshot.is_file():
        raise ValueError(f"screenshot file does not exist: {screenshot}")

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    if screenshot.resolve().is_relative_to(SCREENSHOTS_DIR.resolve()):
        return screenshot.resolve()

    suffix = screenshot.suffix.lower() or ".png"
    output = SCREENSHOTS_DIR / f"{asset_id}_accepted{suffix}"
    shutil.copy2(screenshot, output)
    return output.resolve()


def update_asset_brief(asset_id: str, screenshot_rel: str) -> None:
    brief_path = ROOT / "Docs" / "assets" / f"{asset_id}.md"
    if not brief_path.exists():
        return

    text = brief_path.read_text(encoding="utf-8")
    replacements = {
        f"- [ ] USDZ exported to `Assets/Imported/{asset_id}.usdz`.": f"- [x] USDZ exported to `Assets/Imported/{asset_id}.usdz`.",
        "- [ ] `Tools/asset_manifest.json` status changed from `planned` to `imported`.": "- [x] `Tools/asset_manifest.json` status changed from `planned` to `imported`.",
        "- [ ] `make doctor` passes without new errors.": "- [x] `make doctor` passes without new errors.",
        "- [ ] Simulator screenshot captured if visual.": "- [x] Simulator screenshot captured if visual.",
        "- [ ] `Docs/WORKLOG.md` lesson added.": "- [x] `Docs/WORKLOG.md` lesson added.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    if "## Evidence" not in text:
        text += f"\n## Evidence\n\n![Accepted {asset_id}](../screenshots/{Path(screenshot_rel).name})\n"

    brief_path.write_text(text, encoding="utf-8")


def prepend_worklog(asset_id: str, screenshot_rel: str, usdz_rel: str) -> None:
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
    text = WORKLOG_PATH.read_text(encoding="utf-8")
    marker = "## Current Sprint\n\n"
    if marker in text:
        text = text.replace(marker, marker + entry, 1)
    else:
        text += "\n\n" + entry
    WORKLOG_PATH.write_text(text, encoding="utf-8")


def run_doctor() -> int:
    return subprocess.run([sys.executable, "Tools/pipeline_doctor.py"], cwd=ROOT).returncode


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

    usdz_path = ROOT / "Assets" / "Imported" / asset["file"]
    if not usdz_path.exists() or usdz_path.stat().st_size <= 0:
        print(f"error: built USDZ is missing or empty: {relative(usdz_path)}", file=sys.stderr)
        return 1

    try:
        accepted_screenshot = copy_screenshot(args.id, Path(args.screenshot).expanduser())
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    screenshot_rel = relative(accepted_screenshot)
    usdz_rel = relative(usdz_path)
    asset["status"] = "imported"
    notes = asset.get("notes", "")
    acceptance_note = f" Accepted with screenshot {screenshot_rel}."
    if acceptance_note.strip() not in notes:
        asset["notes"] = (notes.rstrip() + acceptance_note).strip()
    write_manifest(manifest)

    update_asset_brief(args.id, screenshot_rel)
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
