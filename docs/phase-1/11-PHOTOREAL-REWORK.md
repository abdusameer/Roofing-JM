# 11 · Photoreal Rework (roof sequence)

JM Roofing concept, 2026-09-30 / 10-01. This replaces **only the production method of the roof
experience**. Phase 0 truth, copy architecture, tiers, proof, compliance and the estimate flow are
unchanged. Nothing has been committed, pushed or deployed.

## 1. What changed and why

The Phase 1 proxy (EEVEE slab roof, scrubbed H.264, drawn SVG overlays) read as a diagram. The direction
was to stop and rebuild the roof as a **photoreal Cycles render of one verified roof system**, delivered as
a **WebP image sequence on one canvas**, with scroll mapped straight to frame number by
**GSAP ScrollTrigger (`scrub: true`)**. Not reused: the low-detail slab, blue rain strokes, washed-out light
and the clipped label layout. Generative video is not used for the roof, anatomy, panel or reassembly.
The only generated pixels are three distant background plates (§7).

| | Phase 1 proxy (archived) | Photoreal rework |
| --- | --- | --- |
| Scene | `blender/build_scene.py`, EEVEE, proxy slabs | `blender/prod/*.py` → `blender/roof_master.blend`, Cycles (Metal GPU, OIDN) |
| Delivery | one MP4 per orientation, 406 frames | WebP sequences: desktop 168 frames 1600×900, portrait 112 frames 900×1200 |
| Scrub | native scroll → `video.currentTime` | GSAP ScrollTrigger `scrub: true`: `frame = round(progress × (count − 1))` |
| Weather | drawn SVG strokes and arrows | rendered: particles, wet shading, refraction, light |
| Labels | projected text labels (clipped) | text only in HTML cards; numbered markers 1–5 on the layers |

The proxy pipeline, clips, stills, overlays and screenshots are kept in `archive/proxy-v1/`.

## 2. The roof system (one model, real scale)

Single-story LA stucco house, 12.0 × 8.4 m, 0.5 m overhang, **5:12 hip roof**. Equal pitches make every
layer offset a vertical translation, so each layer is a true shell of the one below.

| Layer (collection) | Object(s) | Real thickness / spec |
| --- | --- | --- |
| L5 Deck | `Deck_OSB` (ridge-vent slot cut) | 11.1 mm (7/16″ OSB) |
| L4 Drip edge | `DripEdge_*` (4 eaves, mitred at the hips) | 0.9 mm sheet, Solidify; under the underlayment at eaves |
| L3 Underlayment | `Underlayment` (slot cut) | 1.2 mm, laps the drip edge |
| L2 Shingles | `StarterCourse_*`, `Shingles_{Front,Right,Back,Left}` | OC Duration geometry: 13¼″ × 39⅜″ shingles, **5⅝″ exposure**, laminated base layer + random-width teeth, staggered offsets ≥ 12 cm, every course tilting over the two below; 0.7 mm bevels |
| L1 Hip and ridge caps | `HipRidgeCaps`, `RidgeVent`, `RidgeCap_Final` (the lock piece) | folded caps on both slopes |
| Eave | `Fascia_*`, `Soffit_*`, `SoffitVent_*`, `Gutter_*` (K-style, open profile + Solidify), hangers, downspout | painted dark bronze / white |
| Structure | `Rafters`, `Insulation_Context` | context only |
| Penetration | `PipeVent`, `PipeBoot_Collar`, `PipeBoot_Flange` | on the panel |

Every layer has its own collection and a **lift empty** (`Lift_L1…L5`) at the roof base (0, 0, 2.77 m) as a
clean pivot; children carry clean origins. Cut faces are capped (bisect + `holes_fill`, EXACT booleans
for solids), so no section shows a hollow shell.

## 3. Timeline (one master, 168 frames @ 24 fps; `blender/prod/timeline.json`)

| Beat | Frames | What the render shows |
| --- | --- | --- |
| Completed roof | 0–11 | clear afternoon, three-quarter view |
| Anatomy | 12–47 | caps, shingles, underlayment, drip edge, deck lift straight up in that order (1.25 / 1.10 / 0.78 / 0.52 / 0.30 m) |
| Isolate the panel | 48–63 | the panel's slice of every layer slides straight out (48–56), closes into one sample and rises to its hero position beside the house (56–63) |
| Heat | 64–81 | high, hard sun (el 62°), short shadows, a faint refractive haze; no glow, no numbers |
| Wind | 82–99 | low dry light, fine dust streaming past; every shingle stays flat |
| Rain | 100–123 | storm light, falling rain at every depth, splashes, beads, wet shading, thin runoff, drips off the drip edge |
| Clear | 124–131 | rain stops, the surface starts drying |
| Return | 132–145 | the sample re-opens to its layer heights, slides home into its openings |
| Reassemble | 146–159 | deck → drip edge → underlayment → shingles → caps; the last ridge cap seats at 159 |
| Hold | 160–167 | the finished roof in golden-hour light |
| Proof · "BUILT FOR EVERYTHING." · "GET AN ESTIMATE NOW." | — | HTML sections after the sequence (the final image is frame 167) |

## 4. The Proof Panel contract (verified on every frame by the build)

- **Cut from the master geometry:** the panel pieces are the master objects intersected with three stepped
  prisms (deck to 1.83 m up-slope, underlayment 1.64 m, shingles 1.44 m), and the same prisms cut the
  matching openings out of the masters. Shingles are split with the same three planes and capped.
  14 pieces: deck, drip edge, underlayment, starter course, shingles, fascia, soffit, soffit vent, gutter,
  hangers, rafters, pipe, boot collar, boot flange.
