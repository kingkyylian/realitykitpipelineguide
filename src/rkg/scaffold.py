from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from rkg.spec import assert_valid_game_spec


JsonDict = dict[str, Any]


def init_game(spec: Mapping[str, Any], output: Path, *, force: bool = False) -> None:
    assert_valid_game_spec(spec)
    output = output.resolve()
    if output.exists() and any(output.iterdir()) and not force:
        raise ValueError("output directory is not empty; pass --force to overwrite generated files")

    game = spec["game"]
    game_id = str(game["id"])
    display_name = str(game["display_name"])
    swift_name = _swift_name(game_id)
    bundle_suffix = _bundle_suffix(game_id)

    _make_dirs(output, swift_name)
    _write_json(output / "GameSpec.json", dict(spec))
    _write_json(output / "rkp.json", _rkp_config(swift_name))
    _write_json(output / "Tools" / "asset_manifest.json", _asset_manifest(spec))

    _write_text(output / "project.yml", _project_yml(swift_name, display_name, bundle_suffix))
    _write_text(output / "Sources" / swift_name / f"{swift_name}App.swift", _app_swift(swift_name))
    _write_text(output / "Sources" / swift_name / "ContentView.swift", _content_view_swift(display_name, spec))
    _write_text(output / "Sources" / swift_name / "GameView.swift", _game_view_swift(spec))
    _write_text(output / "Docs" / "WORKLOG.md", _worklog(display_name))
    _write_text(output / "Docs" / "ai-handoff.md", _handoff(display_name, game_id))
    _write_text(output / "Docs" / "store" / "metadata.md", _metadata(display_name, spec))
    _write_text(output / "Docs" / "store" / "review-notes.md", _review_notes(display_name, spec))
    _write_text(output / "Docs" / "store" / "privacy.md", _privacy_notes(display_name, spec))


def _make_dirs(output: Path, swift_name: str) -> None:
    for rel in [
        "Assets/Imported",
        "Assets/Textures",
        "Assets/Source",
        "Docs/assets",
        "Docs/screenshots",
        "Docs/store",
        "Tools/blender",
        f"Sources/{swift_name}",
        "Tests",
    ]:
        (output / rel).mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _swift_name(game_id: str) -> str:
    return "".join(part.capitalize() for part in game_id.split("_"))


def _bundle_suffix(game_id: str) -> str:
    return re.sub(r"[^a-z0-9]", "", game_id.lower())


def _swift_string_literal(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=True)


def _yaml_string(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=True)


def _rkp_config(swift_name: str) -> JsonDict:
    return {
        "manifest": "Tools/asset_manifest.json",
        "assets_dir": "Assets/Imported",
        "docs_dir": "Docs",
        "blender_dir": "Tools/blender",
        "textures_dir": "Assets/Textures",
        "source_dir": "Assets/Source",
        "tests_dir": "Tests",
        "xcode_project": f"{swift_name}.xcodeproj",
        "xcode_scheme": swift_name,
        "xcode_destination": "generic/platform=iOS Simulator",
        "derived_data_path": "Build/DerivedData",
    }


def _asset_manifest(spec: Mapping[str, Any]) -> JsonDict:
    game = spec["game"]
    manifest_assets = []
    for asset_id, asset in spec["assets"].items():
        manifest_assets.append(
            {
                "id": asset_id,
                "status": "planned",
                "type": asset["type"],
                "file": f"{asset_id}.usdz",
                "budget": asset["budget"],
                "fallback": asset["fallback"],
                "scale": "1 Blender unit = 1 meter",
                "origin": "centered for runtime placement unless the asset brief says otherwise",
                "collision": "match gameplay role, not raw mesh bounds",
            }
        )
    return {
        "project": game["display_name"],
        "scale": "1 Blender unit = 1 meter",
        "assets": manifest_assets,
    }


def _project_yml(swift_name: str, display_name: str, bundle_suffix: str) -> str:
    return f"""name: {swift_name}
options:
  bundleIdPrefix: com.kyylian
  deploymentTarget:
    iOS: "18.0"
settings:
  base:
    SWIFT_VERSION: 5.0
    MARKETING_VERSION: 0.1.0
    CURRENT_PROJECT_VERSION: 1
targets:
  {swift_name}:
    type: application
    platform: iOS
    sources:
      - path: Sources/{swift_name}
      - path: Assets/Imported
        type: folder
        buildPhase: resources
      - path: Assets/Textures
        type: folder
        buildPhase: resources
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: com.kyylian.{bundle_suffix}
        PRODUCT_NAME: {swift_name}
        GENERATE_INFOPLIST_FILE: YES
        INFOPLIST_KEY_CFBundleDisplayName: {_yaml_string(display_name)}
        INFOPLIST_KEY_UIApplicationSceneManifest_Generation: YES
        INFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents: YES
        INFOPLIST_KEY_UILaunchScreen_Generation: YES
        TARGETED_DEVICE_FAMILY: "1,2"
"""


def _app_swift(swift_name: str) -> str:
    return f"""import SwiftUI

@main
struct {swift_name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}
"""


