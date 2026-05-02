# Mobile Asset Budget

Use this as a starting point, then adjust after profiling on device.

| Asset Type | Triangle Target | Texture Target | Notes |
| --- | ---: | ---: | --- |
| Small target | 500-1,500 | 512-1024 | Main silhouette can be cleaner than hidden sides. |
| Projectile | 100-400 | Procedural | Prefer generated mesh/material first. |
| Arena prop | 500-2,000 | 512-1024 | Atlas repeated props. |
| Hero object | 3,000-8,000 | 1024-2048 | Use sparingly on mobile. |
| Background object | 100-800 | 256-512 | Avoid expensive shadows/materials. |

## RealityKit Notes

- Minimize transparency.
- Minimize dynamic shadows.
- Keep skeletal animation joint counts modest.
- Prefer fewer material slots.
- Profile before raising texture resolution.
