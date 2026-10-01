# 02 · Roof and Condition Spec

JM Roofing 3rd Generation, unofficial Lumera prospect concept. Phase 0, 2026-09-30.

> **Status: conceptual. Not approved for construction guidance.** Every detail below needs sign-off from JM's owner (a C39 licensee) and a building-science reviewer before anything is published. The experience must never read as installation instructions, show people on a roof, or encourage anyone to climb onto one.

---

## 1. Selected roof assembly

**Owens Corning TruDefinition® Duration® COOL laminated asphalt shingles, color Oyster Shell, on a steep-slope hip roof. Solid wood sheathing, underlayment, metal drip edge, and a ventilated attic, on a single-story Los Angeles stucco house.**

| Why this assembly | Evidence |
| --- | --- |
| It is what JM visibly installs most | Their own posts name "Owens Corning Duration" and "Duration COOL", colors Oyster Shell and Shasta White [S09]. At least four shingle reroofs appear in their Google photos; only one metal roof and no tile [S03]. |
| It matches their permits | BuildZoom's permit descriptions read "Class A or B roof covering material weighing less than 6 pounds per sq. ft." [S08]. That is the LADBS express-reroof category for lightweight coverings [S28], and tile is too heavy for it. |
| It fits the region's rules | Steep-slope reroofs covering about half the roof or more (the 2025 form says "50% or more"; the CEC 2022 fact sheet and LADBS say "more than 50%") in climate zones 4 and 8–15 need a cool roof (aged solar reflectance ≥0.20 and thermal emittance ≥0.75, or SRI ≥16) unless an exception applies [S17][S18]. The City of LA requires a CRRC-rated cool roof product for residential replacements over 50% [S28]. JM's area sits in zones 8 and 9 (§6). |
| The product documents the three jobs the story needs | Solar-reflecting granules (heat), Tru-Bond sealant and the SureNail fabric nailing zone (wind), and 5⅝″ exposure on a 13¼″ shingle (rain lapping) [S12][S13]. |
| Oyster Shell is JM's documented color | Named in two JM project posts [S09]. CRRC Product ID **0890-0012**, calculated aged solar reflectance **0.22**, thermal emittance **0.92**, SRI **22** [S12]. |

**Rejected alternatives**

| Option | Why not |
| --- | --- |
| Standing-seam metal (a real "panel") | Only one JM project seen [S03]. It would be the showpiece job, not their typical one. Keep it as a Phase 2 variant if the owner wants to sell more metal. |
| Concrete or clay tile | Listed only on Thumbtack [S06], never seen in their photos, and the permit weight class points away from it [S08][S28]. |
| Low-slope coating (Polyfresko G) | Real, but only on flat sections [S09]. It could be a secondary "flat section" note later. |
| Any hybrid | Banned by the brief. It would also misrepresent what JM installs. |

---

## 2. The house and the isolated panel (modeling definitions)

**House (modeling assumption, to be matched to a JM reference job with owner permission):** a single-story, stucco-walled LA bungalow with a hip roof and a small front porch roof meeting the main wall. The porch-to-wall joint lets the anatomy show step and kick-out flashing truthfully. The slope is modeled in the ordinary residential range; the exact pitch is taken from the reference job. It must **not** reproduce a specific customer's house.

**The isolated panel ("the eave corner"):** a slice about 4 ft wide taken beside a hip line, running from the gutter up the slope about 6 ft. The width and height are modeling values. It contains, top to bottom and outside to inside:

| In the panel | Why it's there |
| --- | --- |
| Hip-cap shingles along one side | The edge where wind acts on the hip line |
| Field shingles (Duration COOL, Oyster Shell) with visible exposure and headlap | Heat (granules), wind (sealant and nail zone), rain (lapping) |
| One plumbing-vent boot near the top | A real penetration and seal for the rain chapter |
| Starter course at the eave | The sealed first edge (wind) |
| Metal drip edge at the eave | The edge water leaves by (rain) |
| Underlayment | The secondary water layer (rain) |
| Solid sheathing (decking) | What the roof is nailed to |
| Rafter tails, fascia, and a soffit intake vent | Where attic air enters (heat) |
| Gutter on the fascia, ending in an outlet | The end of the drainage path (rain) |

