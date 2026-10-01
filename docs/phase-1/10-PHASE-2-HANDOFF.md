# 10 · Phase 2 Handoff

JM Roofing concept, 2026-09-30. Phase 1 is complete: the experience is fully decided and its hardest interaction (one continuous, scroll-reversible roof with a Proof Panel that returns exactly) works in a real browser on desktop and mobile. **Nothing has been committed, pushed or deployed.**

## 1. Decided (do not reconcept)

| Area | Decision | Where |
| --- | --- | --- |
| Sequence | Completed roof → anatomy → Proof Panel → heat → wind → rain (clears) → exact return → reassembly (ridge cap lock) → proof → "Built for everything." → Get an estimate now | 02, 03 |
| Mechanism | The panel is cut from the master objects by the same prisms that cut the openings (shingles by the same planes, capped). The stepped cutaway shows deck / underlayment / shingles. Translation only; the exact return is verified on every frame by the build. | `blender/prod/build.py`, 11 §4 |
| Medium | **Photoreal Cycles master (`blender/roof_master.blend`) → WebP image sequences on one canvas, scrubbed by GSAP ScrollTrigger (`scrub: true`)**, HTML text, stills. No runtime WebGL. | 05 ADR-002, 11 |
| Visual system | Plaster/graphite/redline; Archivo + Plex Mono; three-weight line language; no navy template | 00 |
| Copy architecture and claim tags | Every line tagged; prohibited claims absent | 01 |
| Tiers and fallbacks | Desktop, phone portrait, reduced motion, static (no JS, Save-Data, 2G, low-power, failed media, landscape phone) | 04, 06 |
| Budgets | All met | 09 §7 |

## 1a. Photoreal rework status (2026-10-01)

Done:
- the laminated Duration-geometry shingles (5⅝″ exposure)
- the full layer stack at real thickness, with named objects and pivots
- PBR dry and wet materials
- the photoreal look-dev gate (11 §5)
- desktop (168) and portrait (112) WebP sequences with a poster, keyframes and the final frame
- the frame-to-scroll manifest and the GSAP engine

Open:
- **Colour:** the render shows **Night Sky**, but JM's posts name **Oyster Shell**. Re-render in Oyster Shell if the owner prefers it; it's a material change plus a full re-render, about 3 hours.
- **Unmodelled detail:** the porch-to-wall step and kick-out flashing are still not modelled.
- **Sample geometry:** the house massing is still a generic sample.
- **Real devices:** iOS Safari and mid-range Android performance of the canvas engine is still unproven.

## 2. What Phase 2 must produce

1. **Production model and look** (same scene, same choreography):
   - laminated shingle profile and true Oyster Shell blend
   - real cap, ridge-vent, drip-edge, underlayment, boot and gutter products once JM answers Q-R1–R5
   - the porch-to-wall joint with step and kick-out flashing (missing in the proxy)
   - house massing from a consenting JM job (Q-R7)
   - optional rendered water along the true lap paths
2. **SME review** of the anatomy, drainage and airflow depiction, the CRRC/Title 24 statement, and the wind wording (SME-1–3) on keyframe stills **before** the full production render.
3. **Authentic proof:** replace the four slots with JM's permitted originals (07 §3) in JM's own caption format.
4. **Copy pass:** resolve "Built for everything." with owner and counsel (01 §6), the estimate wording, a Spanish version if Q-A4 is yes, and confirmed services only.
5. **Production site around the slice:** services (verified only), where we work (after Q-B6), estimate flow with an owner-approved endpoint (Pages can't process forms), `RoofingContractor` JSON-LD with verified fields, privacy notice.
6. **Device QA:** real iPhone Safari and Android Chrome scrubbing; VoiceOver/NVDA; forced colors; 200% zoom.
7. **Launch hygiene:** remove the concept bar and tags, flip `noindex` to index, add a CSP `<meta>`, gzip/minify (Pages handles gzip), recheck CSLB (workers' comp after 10/06/2026), and refresh rating dates.

## 3. Acceptance criteria for Phase 2

- Everything in Phase 0 05 §4 still holds: 0 overflow, 0 console errors, ≥44px targets, Lighthouse mobile Perf ≥85 and A11y/BP/SEO ≥95, LCP <2.5 s, CLS <0.1, pin ≤8 / ≤5 viewport heights, budgets.
- **Real-device scrub:** iPhone (current iOS, Safari) and a mid-range Android hold ≥45 fps median with no visible seek stall. Otherwise phones switch to stepped stills (already implemented) and that is recorded.
- The continuity proof is re-run on the production scene: frozen-light frames 112 vs 330 are pixel-identical.
- Every public statement is VERIFIED, or approved in writing by the owner or counsel.
- The SME sign-off on 02 is filed.
- Every proof asset has written permission on file.

## 4. Risks carried forward

| Risk | Mitigation |
| --- | --- |
| iOS Safari seek behaviour (untested) | The stepped-stills fallback exists; GOP 6 with no B-frames; test first in Phase 2 |
| Render time for production detail (~20 min per pass on the M2 for both orientations at proxy detail; more with richer materials) | Keep raw frames outside iCloud; use `--skip-existing`; review keyframes before full renders |
| Owner declines, or wants metal promoted | The scene is parameterized; standing-seam is a documented variant (Phase 0 02 §1) |
| Claim drift in copy | `tools/check.mjs` blocks known prohibited strings; counsel review before launch |
| Workers' comp lapses (cancellation date 10/06/2026) | Recheck CSLB before any "insured" wording |

## 5. Exact first production task for Phase 2

> **Real-device scrub test, then lock the medium.** Serve `prototype/roof-sequence/` from `tools/serve.mjs` on the local network (or a private, `noindex`, unlisted preview the user approves). Scrub the full sequence on a real iPhone in Safari and a mid-range Android in Chrome. Record median fps, seek stalls and LCP, and confirm reverse scrolling, rotation and reduced motion. This decides whether phones keep the clip or use the stepped-stills mode, before any money goes into production renders.

The task after that: run the SME and owner review of the eight keyframe stills (`media/stills-*`), then start the production model pass in `blender/build_scene.py`.

## 6. How to open the prototype

```
cd ~/Documents/Roofing-JM
node tools/serve.mjs
```

Open http://127.0.0.1:4410/Roofing-JM/prototype/roof-sequence/. Add `?tier=static`, `?tier=reduced`, `?tier=mobile` or `?tier=desktop` to force a tier for review.

## 7. Files

| Path | Purpose |
| --- | --- |
| `prototype/roof-sequence/index.html`, `styles.css`, `sequence.js` | The vertical slice (isolated route) |
| `prototype/roof-sequence/media/` | Clips, stills, anchors |
| `blender/build_scene.py`, `render.py`, `camera_poses.json`, `continuity_check.py` | Master scene and renders |
| `tools/render-all.sh`, `gen-overlays.mjs`, `check.mjs`, `serve.mjs`, `qa.mjs` | Pipeline, checks, base-path server, QA |
| `docs/phase-1/00–10`, `docs/phase-1/screenshots/` | This phase's documents and evidence |
| `.gitignore` | Ignores `review/`, `.blend`, `qa/out/`, `.claude/` |
