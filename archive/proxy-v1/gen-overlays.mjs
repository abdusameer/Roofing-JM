// Generates the weather / anatomy overlay SVGs and static markers from the Blender anchor
// exports, and writes them into prototype/roof-sequence/index.html between gen markers.
// The same markup serves the static figures (no JS) and is cloned into the motion stage.
//   node tools/gen-overlays.mjs
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const SITE = path.join(ROOT, "prototype/roof-sequence");
const HTML = path.join(SITE, "index.html");
const ORIENTS = { desk: "desktop", port: "portrait" };
const r1 = (v) => Math.round(v * 10) / 10;

function load(cam) {
  const f = path.join(SITE, "media", `anchors-${cam}.json`);
  return fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf8")) : null;
}

function at(A, name, frame) {
  const d = A.anchors[name];
  if (!d) throw new Error("missing anchor " + name);
  const i = d.from === d.to ? 0 : Math.max(0, Math.min(d.to, frame) - d.from);
  return { x: d.xy[i * 2] * A.size[0], y: d.xy[i * 2 + 1] * A.size[1] };
}
const add = (p, dx, dy) => ({ x: p.x + dx, y: p.y + dy });
const mix = (a, b, t) => ({ x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t });
const pts = (list) => list.map((p) => `${r1(p.x)},${r1(p.y)}`).join(" ");

function head(p, from, cls, size = 11) {
  const ang = Math.atan2(p.y - from.y, p.x - from.x);
  const a = { x: p.x - size * Math.cos(ang - 0.45), y: p.y - size * Math.sin(ang - 0.45) };
  const b = { x: p.x - size * Math.cos(ang + 0.45), y: p.y - size * Math.sin(ang + 0.45) };
  return `<path class="head ${cls}" d="M${r1(p.x)} ${r1(p.y)}L${r1(a.x)} ${r1(a.y)}L${r1(b.x)} ${r1(b.y)}Z"/>`;
}
const svg = (A, id, body) =>
  `<svg class="ov" data-ov="${id}" viewBox="0 0 ${A.size[0]} ${A.size[1]}" preserveAspectRatio="none" aria-hidden="true" focusable="false">${body}</svg>`;

const W = 200; // weather anchors are static (panel and camera hold 165-280)
const g = (A, i, j) => at(A, `g${i}_${j}`, W);

function heat(A) {
  const [w, h] = A.size; const s = Math.min(w, h) / 900;
  let b = "";
  for (const [i, j] of [[1, 2], [3, 4], [5, 5]]) {
    const t = g(A, i, j);
    const src = add(t, -0.07 * w, -0.30 * h);
    b += `<line class="sun draw" pathLength="100" x1="${r1(src.x)}" y1="${r1(Math.max(src.y, 0.03 * h))}" x2="${r1(t.x)}" y2="${r1(t.y)}"/>` + `<g class="fade">${head(t, src, "c-sun")}</g>`;
    const out = add(t, 0.08 * w, -0.2 * h);
    b += `<line class="sun-back fade" x1="${r1(t.x)}" y1="${r1(t.y)}" x2="${r1(out.x)}" y2="${r1(out.y)}"/>`;
  }
  const sa = at(A, "p_seal_a", W), sb = at(A, "p_seal_b", W);
  b += `<line class="hot draw" pathLength="100" x1="${r1(sa.x)}" y1="${r1(sa.y)}" x2="${r1(sb.x)}" y2="${r1(sb.y)}"/>`;
  const so = at(A, "p_soffit", W), ue = at(A, "p_underlay_edge", W), bd = at(A, "p_band_deck", W), up = at(A, "p_up", W);
  const start = add(so, 0.012 * w, 0.09 * h), end = add(up, -0.035 * w, -0.06 * h);
  b += `<polyline class="air flow" points="${pts([start, so, ue, bd, up, end])}"/>` + head(end, up, "c-air", 12 * s);
  return svg(A, "heat", b);
}

