# 05 · Phase 1 Handoff

JM Roofing 3rd Generation, unofficial Lumera prospect concept. Phase 0, 2026-09-30.

---

## 1. Phase 0 exit gate

| Gate item | Determined? | Where |
| --- | --- | --- |
| Real client or labeled concept | **Yes.** Real business, unofficial prospect concept, not commissioned | 00 §1 |
| Primary audience | **Yes.** LA homeowner planning a replacement (leak callers routed to the phone) | 01 §2 |
| Primary CTA | **Yes.** Request a free estimate (label pending owner confirmation); secondary: call | 01 §3 |
| Verified public claims | **Yes.** Truth matrix with V/S/U/P for 38 items; claim-safety review | 00 §3–4 |
| Exact roof system | **Yes (provisional on owner confirmation).** OC TruDefinition Duration COOL, Oyster Shell, hip roof, vented attic | 02 §1–3 |
| Relevant weather | **Yes.** Heat, Santa Ana wind, winter rain. No hail, snow, hurricanes; fire not dramatized | 02 §4 |
| Authentic proof sources | **Yes (identified, not permitted).** JM's Google photos, Instagram posts and reels, reviews | 00 rows 29–35; 04 §1 |
| Asset provenance | **Yes.** Nothing local; policy for stock and generated assets | 04 §1 |
| Technical medium | **Yes.** Blender master → prerendered chapter clips + DOM/SVG + stills | 04 §2 |
| Mobile and fallback behavior | **Yes.** Four tiers, pin limits, spike with kill criteria | 04 §4 |
| Phase 1 acceptance criteria | **Yes** | §4 below |
| Unresolved owner and expert questions | **Yes, recorded** | §6 below |

**Phase 0 is complete.** Uncertainty remains only in the recorded questions. None of it was filled with invented content.

---

## 2. What Phase 1 may create

Phase 1 is a **private, unofficial pitch prototype** built only on **Verified** facts (status V in 00 §3), with labeled placeholders for everything else.

| May create | May not |
| --- | --- |
| A scripted Blender master scene (house, roof assembly, eave-corner panel) in the repo under `blender/` | Any public deploy, indexing, or link shared beyond the user without the user's explicit OK |
| Five continuity keyframe stills, then the chapter renders | Live lead capture (the form is inert; the phone is plain text) |
| Encoded desktop and portrait chapter clips, stills and posters | JM's logo, photos, reviews or videos on the page. Placeholders labeled "JM project photo" instead, until permission. The typed name is fine. |
| The site shell: semantic HTML, the four tiers, the scrub engine, DOM/SVG annotations, header, bottom bar, inert form | Any claim with status S, U or P; "Built for everything"; unqualified warranty, "since 1964", "insured", financing, solar, emergency |
| A QA harness (headless Chrome, seven viewports, reduced-motion flip, blocked-video test, Lighthouse) | Generated imagery presented as JM work; stock imagery |
| A Phase 1 report | Paid generation without cost approval |

### Sequence

| Step | Task | Exit check |
| --- | --- | --- |
| **P1-0 (first task)** | **Build the scripted Blender master scene** to 02 §2–3 and render **five continuity keyframes, each in 16:9 and portrait**: (1) completed home, (2) anatomy separated, (3) panel isolated, (4) panel at the rain peak with the drainage path, (5) reassembled home with room for the CTA | The user reviews the stills for continuity and originality (03 §5). Accuracy checklist 02 §3 is ticked. No full animation render before this passes. |
| P1-1 | Mobile scrub spike: one portrait chapter clip, scrubbed on a real iPhone (Safari) and a mid-range Android (Chrome) | ≥50 fps median, no visible seek stall. Otherwise choose tier 2b (04 §2) |
| P1-2 | Site shell, static tier first (tier 4), then tiers 3 → 2 → 1 | All content and CTAs present with JS off |
| P1-3 | Full chapter renders and encodes | Budgets in 04 §2 |
| P1-4 | Scrub engine and anchored annotations | §4 criteria |
| P1-5 | QA and the Phase 1 report | §4 all pass or listed as exceptions with reasons |

---

## 3. Precise first task for Phase 1