The panel is cut from **the same master model** as the house. It is never a separately modeled "hero" object (03 §6).

---

## 3. Component specification

**Verification key:** **Code** = California Residential Code · **Mfr** = Owens Corning publication · **Assoc/Gov** = ARMA, DOE or FEMA guidance · **JM?** = JM's actual practice unknown, owner to confirm.

| Component | Specification used for the model | Sources | Open item | Reviewer |
| --- | --- | --- | --- | --- |
| **Visible material** | Laminated architectural shingle, 13¼″ × 39⅜″, 5⅝″ exposure, 64 shingles per square. Granule surface. A fiberglass mat core coated in asphalt; granules shield the asphalt from UV. | Mfr [S12][S13]; Assoc [S21] | Confirm JM still installs this line and color | JM owner |
| **Hip/ridge treatment** | Cap shingles over the hip and ridge lines | Mfr system list [S13]; Gov [S23] | Which cap product JM uses (**JM?**) | JM owner |
| **Eave edge** | Metal drip edge at eaves. Extends ≥¼″ below the sheathing and ≥2″ up onto the deck, fastened ≤12″ o.c. **At eaves the underlayment goes over the drip edge.** | Code R905.2.8.5 [S15] | Drip edge profile and color (JM paints flashing; one post says "flashing paint color: white" [S09]) | JM owner |
| **Rake edge** | Not present on a pure hip roof. On a gable variant, the underlayment goes **under** the drip edge at rakes. | Code R905.2.8.5 [S15] | Only if the reference house has gables | JM owner |
| **Starter** | Starter course at the eave, with sealant, before the first course | Gov [S23]; Mfr system [S13] | Starter product (**JM?**) | JM owner |
| **Underlayment** | Code-compliant underlayment over the whole deck, lapped shingle-fashion (upper sheet over lower). Code names ASTM D226 Type I/II where there is no wind design, Type II where there is. Other products need an approved evaluation. | Code R905.1.1 [S15] | Product type: felt or synthetic (**JM?**) | JM owner, SME |
| **Flashing: walls** | Step flashing at roof-to-wall joints, at least 4″ high and 4″ wide. **Kick-out flashing** where the porch eave meets the wall, turning water away from the wall. | Code R905.2.8.3, R903.2.1 [S15] | JM's method (**JM?**) | JM owner |
| **Flashing: penetrations** | The vent-pipe boot follows the shingle manufacturer's printed instructions. The flange is shingled in: courses above lap over it, the course below sits under it. | Code R905.2.8.4 [S15] | Boot product (**JM?**) | JM owner |
| **Valleys** | None on the modeled house. If added: open valleys need a metal lining at least 24″ wide; closed valleys follow the manufacturer. | Code R905.2.8.2 [S15] | Only if the reference house has valleys | JM owner |
| **Fastening** | Nails: minimum 12-gauge shank, ⅜″ head, driven ¾″ into the sheathing. At least 4 fasteners per shingle, or more if the manufacturer requires it. OC advertises 130-MPH wind-warranty performance with 4 nails in the SureNail fabric nailing zone. DOE guidance recommends 6 nails in high-wind areas. | Code R905.2.5–2.6 [S15]; Mfr [S12]; Gov [S23] | 4 or 6 nails (**JM?**) | JM owner, OC tech services |
| **Sealant** | A factory sealant strip, thermoplastic and activated by the sun's heat. It bonds each shingle to the one below and supplies most of the wind resistance. OC Tru-Bond sealant grips the fabric nailing strip below. | Assoc [S21]; Mfr [S12] | None | SME |
| **Ventilation** | A vented attic. Intake at the eaves (soffit), exhaust high on the roof (ridge or roof vents), balanced with about 50–60% intake and 40–50% exhaust. It removes heat and moisture. | Assoc [S22] | Exhaust type on hip roofs (**JM?**). Net-free-area math is not shown to visitors. | JM owner, SME |
| **Drainage** | Water runs over the exposed shingle faces, crosses each course line downhill, leaves the roof over the drip edge into the gutter, then the outlet and downspout. Each course covers about 7⅝″ of the one below (13¼″ − 5⅝″). | Derived from Mfr [S12]; Code [S15] | None | SME |
| **Gutters** | Gutter on the fascia with an outlet at the corner | JM service listing [S04][S09] | Profile, material, size (**JM?**) | JM owner |
| **Decking** | Solid wood sheathing (plywood or OSB). LADBS express reroof permits distinguish "over existing solid sheathing" from "over new solid sheathing". Reviews mention damaged wood being replaced. | Gov [S28]; reviews [S04] | Plywood or OSB, and how often new sheathing is needed (**JM?**) | JM owner |
| **Insulation** | **Not a roof layer in this assembly.** It lies on the attic floor, below the ventilated attic space. Shown only as grey context and never as JM scope. (Title 24 lists R-38 ceiling insulation as one exception to the cool-roof rule [S17].) | Gov [S17] | Does JM do attic insulation? | JM owner, SME |
| **Fire class** | ASTM E108 / UL 790 Class A. Class A is required in LA Very High Fire Hazard Severity Zones for these reroofs. | Mfr [S12]; Gov [S28] | One fact line only (§5) | SME |
| **Cool-roof rating** | CRRC 0890-0012: aged SR 0.22, TE 0.92, SRI 22 (OC, 2018 publication) | Mfr [S12] | Confirm the current CRRC directory entry | SME |