function wind(A) {
  const [w, h] = A.size; const lift = -0.014 * h;
  let b = "";
  for (const i of [0, 2, 4, 6]) {
    const e = g(A, i, 7), m = g(A, i, 4), t = g(A, i, 0);
    const p0 = add(e, 0.06 * w, 0.08 * h), p1 = add(e, 0, lift), p2 = add(m, 0, lift), p3 = add(t, 0, lift), p4 = add(t, -0.05 * w, -0.05 * h);
    const line = pts([p0, p1, p2, p3, p4]);
    b += `<polyline class="air flow" points="${line}"/><polyline class="dust flow" points="${line}"/>` + head(p4, p3, "c-air", 11);
  }
  const ea = at(A, "p_eave_a", W), eb = at(A, "p_eave_b", W);
  b += `<line class="edge draw" pathLength="100" x1="${r1(ea.x)}" y1="${r1(ea.y)}" x2="${r1(eb.x)}" y2="${r1(eb.y)}"/>`;
  const na = at(A, "p_nail_a", W), nb = at(A, "p_nail_b", W);
  b += `<line class="nails fade" x1="${r1(na.x)}" y1="${r1(na.y)}" x2="${r1(nb.x)}" y2="${r1(nb.y)}"/>`;
  const sa = at(A, "p_seal_a", W), sb = at(A, "p_seal_b", W);
  b += `<line class="hot" x1="${r1(sa.x)}" y1="${r1(sa.y)}" x2="${r1(sb.x)}" y2="${r1(sb.y)}"/>`;
  return svg(A, "wind", b);
}

function rain(A) {
  const [w, h] = A.size;
  let b = "";
  // falling rain: dashed strokes that move only when the reader scrolls
  for (const i of [0, 1, 2, 3, 4, 5, 6]) for (const j of [1, 4]) {
    const t = g(A, i, j), s = add(t, -0.02 * w, -0.42 * h);
    b += `<line class="drop flow" x1="${r1(s.x)}" y1="${r1(Math.max(0, s.y))}" x2="${r1(t.x)}" y2="${r1(t.y)}"/>`;
  }
  // sheet flow down each column, over every course line
  for (const i of [0, 1, 2, 4, 5, 6]) {
    const col = [0, 1, 2, 3, 4, 5, 6, 7].map((j) => g(A, i, j));
    b += `<polyline class="water flow" points="${pts(col)}"/>`;
  }
  // the boot column splits around the pipe
  const bootL = mix(g(A, 2, 1), g(A, 3, 2), 0.5), bootR = mix(g(A, 4, 1), g(A, 3, 2), 0.5);
  for (const side of [bootL, bootR]) b += `<polyline class="water flow" points="${pts([g(A, 3, 0), side, g(A, 3, 3), g(A, 3, 5), g(A, 3, 7)])}"/>`;
  // over the drip edge into the gutter, then along the gutter toward the corner outlet
  const ga = at(A, "p_gutter_a", W), gb = at(A, "p_gutter_b", W);
  for (const i of [1, 3, 5]) {
    const e = g(A, i, 7), into = mix(ga, gb, i / 6);
    b += `<line class="water draw" pathLength="100" x1="${r1(e.x)}" y1="${r1(e.y)}" x2="${r1(into.x)}" y2="${r1(into.y)}"/>` + `<g class="fade">${head(into, e, "c-water", 9)}</g>`;
  }
  const gEnd = add(ga, (ga.x - gb.x) * 0.25, (ga.y - gb.y) * 0.25);
  b += `<line class="water flow" x1="${r1(gb.x)}" y1="${r1(gb.y)}" x2="${r1(gEnd.x)}" y2="${r1(gEnd.y)}"/>` + `<g class="fade">${head(gEnd, gb, "c-water", 12)}</g>`;
  // second layer: the exposed underlayment band at the cutaway
  const bu = at(A, "p_band_under", W), dir = { x: g(A, 6, 0).x - g(A, 0, 0).x, y: g(A, 6, 0).y - g(A, 0, 0).y };
  const u0 = add(bu, -dir.x * 0.42, -dir.y * 0.42), u1 = add(bu, dir.x * 0.42, dir.y * 0.42);
  b += `<line class="band fade" x1="${r1(u0.x)}" y1="${r1(u0.y)}" x2="${r1(u1.x)}" y2="${r1(u1.y)}"/>`;
  return svg(A, "rain", b);
}

