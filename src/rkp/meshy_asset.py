#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path

_BASE = "https://api.meshy.ai/openapi/v2/text-to-3d"
_POLL_INTERVAL = 5
_TIMEOUT = 300


def _request(url: str, api_key: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _create_task(prompt: str, api_key: str) -> str:
    result = _request(_BASE, api_key, {
        "mode": "preview",
        "prompt": prompt,
        "target_formats": ["usdz"],
        "should_remesh": True,
        "topology": "quad",
        "target_polycount": 1500,
    })
    return result["result"]


def _refine_task(preview_id: str, api_key: str) -> str:
    result = _request(_BASE, api_key, {
        "mode": "refine",
        "preview_task_id": preview_id,
        "target_formats": ["usdz"],
        "enable_pbr": True,
    })
    return result["result"]


def _poll(task_id: str, api_key: str, label: str) -> dict:
    deadline = time.time() + _TIMEOUT
    while time.time() < deadline:
        data = _request(f"{_BASE}/{task_id}", api_key)
        status = data.get("status", "")
        progress = data.get("progress", 0)
        print(f"\r  {label}: {status} {progress}%", end="", flush=True)
        if status == "SUCCEEDED":
            print()
            return data
        if status == "FAILED":
            print()
            raise RuntimeError(f"Meshy task failed: {data.get('message', 'unknown error')}")
        time.sleep(_POLL_INTERVAL)
    raise TimeoutError(f"Meshy task timed out after {_TIMEOUT}s")


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)


def generate_usdz(
    prompt: str,
    asset_id: str,
    output_path: Path,
    api_key: str | None = None,
    refine: bool = False,
) -> Path:
    key = api_key or os.environ.get("MESHY_API_KEY")
    if not key:
        raise ValueError("MESHY_API_KEY not set")

    print(f"  meshy: creating preview task for '{prompt}'")
    preview_id = _create_task(prompt, key)
    preview_data = _poll(preview_id, key, "preview")

    if refine:
        print(f"  meshy: refining for PBR texture")
        refine_id = _refine_task(preview_id, key)
        final_data = _poll(refine_id, key, "refine")
    else:
        final_data = preview_data

    usdz_url = final_data.get("model_urls", {}).get("usdz")
    if not usdz_url:
        raise RuntimeError("Meshy response missing USDZ URL")

    print(f"  meshy: downloading USDZ")
    _download(usdz_url, output_path)
    return output_path