### Anatomy order for the separation

Each layer is shown at the place where it does its job. Flashing is not drawn as a flat sheet, and insulation is not drawn as a roof layer.

1. Hip caps and field shingles (surface)
2. Starter course, drip edge, pipe boot, and on the porch joint step and kick-out flashing (edges and openings)
3. Underlayment
4. Sheathing (decking)
5. Ventilated attic: soffit intake → exhaust path, drawn as an airflow line (DOM/SVG, not geometry)
6. Ceiling insulation, greyed and labeled as context

> Correction to the brief's list ("Surface, Underlayment, Flashing, Ventilation, Decking, Insulation"): flashing belongs at edges and openings, ventilation is airflow through the attic, and insulation lies below the attic. Stacking them as flat slabs would be wrong for this assembly.

---

## 4. Relevant conditions for JM's area

| Condition | Include? | Evidence | What it teaches |
| --- | --- | --- | --- |
| **Heat and sun** | **Yes** | JM's jobs fall in climate zones 8 and 9 [S19] (§6), where Title 24 cool-roof rules apply to reroofs [S17][S18]. JM already sells Duration COOL [S09]. | Reflective granules, and attic ventilation carrying heat out. Heat also sets the sealant, which leads into wind. |
| **Wind (Santa Ana)** | **Yes** | NWS: strong, hot, dust-bearing winds from inland desert regions [S26]. Humidity drops sharply as the air descends; the season runs roughly September to May, strongest through passes and canyons [S31]. | Sealed courses, the nailing zone, the starter edge, the hip caps. |
| **Rain (winter storms)** | **Yes** | Downtown LA season normal is 14.25 in (NCEI 1991–2020), with January and February the wettest months at 3.29 in and 3.64 in [S27]. JM posted about El Niño storm prep [S09]. | Lapping, underlayment, drip edge into gutter, boot and kick-out flashing. |
| Hail, snow, hurricanes | **No** | Not characteristic of the area. Rare tropical-remnant rain (for example, 2.48 in on 2023-08-20 [S27]) is folded into "rain", not a separate condition. | — |
| Wildfire | **Not dramatized** | Relevant in parts of the area, and Class A is required in VHFHSZ [S28]. But depicting fire after the 2025 LA fires is sensitive, and Class A is not "fireproof". | One factual line in the anatomy (Class A) only if the SME and owner approve. |
| Earthquake | No | Not a weather function of the roof covering | — |

**Lighting follows the LA calendar.** Summer high sun (heat) → autumn low, dry, clear light with offshore wind (Santa Ana) → winter overcast and rain → the washed-clear day after a storm (return and reassembly). Every change in light has a seasonal reason. There is no arbitrary color grading.

