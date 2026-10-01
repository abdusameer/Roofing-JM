# 09 · Test and Performance Report

## 0. Photoreal rework: final results (2026-10-01)

Run on the final media: desktop 168 frames (8.40 MB), portrait 112 frames (3.18 MB). Apple M2 (8 GB),
headless Chrome through CDP, served under the real Pages base path. §1–§9 below are the archived proxy-slice
results.

| Gate | Result |
| --- | --- |
| `node tools/check.mjs` | **134 / 134 passed**: files and paths, frame counts and sizes, master-map monotonicity, poster = frame 0, final = last frame, 7 fallback keyframes, anchors per frame, HTML chapters = timeline, chapter heights = frame counts, `scrub: true` + mapping formula, GSAP pinned with SRI, compliance strings, budgets, master `.blend` + plates present |
| Proof Panel contract (build) | translation only (max rotation delta **0.0**); exact home (max offset **0.0 m**) on frames 0–11 and 157–167; 14 pieces |
| Screenshots (`qa.mjs shots`) | 7 viewports (1440, 1280, 1024 desktop; 768, 430, 390, 360 mobile): **0** horizontal overflow, **0** markers off-stage or under a card, **0** blank stages, **0** inexact frames, **0** console errors, **0** failed requests. Images in `screenshots/{desktop,mobile}/`. |
| Behaviour (`qa.mjs behaviour`) | **11 / 11 ok**: engine (GSAP, all 168 frames), fast jumps back to frame 0, slow wheel forward then reverse back to frame 0, mapping `frame = round(progress × 167)` exact at 5 sample positions, refresh restores the exact frame, resize (1 stage, 1 canvas, 5 markers), reduced motion live flip both ways, blocked CDN (native fallback, same frame), touch swipe (portrait sequence), rotation (landscape → static → back) |
| Reduced motion / 2G / low power | reduced and 2G request **0** sequence frames; 2 cores → static |
| Slow network (3G, 200 KB/s) | HTML + CTA **0.72 s**, poster **1.43 s**, **0** blank samples while jumping ahead of downloads; nearest downloaded frame stands in; ≤ 4 downloads in flight |
| Failed media (sequence blocked) | static story, reader's place kept (`media-failed`) |
| Below the sequence | no chapter card visible on proof / final / estimate (probe at 100 / 400 / 1200 ms) |
| Frame pacing (`QA_GPU=1 qa.mjs perf`) | desktop 1440: **59.9 fps** median, p95 16.8 ms, 0 frames > 50 ms; mobile 390 with 4× CPU: **59.9 fps**, p95 16.7 ms, 0 > 50 ms; decoded bitmaps held: 31 / 23 |
| Lighthouse (mobile) | Performance **96**, Accessibility **100**, Best Practices **100**, SEO 63 (only `noindex`, intentional); LCP 2.6 s, CLS 0, TBT 0 ms |
| Lighthouse (desktop) | Performance **100**, Accessibility **100**, Best Practices **100**, SEO 63; LCP 0.6 s, CLS 0.007, TBT 0 ms |
| Payload | HTML/CSS/JS ≈ 23 + 15 KB; GSAP + ScrollTrigger 42 KB; manifest 30 KB; poster 56 KB; sequence 8.40 MB desktop / 3.18 MB portrait (budgets 18 / 10 MB), largest frame 89 KB |
| Render | desktop 2.9 h, portrait 1.2 h on the M2 (Cycles Metal, 36 / 32 samples, OIDN) |

Found and fixed during QA:
- **Desktop cards overlapping:** chapters can be shorter than their text (the opening is 12 frames). Fix: one fixed text column that crossfades.
- **Mobile text running ahead of the frames:** a desktop-only rule leaked into mobile. Fix: the rule is scoped to desktop, and chapters are offset so each card's middle meets the text band's middle at its chapter's middle frame.
- **Smeared transition frames:** a 0.45 shutter smeared the fast camera move into the panel close-up. Fix: shutter 0.12 everywhere except the rain beat.
- **Stray drops after the storm:** they read as specks with the short shutter. Fix: the rain and drip particle systems switch off for rendering after the clear beat (`show_render` keyed). Scaling the drops to zero was rejected because it multiplied render time about 4×.
- **Cards staying visible below the sequence:** fixed by a geometric in-sequence test.
- **Slow-network jumps showing the poster:** fixed by decoding the nearest downloaded frame at any distance as a stand-in.

Not tested: real iOS Safari and Android hardware, and a screen-reader pass on real assistive technology (10 §3 still applies).


Run on 2026-09-30, Apple M2 (8 GB), macOS, Chrome 153 (headless, through CDP), against the **real Pages base path**: `tools/serve.mjs` serves the repo at `/Roofing-JM/` with HTTP Range support. Raw results: `qa/out/report-shots.json`, `report-behaviour.json`, `report-perf.json`, `lighthouse-mobile.json`, `lighthouse-desktop.json` (git-ignored; regenerate with the commands in §8).

