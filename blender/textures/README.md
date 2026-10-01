# Texture sources · roof master

Every surface of the roof, house and weather is a **procedural PBR material at real-world scale**
(object-space metres), defined in `blender/prod/materials.py`. There are no bitmap textures on any
modelled surface, so nothing here needs re-baking when geometry changes. The only bitmaps are the three
distant background plates below.

## Procedural materials (source: `blender/prod/materials.py`)

| Material | Real-world basis | Maps driven procedurally |
| --- | --- | --- |
| `Shingle_NightSky`, `Cap_NightSky` | Duration COOL, Night Sky colour; ~1.2 mm granules | per-tab tone (face attribute `tone`), laminate shadow band (`shadow`), 2–6 cm blend mottling, light / blue-grey granule specks, soot variation, roughness 0.84–0.96, granule bump, wet state |
| `Underlayment` | synthetic underlayment, light grey with printed lap lines every 1 m | woven micro-bump, printed lines, wet state |
| `OSB` | 7/16″ oriented strand board | stretched flake voronoi in three tones, fibre bump |
| `Lumber` | framing lumber | grain noise, bump |
| `Trim / DripEdge / Gutter_DarkBronze`, `Soffit_White`, `BootFlange` | painted aluminium / steel | colour variation, pointiness edge wear (kept low on thin sheet metal), fine bump, wet state |
| `SoffitVentMetal` | perforated soffit vent | voronoi perforations |
| `Stucco` | LA sand-finish stucco | two-scale noise, ground-line dirt, bump |
| `Glass`, `Interior` | clear glazing, warm interior | transmission; emissive interior so windows read lit |
| `Lawn`, `Concrete`, foliage | site context | noise colour, bump, wet state; lawn alpha fades into the plate beyond ~32 m |
| `Water`, `RainDrop`, `Dust` | rain, beads, runoff, splashes, Santa Ana dust | transmission / IOR 1.333; dust is half-transparent matte |
| `HeatShimmer` | rising hot air | refraction IOR 1.012 through slow 4D noise, masked to zero at every edge |

**Dry and wet** are one material each: the scene property `wet` (0–1, keyframed) darkens albedo,
lowers roughness and adds a clear water coat (IOR 1.33). `heat`, `heat_t`, `plate_rain` and `plate_gold`
drive the heat haze and the backdrop crossfade the same way.

## Background plates (`plates/`)

AI-generated scenery used **only** as the distant backdrop (hills, palms, sky) on a camera-facing
cylinder 300 m away. They never show the roof, the house or any work, and must never be presented as
JM Roofing's work or a real location.

| File | Size | Generated with | Job |
| --- | --- | --- | --- |
| `clear-afternoon.png` | 3840×1648 | Higgsfield · GPT Image 2.5, 21:9, 4K, high quality, text prompt (LA late-afternoon horizon, hills, palms, no buildings in the foreground) | two candidates: `35e2daea…`, `ecfb96f6…` (one kept) |
| `rain-overcast.png` | 3840×1648 | same model, the clear plate as layout reference, "change only the weather: a Los Angeles winter rainstorm" | `d420af77…` |
| `golden-hour.png` | 3840×1648 | same model, the clear plate as layout reference, "change only the time of day: golden hour" | `4ea18d51…` |

Generated 2026-10-01 (UTC) with the user's explicit permission to use Higgsfield; about 17 credits.
Horizon row sits at 0.78 of the image height; the golden plate's sun is at the right edge (u ≈ 0.96).
The scene mixes them by `plate_rain` / `plate_gold` and adds a slight warm grade for heat.
