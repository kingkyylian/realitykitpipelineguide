# Blender to USDZ Checklist

## Scene Setup

- Unit scale: metric.
- 1 Blender unit equals 1 meter.
- Object forward/up axes documented in the Blender file.
- Object origin placed for gameplay, not for modeling convenience.
- Transforms applied before export.

## Mesh

- Remove hidden faces.
- Keep silhouette detail where players can see it.
- Use lower detail for underside/backside surfaces.
- Avoid tiny geometry that can be baked into textures.
- Name objects with stable snake_case names.

## UV and Materials

- UVs do not overlap unless intentionally mirrored.
- Texture sizes match `Tools/asset_manifest.json`.
- Prefer power-of-two texture dimensions.
- Keep material count low.
- Pack small props into atlases when possible.
- For the first texture teaching asset, use one base color texture only.
- Start with 512x512; use 1024x1024 only if simulator screenshots show a clear improvement.
- Use simple, readable color regions so missing or flipped UVs are obvious.
- Name texture files with the asset prefix, for example `target_basic_textured_basecolor.png`.
- Keep roughness/metallic as material values for now; do not add extra texture maps until base color import is verified.
- For USD export, match the shader UV Map node's `uv_map` field to the UV primvar name. The active Blender UV layer alone is not enough.
- If the source USDZ uses the `st` primvar, write the corrected UVs back to `st` before export.

## Export

- Export selected object only.
- Export as `.usdz` for quick RealityKit testing.
- Put final exports in `Assets/Imported`.
- Keep source `.blend` files outside the app target or in a separate art repository.
- Confirm textures are embedded in the USDZ or included by the export package before handing off.
- The first texture handoff path is `Assets/Imported/target_basic_textured.usdz`.

## Import Test

- Open in Reality Composer Pro.
- Confirm scale, pivot, material, and orientation.
- Add to the app only after the standalone import looks correct.
- In the app HUD, confirm the status changes to `target_basic_textured ready`.
- Capture a simulator screenshot and compare it with the untextured `target_basic` screenshot.
