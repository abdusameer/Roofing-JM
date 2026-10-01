# 00 · Baseline and Truth

**Project:** Roofing website, Lumera Creative
**Business:** JM Roofing 3rd Generation, Los Angeles (real business)
**Internal thesis:** "ONE ROOF. EVERY CONDITION." (internal only, see §4)
**Phase:** 0, research and truth. Nothing here is final copy or approved for publication.
**Prepared:** 2026-09-30. All online facts were accessed on 2026-09-30 unless a row says otherwise.

---

## 1. Project mode

| Question | Decision | Why |
| --- | --- | --- |
| Real client or Lumera Concept Study? | **Real business, unofficial prospect concept.** JM Roofing 3rd Generation was named by the user on 2026-09-30. The business has not commissioned, reviewed, or approved anything. | The user supplied the business and its Google Maps listing. They describe it as a contractor with no website and strong Google reviews that Lumera wants to pitch. |
| What the pitch build may do | Show the real name, the verified license facts, and a clearly labeled concept of the experience. | Same pattern as the BB's and Tirzah's pitches. |
| What the pitch build may not do | Go public or indexed, take real leads, show unverified claims, or use JM's photos, reviews, or logo files without the owner's permission. | See §5. California treats advertising for construction work as regulated, and the FTC rules on claims and reviews apply once the site is public. |

User context (internal, not a business fact): the user describes the prospect as reputable and able to pay for premium work. Pricing expectations are a sales matter and are not recorded as a business fact anywhere in Phase 0.

---

## 2. Repository and baseline audit (Task A)

### 2.1 Workspace

| Item | Finding |
| --- | --- |
| Session working directory | `~/Downloads/10k-websites`. It holds the 10k-websites skill (`SKILL.md`, `references/`) and a `.claude/launch.json` with two stale entries (`rok-site`, `fellow-preview`) that point at paths moved to `~/Documents` on 2026-09-26. There is no roofing code, and it is not a git repository. Nothing was saved there, per the standing rule to keep that folder clean. |
| Project repository | `https://github.com/abdusameer/Roofing-JM.git`, supplied by the user on 2026-09-30 and cloned to `~/Documents/Roofing-JM`. |
| Git status | **Empty repository.** Branch `main`, no commits, remote `origin` set, nothing staged. The only files are this `docs/phase-0/` folder, written in Phase 0 and left uncommitted. |
| Existing uncommitted work | None besides these docs. |

### 2.2 Application baseline

Every row below is **none**, because the repository is empty.

| Area | Finding | Phase 1 implication |
| --- | --- | --- |
| Framework and structure | None | Stack chosen in 04 §3 |
| Package manager and lockfile | None; no lockfile | Nothing to preserve |
| Build and dev commands | None | Defined in Phase 1 |
| Routing | None | Single page plus anchors (01 §5) |
| Styling system | None | Chosen in Phase 1 |
| Animation or 3D libraries | None | 04 §3 |
| Forms, analytics, SEO, structured data | None | 01 §6 and 05 |
| Asset directories | None | 04 §1 |
| Hosting and deployment config | None. `https://abdusameer.github.io/Roofing-JM/` returns 404, so GitHub Pages is not enabled. | If Pages is used later, the base path is `/Roofing-JM/`. Use relative URLs only. Pages cannot send response headers, so `noindex` must go in a `<meta>` tag. |
| Responsive, accessibility, console | Nothing to run | The seven Phase 0 viewports become Phase 1 QA sizes (05 §4) |

**Viewport inspection:** not possible, because there is no application to run. JM Roofing also has no website: its Google listing shows "Add website" [S03]. I inspected competitor sites at 1440×900 and 390×844 instead (03 §3).

### 2.3 Local toolchain (checked, nothing installed)

