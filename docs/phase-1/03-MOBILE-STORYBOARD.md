# 03 · Mobile Storyboard

Tier 2 (<1024px wide or coarse pointer, portrait). A **separate composition**: clip `media/sequence-portrait.mp4`, 864×1080 (4:5), rendered from the same Blender scene and timeline through a portrait camera with its own framing. Nothing is cropped from desktop. Screenshots: `docs/phase-1/screenshots/mobile/`.

## Layout

```
┌────────────────────────────┐  header 56px: name + CSLB line, Menu (≥44px)
├────────────────────────────┤
│ note (top-left)   HEAT chip│  stage: sticky under the header, 52svh, ABOVE the cards
│                            │  4:5 frame covers the width on phones; on tablets it is
│      roof / panel          │  contained, with side bands in the frame's own floor colour
│      one label             │
│              [Skip ↓ pill] │
├────────────────────────────┤
│ card text scrolls up here  │  reading area (~285px at 390×844); cards pass under the stage
│                            │
├────────────────────────────┤
│ Phone (323)…  [GET AN EST.]│  action bar, safe-area aware, 48px button
└────────────────────────────┘
```

## Beats

Same frames as desktop. Scroll lengths are `--len-m`. Total pinned distance: 4.90 viewport heights at 390×844 and 4.94 at 360×800 (limit 5). Every chapter is ≤112svh (limit 120).

| # | Beat | Frames | Scroll | Portrait framing | In-stage | Card | Shot |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Completed roof | 0 | 62svh (content-sized ~98) | House centered, full width | Skip pill | H1, instruction, product line | 01 |
| 2 | Anatomy | 0→112 | 112svh | Camera rises; the exploded stack fills the frame height (portrait suits the stack) | One label at a time (the newest layer) | Layer list 1–7 | 02, 03 |
| 3 | Panel | 112→165 | 50svh | Panel center-frame; its shadow on the floor anchors it | "The proof panel: every layer"; note on | Panel card | 04 |
| 4 | Heat | 165→195 | 58svh | Locked | Rays, sealant, airflow; the label "Sealant bonds in the sun"; HEAT chip | Heat card | 05 |
| 5 | Wind | 195→225 | 58svh | Locked | Streamlines, eave edge, nails; "Nails, under the next course"; WIND chip | Wind card | 06 |
| 6 | Rain → clears | 225→280 | 62svh | Locked | Rain, sheet flow, gutter; "Drip edge into the gutter"; RAIN chip; fades before the return | Rain card | 07, 08 |
| 7 | Return | 280→330 | 42svh | Back to the stack | "Back to the exact spot" | Return card | 09 |
| 8 | Reassembly | 330→405 | 62svh | Pulls back to the whole house | "Final ridge cap locks" | Bridge | 10, 11 |
| 9–11 | Proof → Built for everything. → Estimate | — | Normal | — | — | Single-column cards; the final image stacks above the headline and CTA | 12–14 |

## Mobile rules applied

- Fewer simultaneous labels (one), shorter pins, less camera travel (portrait poses sit closer to the stack, so the move is shorter).
- Larger targets: menu, skip pill, action bar and form fields are all ≥44px.
- No hover anywhere. Native touch scroll (tested with a synthesized touch swipe).
- No horizontal overflow at 768, 430, 390 and 360 widths.
- The `svh` stage height means no jump when the URL bar shows or hides. The menu panel uses `100dvh`.
- Rotation: portrait → landscape phone switches to the static story (tier 4); turning back restores the motion tier at the same chapter (tested).
- **Tablet (768×1024):** the same mobile composition, with the contained 4:5 frame centered and side bands in the floor color of the current still.
