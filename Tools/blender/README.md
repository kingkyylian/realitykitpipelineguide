# Blender Authoring Tools

This folder contains Blender-side starter scripts for the asset pipeline.

The public repo does not require Blender to build the iOS app because final USDZ files are already committed under `Assets/Imported`. Blender is needed when you want to create or regenerate assets.

## Run the Arena Floor Script

From the repository root:

```bash
blender --background --python Tools/blender/create_arena_floor.py
```

The script creates a 3.2m x 3.2m floor plane as an 8x8 grid, assigns a generated 512x512 grid texture, writes UVs to a layer named `st`, saves an optional source `.blend` under `Assets/Source`, and exports `Assets/Imported/arena_floor.usdz`.

## Authoring Contract

- 1 Blender unit equals 1 meter.
- Object origin should be gameplay-friendly.
- Final app assets go to `Assets/Imported`.
- Optional source files and notes go to `Assets/Source`.
- UV layer for RealityKit/USD should be named `st` unless the asset contract says otherwise.