## 1. Existing checks

The repository had **no lint, type-check, test suite or build step** (Phase 0 00 §2). Phase 1 adds `node tools/check.mjs` as the gate:

- JS syntax for all scripts
- every local `src`/`href` relative and present
- chapter frame ranges equal to the Blender timeline
- the panel-return check
- required disclosures present and prohibited claims absent
- payload budgets

**Result: 100 checks passed, 0 failed.** The "production build" is the static folder itself; it was tested as served under `/Roofing-JM/`.

## 2. Viewports and screenshots

`node tools/qa.mjs shots`: every state at 1440×900 and 390×844, key states at the other five sizes, and reduced-motion compositions at 1440 and 390. **71 screenshots** reviewed by eye.

| Viewport | Tier | Horizontal overflow | Clipped labels | Undersized targets | CTA visible | License present | Console errors | Failed requests |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1440×900 | desktop | 0 | 0 | 0 | every state | ✓ | 0 | 0 |
| 1280×800 | desktop | 0 | 0 | 0 | ✓ | ✓ | 0 | 0 |
| 1024×768 | desktop | 0 | 0 | 0 | ✓ | ✓ | 0 | 0 |
| 768×1024 | mobile (contained 4:5) | 0 | 0 | 0 | ✓ | ✓ | 0 | 0 |
| 430×932 | mobile | 0 | 0 | 0 | ✓ | ✓ | 0 | 0 |
| 390×844 | mobile | 0 | 0 | 0 | ✓ | ✓ | 0 | 0 |
| 360×800 | mobile | 0 | 0 | 0 | ✓ | ✓ | 0 | 0 |

**Desktop screenshots** (`screenshots/desktop/`):
- 01 opening · 02 anatomy-lift · 03 anatomy-full · 04 panel · 05 heat · 06 wind · 07 rain · 08 rain-clears · 09 return · 10 reassembly · 11 lock · 12 proof · 13 final · 14 estimate
- 20–23 reduced-motion (opening, anatomy diagram, heat, rain)

**Mobile screenshots** (`screenshots/mobile/`): the same numbering.

### Problems found and fixed during review

| # | Problem (seen in screenshots or by the checks) | Fix |
| --- | --- | --- |
| 1 | Opening frame cut off at the bottom: the concept bar and header pushed the sticky stage down about 94px | Fixed-height bar on desktop; sequence pulled up under the header |
| 2 | House composed too far right for a 4:3 cover crop | Re-framed every desktop pose to about 60% of the frame width; re-rendered |
| 3 | Phone cards scrolled *over* the stage | Stage raised above the cards on phones |
| 4 | Phone header wrapped to three lines; skip link crowded it | Single-line brand + license; skip moved to a stage pill |
| 5 | Labels hidden under the text card or header; labels overlapping | Visible-area bounds in stage coordinates, hide-if-anchor-hidden, side flip / centered mode, declutter |
| 6 | Final headline below the fold under a large image | Headline and CTA laid over the empty floor of the finished-roof frame |
| 7 | Illustration note clipped at 1024px (positioned inside the overflowing cover frame) | Note and chip positioned on the stage itself |
| 8 | Rail links 40px tall | 44px |
| 9 | Card margins collapsing through chapters added 756px of dead scroll; desktop pin 8.35 viewport heights, phone 5.52 | Spacing moved to padding; phone lengths trimmed → **7.47** and **4.90** viewport heights |
| 10 | On slow networks the clip could show a stale frame for an unbuffered seek | `buffered()` guard: show the matching still until those frames arrive |
| 11 | Hidden opening figures downloaded both stills | `loading="lazy"` on hidden figures |
| 12 | QA screenshots taken before the async scroll event (harness bug) | Settle waits a frame, then requires two stable reads |

## 3. Behaviour (`node tools/qa.mjs behaviour`)

