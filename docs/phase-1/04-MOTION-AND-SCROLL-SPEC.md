# 04 · Motion and Scroll Spec

> **Photoreal rework (2026-10-01): §0 is current.** §1–§2 below describe the archived proxy engine.

## 0. Current engine: image sequence + GSAP ScrollTrigger

Implementation: `prototype/roof-sequence/sequence.js`, with GSAP 3.14.2 and ScrollTrigger from cdnjs, pinned with SRI. Frames
are rendered from one 168-frame master timeline (`blender/prod/timeline.json`, beats in 11 §3).

```
progress = ScrollTrigger progress of #sequence   (start "top top", end "bottom bottom", scrub: true)
frame    = round(progress × (count − 1))          desktop count 168 · portrait count 112
master   = manifest.sequences[kind].master[frame]  (portrait index → master time; drives chip, rail, markers)
chapter  = height --n × --u (frames × scroll unit); trailing space = one viewport − one unit,
           so chapter k starts exactly at frame f0(k)
```

- `scrub: true` means no smoothing or easing: the frame is a pure function of scroll position, and scrolling back plays it backwards.
- Nothing autoplays. Stopping the scroll stops the picture.
- **Blocked CDN:** the identical mapping runs on native scroll (`progressNow()`), verified to give the same frame.
- **Loading:**
  1. the poster, which is frame 0
  2. the first chapter
  3. keyframes (every 8th / 6th frame)
  4. the rest in groups of 12 / 10, nearest group to the reader first
  5. downloads capped at 4 / 3 in flight
- **Memory:** compressed blobs are kept for every frame. `ImageBitmap`s exist only within ±10 / ±7 frames of the current one; the rest are `close()`d.
- **Never blank:** the canvas stays hidden over the poster until its first draw, and then always draws the nearest decoded frame.
- **Desktop text:** one fixed text column; the active chapter's card crossfades in (0.28 s; instant under reduced motion). A focused card always shows.
- **Phones:** cards scroll beneath the pinned 3:4 stage (`--stage-h: min(60svh, 133vw)`).
- **Markers 1–5:** each is shown only while its projected point is visible (Blender ray cast) and on stage, master frames 34–50.


Implementation: `prototype/roof-sequence/sequence.js` (about 7 KB gzipped, no dependencies). Frames are baked in Blender (`blender/build_scene.py`); scroll only chooses which frame is shown.

## 1. Timeline (30 fps nominal, 406 frames)

| Chapter | Frames | What moves (Blender keys) |
| --- | --- | --- |
| opening | 0 | Nothing (hold) |
| anatomy | 0–112 | Layer lifts, top-down; camera 0→104 |
| panel | 112–165 | Panel out along the normal (112→130), then forward and turned (130→165); `dim` 118→160; DOF f/22→f/1.2 |
| heat | 165–195 | Sun to 74° elevation, warm (165→192) |
| wind | 195–225 | Sun to 27°, dry autumn color (→212) |
| rain | 225–280 | Overcast 225→240; `wet` 228→248; clears 262→280 (wet→0) |
| return | 280–330 | Panel keys mirror 165→130→112; `dim` 285→326; camera back |
| reassembly | 330–405 | Layers settle bottom-up; final ridge cap 386→**395 lock**; light lift 395–399; camera pulls back 336→398 |

Every curve is Bezier with auto-clamped handles, so each move eases in and out, and holds sit between moves.

## 2. Scroll → frame mapping (deterministic)

```
trigger  = innerHeight × (desktop 0.50 | mobile 0.74)
active   = last chapter whose top ≤ scrollY + trigger
p        = clamp((scrollY + trigger − top) / (height − hold), 0, 1)     // hold: desktop reassembly tail, 45svh
target   = f0 + (f1 − f0) × p
```

- Native scroll only. No scroll-jacking, no smooth-scroll library, no horizontal scroll, no intro gate.
- The same scroll position always gives the same frame (tested: 252.5 twice). Scrolling up reverses cleanly; stopping stops.
- **Smoothing** applies to the displayed frame only: `shown += (target − shown)·(1 − 0.78^(dt/16.7))`. This is frame-rate independent, snaps within 0.04 of a frame, and then **the requestAnimationFrame loop stops**. There is no permanent loop (tested: `raf` is false after every scroll).