---

## 5. The locked experience (v2), reconciled with the brief

The user's second brief (2026-09-30) replaces the first sequence (weather on the whole roof, then anatomy). **Locked order:** Completed roof → Anatomy → Isolation → Weather on the panel (Heat → Wind → Rain) → Panel returns → Reassembly + CTA → Authentic proof → Estimate.

Rules carried over from the first brief:

- One recognizable house and roof: the same geometry, materials, lighting logic and camera orientation throughout. The weather only adds water, air movement, dust and light. It never swaps the model.
- Every weather state teaches one roofing job, and each transition follows physical or seasonal logic.
- Nothing essential lives only in the animation (01 §4). No scroll hijacking, no forced horizontal scroll, no hover-only information, no intro gate.
- "Paused" means the weather clears and stops before reassembly. It does not mean frozen weather.
- The final beat: the last hip cap seats and the CTA lands with it. In the brief this beat includes "impact, vibration, lighting change". Implementation limits:
  - **Impact:** a settle of 2 px or less, 150 ms or less, on the stage image only, never the page. None under reduced motion.
  - **Light change:** baked into the rendered frames.
  - **Vibration:** not recommended. The Vibration API does not work in Safari or iOS, has dropped from recent Firefox, and is not Baseline [S36][S37]. It carries no meaning and can startle people. If the user insists: Android only, only on an explicit tap of the CTA, never on scroll.
- The heading "Built for everything" is **not approved** as public copy (00 §4).

---

## 6. Climate zones of JM's documented job locations

From the SoCalREN climate-zone directory (2018 edition) [S19]. **Confirm with the CEC's current zone tool before publishing any zone claim.**

