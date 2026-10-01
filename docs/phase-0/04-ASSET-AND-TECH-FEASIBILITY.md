# 04 · Asset Provenance and Technical Feasibility

JM Roofing 3rd Generation, unofficial Lumera prospect concept. Phase 0, 2026-09-30.

---

## 1. Asset and provenance audit (Task G)

**Local assets in the repo: none.** The repository is empty (00 §2). Every item below is either observed publicly (owned by JM or third parties, not in hand) or still to be created.

| Asset | Where observed | Resolution / format | Orientation | Ownership / source | Permission | Authentic / stock / licensed / generated | Intended use | Replacement or crop needed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Logo** | Instagram avatar; a yard sign and flyer visible in Google photos and reels [S09][S03] | Low-res raster (avatar crop of a card-style graphic: blue ground, red house outline, white "JM Roofing", yellow "3rd Generation" script, two phone numbers) | Landscape card cropped to a circle | JM (presumed) | **None** | Authentic | Header mark | **Vector original** (SVG/AI/PDF), plus a simplified mark for ≤32 px. The second phone number on the card must be confirmed. |
| Fonts | None identified; the logo uses a script display face | — | — | Unknown | — | — | Phase 1 web type | Choose OFL/Google Fonts in Phase 1. Ask whether the logo's typeface is licensed. |
| Brand colors | Inferred from the logo only (blue, red, yellow, white) | Not sampled from a source file | — | JM | — | — | Logo only (03 §3) | Brand file from the owner, if one exists |
| **Project photos** | Google 65+ (about 11 visible without sign-in, some uploaded by the business, some by customers) [S03]; Yelp 14 [S04]; Thumbtack [S06]; Instagram 264 posts [S09] | Web-compressed JPEG. Google's viewer serves up to 1440×1440 | Mostly square or portrait (reels) | **Mixed:** business-uploaded vs customer-uploaded | **None** | Authentic | Proof section, gallery | **Full-resolution originals from JM's phone or drone**, with EXIF GPS stripped; customer consent; house numbers and plates blurred |
| Before/after pairs | Instagram "AFTER" reels [S09] | Video | Portrait | JM | None | Authentic | Optional proof | Originals of both states from the same angle |
| Crew / owner photos | People appear in Google photos and reels; identities unconfirmed [S03][S09] | Web | Mixed | JM / individuals | None | Authentic | Optional "who we are" | Owner-approved portraits with releases. Nobody shown on a roof. |
| **Drone photo / video** | Instagram drone reels; a 0:30 video on Google [S03][S09] | Compressed video | Portrait edits | JM | None | Authentic | Proof section | Raw drone originals (ideally 4K) and the name of the pilot or service |
| Roof-detail photos | None seen | — | — | JM | — | — | **Modeling reference** (not publication): tear-off, underlayment, drip edge, boot, vents | In-progress detail photos from 2–3 jobs |
| Customer testimonial videos | Several reels with customers on camera [S09] | Video | Portrait | JM and the customers | None | Authentic | Optional proof | Signed releases, or leave out |
| Reviews | Google 58, Thumbtack 223, Yelp 3 [S03][S06][S04] | Text | — | The reviewers, under platform terms | None | Authentic | Dated rating lines; quotes only with consent or an official embed | FTC reviews rule (00 §5) |
| License / insurance evidence | CSLB public record [S01] | Web record | — | Public record | Public | Authentic | License number on every page; bond and comp facts | GL certificate from the owner; re-check comp after 10/06/2026 |
| Manufacturer diagrams and swatches | OC data sheets [S12][S13] | PDF | — | Owens Corning | Not licensed | Licensed third-party | **Reference only** | Don't reproduce. Use JM's own photos of installed color. |
| Illustrations | None | — | — | — | — | — | — | Lumera authors annotation SVGs |
| **3D assets** | None | — | — | — | — | — | Master model | **Authored by Lumera in Blender** from 02 §3. Owned by Lumera until engaged. Labeled illustration. |
| HDRI / sky lighting | None | — | — | — | — | — | Blender lighting | Prefer CC0 HDRIs (check the license at download, record the source) |
| Stock | None | — | — | — | — | — | — | **Policy: none** |
| Generated | None. Nothing was generated in Phase 0. | — | — | — | — | — | — | **Policy:** no generated house, roof, worker, storm or damage may ever be presented as JM's project, crew, customer or performance. Anything generated must carry a "Concept image" label. |