> **P1-0:** In `~/Documents/Roofing-JM/blender/`, write `build_scene.py`. Run it headless with Blender 5.2 LTS to construct the single-story LA stucco house with a hip roof and porch-to-wall joint, and the full OC Duration COOL (Oyster Shell) assembly from 02 §3: caps, field shingles at 5⅝″ exposure, starter, eave drip edge under the underlayment, underlayment, solid sheathing, soffit intake, gutter, vent boot, step and kick-out flashing. Include the eave-corner panel defined in 02 §2 as a cut of the same geometry. Render the five keyframes in 16:9 and portrait to a git-ignored `review/` folder for the user's continuity and accuracy review.

---

## 4. Phase 1 acceptance criteria (measurable)

### Truth and claims
1. Every public-facing statement maps to a row with status **V** in 00 §3, or is visibly marked as a placeholder. **0 exceptions.**
2. The CSLB license number (#1084651) appears in the header or footer in **all four tiers** and with JS disabled.
3. "Unofficial concept by Lumera Creative. Not affiliated with or approved by JM Roofing 3rd Generation." is visible in the footer and in the opening view. `<meta name="robots" content="noindex">` is present.
4. The weather sequence carries the label "Illustration of how each layer works. Not a product test."
5. No stock images. No generated image of a house, roof, person or weather is presented as JM work (manual audit list in the report).

### Continuity and accuracy
6. All frames come from one Blender scene file and camera rig. A frame diff at matched poses (keyframes 1 vs 5) shows **no geometry change**, only light.
7. Anatomy order, lap directions, drip edge under the underlayment at the eave, and the drainage path all match 02 §3. Checklist signed by the user (and by the SME before any public release).
8. No person, ladder or first-person roof view appears anywhere.

### Content and conversion
9. The H1 and primary CTA are visible at first paint on all seven viewports, before any clip loads.
10. The header CTA, phone (as text) and nav stay reachable throughout the sequence on desktop. The bottom bar (≥44 px targets, safe-area aware) is visible throughout on phones.
11. The skip-animation link moves focus to the proof or estimate section.

### Tiers
12. Tier gates re-evaluate on rotation, resize and a live reduced-motion flip in both directions, with no blank stage (tested headlessly).
13. With video requests blocked, the page is complete (tier 4) within 4 s of the stall.
14. Pinned distance: desktop ≤8 viewport heights total; phone ≤120svh per chapter and ≤5 viewport heights total.

### Performance (Lighthouse and lab, mobile profile)
15. LCP < 2.5 s, CLS < 0.1, and INP (or a TBT proxy in lab) within the 200 ms target.
16. Lighthouse mobile: Performance ≥85; Accessibility, Best Practices and SEO ≥95 (SEO judged with `noindex` excluded).
17. Payloads within 04 §2 budgets. No rAF callbacks while the stage is offscreen (measured with a Performance trace).

### Accessibility
18. Axe or Lighthouse: 0 critical or serious violations. Manual keyboard pass: every control reachable, visible focus, no traps.
19. Every state has an HTML text equivalent. The anatomy is an `<ol>`. All stills have meaningful `alt`.
20. Worst-frame text contrast: ≥4.5:1 for body text and ≥3:1 for large text, on the composited page.

### Responsive
21. No horizontal overflow (`scrollWidth ≤ innerWidth`) at 1440×900, 1280×800, 1024×768, 768×1024, 430×932, 390×844, 360×800.
22. No overlapping or clipped text and no content covered by the bottom bar at those sizes (screenshots in the report).
23. Zero console errors at desktop and phone sizes.

### Repo hygiene
24. Raw renders, `.blend` backups and `docs/phase-0/evidence-local/` are git-ignored. The committed media is only the encoded output within budget.

---

## 5. Exact assets needed from JM (for production, or to replace placeholders)

1. **Logo:** vector file (SVG, AI or PDF) and any brand colors or fonts they use.
2. **Project photos:** full-resolution originals of 8–12 finished roofs, including the City of Bell Duration COOL Oyster Shell job, the 4-unit Oyster Shell job, the Shasta White + Polyfresko G job, and the hillside standing-seam metal job. Include product, color, city and month/year for each.
3. **Drone originals:** raw clips (ideally 4K) of 3–5 finished roofs, plus the pilot or service name.
4. **In-progress detail photos** (modeling reference, not for publication unless approved): tear-off, sheathing, underlayment, drip edge, starter, vent boot, vents, gutters.
5. **Permissions:** written OK to use photos, videos and reviews; customer releases for any customer seen or any identifiable house; approval to name cities.
6. **Documents:** general liability certificate; confirmation that workers' comp is in force after 10/06/2026; workmanship-warranty terms (if any); financing lender and terms (if any); the license basis for any solar work.
7. **Owner portrait(s) and family story** with names and dates, if they want the "3rd generation" story told.

---

## 6. All open questions, grouped

### For JM's owner

**Business facts**
- Q-B1 Exact legal name for the footer (00 row 2)?
- Q-B2 Is 1242 E 59th St a public business address, or should the site show only "Los Angeles"?
- Q-B3 Real business hours? Google, Birdeye and Yelp disagree (00 row 8).
- Q-B4 What should the second phone number on the logo card be used for?
- Q-B5 A business email?
- Q-B6 Which cities do you want to be known for serving?
- Q-B7 Women-owned and Latino-owned: who does that describe, and do you want it on the site?
- Q-B8 The family history: who started in 1964, and how is today's company connected (00 row 27)? Is the Camarillo "3rd Generation Roofing" license (#778450) part of that story? (Internal only; never published.)
- Q-B9 General liability insurance: can we see the certificate? Is workers' comp renewing past 10/06/2026?
- Q-B10 Do you offer a workmanship warranty? What are the terms?
- Q-B11 Financing: which lender, and what terms?
- Q-B12 Solar: what exactly do you do (detach and reset for a reroof?), and under which license or partner?
- Q-B13 Emergency help: do you tarp or repair leaks the same day? Any hours limits? (No "24/7" claim without this.)
- Q-B14 Commercial and industrial work: yes or no?

**Conversion**
- Q-A1 to Q-A5 (01 §7): leak vs replacement mix; where requests go; free-estimate limits; Spanish; multi-unit.
- Q-C1 Do you give estimates from photos?

**Roof practice** (02 §8)
- Q-R1 to Q-R7: Duration line and colors; underlayment, starter, cap, drip edge and vent products; nail count; hip-roof exhaust venting; gutters; sheathing replacement; permission to model on one of your jobs.

**Assets:** §5 list.

### For a roofing / building-science reviewer
- SME-1 Anatomy order, drainage and airflow depiction for a vented hip roof (02 §3).
- SME-2 The current CRRC listing for Duration COOL Oyster Shell and a correct Title 24 statement for zones 8 and 9. Check CRC section numbers against the 2025 edition.
- SME-3 Wind depiction (edge and corner emphasis); how to state the 130-MPH limited-warranty figure without implying performance.
- SME-4 Whether the "Class A" fact line is appropriate.

### For counsel (before any public release)
- L-1 Public use of "One roof. Every condition." or any "Built for…" line (00 §4).
- L-2 Review-display policy under the FTC rule; use of platform ratings.
- L-3 Contractor advertising requirements (license number, classification scope).

### For the user (Lumera decisions)
- D-1 **Proceed to Phase 1 as a private pitch prototype using only Verified facts and placeholders?** (Recommended: yes.)
- D-2 Keep JM's logo out of the pitch until permission, as with Tirzah's? (Recommended: yes; typed name only.)
- D-3 Drop the haptic "vibration" and keep a ≤2 px visual settle? (Recommended: yes, 02 §5.)
- D-4 Keep "ONE ROOF. EVERY CONDITION." internal and replace the public "BUILT FOR EVERYTHING." with a scoped line to be written in Phase 1? (Recommended: yes.)
- D-5 Commit these Phase 0 docs to `main`? They are uncommitted; nothing has been pushed.

---

## 7. Risks carried into Phase 1

| Risk | Likelihood | Response |
| --- | --- | --- |
| Blender modeling and render time is higher than a video-generation build | High | Keyframe gate (P1-0) before full renders; scripted scene makes re-renders cheap to trigger |
| iOS scrub quality | Medium | P1-1 spike, tier 2b |
| Owner rejects the pitch, or owner facts change the roof system (e.g., they want metal promoted) | Medium | Master scene parameterized by assembly; metal is a documented variant (02 §1) |
| Claims creep during copywriting | Medium | Acceptance criterion 1; counsel before launch |
| Workers' comp lapses after 10/06/2026 | Unknown | Re-check CSLB before any "insured" wording |

---

## 8. Readiness

**Phase 1 is ready to begin as a private, unofficial pitch prototype** once the user confirms D-1. It needs no owner answers because it uses only Verified facts and labeled placeholders.

**A production (client) build is not ready.** It needs JM's answers to the owner questions (§6), the assets in §5, SME sign-off on 02, and counsel review of claims.
