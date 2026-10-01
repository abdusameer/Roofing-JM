# 05 · Rendering ADR

> **Superseded by ADR-002 (below, 2026-10-01).** ADR-001 is kept as the record of the proxy slice; its
> files live in `archive/proxy-v1/`.

**ADR-001 · Rendering medium for the roof sequence**
Status: **Superseded** (Phase 1, 2026-09-30). Follows the Phase 0 recommendation (`docs/phase-0/04` §2). The prototype produced evidence that it is viable, so there was no reason to switch.

## Context

The sequence needs one recognizable house and one physical roof panel that stay continuous through:
- layer separation
- a cutaway lifting out
- three light and weather states
- an exact return
- reassembly

It must be scroll-controlled in both directions, work on phones, have complete reduced-motion and failure fallbacks, keep all facts in HTML, and fit GitHub Pages (static, no build server). Phase 1 rules out final photoreal assets, so proxy geometry is acceptable if it respects the verified roof structure.

## Options considered (serious candidates only)

| Option | Verdict | Deciding reason |
| --- | --- | --- |
| DOM, CSS and SVG only | Rejected | A hip roof with nested layer shells, a tilting cutaway and a camera pull-back can't be drawn convincingly in 2.5D. Continuity would rely on drawings that change between states. |
| WebGL / Three.js | Rejected for Phase 1 | Real depth and independent transforms are needed, but the story is an authored, fixed camera path, so real-time interaction adds nothing yet. It would need a parallel no-WebGL fallback anyway, with GPU risk on mid-range phones. |
| React Three Fiber | Not applicable | There is no React in the stack and no framework migration is allowed. |
| Prerendered image sequence (canvas) | Rejected | 406 frames × 2 orientations as WebP is several times the video size, with more requests and decode memory. Bounded windowing is possible but adds complexity for no visual gain. |
| Responsive video alone | Partial | Good scrubbing, but text can't live in video and there is no fallback when media fails. |
| **Hybrid: Blender master → prerendered video per orientation + DOM/SVG layer + stills** | **Accepted** | One scene gives identity by construction. Offline light gives weather without shaders. HTML carries every word. The stills give every fallback for free. |

## Decision

1. **One scripted Blender scene** (`blender/build_scene.py`, Blender 5.2 LTS, EEVEE) is the single source of truth. The Proof Panel is cut from the layer solids by the same prisms that cut the holes, so it can only be the same geometry.
2. **Two cameras with one choreography:** a desktop 16:9 render at 1600×900 and a portrait 4:5 render at 864×1080. Same frames, same keys.
3. **Delivery:** one H.264 clip per orientation (GOP 6, no B-frames), scrubbed by native scroll, plus 8 WebP stills per orientation.
4. **All text, labels, leaders, airflow and water paths are DOM/SVG,** positioned from per-frame anchor data exported from Blender.
5. **No runtime WebGL.** So there is no no-WebGL tier, no canvas, and no context loss to handle.

Deviation from Phase 0: Phase 0 planned *per-chapter* clips. The full clips came in at 3.8 MB (desktop) and 2.5 MB (portrait), well under the 12 MB and 6 MB budgets, so one clip per orientation is simpler and scrubs across chapter boundaries without switching sources. Per-chapter splitting stays available for Phase 2 if final renders grow.

## Evidence (09 has the full report)