### Visual integrations available (checked, nothing generated)

| Tool | Availability | How it could be used later |
| --- | --- | --- |
| **Blender 5.2.0 LTS** | Installed; headless: `/Applications/Blender.app/Contents/MacOS/Blender -b -P <script.py>` | **Primary.** Build the master scene with Python for reproducibility; keyframe the anatomy, isolation and reassembly; add weather with geometry nodes and particles (authored water paths, not a fluid sim); render desktop and portrait passes; export per-frame 2D anchor JSON for DOM labels; export glTF for any later real-time upgrade. |
| **Higgsfield CLI** 1.1.26 | Signed in, Plus plan, 591.5 credits; image, video and 3D models listed (Hunyuan3D, Meshy, Seedance, etc.) | **Not recommended for the roof.** Generative video can't hold exact layer geometry across a continuous camera move, and text or image-to-3D meshes aren't accurate enough for construction. Optional: labeled look-development stills for internal moodboards, with cost approval. |
| ffmpeg | Installed | Encode chapter clips (H.264 short GOP or all-intra, plus a WebM/AV1 test), posters, contact sheets |
| Chrome headless (CDP) + Lighthouse 12.8.2 (cached) | Installed | Seven-viewport QA, reduced-motion emulation, blocking video requests to test fallbacks, Lighthouse |

---

## 2. Implementation options compared (Task H)

Ratings: **S** strong · **F** fair · **W** weak.