def _content_view_swift(display_name: str, spec: Mapping[str, Any]) -> str:
    game = spec["game"]
    loop = spec["loop"]
    title = _swift_string_literal(display_name)
    subtitle = _swift_string_literal(f"{game['archetype']} / {game['session_seconds']}s")
    player_action = _swift_string_literal(loop["player_action"])
    return f"""import SwiftUI

struct ContentView: View {{
    @State private var score = 0
    @State private var isPlaying = false

    var body: some View {{
        ZStack(alignment: .top) {{
            GameView()
                .ignoresSafeArea()

            VStack(spacing: 8) {{
                HStack {{
                    VStack(alignment: .leading, spacing: 2) {{
                        Text({title})
                            .font(.headline)
                        Text({subtitle})
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }}
                    Spacer()
                    Text("Score \\(score)")
                        .font(.headline.monospacedDigit())
                }}

                HStack {{
                    Text({player_action})
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button(isPlaying ? "Reset" : "Start") {{
                        isPlaying.toggle()
                        if !isPlaying {{
                            score = 0
                        }}
                    }}
                    .buttonStyle(.borderedProminent)
                }}
            }}
            .padding()
            .background(.thinMaterial)
        }}
    }}
}}
"""


def _game_view_swift(spec: Mapping[str, Any]) -> str:
    asset_id = _swift_string_literal(_primary_runtime_asset_id(spec))
    return """import RealityKit
import SwiftUI

struct GameView: UIViewRepresentable {
    func makeUIView(context: Context) -> ARView {
        let view = ARView(frame: .zero, cameraMode: .nonAR, automaticallyConfigureSession: false)
        let anchor = AnchorEntity(world: .zero)

        let floor = ModelEntity(
            mesh: .generatePlane(width: 2.4, depth: 2.4),
            materials: [SimpleMaterial(color: .darkGray, roughness: 0.8, isMetallic: false)]
        )
        floor.position = [0, -0.45, 0]
        anchor.addChild(floor)

        let target: Entity
        if let imported = try? Entity.load(named: __RKG_ASSET_ID__) {
            imported.scale = [1, 1, 1]
            target = imported
        } else {
            target = proceduralTarget()
        }
        target.position = [0, 0, -1.2]
        anchor.addChild(target)

        view.scene.addAnchor(anchor)
        view.cameraTransform = Transform(
            scale: .one,
            rotation: simd_quatf(angle: 0, axis: [0, 1, 0]),
            translation: [0, 0.35, 1.2]
        )
        return view
    }

    func updateUIView(_ uiView: ARView, context: Context) {}

    private func proceduralTarget() -> ModelEntity {
        ModelEntity(
            mesh: .generateSphere(radius: 0.18),
            materials: [SimpleMaterial(color: .systemRed, roughness: 0.35, isMetallic: false)]
        )
    }
}
""".replace("__RKG_ASSET_ID__", asset_id)


def _primary_runtime_asset_id(spec: Mapping[str, Any]) -> str:
    assets = spec["assets"]
    for asset_id, asset in assets.items():
        if isinstance(asset, Mapping) and asset.get("type") == "gameplay_target":
            return str(asset_id)
    return str(next(iter(assets)))


def _worklog(display_name: str) -> str:
    return f"""# Worklog

## Factory Scaffold

Goal: Create the first generated RealityKit game skeleton for {display_name}.
Verification: Run `python3 Tools/rkp.py doctor`, then generate/build with XcodeGen and xcodebuild when Xcode is available.
Lesson: Keep procedural placeholders until imported assets are accepted with screenshot evidence.
"""


def _handoff(display_name: str, game_id: str) -> str:
    return f"""# AI Handoff

Project: {display_name}
Game id: {game_id}

Start from `GameSpec.json`. Keep RKP as the asset acceptance source of truth. Do not mark any asset imported without `rkp accept-asset` and screenshot evidence.
"""


def _metadata(display_name: str, spec: Mapping[str, Any]) -> str:
    game = spec["game"]
    loop = spec["loop"]
    return f"""# Store Metadata Draft

App Name: {display_name}
Subtitle: Fast {game["archetype"].replace("_", " ")} sessions
Monetization: {game["monetization"]}

## Description Draft

{display_name} is a short-session arcade game where players {loop["player_action"]}. Sessions last {game["session_seconds"]} seconds and focus on clean input, readable targets, and repeatable score improvement.

## Screenshot Checklist

- gameplay_start
- mid_session
- results
"""


def _review_notes(display_name: str, spec: Mapping[str, Any]) -> str:
    game = spec["game"]
    return f"""# App Review Notes

{display_name} is a standalone RealityKit game.

- Login required: no
- Backend required: no
- Session length: {game["session_seconds"]} seconds
- Core input: {game["input"]}
- Monetization: {game["monetization"]}

All screenshots and metadata should describe actual gameplay before submission.
"""


def _privacy_notes(display_name: str, spec: Mapping[str, Any]) -> str:
    return f"""# Privacy Notes

{display_name} scaffold default:

- No account system.
- No analytics SDK.
- No advertising SDK.
- No network requirement.
- No personal data collection.

Update this file before submission if monetization, analytics, ads, Game Center, or backend services are added.
"""
