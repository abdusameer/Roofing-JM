// Static checks for the roof-sequence prototype (no dependencies). The repo has no build step,
// so this is the "production build" gate: it fails on anything that would ship broken.
//   node tools/check.mjs
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const SITE = path.join(ROOT, "prototype/roof-sequence");
const html = fs.readFileSync(path.join(SITE, "index.html"), "utf8");
const js = fs.readFileSync(path.join(SITE, "sequence.js"), "utf8");
const fails = [], notes = [];
const ok = (cond, msg) => (cond ? notes.push("ok  " + msg) : fails.push("FAIL " + msg));
const exists = (p) => fs.existsSync(path.join(SITE, p));
const kb = (p) => fs.statSync(path.join(SITE, p)).size / 1024;

// 1. JS syntax
for (const f of ["prototype/roof-sequence/sequence.js", "tools/qa.mjs", "tools/serve.mjs"]) {
  try { execFileSync(process.execPath, ["--check", path.join(ROOT, f)]); ok(true, "syntax " + f); } catch (e) { ok(false, "syntax " + f); }
}
// 2. every local src/href/srcset resolves (relative URLs only, so the Pages base path works)
const refs = [...html.matchAll(/(?:src|href|srcset)="([^"#][^"]*)"/g)].map((m) => m[1]).filter((u) => !/^(https?:|data:|mailto:|tel:)/.test(u));
for (const r of refs) {
  ok(!r.startsWith("/"), "relative url " + r);
  ok(exists(r.split("?")[0]), "exists " + r);
}
// 3. the image sequences and the step-to-file manifest (Phase 2B, Higgsfield clips)
const M = JSON.parse(fs.readFileSync(path.join(SITE, "media/hf/manifest.json"), "utf8"));
const TL = { last: M.lastMasterFrame, chapters: M.chapters };
const RANGE = { desktop: [200, 400, 1440, 813], mobile: [100, 220, 900, 508] };
for (const kind of ["desktop", "mobile"]) {
  const S = M.sequences[kind];
  ok(!!S, `sequence ${kind} in manifest`);
  if (!S) continue;
  const [lo, hi, w, h] = RANGE[kind];
  ok(S.count >= lo && S.count <= hi, `${kind} scroll steps ${S.count} within ${lo}-${hi}`);
  ok(S.width === w && S.height === h, `${kind} frames ${S.width}x${S.height}`);
  const files = fs.readdirSync(path.join(SITE, "media/hf", kind)).filter((f) => f.endsWith(".webp"));
  ok(files.length === S.files, `${kind}: ${files.length} webp files = ${S.files} unique images`);
  ok(S.map.length === S.count && S.map.every((f) => f >= 0 && f < S.files), `${kind}: every step maps to an image`);
  ok(S.master.length === S.count && S.master[0] === 0 && S.master[S.count - 1] === TL.last, `${kind}: master map spans 0-${TL.last}`);
  ok(S.master.every((m, i) => i === 0 || m > S.master[i - 1]), `${kind}: master map strictly increasing (reverse scroll = reverse time)`);
  ok(S.first > 0 && S.keyframes.every((k) => k >= 0 && k < S.count), `${kind}: first-chapter and keyframe lists valid`);
  const st = M.stills[kind];
  ok(st.poster && st.poster.frame === 0, `${kind}: poster is step 0`);
  ok(st.final && st.final.frame === S.count - 1, `${kind}: final image is the last step`);
  const fb = Object.keys(st).filter((k) => k !== "poster" && k !== "final");
  ok(fb.length >= 5 && fb.length <= 7, `${kind}: ${fb.length} fallback keyframes`);
  for (const k of Object.keys(st)) ok(exists(`media/hf-stills/${kind}/${k}.webp`), `still ${kind}/${k}`);
}
// the return and the reassembly are the forward clips exactly reversed (same images, opposite order)
{
  const S = M.sequences.desktop, B = M.beats, seg = (k) => S.map.slice(B[k][0], B[k][1] + 1);
  ok(JSON.stringify(seg("return")) === JSON.stringify(seg("panel").slice().reverse()), "return = clip B frames reversed");
  ok(JSON.stringify(seg("reassembly")) === JSON.stringify(seg("anatomy").slice().reverse()), "reassembly = clip A frames reversed");
  ok(seg("hold").every((f) => f === S.map[S.count - 1]) && seg("hold")[0] !== seg("reassembly").slice(-1)[0], "final hold is the separate roof-complete-master image");
  ok(JSON.stringify(M.order) === JSON.stringify(["clip A forward", "clip B forward", "clip C", "clip B reversed", "clip A reversed", "final hold: roof-complete-master"]), "required website order");
}
// 4. chapter ranges in the HTML match the Blender timeline, and heights follow frame counts
const chs = [...html.matchAll(/data-ch="(\w+)" data-f0="(\d+)" data-f1="(\d+)" style="--n:(\d+)"/g)];
ok(chs.length === TL.chapters.length, `${chs.length} chapters in HTML`);
let sum = 0;
chs.forEach((m, i) => {
  const c = TL.chapters[i] || {};
  ok(m[1] === c.id && +m[2] === c.f0 && +m[3] === c.f1, `chapter ${m[1]} ${m[2]}-${m[3]} matches timeline`);
  ok(+m[4] === +m[3] - +m[2] + 1, `chapter ${m[1]} height = ${m[4]} frames`);
  sum += +m[4];
});
ok(sum === TL.last + 1, `chapter frames sum to ${TL.last + 1}`);
// 5. engine contract: one canvas, GSAP ScrollTrigger scrub, linear mapping, no video, CDN pinned with SRI
ok(/<canvas class="stage-canvas"/.test(html) && !/<video/.test(html), "one canvas stage, no video element");
ok(/scrub: true/.test(js) && /Math\.round\(clamp\(p, 0, 1\) \* \(S\.count - 1\)\)/.test(js), "scrub: true and frame = round(progress × (count − 1))");
for (const lib of ["gsap.min.js", "ScrollTrigger.min.js"]) {
  ok(new RegExp(`cdnjs\\.cloudflare\\.com/ajax/libs/gsap/3\\.14\\.2/${lib.replace(".", "\\.")}" integrity="sha512-`).test(html), `${lib} pinned with SRI`);
}
ok(/createImageBitmap/.test(js) && /nearestReady/.test(js), "decode window + nearest-ready frame (never blank)");
// 6. compliance strings that must be present in every tier (they live in static HTML)
ok(/<meta name="robots" content="noindex/.test(html), "noindex meta");
ok((html.match(/1084651/g) || []).length >= 3, "CSLB license number in header, proof and footer");
ok(html.includes("Unofficial concept by Lumera Creative. Not affiliated with or approved by JM Roofing 3rd Generation."), "concept notice");
ok(html.includes("Concept visualization of how each layer works. Not a product test."), "visualization-not-test label");
ok(/AI-generated concept visualization/.test(html) && /does not demonstrate real roof performance/.test(html) && /not a photo or video of JM Roofing projects/.test(html), "AI provenance and no-performance-claim in footer");
ok(!/lifetime warranty|since 1964|insured|financing|24\/7|emergency|\bfree\b|solar panel|\bmph\b|°F/i.test(html.replace(/<!--[\s\S]*?-->/g, "")), "no prohibited claims or readings in markup");
ok(/method="dialog"/.test(html), "concept form cannot submit anywhere");
// 7. payload budgets
const MB = (b) => b / 1048576;
ok(MB(M.sequences.desktop.bytes) <= 18, `desktop sequence ${MB(M.sequences.desktop.bytes).toFixed(2)} MB <= 18 MB`);
ok(MB(M.sequences.mobile.bytes) <= 8, `mobile sequence ${MB(M.sequences.mobile.bytes).toFixed(2)} MB <= 8 MB`);
ok(M.sequences.desktop.maxFrameBytes / 1024 <= 160, `largest desktop frame ${(M.sequences.desktop.maxFrameBytes / 1024).toFixed(0)} KB <= 160 KB`);
ok(kb("media/hf-stills/desktop/poster.webp") <= 200, `desktop poster ${kb("media/hf-stills/desktop/poster.webp").toFixed(0)} KB <= 200 KB`);
ok(kb("media/hf-stills/mobile/poster.webp") <= 110, `mobile poster ${kb("media/hf-stills/mobile/poster.webp").toFixed(0)} KB <= 110 KB`);
// 8. production sources and provenance ship with the repo
const P = JSON.parse(fs.readFileSync(path.join(ROOT, "higgsfield/provenance.json"), "utf8"));
for (const m of P.masters) ok(fs.existsSync(path.join(ROOT, m.local)), "master " + m.name);
for (const c of P.clips) ok(fs.existsSync(path.join(ROOT, c.local)), "clip " + c.name);
ok(P.credits.actual > 0 && typeof P.status === "string" && /not a product test/.test(P.status), "provenance records cost and concept status");

console.log(notes.length + " checks passed");
if (fails.length) { console.log(fails.join("\n")); process.exit(1); }
console.log("all checks passed");
