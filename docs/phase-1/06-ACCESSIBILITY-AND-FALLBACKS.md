# 06 · Accessibility and Fallbacks

> **Photoreal rework (2026-10-01):**
> - The stage is now a canvas inside the same `aria-hidden` stage, with no focusable descendants.
> - Drawn overlays and projected text labels are gone. Numbered markers 1–5 (`aria-hidden`) match the anatomy list.
> - Desktop cards share one fixed column: inactive cards are transparent, not hidden, so screen readers still read every chapter, and `:focus-within` reveals a focused card.
> - Static and reduced-motion figures now use the rendered keyframes (`media/stills/*`) with new alt text.
> - Tiers and fallbacks are unchanged. A blocked CDN uses the native-scroll mapping, and a blocked sequence falls back to the static story.

Target: WCAG 2.2 AA (plus 44px targets per the brief). Tested headlessly (09 §3, §5); a manual screen-reader pass on real assistive technology is still owed (§5 below).

## 1. Structure and semantics

| Item | Implementation | Status |
| --- | --- | --- |
| Landmarks | `header` (banner), `nav` ×3 (primary, mobile primary, sequence chapters) each with `aria-label`, `main`, `footer` | Pass (Lighthouse 100) |
| Headings | One `h1` (opening). `h2` per chapter, proof, final, estimate. `h3` for slots. No skipped levels. | Pass |
| Sequence summary | A screen-reader-only paragraph at the start of the sequence names the eight steps and says the moving picture only illustrates the text | Implemented |
| Stage | `aria-hidden="true"`, no focusable descendants. The video has `tabindex="-1"` and no audio. Every fact on the stage is repeated in chapter text. | Pass |
| Roof layers | An ordered list (`<ol class="layers">`) of 7 items. In the static anatomy figure, numbered markers match the list (the markers are `aria-hidden`; the list is the text equivalent). | Pass |
| Weather states | Each has a `h2` (HEAT/WIND/RAIN) and a bulleted list of functions. Static figures carry descriptive `alt`. | Pass |
| Scroll progress | **Never announced.** There are no live regions on the sequence. `aria-current="step"` on the rail updates only when the chapter changes. | Pass |
| CTA | Real links: "Get an estimate now" → `#estimate` (header, opening card, final, action bar) | Pass |
| Form | Visible labels, `autocomplete`, `inputmode`, `aria-describedby` pointing at the concept notice, a status line in a `role="status"` live region | Pass |

## 2. Keyboard and focus

- **Tab order** (tested): Skip link → brand → The roof → Proof → Estimate → Get an estimate now → rail: Roof, Anatomy, Panel, Heat, Wind, Rain, Return, Together, Skip to proof → content links → form. **Every stop showed the focus ring.**
- **Skip link:** Enter moves focus to `#proof` (`tabindex=-1` section), which lands 72px from the top under the sticky header. No focus traps. The `<details>` menu opens and closes with Enter/Space.
- **Focus style:** 3px redline outline with 3px offset (a 2px plaster gap on dark buttons). Contrast: 4.8:1 against plaster.

## 3. Visual

- **Text contrast:**
  - ink on plaster 13.3:1, ink-2 7.5:1, ink on sheet cards 15.3:1
  - cards sit on a 95%-opaque sheet over the stage, so card text never depends on video frames (worst case is the card itself)
  - labels: ink on a sheet box
- **Non-text:** weather lines 3.3–4.6:1 on their own tinted stage. Redline 4.8:1.
- **Targets:** every visible control is ≥44×44px. The automated check found **0 undersized targets** across all 71 screenshots.
- **Reflow:** no horizontal overflow at 360–1440px. Text resizes with `clamp()`. Uppercase is CSS-only, so the source stays sentence case.
- **Motion:** nothing autoplays. Everything moves only with scroll. No flashing, no shake, no haptics.

## 4. Experience tiers and fallbacks

All tiers keep the same content, order and CTAs. The default CSS is the static story, so **no JS = full story**.

| Condition | Detection | Result | Tested |
| --- | --- | --- | --- |
| Full desktop | width ≥1024, height ≥600, fine pointer | Pinned 16:9 stage, cards, rail | Yes |
| Tablet / phone portrait | otherwise | Pinned 4:5 stage above cards, one label, chip, skip pill, action bar | Yes (768, 430, 390, 360) |
| `prefers-reduced-motion` | Media query, **live in both directions** | Static story: no scrub, no pin, no parallax, no video request. Anatomy diagram with numbered markers and list, then ordered Heat → Wind → Rain with drawn overlays at their final state, then proof and CTA. | At load: 0 video requests. Live flip in and out. |
| Save-Data / 2G | `navigator.connection` | Static story | 2G → static, no clip requested |
| Low-power | `deviceMemory ≤1` or `hardwareConcurrency ≤2` | Static story | 2 cores → static |
| No WebGL / canvas failure / context loss | — | **Not applicable.** The prototype uses no WebGL or canvas, so these failures can't occur. | — |
| Failed media | `<video>` error event | Switches to the static story at the same chapter, with `media-failed` on `<html>` | Blocked `*.mp4` → static, figures shown, reader kept at the rain chapter |
| Slow connection (3G-class) | Buffered-range guard | The motion layout keeps the **nearest still** for any frame not yet downloaded (never a stale frame). The clip takes over as it buffers. HTML, H1 and CTA in about 0.63 s. | Yes |
| Landscape phone | landscape + coarse + height ≤540 | Static story (no cramped pin) | Rotation test |
| No JS | — | Static story; the form cannot submit (`method="dialog"`) | By construction (default CSS) |

## 5. Not yet verified (carried to Phase 2)

- VoiceOver (iOS/macOS) and NVDA passes on a real device and screen reader.
- Real iPhone Safari and Android Chrome scrubbing (headless emulation isn't a device).
- Windows High Contrast / forced-colors check (overlays rely on stroke colors).
- 200% zoom pass on desktop with the sticky card.
