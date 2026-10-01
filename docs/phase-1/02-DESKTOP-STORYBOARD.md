# 02 · Desktop Storyboard

Tier 1 (≥1024px wide, ≥600px tall, fine pointer, motion allowed). Clip `media/sequence-desktop.mp4`: 1600×900, 406 frames. The stage is sticky at 100svh; cards scroll over its left column; the chapter rail is on the right. Screenshots: `docs/phase-1/screenshots/desktop/NN-state-WxH.jpg`.

Frames are the Blender timeline (`blender/build_scene.py`, `TL`). Scroll length is each chapter's `--len` in svh. Total pinned distance is 7.47 viewport heights at 1440×900 (limit 8).

| # | Beat | Frames | Scroll | Camera | Model | Light | Overlay and labels | Card | Shot |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **Completed roof** | 0 (hold) | 70svh | Front-left three-quarter, house at ~60% of the frame | Complete | Clear LA daylight | None | H1 "Every layer has a job.", "Scroll beneath the surface.", product line with tag, CTA | 01 |
| 2 | **Anatomy** | 0→112 | 150svh | Rises and widens to frame the stack (0→104), then holds | Layers lift vertically, top-down: caps + ridge vent (10–36), shingles (28–54), underlayment (46–72), drip edge (62–84), deck (78–104). The eave-corner panel stays in place as a complete stack; every lifted layer shows the matching hole. | Clear | Labels follow each lift (at most three at once). The attic airflow line (soffit → ridge) and the insulation label appear at 98–124. | Numbered layer list 1–7 | 02, 03 |
| 3 | **Panel isolates** | 112→165 | 80svh | Moves in to the panel (118→165), depth of field on the panel | The panel moves 0.55 m out along the roof normal (112→130), then forward and turns to show its stepped cutaway (130→165). The house dims to haze but stays visible. | Clear → summer (sun climbs) | "The proof panel: every layer"; illustration note on | "One corner, every layer." | 04 |
| 4 | **Heat** | 165→195 | 100svh | Locked on the panel | Static | High, warm summer sun; floor warms | Incoming sun rays, reflected rays (dotted), the sealant line bonding (draws on), attic air path along the cut edge. Labels: Reflective granules · Sealant bonds in the sun · Attic air carries heat out. HEAT chip. | Heat card | 05 |
| 5 | **Wind** | 195→225 | 100svh | Locked | Static: courses stay flat (no failure) | Low, dry autumn light | Airflow over the eave and up-slope with dust dots, eave edge emphasized in redline, nail line dotted, sealant line held. Labels: Sealed courses stay flat · Nails, under the next course · Starter course seals the eave. WIND chip. | Wind card | 06 |
| 6 | **Rain** | 225→262 | 110svh (rain and clearing) | Locked | Shingles darken (wet) 228→248 | Overcast, cool | Rain strokes, sheet flow down every column, a split around the boot, arrows over the drip edge into the gutter, gutter flow toward the corner outlet, the underlayment band dashed. Labels (staggered): Each course laps the one below · Boot sheds water past the pipe · Underlayment: the second layer · Drip edge into the gutter. RAIN chip. | Rain card | 07 |
| 6b | **Clears** | 262→280 | (same chapter) | Locked | Shingles dry 262→280 | Washed-clear | The rain overlay fades out before the panel moves | Rain card ("the storm clears") | 08 |
| 7 | **Return** | 280→330 | 70svh | Back out to the stack framing (280→326) | The panel reverses the same keys: 280 = 165 pose, 315 = 130 pose, **330 = 112 pose exactly**. The house un-dims. | Washed-clear | "Back to the exact spot" | "Back to the exact spot." | 09 |
| 8 | **Reassembly** | 330→405 | 110svh + 45svh hold | Pulls back past the opening framing to full context (336→398) | Layers settle bottom-up: deck (330–350), drip edge (344–360), underlayment (354–372), shingles (366–384), caps (378–390). **The final ridge cap locks at 395.** | Washed; light lift at 395–399 | "Final ridge cap locks" redline lock marker | "Every layer. Working together." | 10, 11 |
| 9 | **Proof** | — | Normal scroll | — | — | — | — | License, bond, ratings (all platforms, dated), modeled product (pending), owner-asset slots | 12 |
| 10 | **Built for everything.** | — | Normal scroll | Finished-roof still | — | — | — | Headline over the empty floor of the frame, CTA "Get an estimate now", concept tag | 13 |
| 11 | **Estimate** | — | — | — | — | — | — | Inert form, phone as text | 14 |

**Always reachable:**
- Fixed header with name, license, nav, phone and CTA.
- Skip link (first Tab stop).
- Rail with eight chapter links plus "Skip to proof", shown while the sequence crosses mid-screen.

**Other viewports:** 1280×800 and 1024×768 use the same composition, with a cover crop of the 16:9 frame (1024 crops about 170px per side). Labels stay clear of the card and the rail (screens 01/03/05/07/11 at each size).