## 3. Picture

- **Clip:** H.264 High, GOP 6, no B-frames, `+faststart`. Seeks go to `(frame + 0.25)/30`, with one seek in flight at a time (the latest target waits in `pending`), and are skipped when the rounded frame hasn't changed.
- **Underlay:** an `<img>` showing the **nearest rendered still** to the current frame (8 stills per orientation). It shows before the clip is ready, while it loads, whenever the needed part of the clip isn't buffered yet (the `buffered()` guard, so no stale frame is ever shown), and if the clip never arrives.
- **Loading:** the clip loads only after `load` plus idle (`requestIdleCallback`, 1.5 s timeout). The opening still is preloaded and is the LCP element.
- **Stage background** follows the sampled floor color of the nearest still, so contained frames (tablets) never show a seam.

## 4. Overlays and labels

- **Overlays:** SVG (heat, wind, rain, anatomy airflow) generated from Blender anchors by `tools/gen-overlays.mjs`. A CSS variable `--p` (0→1) drives the drawing:
  - draw-on: `stroke-dashoffset` with `pathLength=100`
  - flow: dashes moving with `--p`
  - fade: `opacity` derived from `--p`

  Windows (frames): anatomy 98–112 (fades by 124), heat 165–195, wind 195–225, rain 225–262 (fades out by 280, **before the return**).
- **Labels:** HTML, positioned per frame from `anchors-<orient>.json` with linear interpolation between frames. Each fades over 4 frames. Labels hide when their anchor is hidden, flip side or center below their dot to stay inside the stage, and are decluttered (newest-only on phones, 30px vertical nudge on desktop).
- **Condition chip:** HEAT 165–196 · WIND 196–226 · RAIN 226–280. **Illustration note:** frames 120–326.
- **Lock:** the final ridge cap seats at frame 395 with a baked light lift. The "Final ridge cap locks" marker fades in at 389. No screen shake and no haptics.

## 5. Performance rules

- Every per-frame DOM write is delta-gated: transform strings, opacity, `--p`, the still `src`, the stage background, rail `aria-current`.
- No layout reads inside the loop. Geometry (chapter tops and heights, frame box, label widths, usable area) is measured on start, `load`, `pageshow` and resize (rAF-throttled).
- Two IntersectionObservers:
  - any intersection gates the loop, so **nothing runs offscreen** (tested)
  - a middle-band observer (`-45%` root margins) toggles the rail and skip pill
- One `<video>` per page. Its source is removed and `load()` is called when leaving the motion tiers.
- Listeners, observers and timers are removed in `stopMotion()`.

## 6. Lifecycle and resilience

| Event | Behaviour (all tested headlessly, 09 §3) |
| --- | --- |
| Refresh midway | The browser restores scroll. `pageshow`/`load` re-measure and render the exact frame (5249px → frame 252.5, rain still) |
| Resize | rAF-throttled re-measure. No duplicated stage, labels or overlays (1 / 20 / 4 after three resizes) |
| Orientation change | Live tier gates. A landscape phone goes to static; turning back restores mobile at the same chapter |
| Reduced motion (live, both ways) | Switches to the static story: video source removed, figures shown. Switching back restores desktop with labels |
| Media error | `error` → static tier, reader kept on the same chapter |
| Slow media | Stepped stills continue; the clip takes over when the needed frames are buffered |
| Skip / CTA | Skip link (first Tab stop), rail "Skip to proof", phone skip pill. The header and action-bar CTA reach `#estimate` at any point |

## 7. Tier gates (head script, re-evaluated on change)

```
?tier=static|reduced|desktop|mobile                  → forced (QA only)
prefers-reduced-motion: reduce                       → reduced (flat story)
saveData or effectiveType 2g/slow-2g                 → static
deviceMemory ≤ 1 or hardwareConcurrency ≤ 2          → static (low-power heuristic)
landscape + coarse pointer + height ≤ 540            → static
min-width 1024 + min-height 600 + not coarse pointer → desktop
otherwise                                            → mobile
```