| ZIP (locality) | Zone |
| --- | --- |
| 90001 Florence / South Central (JM's address) | 8 |
| 90011 South Central (Thumbtack area) | 8 |
| 90201 Bell / Bell Gardens / Cudahy | 8 |
| 90280 South Gate | 8 |
| 90301–90302 Inglewood | 8 |
| 91601 North Hollywood | 9 |
| 91356 Tarzana | 9 |
| 91402 Panorama City | 9 |
| 90210 Beverly Hills | 9 |

Both zones fall under the cool-roof requirement for steep-slope reroofs (zones 4 and 8–15) [S17]. Exceptions include R-38 ceiling insulation, a radiant barrier, no attic ducts (zone 9), and R-2 or more at the roof deck [S17][S18].

---

## 7. Condition-state matrix

### 7a. Behavior, learning, evidence

| # | State | Physical roof behavior | What the visitor learns | Relevant service | Verified supporting evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | **Clear / completed roof** | The finished roof at rest in daylight | This is a real LA home and a real JM roof type; who JM is; how to get an estimate | Replacement | License [S01]; product JM installs [S09]; product data [S12] |
| 2 | **Anatomy** (weather paused, none yet) | Layers separate along their true stacking direction, each staying over its footprint | A roof is a system of layers, and each has a job | Replacement, repair | Code components [S15]; ARMA [S21] |
| 3 | **Isolation** | The eave-corner panel moves forward along the slope's normal; the house dims but stays in view | "Watch one piece of your roof work" | — | Panel contents (§2) |
| 4 | **Heat** | Granules reflect part of the sunlight (aged SR 0.22); the rest heats the surface; attic air flows in at the soffit and out high on the roof; the sun's heat sets the sealant strip | Cool-rated granules; why attic ventilation matters; that sun is what bonds the shingles | Cool-roof replacement (Title 24) | [S12] [S17] [S18] [S20] [S21] [S22] |
| 5 | **Wind** | Offshore wind moves across the eave and hip. The sealed courses stay flat; the nails in the nailing zone and the starter edge hold | Why sealant, nailing zone and edges matter; what the wind rating is and isn't (a *limited warranty* figure) | Replacement, repair of lifted or missing shingles | [S12] [S21] [S23] [S24] [S26] [S31] |
| 6 | **Rain** | Water sheets down the exposed faces, crosses each course's headlap, runs past the boot, over the drip edge into the gutter; a cutaway shows the underlayment beneath lapped the same way | The drainage path; underlayment as a second layer; why flashing at openings matters | Leak repair, replacement, gutters | [S15] (R905.2.8.5, R905.2.8.4, R903.2.1) [S27] [S09] |
| 7 | **Clearing / panel returns** | Rain stops; the last water drains out of the gutter; the panel slides back along the same path | The layers worked together | — | Illustration only, labeled (00 §4) |
| 8 | **Reassembly + CTA** | Layers close in reverse order; the camera pulls back; the last hip cap seats; the CTA lands | The finished roof again, now understood | Free estimate (once confirmed) | [S09] (free estimates, pending) |
| 9 | **Authentic proof** | Real JM roofs with product and color labels | JM installs this for real, in LA | All confirmed services | [S03] [S08] [S09] (permissions pending) |
| 10 | **Final conversion** | Estimate form and phone | How to start, and what happens next | Estimate | Owner process (pending) |

### 7b. Visual, transition, fallbacks, reviewer

| # | Visual opportunity | Transition logic (into the next state) | Mobile fallback | Reduced-motion fallback | Accuracy reviewer |
| --- | --- | --- | --- | --- | --- |
| 1 | Low three-quarter view of the house under clear sky | Motion pauses and the camera moves in; layers begin to lift | Portrait framing of the same view (house centered, roof in the upper half) | Static composed still with H1 and CTA | JM owner (house type) |
| 2 | Clean separation with generous gaps; labels in DOM beside the layers | One layer is chosen: the eave corner | Layers stack vertically in the portrait frame; labels become cards below the image | Still of the separated state plus an `<ol>` of layers | JM owner, SME |
| 3 | Panel forward, house dimmed behind (never a black void) | Summer: the sun climbs | Panel fills the portrait frame (the tall slice suits portrait) | Still | — |
| 4 | Hard overhead light; reflected-light rays and an attic airflow line (SVG over the frame); the sealant line darkens as it bonds | The sealant set by the sun is what holds in wind; the light lowers to autumn | Same frames; the airflow line stays in the image, the text sits in a card | Still plus a text list of what heat does | SME (numbers), OC tech (sealant) |
| 5 | Dust and dry leaves (sparse) streaming across the edge; tabs stay down; a pressure arrow at the eave and hip; the nail line highlighted | Santa Ana season gives way to winter storms; clouds build | Fewer particles; slower | Still with the nail line and sealant labeled | JM owner (nail count), SME |
| 6 | Water sheeting in the true direction; a cutaway at one course shows the underlayment; water leaves over the drip edge into the gutter | The storm passes | Shorter clip; the drainage line drawn in SVG | Still with the drainage path drawn | JM owner, SME |
| 7 | Last drops leave the outlet; washed-clear light | Panel returns home | Same | Skipped (text only) | — |
| 8 | Layers close; pull back; the final cap seats with a ≤2 px settle; baked light lift; the CTA appears beside the house | Page continues to proof | CTA also in the sticky bar | Final still with the CTA; no settle | Counsel (copy near the CTA) |
| 9 | JM photos with product/color captions (their own format) | Proof → estimate | Single-column cards | Same | JM owner (permissions) |
| 10 | Plain form, big phone | End | Bottom bar remains | Same | — |

---

## 8. Questions for JM and the reviewers (also in 05 §6)

- Q-R1 Do you still install Owens Corning Duration / Duration COOL most? Which colors most?
- Q-R2 Which underlayment, starter, hip/ridge cap, drip edge and vent products do you use?
- Q-R3 How many nails per shingle do you use: 4 or 6?
- Q-R4 What exhaust ventilation do you install on hip roofs: ridge vent, roof vents, other?
- Q-R5 What gutter profile, material and size do you usually install?
- Q-R6 How often do LA reroofs need new sheathing?
- Q-R7 Can we model the house on one of your jobs (with the homeowner's OK), without showing the real address?
- SME-1 Confirm the anatomy order and the drainage and airflow depictions for a vented hip roof.
- SME-2 Confirm the current CRRC listing and how to state Title 24 applicability for JM's area.
- SME-3 Confirm the wind depiction (edge and corner emphasis per ASCE 7 roof zones). No primary source was pulled in Phase 0.

---

## 9. Sources (roof and climate)

All accessed 2026-09-30.

| ID | Source | URL |
| --- | --- | --- |
| S12 | Owens Corning, TruDefinition Duration COOL data sheet, Pub. 10021534-B (Mar 2018) | https://images.thdstatic.com/catalog/pdfImages/9a/9a834ee0-8321-4c82-af87-e06414fb2fb4.pdf |
| S13 | Owens Corning, TruDefinition Duration data sheet (incl. Total Protection Roofing System) | https://champion.owenscorning.com/downloaddmsassets/2147484921.pdf |
| S15 | California Residential Code 2022, Ch. 9 Roof Assemblies (UpCodes). The 2025 edition took effect 2026-01-01 [S16]; confirm section numbers against it | https://up.codes/viewer/california/ca-residential-code-2022/chapter/9/roof-assemblies |
| S16 | Riverside County: 2025 California Building Standards Code effective 2026-01-01 (search result, corroborated by several jurisdictions) | https://building.rctlma.org/news/2025-california-building-standards-code-effective-january-1-2026 |
| S17 | California Energy Commission, Energy Efficient Cool Roofs, Single-Family (2022 Standards) | https://www.energy.ca.gov/sites/default/files/2023-08/2022_Res_SF_Cool_Roof_ada.pdf |
| S18 | 2025 CF1R-ALT-01-E Residential Re-Roof, §150.2(b)1I (City of Roseville copy) | https://www.roseville.ca.gov/Documents/Development%20Services/Applications%20Forms%20and%20Handouts/Building/Forms/2025%20Residential%20Re-Roof%20CF1R-ALT-01-E.pdf |
| S19 | SoCalREN Climate Zone Directory, County of Los Angeles (2018) | https://socalren.org/sites/default/files/contractor/Climate_Zones_Handout_-_SoCalREN_2018.pdf |
| S20 | LBNL Heat Island Group, Cool Roofs | https://heatisland.lbl.gov/coolscience/cool-roofs |
| S21 | ARMA, Residential Asphalt Roofing Manual (2014) | https://www.asphaltroofing.org/wp-content/uploads/2017/06/ARMA-Residential-Manual-Final-2.14.14.pdf |
| S22 | ARMA, Why Ventilation Is Important | https://www.asphaltroofing.org/why-ventilation-is-important/ |
| S23 | U.S. DOE Building America Solution Center, Asphalt Shingle Roofs | https://basc.pnnl.gov/resource-guides/asphalt-shingle-roofs |
| S24 | FEMA 499 Technical Fact Sheet No. 20, Asphalt Shingle Roofing for High-Wind Regions (Aug 2005) | https://apps.floridadisaster.org/hrg/downloads/FEMA_hgcc_fact20_Asphalt_Shingle_Roofing_for_High_Winds.pdf |
| S26 | NOAA NWS Glossary: Santa Ana wind | https://forecast.weather.gov/glossary.php?word=santa+ana+wind |
| S27 | LA Almanac, Downtown LA monthly rainfall normals (NCEI 1991–2020) | http://www.laalmanac.com/weather/we08.php |
| S28 | LADBS P/GI 2020-003 Express Permits (rev. 04-20-2022) | https://dbs.lacity.gov/sites/default/files/efs/pdf/publications/ib-p-gi-2020-003-express-permits_rev-12-16-2021.pdf |
| S31 | R. Fovell (Univ. at Albany), The Santa Ana Winds FAQ | https://www.atmos.albany.edu/facstaff/rfovell/SantaAna/santa_ana_faq.html |
| S36 | MDN, Vibration API | https://developer.mozilla.org/en-US/docs/Web/API/Vibration_API |
| S37 | Can I use: Vibration API | https://caniuse.com/vibration |

JM business sources S03, S04, S06, S08 and S09 are listed in 00 §7.