| Requirement | Result |
| --- | --- |
| Continuous identity | Frames 112 and 330 rendered with the light frozen are **pixel-identical** (PSNR = ∞) in both cameras. Panel matrix at frames 0, 112, 330 and 405 is identical; the return path mirrors the outbound keys exactly. |
| Reverse scrubbing | Deterministic: the same scroll position gives the same frame. A slow wheel forward to frame 107 and back returns to frame 0. |
| Frame pacing | 59.9 fps median, p95 16.7–16.8 ms, 0 frames over 50 ms, on desktop and on a mobile profile with 4× CPU slowdown (headless Chrome). |
| Load | Lighthouse mobile: LCP 2.3 s, CLS 0, TBT 0 ms, Performance 98. Desktop: LCP 0.5 s, Performance 100. The clip loads after `load` + idle and never blocks first paint. |
| Payload | HTML 9.8 KB, CSS 6.2 KB, JS 6.9 KB, anchors about 14 KB (all gzipped). Clips 3.8 MB / 2.5 MB. Stills 13–36 KB each. |
| Fallbacks | Blocked clip → static story. Reduced motion → no clip request. 2G and low-power → static. A slow clip → stepped stills, then the clip. |

## Consequences

- **Editing cost:** any geometry, camera or material change means re-rendering about 406 frames per orientation, roughly 20 minutes total on this M2 once raw frames are kept **outside iCloud-synced `~/Documents`**. Syncing them stalled the first render for over an hour. `tools/render-all.sh` writes them to `$TMPDIR` by default and `--skip-existing` resumes a partial render.
- **Copy and overlay changes** need no re-render (HTML/SVG). Anchor-driven overlays regenerate in seconds (`node tools/gen-overlays.mjs`).
- **Real-device risk:** iOS Safari seek behaviour is not proven. Headless Chrome can't stand in for it (10 §3).

## Kill and upgrade criteria

- **Kill (phones):** if a real iPhone (Safari) or a mid-range Android scrubs below about 45 fps median, or shows visible seek stalls, phones switch to the stepped-stills mode that already exists in the engine (no new code: the stills underlay is always live). Content is unchanged.
- **Upgrade (optional, Phase 3+):** real-time Three.js only if a later phase adds interaction ("turn the panel yourself"). Export glTF from the same Blender scene so identity is kept.

---

**ADR-002 · Photoreal Cycles master → WebP image sequence on one canvas, scrubbed by GSAP ScrollTrigger**
Status: **Accepted** (2026-10-01). Supersedes ADR-001. Full record: `11-PHOTOREAL-REWORK.md`.

**Context.** The proxy read as a diagram: a low-detail slab, drawn blue rain strokes, washed-out light and
clipped labels. The direction was to replace the roof's production method only:
- photoreal Blender (Cycles), one verified roof system at real scale
- a WebP image sequence on one stable canvas
- GSAP ScrollTrigger with `scrub: true`, scroll progress mapped directly to frame number
- no live browser geometry as the primary visual
- no generative video for the technical roof

**Decision.**
1. `blender/prod/` builds `blender/roof_master.blend` (editable, kept in git). Every layer is a named object in its own collection with a clean pivot. The Proof Panel is cut from the masters, and the build verifies translation only and an exact return on every frame.
2. Delivery is one 168-frame master timeline:
   - desktop sequence: 168 frames at 1600×900
   - independently framed portrait sequence: 112 frames at 900×1200, sampling the same master time
   - a poster (frame 0), 7 fallback keyframes and the final image (frame 167)
3. The engine draws a canvas over the poster. Frames load in bounded groups and decode in a window around the current frame. The canvas draws the nearest ready frame and is never blank. GSAP is pinned with SRI, and a native-scroll fallback keeps the same mapping.
4. All words stay in HTML. Drawn overlays are removed; numbered layer markers come from Blender anchors.

**Why not keep video.** Image sequences give exact frame addressing with no seek latency or keyframe
artifacts, and an explicit loading order: poster → first chapter → keyframes → nearest groups. Neither is
possible with a scrubbed `<video>` on iOS. The cost is payload. Sequence budgets are ≤ 18 MB desktop and
≤ 10 MB portrait, set by encoder quality and enforced by `tools/check.mjs`.

**Consequences.**
- A full re-render takes about 3 hours on the M2. Copy, layout and markers need no re-render.
- Real-device performance on iOS Safari and mid-range Android is still unproven. 10 §3 still applies, with the image-sequence engine in place of the clip.