- **Translation only:** the panel is a child set of `PanelRig`; rotations are never keyed.
- **Exact return:** pieces ride their layers during anatomy (no holes), slide out, assemble, then do the
  exact reverse.

`build.py` steps all 168 frames and writes the result to the scene property `manifest.panel_check`:

```
translation_only: true   max_rotation_delta: 0.0
exact_home: true          max_home_offset_m: 0.0   (frames 0–11 and 157–167)
```

## 5. Look: materials, light, camera

- **Materials:** procedural PBR at real scale, with colour variation, roughness, normal detail and edge
  wear, and separate dry and wet states. See `blender/textures/README.md`.
- **Light:** Nishita multiple-scattering sky plus a 0.55° sun; six keyed states (clear, heat, wind, rain,
  washed, golden). AgX "Punchy", exposure +1.4. Cycles at 36 samples (desktop) and 32 (portrait),
  adaptive sampling, OIDN, 8/3/4/8 bounces.
- **Motion blur:** shutter 0.12 everywhere except the rain beat (0.45, where blur draws the streaks).
  Every scrubbed frame can be a resting still. A 0.45 shutter smeared the fast camera swing into the
  panel close-up (frame 56), so those frames were re-rendered.
- **Camera:** one language for both orientations: a close three-quarter from the front left on the
  house, then a level hero on the panel against the far hills (50–62 mm, f/2–2.2, so the background
  falls off). The portrait camera is framed separately on the same keys.
- **Weather is physical:**
  - **Rain:** about 52,000 Newtonian drops with gravity off, so they fall at roughly 9 m/s terminal speed. A dense volume sits in front of the panel. Drops are elongated along their velocity and motion-blurred, and they die on light, ray-invisible collision proxies.
  - **Splashes and beads:** 9,000 clear splashes come off the panel's top faces. 2,600 bead instances grow and shrink with `wet`.
  - **Runoff and drips:** nine runoff curves follow the courses, and 1,300 drips fall off the drip edge into the gutter.
  - **Dust:** 16,000 pre-streaked motes, gone before the rain starts.

## 6. Web delivery (`prototype/roof-sequence/`)

- **One canvas:** `.stage-canvas` sits over a poster `<img>`, which is frame 0 itself, so the swap is invisible.
- **Scroll:** GSAP 3.14.2 and ScrollTrigger 3.14.2 load from cdnjs, pinned with SRI. The tween runs `{ f: count − 1, ease: "none", scrollTrigger: { start: "top top", end: "bottom bottom", scrub: true } }`. Chapter heights are frame counts (`--n`) times one scroll unit (`--u`), so the HTML chapters and the frames stay one linear mapping. Reversing the scroll reverses time. If the CDN is blocked, the same mapping runs on native scroll.
- **Loading order:**
  1. The poster loads with high priority.
  2. Next, the first chapter, then keyframes (every 8th frame on desktop, every 6th on portrait).
  3. Then the rest in groups of 12 or 10, nearest group first.
  4. Downloads are capped at 4 in flight (3 on portrait).
- **Decoding:** frames are kept as compressed blobs. Only ±10 (portrait ±7) are decoded as `ImageBitmap`s, and the rest are closed, so memory stays flat. The canvas always draws the nearest decoded frame. It is never blank.
- **Text:** every word is semantic HTML.
  - **Desktop:** the cards sit in one fixed text column that crossfades to the active chapter.
  - **Phones:** cards scroll beneath the pinned 3:4 stage.
  - **Markers:** numbered markers 1–5 (matching the anatomy list) are projected from Blender anchors and hidden when their point is occluded or off-stage.
- **Tiers and fallbacks (unchanged):** static (no JS, Save-Data, 2G, low power, landscape phone, failed media), reduced motion (the static story with the 7 keyframe stills, and no sequence requests), and the estimate CTA always present.
- **Manifest:** `media/seq/manifest.json` holds:
  - counts, sizes, paths, keyframes
  - the per-frame `master` map (portrait index → master time)
  - chapters, beats, conditions
  - stills
  - projected anchors

## 7. Generated imagery (disclosure)

Three background plates (clear, rain, golden) come from Higgsfield GPT Image 2.5, generated with the
user's permission (about 17 credits; jobs listed in `blender/textures/README.md`). They show only distant
hills, palms and sky on a backdrop 300 m away. The page footer says so: "The distant hills and sky are
AI-generated background plates … used only as scenery." No generated imagery shows a roof, a house or
any work, and none is presented as JM Roofing's.

## 8. Reproduce

```
tools/render-sequence.sh                 # build roof_master.blend → render both sequences → anchors → WebP + manifest
node tools/check.mjs                      # static gate
node tools/qa.mjs shots|behaviour|perf    # headless Chrome QA
```

Raw PNG frames go to `$TMPDIR/roof-frames`, outside iCloud. The script resumes and skips finished
frames. Measured on the M2:
- Desktop sequence: 2.9 h at 36 samples, roughly 28–350 s per frame. Close return frames with shallow depth of field are the slowest.
- Portrait sequence: 1.2 h at 32 samples.
- Encode: q82 for desktop gives 8.40 MB; q80 for portrait gives 3.18 MB.

## 9. Results

See 09 §0. In short:
- 134/134 static checks pass.
- 7 viewports are clean.
- 11/11 behaviour checks pass.
- Frame pacing is 59.9 fps median on desktop and on a 4× slowed phone profile.
- Lighthouse scores mobile Performance 96 and desktop 100, with Accessibility and Best Practices at 100 on both.