| Test | Result |
| --- | --- |
| Fast scroll: large jumps anatomy → rain → end → top | Converges to frame 0; the rAF loop stops ✓ |
| Slow scroll (wheel gesture, 600 px/s) forward, then reverse | Forward to frame 107.4; reverse to **0** ✓ |
| Determinism | The same scroll position gives the same frame twice (252.51) ✓ |
| Refresh midway | Scroll restored (4670px) → frame 252.51, rain still ✓ |
| Arbitrary resize (1100×700 → 1600×1000 → 1440×900) | 1 stage, 20 labels, 4 overlays: no duplicates ✓ |
| Keyboard | Tab order as listed in 06 §2; every stop shows the ring ✓. Skip link focuses `#proof` ✓ |
| Touch | Synthesized touch swipe on a 390×844 touch profile scrolls natively and drives the frames (→ 67.4) ✓ |
| Rotation | Portrait → landscape phone = static tier, 0 overflow; back to portrait = mobile tier at the same chapter ✓ |
| Reduced motion at load | Tier `reduced`, **0 video requests** ✓ |
| Reduced motion live flip, both ways | → static story (stage hidden, video source removed, figures shown); ← desktop again with labels ✓ |
| Low-power (2 logical cores) | Static tier ✓ |
| Slow network (400 ms latency, 50 KB/s) | HTML, H1 and CTA ready in 0.63 s. Motion tier with stepped stills; clip usable after about 4 s ✓ |
| 2G | Static tier ✓ (no clip requested by the page, verified separately with `?tier=static`; the one `.mp4` in that run's log was an in-flight request from the previous test page) |
| Failed media (`*.mp4` blocked) | Static tier, `media-failed`, figures shown, reader kept at the rain chapter ✓ |
| Console / failed first-party requests (whole suite) | **0 / 0** |

## 4. Continuity of the Proof Panel

| Check | Result |
| --- | --- |
| Panel rig world matrix at frames 0, 112, 330, 405 | Identical to 9 decimals (`returnExact: true`, both cameras) |
| Return path keys | 280 = 165 and 315 = 130 (`pathMirrored: true`) |
| Frames 112 vs 330 rendered with the light frozen | **Pixel-identical, PSNR = ∞** (desktop and portrait) |
| Frames 112 vs 330 as shipped | PSNR 33.2 dB. The difference is only the intended light (clear vs washed-after-storm). |

## 5. Lighthouse 12.8.2 (default throttling)

| Profile | Performance | Accessibility | Best Practices | SEO | SEO excluding the intentional `noindex` | FCP | LCP | TBT | CLS | Speed Index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mobile (Moto G Power, slow 4G) | **98** | **100** | **100** | 63 | **100** | 1.6 s | **2.3 s** | **0 ms** | **0** | 1.6 s |
| Desktop | **100** | **100** | **100** | 63 | **100** | 0.5 s | **0.5 s** | **0 ms** | **0.004** | 0.5 s |

- LCP element: the preloaded opening still (`stills-*/opening.webp`).
- An earlier mobile run measured LCP 1.6 s; run-to-run variance is about ±0.7 s.
- **Open opportunities:**
  - text compression: the local server sends no gzip; GitHub Pages does
  - render-blocking Google Fonts CSS
  - unminified CSS/JS (5–6 KB)

## 6. Frame pacing (`QA_GPU=1 node tools/qa.mjs perf`)

A rAF cadence sampled during a scripted scroll through the whole sequence.

| Profile | Frames sampled | Median | p95 | FPS (median) | Frames >50 ms | Loop idle after scroll |
| --- | --- | --- | --- | --- | --- | --- |
| Desktop 1440×900 | 291 | 16.7 ms | 16.7 ms | 59.9 | 0 | ✓ |
| Mobile 390×844, CPU 4× slower | 170 | 16.7 ms | 16.8 ms | 59.9 | 0 | ✓ |

**Offscreen:** with the sequence out of view, the `in-seq` class is off and no rAF is scheduled ✓.

**Caveat:** this is main-thread cadence in headless Chrome on an M2. It is not video-decode presentation on a real phone. A real-device test is required (10 §3).

## 7. Payload

| Resource | Size (gzip where text) | Budget (Phase 0 04 §2) |
| --- | --- | --- |
| HTML | 9.8 KB (35.5 KB raw, including inline overlay SVG) | critical HTML+CSS+JS ≤100 KB ✓ (22.9 KB) |
| CSS | 6.2 KB | ✓ |
| JS | 6.9 KB | engine ≤30 KB ✓ |
| Anchors JSON | 14 KB per orientation (loaded after first paint) | — |
| Fonts | Archivo 88 KB woff2 + Plex Mono 10 KB | ≤2 families ✓ |
| Opening still | 24.6 KB desktop / 19.6 KB portrait | ≤150 / ≤90 KB ✓ |
| Clip | 3.8 MB desktop / 2.5 MB portrait (after load + idle) | ≤12 / ≤6 MB ✓ |
| Pinned distance | 7.47 viewport heights desktop; 4.90 / 4.94 phone | ≤8 / ≤5 ✓ |

## 8. How to rerun

```
node tools/check.mjs
node tools/serve.mjs                    # http://127.0.0.1:4410/Roofing-JM/prototype/roof-sequence/
QA_TMP=$TMPDIR node tools/qa.mjs shots
QA_TMP=$TMPDIR node tools/qa.mjs behaviour
QA_TMP=$TMPDIR QA_GPU=1 node tools/qa.mjs perf
```

Lighthouse: `node ~/.npm/_npx/8003d8991b0d346b/node_modules/lighthouse/cli/index.js <url> [--preset=desktop]`.

## 9. Not tested

- Real iPhone Safari, real Android Chrome, Firefox and desktop Safari.
- VoiceOver / NVDA, forced colors, 200% zoom.
- Real field data (CrUX).
- Hosting on GitHub Pages itself. The base path was emulated locally; nothing was deployed, by instruction.