const ANAT = 110; // camera holds 104-118
const ANAT_MARKS = [["caps", 1], ["shingles", 2], ["underlay", 3], ["drip", 4], ["deck", 5], ["attic", 6], ["insulation", 7]];
function anatomy(A) {
  const [w, h] = A.size;
  const so = at(A, "soffit", ANAT), at_ = at(A, "attic", ANAT), ro = at(A, "ridge_out", ANAT);
  const start = add(so, 0.01 * w, 0.07 * h), end = add(ro, -0.01 * w, -0.06 * h);
  const body = `<polyline class="air flow" points="${pts([start, so, at_, ro, end])}"/>` + head(end, ro, "c-air", 11);
  const marks = ANAT_MARKS.map(([n, k]) => { const p = at(A, n, ANAT); return `<span class="mk" aria-hidden="true" style="left:${r1((p.x / w) * 100)}%;top:${r1((p.y / h) * 100)}%">${k}</span>`; }).join("");
  return svg(A, "anatomy", body) + marks;
}

// stage background per still = the render's own floor colour, so contain/cover edges never show a seam
function stillBg(cam) {
  const out = {};
  const dir = path.join(SITE, "media", `stills-${cam}`);
  if (!fs.existsSync(dir)) return out;
  for (const f of fs.readdirSync(dir).filter((f) => f.endsWith(".webp"))) {
    // average of the left and right edge strips: the pixels that meet the page when the frame is contained
    const strip = (x) => execFileSync("ffmpeg", ["-loglevel", "error", "-i", path.join(dir, f), "-vf", `crop=10:ih:${x}:0,scale=1:1`, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]);
    const l = strip(0), r = execFileSync("ffmpeg", ["-loglevel", "error", "-i", path.join(dir, f), "-vf", "crop=10:ih:iw-10:0,scale=1:1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]);
    out[f.replace(".webp", "")] = "#" + [0, 1, 2].map((k) => Math.round((l[k] + r[k]) / 2).toString(16).padStart(2, "0")).join("");
  }
  return out;
}

let html = fs.readFileSync(HTML, "utf8");
const meta = { stills: {}, bg: {} };
for (const [key, cam] of Object.entries(ORIENTS)) {
  const A = load(cam);
  if (!A) { console.warn("no anchors for", cam); continue; }
  meta.stills[cam] = A.stills; meta.bg[cam] = stillBg(cam); meta.timeline = A.timeline; meta.lock = A.lock;
  if (!A.panelCheck.returnExact || !A.panelCheck.pathMirrored) throw new Error(`panel return check failed for ${cam}`);
  const parts = { anatomy: anatomy(A), heat: heat(A), wind: wind(A), rain: rain(A) };
  for (const [id, markup] of Object.entries(parts)) {
    const re = new RegExp(`(<!--gen:ov:${id}:${key}-->)[\\s\\S]*?(<!--/gen-->)`);
    if (!re.test(html)) throw new Error(`marker gen:ov:${id}:${key} missing`);
    html = html.replace(re, `$1${markup}$2`);
  }
}
const metaTag = `<script type="application/json" id="roof-meta">${JSON.stringify(meta)}</script>`;
html = /<script type="application\/json" id="roof-meta">[\s\S]*?<\/script>/.test(html)
  ? html.replace(/<script type="application\/json" id="roof-meta">[\s\S]*?<\/script>/, metaTag)
  : html.replace('<script src="sequence.js" defer></script>', metaTag + '\n<script src="sequence.js" defer></script>');
fs.writeFileSync(HTML, html);
console.log("overlays written", Object.keys(meta.stills), JSON.stringify(meta.bg));
