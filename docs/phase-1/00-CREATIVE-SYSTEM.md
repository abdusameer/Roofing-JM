# 00 · Creative System

JM Roofing 3rd Generation, unofficial Lumera prospect concept. Phase 1, 2026-09-30.

> **Provisional system.** JM's real brand files (logo vector, colors, fonts) are not in hand and their use is not permitted yet (Phase 0, 00 rows 1 and 34; 04 §1). This system is built around the roof itself. JM's name is typed, never drawn as a logo. When the owner supplies brand files, the logo goes in the header, and its blue/red/yellow stays inside the logo rather than driving the page (Phase 0, 03 §3).

Implemented in `prototype/roof-sequence/styles.css` (tokens at the top of the file).

---

## 1. Idea and motion principle

- **Signature mechanism: the Proof Panel.** A real cutaway of the roof's eave corner, cut from the same model by the same prism as every layer hole. It carries the weather lessons and returns to its exact transform. This is proven by an infinite-PSNR frame diff and an exact matrix match (09 §4).
- **One dominant motion principle:** *the same physical roof stays continuous while the visitor discovers how every layer works.* Only the roof moves. Light changes follow the LA calendar: summer sun → Santa Ana autumn → winter rain → the washed-clear day after. The camera moves only twice: in to the panel, and back out to the whole house.
- **Feel:** an architectural model photographed on a plaster table, annotated like a marked-up drawing. Engineered and tactile, without being a cold dashboard or a CGI showreel.

## 2. Typography

Two families, both open-license from Google Fonts, within the Phase 0 budget of two families.

| Role | Face and setting | Size / leading | Used for |
| --- | --- | --- | --- |
| Display | **Archivo**, width 75, weight 800, uppercase (CSS `text-transform`; the source stays sentence case for screen readers) | `clamp(2.6rem, 1.2rem + 5.2vw, 5.6rem)` / 0.98 | H1 "Every layer has a job.", condition labels HEAT · WIND · RAIN, the bridge, the final line |
| Heading | Archivo, width 75, weight 800 | `clamp(1.9rem, 1.1rem + 2.6vw, 3.1rem)` / 0.98 | Chapter H2s, section heads |
| Body | Archivo, width 100, weight 400; bold terms 700 | 17px / 1.55 | Chapter text, lists |
| Lede | Archivo 600 | 20px | "Scroll beneath the surface." |
| Label | **IBM Plex Mono** 500, often uppercase with 0.06–0.12em tracking | 12–13px | Kickers, roof labels, tags, captions, license line |
| Numerical | IBM Plex Mono 500 | Inherits | License number, phone, ratings dates, CRRC ID |

Why: Archivo's narrow width reads like stencilled site lettering without becoming a cliché. Plex Mono gives labels the precision of drawing callouts.

## 3. Color tokens

| Token | Hex | Role | Contrast |
| --- | --- | --- | --- |
| `--plaster` | `#e3e1db` | Page background. **Sampled from the render floor in clear light**, so page and stage are one surface. | — |
| `--sheet` / `--sheet-2` | `#f1f0ec` / `#ebe9e4` | Cards, labels, form fields | — |
| `--ink` | `#1b1a18` | Text, buttons (asphalt/graphite) | 13.3:1 on plaster, 15.3:1 on sheet |
| `--ink-2` | `#46433d` | Secondary text, tag borders | 7.5:1 on plaster |
| `--line` | `#8a857c` | Hairlines only (decorative, never meaning) | 2.8:1 (non-text, decorative) |
| `--redline` | `#a93a26` | Annotation accent: leaders, dots, markers, focus ring, concept tags | 4.8:1 on plaster (passes as text too) |
| `--deck` | `#b98a4e` | OSB tan, reserved for the deck | — |
| `--sun` | `#a65f0c` | Heat overlay only | 3.3:1 on the heat-lit stage |
| `--air` | `#3f4d58` | Wind overlay only | 4.6:1 on the wind stage |
| `--water` | `#1c5f8d` | Rain overlay only | 3.6:1 on the rain stage |

Weather colors appear only inside their own chapter, as functional diagram lines. **No navy base, no yellow or orange CTA, no blue-orange grading** (Phase 0, 03 §3). The one saturated accent is the redline.

## 4. Grid, spacing, containers

- **Spacing scale (4-based):** 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 · 128 (`--s1…--s10`).
- **Container:** max 1320px. Side gutter `clamp(16px, 4vw, 48px)`.
- **Desktop stage composition:** the text column holds the card (`min(30rem, 36vw)`, left), and the roof is composed at ~58–62% of the frame width (camera lens shift, not CSS). This survives a 4:3 crop: at 1024×768, objects stay clear of both the card and the rail.
- **Flat pages (proof, estimate, static tier):** 12-column logic expressed as two grids: `5fr / 7fr` for chapter text and figure, `5fr / 6fr` for estimate. Cards auto-fit at `minmax(240px, 1fr)`.
- **Phones:** a single column. The stage is pinned at the top (52svh), the reading area sits below it, and the action bar at the bottom.