| Tool | Status |
| --- | --- |
| Node / npm / yarn | v22.14.0 / 11.3.0 / 1.22.22 (pnpm not installed) |
| ffmpeg / ffprobe | Installed (Homebrew). Note: this build has no `drawtext` filter. |
| Google Chrome | Installed. Headless CDP screenshots work with no dependencies. |
| Blender | **5.2.0 LTS** at `/Applications/Blender.app`. Not on `PATH`; call it by its full path. |
| Higgsfield CLI | 1.1.26, signed in, Plus plan, **591.5 credits**. 3D models are listed (Hunyuan3D, Meshy). Nothing was generated. |
| gh / poppler | Not installed. PDFs were read with macOS PDFKit through `osascript`. |

### 2.4 JM's current web presence (no website)

| Channel | What it shows (2026-09-30) | Source |
| --- | --- | --- |
| Google Business Profile | 5.0 ★, 58 reviews, "Roofing contractor", 65+ photos, phone, "identifies as women-owned" and "Latino-owned", no website | [S03] |
| Instagram `@jm.roofing` | 13.1K followers, 264 posts. Bio: "since 1964", C39 license number, "Los Angeles", solar-panel removal/installation, financing, free estimates. Content: drone "AFTER" reels, customer testimonial videos, material callouts | [S09] |
| Threads `@jm.roofing` | 116 followers; bio matches Instagram | [S10] |
| Yelp | 3.7 ★, 3 reviews, **claimed**, "Roofing, Gutter Services", 14 photos | [S04] |
| Thumbtack | 4.7 ★, 223 reviews, 222 hires, "background checked", self-written profile (see §3) | [S06] |
| BBB | Not accredited, not rated, 0 reviews, 0 complaints in 3 years, "business started 12/07/2021" | [S05] |
| Birdeye | 5.0 ★ from 34 Google reviews (stale copy), unclaimed | [S07] |
| BuildZoom | Permit history (see §3), score 111 | [S08] |

---

## 3. Business truth matrix (Task B)

**Status key:** **V** = Verified with source · **S** = Supplied (self-published by the business or supplied by the user), awaiting owner confirmation · **U** = Unknown · **P** = Prohibited from public use until the condition in "Public-use rule" is met.