| Criterion | DOM / CSS / SVG (2.5D illustration) | Three.js (WebGL) | React Three Fiber | Prerendered frame sequence (canvas) | Prerendered video scrub (per-chapter clips) | **Hybrid: Blender master → video chapters + DOM/SVG layer + stills** |
| --- | --- | --- | --- | --- | --- | --- |
| Continuous roof identity | S (one drawing) | S (one model) | S | S (one scene) | S | **S** |
| Exploded anatomy control | F (no true 3D camera) | S | S | S | S | **S** |
| Weather transitions | F (diagrammatic) | F (real-time water and light is hard) | F | S (offline) | S | **S** |
| Mobile reliability | S | F (GPU/thermal variance) | F | F (decoded-frame memory, many requests) | F (iOS seek latency, needs a spike) | **F→S** (portrait encode + stepped fallback) |
| Performance | S | F (runtime cost; 2–5 MB model and textures) | F (plus React) | W–F (6–24 MB of frames) | F (6–12 MB, lazy chapters) | **F** (same as video, gated) |
| Accessibility | S | F (needs parallel DOM) | F | F | F | **S** (all content in DOM; stage decorative) |
| Editability | S | S | S | W (re-render) | W (re-render) | **F** (scripted scene; re-render overnight) |
| Hosting (GitHub Pages) | S | S | S (build step) | S | S | **S** |
| Development complexity | Low–Med | High | High | Med | Med (Lumera's existing scrub pattern) | **Med** |
| Asset production time | Med (illustration) | Med–High (model, materials, shaders) | Med–High | High (render) | High (render) | **High** (render; offset by no shader work) |
| Reduced-motion support | S | F (needs stills anyway) | F | S | S | **S** (stills from the same scene) |
| No-WebGL fallback | S | W (needs a whole fallback) | W | S | S | **S** (uses no WebGL at all) |

### Recommendation

**Hybrid, prerendered delivery.** One scripted Blender master scene is the single source of truth. It renders:

1. Desktop 16:9 chapter clips, scroll-scrubbed.
2. Portrait (9:16 or 4:5) chapter clips for phones.
3. A still per state for the reduced-motion and static tiers.

All words, labels, leader lines, airflow and drainage paths, the CTA and navigation are **DOM/SVG**, positioned from per-frame anchor data exported from Blender.

**Why not real-time WebGL:** the story is a fixed, authored camera path, so interactivity adds nothing yet. Offline rendering gives believable water and light. It works without WebGL on every device, and it avoids shader and GPU risk on mid-range phones. The brief says not to choose WebGL for impressiveness.

**Why not generative video (the 10k-websites Higgsfield pipeline):** the brief requires unchanged geometry and layers across the whole sequence, and generated clips drift. Lumera's scrub engine from that pipeline (drive loop, gating, fallbacks) **is** reused.

**Kill and upgrade criteria:**

- **Mobile spike (first technical task, 05 §2):** on a real iPhone in Safari and a mid-range Android in Chrome, scrubbing one portrait chapter clip must hold a **≥50 fps median** with no visible seek stall. If it fails, phones get tier 2b: each chapter plays a short muted `playsinline` loop when in view (paused offscreen), or stepped stills with crossfades. Content is unchanged.
- **Real-time upgrade (later, optional):** only if a later phase adds interaction (e.g. "turn the panel yourself"). Use the glTF exported from the same master, so identity is preserved.

### Delivery budgets (production targets)

| Item | Budget |
| --- | --- |
| Critical HTML + CSS + JS | ≤100 KB gzipped; scrub engine ≤30 KB gzipped, no framework required |
| Opening image (LCP candidate) | Desktop ≤150 KB (AVIF, WebP fallback); mobile ≤90 KB |
| Chapter clips | Desktop total ≤12 MB (6 chapters); mobile total ≤6 MB; each chapter fetched only once the previous one is half-way through, and never before first paint plus idle |
| Stills (RM / static) | ≤120 KB each, lazy-loaded |
| Web fonts | ≤2 families, subset, `font-display: swap`, one preload |

---

## 3. Stack and hosting for Phase 1

- **Plain HTML, CSS and vanilla JS, no build step.** This matches Lumera's Tirzah's and portfolio builds and suits GitHub Pages. GSAP only if a specific effect needs it. **No Lenis and no scroll-jacking:** native scroll, with smoothing applied to video time only.
- **Base path:** `/Roofing-JM/` if served from GitHub Pages. Use relative URLs throughout.
- **Headers:** Pages can't set them, so use `<meta name="robots" content="noindex">` in the pitch build. Add a CSP later via `<meta>` if needed.
- **Forms:** no backend on Pages. The pitch form is inert. Production needs an owner-approved endpoint.
- **Repo hygiene:** raw renders, `.blend` autosaves and third-party screenshots are git-ignored. Only encoded outputs and scripts are committed.

---

## 4. Experience tiers

Each tier keeps **the same content, the same order, and the same CTAs** (01 §4). Gates are evaluated live on `matchMedia` change events, not once at load.

| Tier | Who gets it | What they see | Gate |
| --- | --- | --- | --- |
| **1. Full desktop** | ≥1024 px, fine pointer, motion allowed, no Save-Data, height ≥600 px | Sticky stage (`100svh`) with 16:9 clips scrubbed by native scroll; DOM labels beside the stage; chapter rail with real links; header CTA; total pinned distance **≤8 viewport heights** | `(min-width:1024px) and (pointer:fine) and (prefers-reduced-motion:no-preference)` and no Save-Data |
| **2. Tablet and mobile (portrait)** | <1024 px or coarse pointer, portrait | Portrait clips; **each chapter pinned ≤120svh**, followed by unpinned text cards; total pinned distance **≤5 viewport heights**; labels as cards; sticky Call · Estimate bar. **2b:** stepped loops or stills if the spike fails | Width or pointer query, portrait |
| **3. Reduced motion** | `prefers-reduced-motion: reduce`, flipped live in both directions | No scrub, no pin, no settle or impact; one still per state plus the same text; the anatomy as an `<ol>` | The media query, live |
| **4. Static fallback** | No JS, Save-Data, 2G-class connection, video error or stall over 4 s, landscape phone (height <500 px and coarse pointer) | Opening still, then semantic HTML sections with lazy stills (or text only if images fail). CTA, phone and license always present | Feature, network and error checks; `<noscript>` baseline |

WebGL is not used, so there is no separate no-WebGL tier. Tier 4 covers every failure path.

---

## 5. Phase 1 targets: performance, accessibility, responsive (Task I)

| Area | Target |
| --- | --- |
| LCP | **< 2.5 s** at p75 mobile and desktop [S38]. The LCP element is the opening still or H1, never video |
| CLS | **< 0.1** [S38]. Reserved aspect ratios for stage, stills and cards; stable header and bottom-bar heights |
| INP | **< 200 ms** [S38]. No long tasks during scroll; delta-gated DOM writes |
| Lighthouse (mobile) | Performance **≥85** where measurable; Accessibility, Best Practices, SEO **≥95** (SEO scored with `noindex` excluded in the pitch) |
| Standard | **WCAG 2.2 AA** |
| Focus | Visible custom focus ring (≥2 px, ≥3:1 contrast) on every interactive element |
| Structure | One H1; H2 per chapter and section; `header`/`nav`/`main`/`footer` landmarks; chapter rail as `nav` with `aria-label` |
| Targets | **≥44×44 px** for all controls. This exceeds the AA minimum of 24 px [S39], per the brief |
| Anatomy alternatives | Every state has an HTML heading and description; the stage is `aria-hidden` with a text equivalent; the anatomy is an ordered list; each still has meaningful `alt` |
| Keyboard | Everything is reachable in logical order; a skip-animation link; chapter links scroll to the correct state; no keyboard traps |
| Motion | Full `prefers-reduced-motion` support (tier 3), including a live flip mid-session |
| Composition | Portrait-specific framing for phones (separate render, not a crop) |
| Viewport units | `100svh` for the sticky stage (no jump when the URL bar moves); `100dvh` for the full-screen menu; `vh` fallback |
| Resize / orientation | Stable across rotation and window resize: gates re-evaluate, stage re-seeks, no blank stage |
| Offscreen | **No rendering loop runs while the stage is offscreen** (IntersectionObserver stops rAF and pauses decoding) |
| First paint | The opening content and CTA render without waiting for any clip |
| Text over footage | Worst-frame contrast ≥4.5:1 for body text and ≥3:1 for large text, measured on the real composited frames |
| Viewports tested | 1440×900 · 1280×800 · 1024×768 · 768×1024 · 430×932 · 390×844 · 360×800 |

---

## 6. Main mobile and performance risks

| Risk | Mitigation |
| --- | --- |
| iOS Safari seek latency makes scrubbing stutter | Short-GOP or all-intra encode, half-frame seek skipping, and the spike with a tier-2b fallback (§2) |
| Payload on cellular | Per-chapter lazy loading, portrait encodes ≤6 MB total, Save-Data → tier 4 |
| Long pinned scroll on phones | ≤120svh per chapter, unpinned cards between, skip link |
| URL-bar resize jumps | `svh` stage, cached geometry, re-seek on resize |
| Labels crowding a small frame | Labels become cards below the image on phones; no leader lines |
| Battery and heat | Loops only while intersecting; no work when idle |
| Render cost of accuracy fixes | **SME and owner review five keyframe stills before any full animation render** (05 §2) |
| Landscape phones | Tier 4 by design |

---

## 7. Sources

All accessed 2026-09-30.

| ID | Source | URL |
| --- | --- | --- |
| S38 | web.dev, Web Vitals (thresholds at p75) | https://web.dev/articles/vitals |
| S39 | W3C, Understanding WCAG 2.2 SC 2.5.8 Target Size (Minimum) | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html |

S01, S03, S04, S06, S09, S12 and S13 are listed in 00 §7 and 02 §9.