## 5. Roof-label treatment

- A **10px dot with a 2px redline ring sits exactly on the anchor** (anchors are exported from Blender per frame). A 28px redline leader runs to a mono 13px label on sheet, with a 1px line border.
- One concise label per layer or job. **At most three on desktop; one on phones** (the newest).
- If an anchor is hidden (under the text column, the header, or off-stage), **its label hides.** It is never moved to point at the wrong thing.
- Text flips side to stay inside the stage. If neither side fits, it centers under the dot with a short vertical leader.
- Labels are decorative duplicates of text that already exists in the chapter (`aria-hidden` stage).

## 6. Technical line and annotation language

| Line | Meaning | Weight |
| --- | --- | --- |
| Solid redline | Edges and structure (eave edge, leaders) | 1.5px leaders, 3.5px emphasized edges |
| Solid sun amber | Heat that arrives; the sealant line bonding | 2.5 / 3.5px |
| Dotted amber | Light that goes back (reflected) | 2px, `2 7` |
| Dashed slate, moving | Air (attic airflow, wind) | 2px, `18 14` |
| Dashed water blue, moving | Water: rain, sheet flow, gutter flow | 2–2.5px |
| Round dots | Hidden things: nails under the next course, dust | 4–5px |
| Dashed redline | The exposed underlayment band ("second layer") | 2px |

Movement is tied to scroll (`--p`). **Nothing moves on a timer**, and nothing moves when the reader stops. There are no gauges, meters or invented numbers. The only number on the stage path is the CRRC listing, which lives in chapter text.

## 7. Buttons and focus

- **Primary:** solid graphite, plaster text, Archivo width 88, 700, uppercase, 0.06em tracking, 3px radius, **48px** high (56px in the final section). Hover lightens slightly. No gradient, no glow.
- **Ghost:** transparent with a graphite border (reserved).
- **Focus:** 3px redline outline, 3px offset. On buttons, a 2px plaster gap keeps the ring readable on graphite. Every interactive element shows it (tab-order test, 09 §3).
- **Targets:** ≥44×44px everywhere: rail links, menu, skip pill, action bar, form fields at 48px.

## 8. Image, material and texture language

- **Renders:** no filters, no grading, no lens effects, no rain on the lens. The stage uses cover sizing on desktop and phones, and contain on tablets with side bands in the frame's own floor color (sampled per still).
- **Materials:** Oyster Shell-like laminated blend with per-tab tone and granule speckle; graphite underlayment; OSB-tan deck; painted-white metal (JM paints flashing white, per their own post); matte stucco; grey (not pink) insulation, so no insulation brand is implied.
- **Photoreal rework (2026-10-01):** Night Sky (dark charcoal) laminated blend, light grey underlayment, OSB-tan deck, dark bronze drip edge, fascia and gutter, warm off-white stucco; procedural PBR with wet states (11 §5). The orange `--signal` (#c2410c) is reserved for the final call to action.
- **Page texture:** none. The plaster is flat; the tactility lives in the model.
- **Captions:** mono, factual: "Proxy illustration by Lumera Creative, not a photo of a JM Roofing project."

## 9. Transition principles

1. Only the roof moves; the interface fades in 200ms or less.
2. Every light change has a seasonal reason (heat → wind → rain → clear).
3. Layers move only along their real stacking direction: vertical for a hip roof of equal pitches.
4. The panel moves out along the roof normal, then forward, and returns along the same keys.
5. The weather clears before the panel returns.
6. The last ridge cap locks with a baked light lift and a redline lock marker. No screen shake, no haptics (D-3).

## 10. Proof-section treatment

- A **definition list of dated facts:** license, bond, ratings on every platform including the lowest, and the modeled product with a "pending owner confirmation" tag. Each fact carries "checked at … on Sep 30, 2026".
- **Hatched "Owner asset required" slots** state exactly what is needed. **No fake project cards.**
- When real assets arrive, each project uses JM's own caption format: product · color · city (with consent) · month/year.

## 11. Mobile composition rules

- Separate **4:5 portrait renders**, never a crop of desktop.
- The stage is pinned under the header at 52svh, *above* the cards, so text never covers the picture.
- One in-stage label at a time. A condition chip (HEAT / WIND / RAIN) top-right; the illustration note top-left.
- A visible **"Skip the sequence"** pill while the sequence crosses mid-screen.
- A bottom action bar with phone (as text) and **Get an estimate now**, inside the safe area.
- Shorter chapters (42–112svh, 4.9 viewport heights pinned in total). Native touch scroll. Nothing depends on hover.
- Landscape phones get the static story (tier 4).