| # | Item | Finding | Status | Source | Public-use rule |
| --- | --- | --- | --- | --- | --- |
| 1 | Public business name | JM ROOFING 3RD GENERATION | **V** | [S01] CSLB, [S03] | Use as written. Styling (e.g. "JM Roofing · 3rd Generation") needs owner approval. |
| 2 | Legal entity | California general corporation "Jm Roofing 3rd Generation", entity #4632293, filed 08/24/2020, active. Birdeye shows "…Corp." | **V** (entity) / **U** (exact suffix) | [S11] via CA SOS data, [S07] | Confirm the exact legal name with the owner before any legal footer text. |
| 3 | Contractor license | CSLB **#1084651**, class **C39 Roofing**, corporation, issued 12/07/2021, expires 12/31/2027, "current and active" | **V** | [S01] | **Required** on the site: B&P §7030.5 puts the license number in all advertising, including electronic [S29]. |
| 4 | Qualifying individual / owner | CSLB qualifier: Jose Salvador Martinez Miranda (≥10% owner). BBB contact "Mr. Jose Miranda, Owner". Thumbtack "Jose Martinez Miranda" | **V** (qualifier) / **S** (title) | [S01], [S05], [S06] | Ask how he wants to be named on the site. |
| 5 | Phone | (323) 245-9154 | **V** | [S01], [S03] | Can go public once the site is approved. A second number appears on the logo image [S09]; it is illegible → **U**. |
| 6 | Email | None found | **U** | none | Owner question |
| 7 | Address | 1242 E 59th St, Los Angeles, CA 90001 (Florence-Firestone) | **V** | [S01], [S03], [S04] | Ask whether this is a public business location. Until then show only "Los Angeles, CA". |
| 8 | Hours | **Conflict.** Google: open today, closes 9 PM [S03]. Birdeye: Mon–Sat 5:00 AM–9:00 PM, Sun closed [S07]. Yelp: 5:45 AM–10:00 PM every day [S04] | **U** | as listed | Don't publish hours until the owner confirms. |
| 9 | Service area | Not declared. BuildZoom permits: Los Angeles, Inglewood, North Hollywood, Tarzana, Panorama City, Beverly Hills, South Gate [S08]. Instagram project: City of Bell [S09]. Thumbtack: "Los Angeles (90011)" [S06] | **U** | [S06], [S08], [S09] | No city lists or "serving all of LA" claims until the owner confirms. |
| 10 | Residential focus | Homeowner reviews and single-family reroof posts | **V** | [S03], [S04], [S08] | OK to say residential. |
| 11 | Multi-unit / commercial / industrial | One Instagram post: "new 4 unit construction roof". Thumbtack says commercial, residential and industrial | **S** | [S09], [S06] | Commercial and industrial claims need owner confirmation. |
| 12 | Roof systems | **Asphalt shingle:** Owens Corning Duration and Duration COOL named in their own posts ("Oyster Shell", "Shasta-White") [S09]; several shingle roofs in Google photos [S03]. **Standing-seam metal:** one business-uploaded photo, May 2026 [S03]. **Low-slope coating:** "Flat roof: Polyfresko G" [S09]. **Also listed:** hot mop, torch down, tile, wood shake, skylights [S06] | Shingle: **S**, strong photo evidence. Others: **S** | [S03], [S06], [S09] | Show only systems the owner confirms. Wood shake may be restricted in LA fire hazard zones; the SME must confirm before it is listed (not verified in Phase 0). |
| 13 | Repair / replacement | Reroof permits (146 permitted projects) and replacement reviews | **V** | [S08], [S03] | OK to say JM does repairs and replacements. |
| 14 | Inspections / maintenance / cleaning | Listed on Thumbtack and aggregators | **S** | [S06] | Owner confirmation |
| 15 | Emergency service | Not claimed. One reel shows a tarped house [S09] | **U** | [S09] | **P** for "emergency", "24/7" or response-time claims |
| 16 | Gutters | Yelp services (claimed listing) and Instagram highlight "Rain gutters" | **S** | [S04], [S09] | Owner confirmation |
| 17 | Solar panels | Instagram bio: "remove / installation for solar panels"; Thumbtack: solar installation | **S** | [S09], [S06] | **P.** CSLB lists only C39 [S01]. Advertising work outside your license classification is a misdemeanor (B&P §7027.1) [S29]. Hold until the owner shows the license basis, e.g. a C-46/C-10 partner for detach-and-reset. |
| 18 | Contractor's bond | $25,000, Platte River Insurance Co., bond #PR2764852, effective 11/29/2025. (BuildZoom's "$15,000" is outdated) | **V** | [S01], [S08] | Phrase as "CSLB contractor's bond on file". A license bond is not a performance guarantee, so never imply one. |
| 19 | Workers' comp | State Compensation Insurance Fund policy #9308368, effective 11/05/2025, **cancellation date 10/06/2026** | **V** with a hold | [S01] | **Re-check on CSLB after 10/06/2026** before any "insured" wording. |
| 20 | General liability | Not found | **U** | none | **P** for the word "insured" until a GL certificate is seen. Thumbtack's "bonded and insured" is self-published. |
| 21 | Manufacturer certification | No Owens Corning network listing found. The search is not conclusive | **U** | [S14] | **P** for OC badges, "certified", "preferred" or "platinum" |
| 22 | Ownership identity | Google: "identifies as women-owned", "identifies as Latino-owned" | **S** | [S03] | Owner confirmation, and who it refers to |
| 23 | Manufacturer warranty | OC Duration / Duration COOL: Limited Lifetime "(for as long as you own your home)", 130-MPH Wind Resistance Limited Warranty, 10-yr TruPROtection non-prorated period, "see actual warranty" (OC publications of 2018 and earlier) | **V** (manufacturer terms as published) | [S12], [S13] | Always write "Owens Corning limited warranty, terms apply" with a link. Never write "lifetime warranty" without the qualifier. Confirm the current terms. |
| 24 | JM's warranty claim | Instagram: "Warranty: lifetime as long as you own your home 👍" | **S** | [S09] | **P** as written, because it reads as JM's own warranty |
| 25 | Workmanship warranty | Not found | **U** | none | Owner question |
| 26 | Financing | Instagram: "financial available"; Thumbtack: "no payment for 12 months" | **S** | [S09], [S06] | **P** until the lender, terms and required disclosures are provided |
| 27 | Years in business | Self-published "since 1964" [S09][S10] and "62 years in operation" [S06]. Records: corporation filed 2020 [S11], CSLB license issued 2021 [S01], BBB start 12/07/2021 [S05]. An expired license #778450 "3RD GENERATION ROOFING" (Camarillo, sole ownership, issued 05/08/2000, expired 05/31/2026) [S02] is linked to JM only by BuildZoom [S08] | **S** (family history) / **V** (entity dates) | as listed | **P** for "62 years in business" and "since 1964" presented as the company's age. Allowed later only as an owner-confirmed family story. Never mention license #778450 publicly. |
| 28 | Project totals | BuildZoom: 146 permitted projects (27 in 2025, 38 in 2024, 24 in 2023), about 44 under $5K and 41 at $5K–$20K. Thumbtack: 222 hires | **V** (third-party counts) | [S08], [S06] | **P** for "hundreds of roofs" style claims. Use only a count the owner confirms. |
| 29 | Ratings | Google **5.0 ★ / 58** [S03]; Thumbtack **4.7 ★ / 223** [S06]; Yelp **3.7 ★ / 3** [S04]; Birdeye 5.0 / 34 (stale Google copy) [S07]; BBB not rated [S05] | **V** (each, dated) | as listed | Show a rating only with its platform, count and "as of" date, updated at launch. Don't hide the platforms you don't show. |
| 30 | Review themes | Google topic tags: "fair pricing" (8), "quick job" (5), "polite crew" (2), "fast roof installation" (2). Reviews mention materials explained, daily progress updates, cleanup, damaged wood replaced, work finished before rain. One Yelp review alleges unfinished work and a request for a 5-star review | **V** | [S03], [S04], [S07] | Quote reviews only with the reviewer's permission or through the platform's own embed. Follow the FTC reviews rule (§5). |
| 31 | Awards | None found | **U** | none | **P** |
| 32 | Response-time claims | None claimed | **U** | none | **P** |
| 33 | Pricing / free estimate | "Free estimates" in the Instagram bio and a post "FREE ESTIMATES NO COST AT ALL!". No prices published | **S** | [S09] | "Free estimate" can be the CTA label once the owner confirms (01 §3). **P** for any prices. |
| 34 | Authentic completed projects | Named-product posts (City of Bell Duration COOL Oyster Shell; 4-unit Duration Oyster Shell; Shasta White + Polyfresko G flat section) [S09]; standing-seam metal hillside hip roof (May 2026) and shingle reroofs [S03] | **V** (they exist) / **P** (use) | [S03], [S09] | Need originals, owner permission, customer consent, and address privacy (04 §1) |
| 35 | Customer testimonial videos | Several reels feature customers on camera | **V** (exist) / **P** (use) | [S09] | Need signed releases |
| 36 | Primary contact and conversion destination | Phone verified. Inbox for estimate requests and SMS capability unknown | **V** / **U** | [S01] | Owner question (01 §3) |
| 37 | Languages | Not stated | **U** | none | Owner question (01 §2) |
| 38 | Fire rating of product | OC Duration: ASTM E108 / UL 790 **Class A** | **V** (manufacturer) | [S12], [S13] | Fact line only (02 §5). Never "fireproof". |

