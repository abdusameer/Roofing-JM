# Phase 2B · Claude Creative + Higgsfield roof experience

2026-10-01. The Blender pipeline is replaced on the page by a Higgsfield workflow: GPT Image 2.5 master
frames and Kling 3.0 start/end-frame clips, directed by Claude. It is a **cinematic concept visualization**,
not engineering testing, construction guidance, or documented product performance. Nothing has been
committed, pushed or deployed. The Blender-era page and media are kept in `archive/blender-v2/`.

## 1. Connection preflight

| Item | Result |
| --- | --- |
| Connector | **No Higgsfield MCP connector was attached to this session.** The already-authorized Higgsfield **CLI** (`higgsfield`, signed in as the user's account) was used instead; it exposes the same models. |
| Credit balance | 574.5 before → **527.75 after** |
| Recent generations | the three Phase 2 background plates (2026-10-01 01:38–01:39 UTC) and two earlier video jobs |
| Image models | GPT Image 2.5, GPT Image 2, Nano Banana / 2 / 2 Lite / Pro, Seedream 4.5 / 5.0, FLUX.2, Flux Kontext, Soul 2.0 / Cinematic / Location / Cast, Recraft V4.1, Ideogram 4.5, Kling O1 Image, Grok Image 2.0, Z Image, and others |
| Video models | Kling v3.0, Kling 3.0 Turbo, Kling 3.0 Omni Edit, Kling 2.6, Seedance 2.5 / 2.0 / 1.5 Pro, Veo 3.1 / 3 / 3.1 Lite, Wan 3.0 / 2.7 / 2.6, MiniMax H3, Hailuo, Grok Video 1.5, Gemini Omni Flash, FLUX 3 Video, and others |
| Kling 3.0 start + end frame | **Available**: `kling3_0` takes `start_image` and `end_image`; modes std / pro / 4k; sound on/off |
| Popcorn / storyboard workflow | **Not available** (no Popcorn in the model or workflow lists). The closest available method was used instead: reference-image editing with GPT Image 2.5, each master taking the previous master as its primary reference. |

## 2. Cost

| Generation | Model and settings | Est. | Actual |
| --- | --- | --- | --- |
| roof-complete-master | GPT Image 2.5, 16:9, 2K, high | 2.75 | 2.75 |
| roof-exploded-master | GPT Image 2.5, 16:9, 2K, high | 2.75 | 2.75 |
| proof-panel-isolated-master | GPT Image 2.5, 16:9, 2K, high | 2.75 | 2.75 |
| Clip A | Kling 3.0 pro (1080p), 5 s, start/end, no audio | 8.75 | 8.75 |
| Clip B | Kling 3.0 pro, 5 s | 8.75 | 8.75 |
| Clip C | Kling 3.0 pro, 12 s, same master as start and end | 21 | 21 |
| **Total** | one output per generation, no variants, no retries | **46.75** | **46.75** |

The Clip A retry was not needed. The mobile portrait set (about 47 credits) was **not generated**; see §6.

## 3. Assets

Job IDs, URLs and local paths are in `higgsfield/provenance.json`.

| Asset | Job | Local file |
| --- | --- | --- |
| roof-complete-master (2688×1520) | `a180b80f-eeae-4f58-9d5f-2f623236087e` | `higgsfield/masters/roof-complete-master.png` |
| roof-exploded-master | `3dad84a7-378b-4992-8862-4ce16e9ea732` | `higgsfield/masters/roof-exploded-master.png` |
| proof-panel-isolated-master | `b074a36f-2cdf-42c9-b6db-486d89ecf192` | `higgsfield/masters/proof-panel-isolated-master.png` |
| Clip A, 121 frames, 1912×1080 @ 24 fps | `8382f5c5-c0a9-4d76-9c21-727fcdc338e7` | `higgsfield/clips/clip-a-anatomy.mp4` |
| Clip B, 121 frames | `80a62786-5f9e-44cc-90d8-a3a0158b060a` | `higgsfield/clips/clip-b-panel.mp4` |
| Clip C, 289 frames | `91d5d110-2b84-4ed0-ab62-3fce1d0a88bd` | `higgsfield/clips/clip-c-weather.mp4` |
| Reference A + crops | (user supplied) | `higgsfield/references/` |

Extracted frames: `$TMPDIR/hf-frames/{a,b,c}/NNNN.png` (121 / 121 / 289), kept outside iCloud.

## 4. Visual consistency review and drift

| Check | Result |
| --- | --- |
| Master vs Reference A | The completed roof matches A's realism closely: charcoal dimensional shingles with granule texture, hip caps, vent pipe, black K-style gutter and downspout, white stucco, stone corner, warm interiors, palms, hillside, late sun. |
| Same house / camera / sky across masters | Yes. Walls, windows, gutter, palms, sky and framing are unchanged across all three masters. |
| Exploded master | A clean, believable stack: shingles with caps and pipe, dark underlayment, metal drip edge, OSB decking, exposed rafters. **Drift:** the small right-hand roof wing became open rafters. |
| Panel master | A rectangular opening runs through every layer. The section (shingles, drip edge, OSB, rafter) has come forward. **Drift:** it overlaps the roof's right side rather than floating fully clear, so it reads as "pulled forward" more than "isolated in open air". |
| Clip A | Accepted. Layers rise in order, there's no melting or multiplying, and the house is stable. **Drift:** the right wing dissolves gradually toward the end frame. |
| Clip B | Accepted. A layered section emerges and comes forward to the panel position. **Drift:** it first appears from the middle of the stack (near the ridge side), not from the front edge, and grows as it approaches. |
| Clip C | Calm → heat → wind (moving clouds, a faint haze) → storm light → clear, with the structure locked throughout. **Defect: the rain beat shows no falling drops, splashes, runoff or drip-edge water,** only storm light and darker shingles. A light wet speckle appears as it clears. |
| Join continuity (mean abs diff, 0–255) | A end → B start 4.84; B end → C start 4.70; C start → C end 1.06. A normal frame-to-frame step is 4.94, so the joins are seamless and the reversed segments play cleanly. |

## 5. Website (`prototype/roof-sequence/`)

Order on the page:
1. Opening hold (Clip A frame 0)
2. Clip A forward
3. Clip B forward
4. Clip C
5. **Clip B reversed**
6. **Clip A reversed**
7. Hold on `roof-complete-master`
8. Proof
9. "BUILT FOR EVERYTHING."
10. "GET AN ESTIMATE NOW"

- The return and reassembly are the forward images in reverse order (through a step→file map). `tools/check.mjs` verifies that they are exact reversals.
- **Engine:** one canvas, GSAP ScrollTrigger `scrub: true`, `step = round(progress × (count − 1))`, `file = map[step]`.
  - Native scroll; reversing the scroll plays it backwards.
  - The poster loads first, then frames in bounded groups; a bounded decoded-image window keeps memory flat; the canvas is never blank.
  - All text is HTML. A static reduced-motion fallback uses 7 keyframe stills.
- **Desktop:** 257 steps, 156 unique images, 1440×813 WebP, 16.29 MB. A and B use every 3rd source frame and C every 4th.
- **Mobile:** 139 steps, 85 images, 900×508, 4.61 MB, with a shorter scroll (2.6 svh per step against 3 svh on desktop). Phones show the **whole 16:9 frame uncropped** under the header until a portrait set exists.
- **Copy:**
  - The footer says the sequence is an AI-generated concept visualization (GPT Image 2.5 stills, Kling 3.0 motion). It is not JM's work and not a product test, and the weather does not demonstrate real roof performance.
  - The stage label reads "Concept visualization … Not a product test."
  - The alt text describes only what the frames show.
- **Files changed:**
  - `index.html`, `styles.css`, `sequence.js`
  - `media/hf/{desktop,mobile}/*.webp` and `media/hf/manifest.json`
  - `media/hf-stills/{desktop,mobile}/*.webp`
  - `tools/build_media_hf.py` (new), `tools/check.mjs`, `tools/qa.mjs`
  - `higgsfield/` (new)

### QA

| Gate | Result |
| --- | --- |
| `node tools/check.mjs` | **135 / 135**, including return = Clip B reversed, reassembly = Clip A reversed, final hold = master, and the required order |
| Screenshots, 7 viewports | 0 overflow, 0 blank, 0 inexact frames, 0 console errors, 0 failed requests. See `screenshots/desktop` (30) and `screenshots/mobile` (36), including reduced-motion shots `20–23-reduced-*`. |
| Behaviour | **11 / 11**: engine, fast jump, slow forward + reverse, exact mapping, refresh, resize, reduced-motion flip, slow 3G (0 blank samples, ≤ 4 in flight), blocked CDN (native fallback, same step), touch swipe, rotation. Failed media falls back to static. Reduced motion and 2G make 0 sequence requests. |
| Frame pacing | 59.9 fps median, 0 frames over 50 ms on desktop and on a 4× CPU-throttled phone profile |
| Below the sequence | no chapter card visible |
| Lighthouse mobile | Performance **96**, Accessibility 100, Best Practices 100, SEO 63 (intentional `noindex`). LCP 2.7 s, CLS 0, TBT 0. |
| Lighthouse desktop | Performance **100**, Accessibility 100, Best Practices 100. LCP 0.7 s, CLS 0.001. |

## 6. Remaining limitations

1. **The rain beat doesn't meet the brief.** No falling drops, splashes, runoff or drip-edge water are visible. Clip C wasn't retried, because the rules allowed a retry only for the first transition. Proposed fix (needs your OK): regenerate Clip C once, with rain carrying most of the prompt and a longer rain share. That's 21 credits at the same settings, or about 10.5 credits if heat/wind and rain are split into two 6 s clips joined on the panel master.
2. **The mobile 9:16 set wasn't generated,** because the brief scoped it to after the desktop proof passes. Estimated cost is about 47 credits: 3 portrait masters at 8.25 plus clips A/B/C at 38.5. Until then, phones show the full 16:9 frame uncropped.
3. **Generative drift (§4):** the right roof wing, the panel overlapping the roof, and Clip B's origin point. Each needs a new master to fix.
4. **No layer markers on the stage.** There's no 3D data to project, so the numbered layer list lives only in the HTML card.
5. **Still to test:** real-device iOS Safari and Android, and a screen-reader pass.
6. **No performance claims:** the generated weather shows mood and sequence only and is never presented as proof of performance. Authentic project proof still waits for owner assets.
