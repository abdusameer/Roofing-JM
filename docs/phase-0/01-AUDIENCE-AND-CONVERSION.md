# 01 · Audience and Conversion

JM Roofing 3rd Generation, unofficial Lumera prospect concept. Phase 0, 2026-09-30. Source IDs refer to the tables in 00 §7 and 02 §9.

---

## 1. What the evidence says about JM's customers

| Signal | Evidence | Source |
| --- | --- | --- |
| Mostly homeowners reroofing single-family homes | Google reviews describe roof replacements; BuildZoom shows reroof permits; Instagram posts show single-story homes from a drone | [S03] [S08] [S09] |
| Mid-size residential jobs | BuildZoom: about 44 permitted projects under $5K and 41 at $5K–$20K, average about $5K (permit valuations, not prices) | [S08] |
| Where they work | Permits in South LA (90001 area), the Southeast cities (Bell, South Gate), Inglewood, and the Valley (North Hollywood, Tarzana, Panorama City), plus Beverly Hills | [S08] [S09] |
| What customers praise | Fair pricing, quick work, polite crew, materials explained, daily updates, cleanup, damaged wood replaced, work finished before rain | [S03] [S07] |
| How JM markets itself | Customer testimonial reels, drone "AFTER" shots, product and color callouts, "free estimates", an El Niño storm-prep post | [S09] |
| How customers reach JM today | Phone and Instagram. There is no website and no public email | [S01] [S03] [S09] |
| One reputational caution | One Yelp review alleges unfinished work | [S04] |

Caveat: JM's customer mix is inferred from public signals. Ask the owner for the real mix (01 §7).

---

## 2. Visitor priority

| Rank | Visitor | Why this rank | What they need from the page |
| --- | --- | --- | --- |
| **1 (primary)** | **LA homeowner planning a roof replacement** (single-family, often an older home; comparing bids before the rainy season) | Matches the permit profile, the review content and JM's own posts | Proof JM is licensed and real; what their new roof is made of; what it will do in LA sun, wind and rain; real finished roofs; an easy free-estimate request |
| 2 (urgent) | Homeowner with an active leak | JM's El Niño and tarp posts; the reviews mention finishing before rain | The phone number, immediately, with no animation in the way. No "emergency" or "24/7" promise until verified (00 row 15) |
| 3 | Owner of a small multi-unit property | One 4-unit project post | The same proof, plus that JM does multi-unit work (to confirm) |
| 4 | Homeowner researching materials (cool roof, shingle vs metal) | Title 24 cool-roof rules apply to most of JM's area (02 §6) | The anatomy and the heat chapter. This visitor is served by the experience itself. |
| 5 (deprioritized) | Commercial manager, builder or GC | Only an unverified Thumbtack claim | Nothing custom until the owner confirms this work |

**Language:** Florence-Firestone, South Gate and Bell are largely Spanish-speaking, and Google lists JM as "Latino-owned" (self-identified). Whether JM serves customers in Spanish is an owner question. If yes, Phase 1 should plan a reviewed Spanish version, not machine translation. The demographic statement here is a planning assumption and was not researched for publication.

---

## 3. Conversion actions

| Role | Action | Condition before it goes live |
| --- | --- | --- |
| **Primary** | **Request a free estimate.** A short form (name, phone, ZIP, "what's going on": replace / leak / repair / not sure, optional note). The owner may prefer "text us" as an equal alternative | Owner confirms estimates are free (00 row 33) and names the inbox or SMS number (00 row 36) |
| **Secondary** | **Call (323) 245-9154** (tap-to-call on phones) | Phone verified [S01]. Hours must be settled first (00 row 8) |
| Supporting | "See finished roofs" (in-page link to the proof section) | Owner-permitted photos |

**Why estimate rather than inspection:** JM publishes "free estimates" [S09], and the primary visitor is planning a replacement. "Inspection" suggests a separate, possibly paid service the business has not described.

**In the unofficial pitch build:** the form is a disabled demo ("Concept preview. This form is not active."). The phone number appears as plain text, not a live link. There is no live lead capture (00 §5).

---

## 4. What must stay reachable during the cinematic sequence

None of these may exist only inside the video or animation stage:

| Element | Desktop | Mobile |
| --- | --- | --- |
| Logo / home link | Fixed header | Compact header |
| Primary nav (Roof, How it works, Projects, Reviews, Estimate) | Header links | Menu button (≥44 px), full-screen menu |
| Phone | Header text link | **Sticky bottom action bar: Call · Free estimate**, inside `env(safe-area-inset-bottom)` |
| Primary CTA | Header button, visible from first paint | Bottom bar |
| CSLB license # | Header utility line or footer. **Present in every tier** | Footer and menu |
| Skip link | "Skip the roof animation" at the start of the sequence, jumping to proof or estimate | Same |
| Chapter navigation | Progress rail with real `<a>` links to each chapter (Anatomy, Heat, Wind, Rain, Reassembly) | Hidden in the menu or as an inline list; no hover-only controls |
| Services, contact, hours | Real HTML sections after the sequence | Same |

The opening H1, one supporting line and the CTA render in HTML from first paint. They never wait for video frames (04 §5).

---

## 5. Page architecture (content order, not copy)

1. **Header**: logo, nav, phone, "Free estimate", license number.
2. **Opening (completed roof)**: the house and finished roof in clear LA daylight. H1, the business name, primary CTA. This is also the LCP element (04 §5).
3. **The roof sequence** (02 §7): anatomy → isolated panel → heat → wind → rain → panel returns → reassembly. The CTA lands with the final piece.
4. **Authentic proof**: owner-permitted finished projects with product and color labels (JM already writes these callouts), dated platform ratings, the license, bond and insurance facts from CSLB.
5. **Services**: only the verified or owner-confirmed list (00 rows 12–17).
6. **Where we work**: only after the owner confirms the service area.
7. **Estimate**: the form plus phone, and what happens next (owner to describe their process).
8. **Footer**: legal name, CSLB #, the manufacturer-warranty qualifier, and in the pitch build the "Unofficial concept" notice.

---

## 6. Forms, analytics and SEO (Phase 1 requirements)

- **Form:** 4 required fields at most. Native inputs with visible labels. `autocomplete` and `inputmode="tel"` / `inputmode="numeric"` for ZIP. Inline errors tied to fields with `aria-describedby`. A honeypot instead of a CAPTCHA at launch. Consent line and privacy link. On success, a plain confirmation with the phone number.
- **Delivery:** GitHub Pages cannot process forms. The production site needs a form service or serverless endpoint that the owner approves. The pitch build sends nothing.
- **Analytics:** none in the pitch build. For production, a privacy-light option, with consent if required.
- **SEO and structured data (production only):** `RoofingContractor` JSON-LD using verified fields only (name, phone, address if approved, license number as an identifier, hours once settled). No `aggregateRating` markup copied from third-party platforms. The pitch build is `noindex`.

---

## 7. Owner questions for this document

Collected with all the others in 05 §6.

- Q-A1 Who calls you most: people replacing a roof, or people with a leak right now?
- Q-A2 Do you want estimate requests by form, text, phone, or all three? Where should they go?
- Q-A3 Are estimates always free? Any limits (distance, roof type)?
- Q-A4 Do you and your crew serve customers in Spanish?
- Q-A5 Do you want multi-unit or commercial work promoted?