---

## 4. Claim-safety review of the creative lines

These lines come from the creative brief. The same FTC substantiation standard covers express and implied objective claims [S32].

| Line | Verdict | Reasoning | Safer direction (placeholder, not final copy) |
| --- | --- | --- | --- |
| "ONE ROOF. EVERY CONDITION." | **Internal only** | "Every condition" implies hail, fire, hurricanes, earthquakes and any wind speed. The warranties are *limited* and name a wind speed (130 MPH) [S12]. A weather sequence that the roof "survives" makes the claim feel objective. | Name only the three LA conditions the page teaches, e.g. "sun · Santa Anas · the rainy season". |
| "BUILT FOR EVERYTHING." | **Prohibited** as public copy | An absolute performance claim nobody can substantiate, and it sits right next to the estimate CTA. | The final beat can keep its energy with a scoped statement about layers working together. Counsel and owner review before use. |
| "Built for Whatever Comes Next" (user's fallback) | **Hold** for counsel and owner review | Softer and closer to puffery, but after an explicit "weather test" it still implies universal durability. | Prefer copy tied to the demonstrated conditions and the named product. |
| "The panel survives" / "weather test" | **Allowed only as a labeled illustration** | Anything that looks like a test result implies lab testing. | Label the sequence "Illustration of how each layer works. Not a product test." Show no wind speeds or rain rates except the manufacturer's rated values with their terms. |
| "Lifetime warranty" | **Prohibited unqualified** | It is the manufacturer's *limited* warranty with conditions [S12]. | "Owens Corning limited lifetime warranty (as long as you own your home). See terms." |
| "Since 1964" / "62 years" | **Prohibited as company age** | The entity dates from 2020–21 [S01][S11]. | An owner-confirmed family history, told as a story with names and dates the owner supplies. |
| "Licensed" | **Allowed** | CSLB #1084651 is active [S01] | Show the license number next to the claim. |
| "Bonded & insured" | "Bonded" allowed with care. **"Insured" on hold** | Workers' comp policy cancels 10/06/2026; no GL certificate seen [S01] | Re-check after 10/06/2026. Ask for the GL certificate. |
| "5-star" | **Allowed only dated and sourced** | Ratings differ by platform [S03][S04][S06] | "5.0 on Google · 58 reviews · as of <date>" |
| "Free estimate" | **Allowed after owner confirmation** | Self-published [S09] | Use as the CTA label. |

---

## 5. Compliance constraints Phase 1 must respect

1. **License number in all advertising.** B&P §7030.5; advertising includes "any electronic transmission" (16 CCR §861) [S29]. The license number goes in the header or footer on every page state, including the static fallback.
2. **Advertise only within your classification.** B&P §7027.1 [S29]. That means C39 roofing only, until another license basis is shown (solar, general building, etc.).
3. **The unofficial pitch is not advertising.** The pitch build uses `noindex`, a visible "Unofficial concept by Lumera Creative. Not affiliated with or approved by JM Roofing 3rd Generation." label, an unlisted URL, and **no live lead capture**. The estimate form is a disabled demo and the phone number is plain text, until the owner approves. Lumera holds no contractor license, so it must never look like it offers roofing work.
4. **Substantiation.** Every objective claim needs a reasonable basis on file before it is published [S32].
5. **FTC Consumer Reviews and Testimonials Rule** (effective 2024-10-21) [S33]: no fake or AI reviews, no incentives conditioned on sentiment, no review suppression, and insider connections must be disclosed. The site must not show only 5-star excerpts in a way that suppresses negative reviews.
6. **Customer privacy.** Drone and project photos can reveal customers' homes and house numbers. Get customer consent, and blur or crop house numbers, plates and faces unless a release covers them.
7. **Manufacturer marks.** Naming Owens Corning products as installed materials is factual. No OC logos, badges or "certified" language without network membership (row 21).

---

## 6. Conflicts log

| Topic | Values seen | Resolution |
| --- | --- | --- |
| Hours | Google closes 9 PM; Birdeye Mon–Sat 5–9, Sun closed; Yelp 5:45 AM–10 PM daily | Owner |
| Rating | 5.0/58 Google; 4.7/223 Thumbtack; 3.7/3 Yelp; 5.0/34 Birdeye; aggregators 4.9/50 | Platform-dated display |
| Company age | "since 1964" / "62 years" vs corporation 2020, license 2021 | Family story only, owner-confirmed |
| Bond amount | CSLB $25,000 vs BuildZoom $15,000 | CSLB is authoritative (BuildZoom is stale) |
| Owner name | Jose Salvador Martinez Miranda (CSLB); Jose Miranda (BBB); Jose Martinez Miranda (Thumbtack) | Owner's preference |
| Services scope | Thumbtack lists tile, shake, hot mop, torch down, solar, commercial, industrial; photos show mostly shingle | Owner, with a license check for solar |

---

## 7. Sources

All accessed 2026-09-30. Aggregator pages (Thumbtack, Birdeye, BuildZoom, bizprofile) are third-party and can be stale; they are never the only source for a public claim.

| ID | Source | URL |
| --- | --- | --- |
| S01 | CSLB license detail #1084651 | https://www.cslb.ca.gov/OnlineServices/CheckLicenseII/LicenseDetail.aspx?LicNum=1084651 |
| S02 | CSLB license detail #778450 | https://www.cslb.ca.gov/OnlineServices/CheckLicenseII/LicenseDetail.aspx?LicNum=778450 |
| S03 | Google Maps listing (user-supplied link) | https://maps.app.goo.gl/Pxb53ERAe2e6dDwb7 |
| S04 | Yelp | https://www.yelp.com/biz/jm-roofing-3rd-generation-los-angeles |
| S05 | BBB profile | https://www.bbb.org/us/ca/los-angeles/profile/roofing-contractors/jm-roofing-3rd-generation-1216-1644514 |
| S06 | Thumbtack profile | https://www.thumbtack.com/ca/los-angeles/roofing/jm-roofing-3rd-generation/service/264969007224693997 |
| S07 | Birdeye | https://reviews.birdeye.com/jm-roofing-3rd-generation-corp-165308711201343 |
| S08 | BuildZoom | https://www.buildzoom.com/contractor/jm-roofing-3-rd-generation |
| S09 | Instagram @jm.roofing | https://www.instagram.com/jm.roofing/ |
| S10 | Threads @jm.roofing | https://www.threads.com/@jm.roofing |
| S11 | bizprofile (CA Secretary of State data) | https://www.bizprofile.net/ca/los-angeles/jm-roofing-3rd-generation |
| S12 | Owens Corning, TruDefinition Duration COOL data sheet, Pub. 10021534-B (Mar 2018) | https://images.thdstatic.com/catalog/pdfImages/9a/9a834ee0-8321-4c82-af87-e06414fb2fb4.pdf |
| S13 | Owens Corning, TruDefinition Duration data sheet | https://champion.owenscorning.com/downloaddmsassets/2147484921.pdf |
| S14 | Owens Corning contractor directory, California (search found no JM listing) | https://www.owenscorning.com/en-us/roofing/contractors/locations/ca |
| S28 | LADBS Information Bulletin P/GI 2020-003, Express Permits (rev. 04-20-2022) | https://dbs.lacity.gov/sites/default/files/efs/pdf/publications/ib-p-gi-2020-003-express-permits_rev-12-16-2021.pdf |
| S29 | CSLB Fast Facts: online marketplaces and advertising (B&P §§7027.1, 7030.5; 16 CCR §861) | https://www.cslb.ca.gov/resources/industrybulletins/online_marketplace_fast_facts.pdf |
| S30 | CSLB C-39 Roofing classification | https://www.cslb.ca.gov/about_us/library/licensing_classifications/Licensing_Classifications_Detail.aspx?Class=C39 |
| S32 | FTC Policy Statement Regarding Advertising Substantiation | https://www.ftc.gov/legal-library/browse/ftc-policy-statement-regarding-advertising-substantiation |
| S33 | FTC Consumer Reviews and Testimonials Rule: Q&A | https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers |

Source IDs continue in 02 (roof and climate) and 03 (competitors).
