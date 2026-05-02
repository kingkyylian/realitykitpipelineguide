# Contributing

This repo is a teaching project. A good contribution should make the game or the learning path clearer.

## Local Setup

1. Install Xcode and XcodeGen.
2. Run `make generate`.
3. Run `make build`.
4. Read `Docs/WORKLOG.md` before starting a new change.

## Asset Changes

- Use a stable `snake_case` asset id.
- Match the USDZ filename to the asset id.
- Update `Tools/asset_manifest.json`.
- Put final app assets in `Assets/Imported`.
- Keep Blender/source-art notes or scripts under `Tools/blender` or `Assets/Source`.
- Capture or update screenshot evidence under `Docs/screenshots`.

## Documentation Changes

- Update `Docs/WORKLOG.md` for meaningful code, asset, or teaching-flow changes.
- Update `Docs/guide.md` when the learning path changes.
- Regenerate `Docs/pdf/realitykit-pipeline-guide.pdf` after editing `Docs/guide.md`.

## Before Opening a PR

Run:

```bash
make release-check
```

If you changed the guide:

```bash
make guide
```
