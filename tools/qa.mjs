// Headless-Chrome QA for the roof-sequence prototype (zero dependencies; Node 22 global WebSocket).
// Serves the repo under the real Pages base path (/Roofing-JM/) with Range support.
//   node tools/qa.mjs shots        numbered screenshots + overflow/marker/console checks, 7 viewports
//   node tools/qa.mjs behaviour    scroll speeds, reverse, refresh, resize, rotation, keyboard, touch,
//                                  reduced motion (load + live flip), slow network (never blank), low power,
//                                  blocked CDN (native fallback), failed media
//   node tools/qa.mjs perf         frame pacing during scripted scroll (desktop, mobile 4x CPU), memory window
// Env: QA_TMP (Chrome profile dir), QA_GPU=1 (enable GPU), QA_ONLY=<substring of a viewport name>
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createServer } from "./serve.mjs";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const OUT = process.env.QA_OUT || path.join(ROOT, "docs/phase-1/screenshots");
const REPORT_DIR = path.join(ROOT, "qa/out");
fs.mkdirSync(REPORT_DIR, { recursive: true });
const MODE = process.argv[2] || "shots";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const server = createServer();
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const ORIGIN = `http://127.0.0.1:${server.address().port}`;
const PAGE = `${ORIGIN}/Roofing-JM/prototype/roof-sequence/`;

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9400 + Math.floor(Math.random() * 400);
const profile = fs.mkdtempSync(path.join(process.env.QA_TMP || os.tmpdir(), "roofqa-"));
const chrome = spawn(CHROME, ["--headless=new", ...(process.env.QA_GPU ? ["--enable-gpu-rasterization"] : ["--disable-gpu"]),
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
  "--autoplay-policy=no-user-gesture-required", "--disable-background-timer-throttling", "about:blank"], { stdio: "ignore" });
let ver;
for (let i = 0; i < 200 && !ver; i++) { try { ver = await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json(); } catch { await sleep(200); } }
const pageTarget = (await (await fetch(`http://127.0.0.1:${PORT}/json`)).json()).find((t) => t.type === "page");
const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let mid = 0; const pend = new Map(); const listeners = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  else if (m.method) for (const l of listeners) l(m);
};
const send = (method, params = {}, timeout = 30000) => new Promise((res, rej) => {
  const id = ++mid; pend.set(id, (m) => (m.error ? rej(new Error(method + ": " + m.error.message)) : res(m.result)));
  ws.send(JSON.stringify({ id, method, params }));
  setTimeout(() => { if (pend.has(id)) { pend.delete(id); rej(new Error("timeout " + method)); } }, timeout);
});
const evaluate = async (expr) => { const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + " " + (r.exceptionDetails.exception?.description || "")); return r.result.value; };

const issues = { console: [], failed: [] };
listeners.push((m) => {
  if (m.method === "Runtime.exceptionThrown") issues.console.push("exception: " + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text));
  if (m.method === "Runtime.consoleAPICalled" && (m.params.type === "error" || m.params.type === "warning")) issues.console.push(m.params.type + ": " + m.params.args.map((a) => a.value ?? a.description).join(" "));
  if (m.method === "Network.loadingFailed" && !m.params.canceled && m.params.blockedReason !== "inspector") issues.failed.push(m.params.errorText + " " + (reqUrls.get(m.params.requestId) || ""));
  if (m.method === "Network.requestWillBeSent") reqUrls.set(m.params.requestId, m.params.request.url);
  if (m.method === "Network.responseReceived" && m.params.response.status >= 400 && m.params.response.url.startsWith(ORIGIN)) issues.failed.push(m.params.response.status + " " + m.params.response.url);
});
const reqUrls = new Map();
await send("Page.enable"); await send("Runtime.enable"); await send("Network.enable");
await send("Network.setCacheDisabled", { cacheDisabled: false });

const VIEWPORTS = [
  { name: "1440x900", w: 1440, h: 900, mobile: false, dpr: 1 },
  { name: "1280x800", w: 1280, h: 800, mobile: false, dpr: 1 },
  { name: "1024x768", w: 1024, h: 768, mobile: false, dpr: 1 },
  { name: "768x1024", w: 768, h: 1024, mobile: true, dpr: 2 },
  { name: "430x932", w: 430, h: 932, mobile: true, dpr: 2 },
  { name: "390x844", w: 390, h: 844, mobile: true, dpr: 2 },
  { name: "360x800", w: 360, h: 800, mobile: true, dpr: 2 },
];
const MOBILE_UA = "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Mobile Safari/537.36";

async function setViewport(v) {
  await send("Emulation.setDeviceMetricsOverride", { width: v.w, height: v.h, deviceScaleFactor: v.dpr, mobile: v.mobile, screenOrientation: v.w > v.h ? { type: "landscapePrimary", angle: 90 } : { type: "portraitPrimary", angle: 0 } });
  await send("Emulation.setTouchEmulationEnabled", v.mobile ? { enabled: true, maxTouchPoints: 5 } : { enabled: false });
  await send("Emulation.setUserAgentOverride", { userAgent: v.mobile ? MOBILE_UA : ver["User-Agent"].replace("HeadlessChrome", "Chrome") });
}
async function load(url = PAGE, waitMedia = true) {
  await send("Page.navigate", { url });
  for (let i = 0; i < 100; i++) { await sleep(100); if (await evaluate("document.readyState === 'complete'")) break; }
  await evaluate("document.fonts.ready.then(() => true)");
  // wait for the first chapter and the keyframes (the planned first wave), like a reader who lingers on the opening
  if (waitMedia) for (let i = 0; i < 160; i++) { const s = await state(); if (!s || s.tier === "static" || s.tier === "reduced" || (s.files && s.loaded >= s.files)) break; await sleep(150); }
}
const state = () => evaluate("window.__roofState ? window.__roofState() : null");
async function settle(maxMs = 6000) {
  // scroll is async: give it a frame, then require the exact frame drawn twice in a row
  await sleep(160);
  const t0 = Date.now(); let s, stable = 0, last = null;
  while (Date.now() - t0 < maxMs) {
    s = await state();
    if (!s || s.tier === "static" || s.tier === "reduced") break;
    const done = s.exact && s.drawn === s.want;
    stable = done && last === s.want ? stable + 1 : done ? 1 : 0; last = s.want;
    if (stable >= 2) break;
    await sleep(70);
  }
  await sleep(120); return s;
}
// scroll so the sequence shows master frame f0 + q (f1 - f0) of a chapter: the same linear mapping as the engine
const chapterY = (id, q) => evaluate(`(() => { const el = document.getElementById(${JSON.stringify(id)}); const seq = document.getElementById('sequence');
  const m = +el.dataset.f0 + ${q} * (+el.dataset.f1 - +el.dataset.f0); const top = seq.getBoundingClientRect().top + scrollY;
  return Math.max(0, Math.round(top + (m / +document.querySelector('.chapter:last-of-type').dataset.f1) * (seq.offsetHeight - innerHeight))); })()`);
const scrollToY = (y) => evaluate(`window.scrollTo(0, ${y}); true`);
async function shot(file, fullPage = false) {
  const r = await send("Page.captureScreenshot", { format: "jpeg", quality: 72, captureBeyondViewport: false });
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, Buffer.from(r.data, "base64"));
}
const checks = () => evaluate(`(() => {
  const vw = document.documentElement.clientWidth;
  const overflow = document.documentElement.scrollWidth - vw;
  const st = document.querySelector('.stage'); const sr = st && getComputedStyle(st).display !== 'none' ? st.getBoundingClientRect() : null;
  // markers must sit inside the visible stage and never under the text card
  const badDots = [];
  if (sr) { const card = [...document.querySelectorAll('.chapter .card')].map(c => c.getBoundingClientRect()).find(r => r.bottom > sr.top + 40 && r.top < sr.bottom - 40);
    for (const d of document.querySelectorAll('.dot')) { if (parseFloat(d.style.opacity || 0) < 0.5) continue; const r = d.getBoundingClientRect();
      const out = r.left < sr.left || r.right > Math.min(sr.right, vw) || r.top < sr.top || r.bottom > sr.bottom;
      const under = card && document.documentElement.classList.contains('tier-desktop') && r.right > card.left && r.left < card.right && r.bottom > card.top && r.top < card.bottom;
      if (out || under) badDots.push(d.textContent + (out ? ' out' : ' under-card')); } }
  const cta = [...document.querySelectorAll('a.btn[href="#estimate"]')].some(a => { const r = a.getBoundingClientRect(); const cs = getComputedStyle(a); return cs.display !== 'none' && cs.visibility !== 'hidden' && r.bottom > 0 && r.top < innerHeight && r.width > 0; });
  const small = [...document.querySelectorAll('a, button, input, select, summary')].filter(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden' || r.width === 0 || e.closest('[aria-hidden="true"]') || e.classList.contains('skip')) return false; if (r.bottom < 0 || r.top > innerHeight) return false; return r.height < 43.5 || r.width < 43.5; }).map(e => (e.textContent || e.id || e.tagName).trim().slice(0, 30));
  const lic = document.body.innerText.includes('1084651');
  const cv = document.querySelector('.stage-canvas'), po = document.querySelector('.stage-poster');
  const blank = !!sr && !(cv.classList.contains('live') || (po.complete && po.naturalWidth > 0));
  return { overflow, badDots, ctaVisible: cta, smallTargets: small, licensePresent: lic, blank, tier: (document.documentElement.className.match(/tier-(\\w+)/) || [])[1] };
})()`);

const STATES = [
  ["01-opening", "ch-opening", 0.2], ["02-anatomy-lift", "ch-anatomy", 0.5], ["03-anatomy-full", "ch-anatomy", 1], ["04-panel", "ch-panel", 1],
  ["05-heat", "ch-heat", 0.7], ["06-wind", "ch-wind", 0.7], ["07-rain", "ch-rain", 0.55], ["08-rain-clears", "ch-rain", 0.95],
  ["09-return", "ch-return", 1], ["10-reassembly", "ch-reassembly", 0.4], ["11-hold", "ch-reassembly", 1],
];
const AFTER = [["12-proof", "proof"], ["13-final", "final"], ["14-estimate", "estimate"]];
const report = { mode: MODE, at: new Date().toISOString(), page: PAGE, results: [] };

async function runShots() {
  const only = process.env.QA_ONLY;
  for (const v of VIEWPORTS) {
    if (only && !v.name.includes(only)) continue;
    await setViewport(v); issues.console.length = 0; issues.failed.length = 0;
    await load();
    const group = v.mobile ? "mobile" : "desktop";
    const full = v.name === "1440x900" || v.name === "390x844";
    const states = full ? STATES : STATES.filter((s) => ["01-opening", "03-anatomy-full", "05-heat", "07-rain", "11-lock"].includes(s[0]));
    const res = { viewport: v.name, tier: (await state())?.tier, shots: [] };
    for (const [n, id, q] of states) {
      await scrollToY(await chapterY(id, q)); const s = await settle();
      const file = path.join(OUT, group, `${n}-${v.name}.jpg`); await shot(file);
      res.shots.push({ n, frame: s?.want, master: s?.master, exact: s?.exact, dots: s?.dots, cond: s?.cond, ...(await checks()) });
    }
    for (const [n, id] of full ? AFTER : AFTER.slice(0, 2)) {
      await evaluate(`document.getElementById('${id}').scrollIntoView({block:'start'}); true`); await sleep(350);
      await shot(path.join(OUT, group, `${n}-${v.name}.jpg`));
      res.shots.push({ n, ...(await checks()) });
    }
    res.console = [...issues.console]; res.failed = [...issues.failed];
    report.results.push(res);
    console.log(v.name, res.tier, "overflow max", Math.max(...res.shots.map((s) => s.overflow)), "bad markers", res.shots.flatMap((s) => s.badDots || []).length,
      "blank", res.shots.filter((s) => s.blank).length, "inexact", res.shots.filter((s) => s.exact === false).length, "console", res.console.length, "failed", res.failed.length);
  }
  // reduced-motion and static compositions
  for (const v of [VIEWPORTS[0], VIEWPORTS[5]]) {
    await setViewport(v);
    await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
    await load(PAGE, false);
    const group = v.mobile ? "mobile" : "desktop";
    for (const [n, id] of [["20-reduced-opening", "ch-opening"], ["21-reduced-anatomy", "ch-anatomy"], ["22-reduced-heat", "ch-heat"], ["23-reduced-rain", "ch-rain"]]) {
      await evaluate(`document.getElementById('${id}').scrollIntoView({block:'start'}); true`); await sleep(500);
      await shot(path.join(OUT, group, `${n}-${v.name}.jpg`));
      report.results.push({ viewport: v.name, n, ...(await checks()) });
    }
    await send("Emulation.setEmulatedMedia", { features: [] });
  }
}

const seqReqs = () => [...reqUrls.values()].filter((u) => u.includes("/media/hf/") && u.endsWith(".webp")).length;
const tierNow = () => evaluate("(document.documentElement.className.match(/tier-(\\w+)/)||[])[1]");
async function runBehaviour() {
  const B = {}; report.behaviour = B;
  const v = VIEWPORTS[0]; await setViewport(v); await load();
  const yA = await chapterY("ch-anatomy", 0.5), yR = await chapterY("ch-rain", 0.5), yEnd = await chapterY("ch-reassembly", 1);
  let s = await state();
  B.engine = { gsap: s.gsap, steps: s.count, files: s.files, loaded: s.loaded, ok: s.gsap && s.loaded === s.files };
  // fast scroll: jump through the sequence in large steps, then stop
  for (const y of [yA, yR, yEnd, 0]) await scrollToY(y);
  s = await settle(); B.fastJumpBackToTop = { frame: s.want, drawn: s.drawn, ok: s.want === 0 && s.drawn === 0 };
  // slow scroll with a real wheel gesture, then reverse: the picture plays backwards to frame 0
  await send("Input.synthesizeScrollGesture", { x: 700, y: 450, yDistance: -1600, speed: 600, gestureSourceType: "mouse" }, 60000);
  s = await settle(); const fwd = s.want;
  await send("Input.synthesizeScrollGesture", { x: 700, y: 450, yDistance: 1600, speed: 600, gestureSourceType: "mouse" }, 60000);
  s = await settle(); B.slowForwardThenReverse = { forwardFrame: fwd, afterReverse: s.want, ok: fwd > 10 && s.want === 0 };
  // mapping is exact and deterministic: frame = round(progress × (count − 1))
  const map = [];
  for (const q of [0.1, 0.33, 0.5, 0.77, 0.95]) {
    const y = await evaluate(`(() => { const seq = document.getElementById('sequence'); return Math.round(seq.getBoundingClientRect().top + scrollY + ${q} * (seq.offsetHeight - innerHeight)); })()`);
    await scrollToY(y); s = await settle();
    const p = await evaluate(`(() => { const seq = document.getElementById('sequence'); return -seq.getBoundingClientRect().top / (seq.offsetHeight - innerHeight); })()`);
    map.push({ q, progress: +p.toFixed(4), frame: s.want, expected: Math.round(p * (s.count - 1)) });
  }
  B.mapping = { samples: map, ok: map.every((m) => m.frame === m.expected) };
  // refresh midway restores a stable state
  await scrollToY(yR); const r1 = (await settle()).want; await send("Page.reload", {});
  for (let i = 0; i < 80; i++) { await sleep(100); if (await evaluate("document.readyState==='complete'")) break; }
  s = await settle(); const y2 = await evaluate("scrollY");
  B.refreshMidway = { restoredScroll: y2, frame: s.want, before: r1, ok: Math.abs(y2 - yR) < 4 && s.want === r1 && s.exact };
  // resize mid-sequence: one stage, one canvas, five markers at most
  for (const [w, h] of [[1100, 700], [1600, 1000], [1440, 900]]) { await setViewport({ ...v, w, h }); await sleep(250); }
  s = await settle();
  const counts = await evaluate("({ stages: document.querySelectorAll('.stage').length, canvases: document.querySelectorAll('canvas').length, dots: document.querySelectorAll('.dot').length })");
  B.resize = { counts, frame: s.want, exact: s.exact, ok: counts.stages === 1 && counts.canvases === 1 && counts.dots <= 5 && s.exact };
  // keyboard: first Tab lands on the skip link, Enter moves focus into proof
  await scrollToY(0); await settle(); await evaluate("document.activeElement && document.activeElement.blur(); true");
  const tabs = [];
  for (let i = 0; i < 14; i++) {
    await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 }); await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
    tabs.push(await evaluate(`(() => { const a = document.activeElement; const cs = getComputedStyle(a); return (a.textContent || a.getAttribute('aria-label') || a.tagName).trim().slice(0, 28) + (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) >= 2 ? ' [ring]' : ' [NO RING]'); })()`));
  }
  B.tabOrder = tabs;
  await evaluate("document.activeElement.blur(); true");
  await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 }); await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 }); await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
  await sleep(400);
  B.skipLink = await evaluate("({ focused: document.activeElement.id, proofTop: Math.round(document.getElementById('proof').getBoundingClientRect().top) })");
  // reduced motion: flip live in both directions
  await scrollToY(yR); await settle();
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] }); await sleep(500);
  const rm1 = await evaluate("({ tier: (document.documentElement.className.match(/tier-(\\w+)/)||[])[1], stage: getComputedStyle(document.querySelector('.stage')).display, figs: getComputedStyle(document.querySelector('#ch-heat .shot')).display })");
  await send("Emulation.setEmulatedMedia", { features: [] }); await sleep(800);
  s = await settle(); const rm2 = { tier: s.tier, frame: s.want, exact: s.exact };
  B.reducedMotionFlip = { toReduced: rm1, back: rm2, ok: rm1.tier === "reduced" && rm1.stage === "none" && rm1.figs !== "none" && rm2.tier === "desktop" && rm2.exact };
  // reduced motion at load: no sequence frame requested at all
  reqUrls.clear(); await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
  await load(PAGE, false); await sleep(1500);
  B.reducedAtLoad = { tier: await tierNow(), sequenceRequests: seqReqs() };
  await send("Emulation.setEmulatedMedia", { features: [] });
  // low power (2 logical cores) -> static
  await send("Emulation.setHardwareConcurrencyOverride", { hardwareConcurrency: 2 });
  await load(PAGE, false); B.lowPower = { tier: await tierNow() };
  await send("Emulation.setHardwareConcurrencyOverride", { hardwareConcurrency: 8 });
  // slow network: HTML + CTA first, poster before frames, never blank while scrubbing ahead of the downloads
  await send("Network.emulateNetworkConditions", { offline: false, latency: 300, downloadThroughput: 200000, uploadThroughput: 50000, connectionType: "cellular3g" });
  await send("Network.setCacheDisabled", { cacheDisabled: true });
  const t0 = Date.now(); await send("Page.navigate", { url: PAGE });
  let ctaAt = null; for (let i = 0; i < 200; i++) { await sleep(100); const ok = await evaluate("!!document.querySelector('#h-opening') && !!document.querySelector('.site-header .btn')").catch(() => false); if (ok) { ctaAt = Date.now() - t0; break; } }
  let posterAt = null; for (let i = 0; i < 200; i++) { const ok = await evaluate("(() => { const p = document.querySelector('.stage-poster'); return p.complete && p.naturalWidth > 0; })()").catch(() => false); if (ok) { posterAt = Date.now() - t0; break; } await sleep(100); }
  const samples = [];
  const ySlow = [await chapterY("ch-heat", 0.5), await chapterY("ch-rain", 0.7), await chapterY("ch-reassembly", 0.5)];
  for (const y of ySlow) { await scrollToY(y); for (let k = 0; k < 6; k++) { await sleep(250); const c = await checks(); const st2 = (await state()) || {}; samples.push({ blank: c.blank, booted: !!st2.tier, want: st2.want, drawn: st2.drawn, loaded: st2.loaded, inflight: st2.inflight || 0 }); } }
  B.slowNetwork = { htmlAndCtaMs: ctaAt, posterMs: posterAt, blankSamples: samples.filter((x) => x.blank).length, maxInflight: Math.max(...samples.map((x) => x.inflight)),
    last: samples[samples.length - 1], ok: samples.every((x) => !x.blank) && samples.every((x) => x.inflight <= 4) };
  await send("Network.setCacheDisabled", { cacheDisabled: false });
  await send("Network.emulateNetworkConditions", { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  // 2G -> static, nothing from the sequence
  await send("Network.emulateNetworkConditions", { offline: false, latency: 1800, downloadThroughput: 8000, uploadThroughput: 4000, connectionType: "cellular2g" });
  await send("Page.navigate", { url: "about:blank" }); await sleep(400);
  reqUrls.clear(); await send("Page.navigate", { url: PAGE }); await sleep(2500);
  B.network2g = { tier: await tierNow(), sequenceRequests: seqReqs() };
  await send("Network.emulateNetworkConditions", { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  // blocked CDN: GSAP missing, the same mapping runs on native scroll
  await send("Network.setBlockedURLs", { urls: ["*cdnjs.cloudflare.com*"] });
  await load(); await scrollToY(yR); s = await settle();
  B.blockedCdn = { gsap: s.gsap, frame: s.want, expected: r1, ok: !s.gsap && s.want === r1 && s.exact };
  await send("Network.setBlockedURLs", { urls: [] });
  // failed media: frames blocked; the full static story must be in place at the reader's place
  await send("Network.setBlockedURLs", { urls: ["*/media/hf/*"] });
  await load(PAGE, false); await scrollToY(yR); await sleep(3000);
  B.failedMedia = await evaluate("({ tier: (document.documentElement.className.match(/tier-(\\w+)/)||[])[1], failed: document.documentElement.classList.contains('media-failed'), stage: getComputedStyle(document.querySelector('.stage')).display, heatFigure: getComputedStyle(document.querySelector('#ch-heat .shot')).display, scroll: scrollY })");
  await send("Network.setBlockedURLs", { urls: [] });
  // touch + mobile: swipe with touch input, rotate to landscape (static) and back
  const m = VIEWPORTS[5]; await setViewport(m); await load();
  await send("Input.synthesizeScrollGesture", { x: 195, y: 650, yDistance: -900, speed: 1200, gestureSourceType: "touch" }, 60000);
  s = await settle(); B.touchSwipe = { tier: s.tier, kind: s.kind, frame: s.want, scroll: await evaluate("scrollY"), ok: s.tier === "mobile" && s.kind === "mobile" && s.want > 0 };
  await setViewport({ ...m, w: 844, h: 390 }); await sleep(600);
  const land = await evaluate("({ tier: (document.documentElement.className.match(/tier-(\\w+)/)||[])[1], overflow: document.documentElement.scrollWidth - innerWidth })");
  await setViewport(m); await sleep(800); s = await settle();
  B.rotation = { landscape: land, backToPortrait: { tier: s.tier, frame: s.want, exact: s.exact }, ok: land.tier === "static" && s.tier === "mobile" && s.exact };
  report.behaviour = B; report.console = [...issues.console]; report.failed = [...issues.failed];
  console.log(JSON.stringify(B, null, 1));
}

async function runPerf() {
  const P = {};
  for (const [name, v, cpu] of [["desktop-1440", VIEWPORTS[0], 1], ["mobile-390-cpu4x", VIEWPORTS[5], 4]]) {
    await setViewport(v); await send("Emulation.setCPUThrottlingRate", { rate: cpu }); await load();
    await evaluate(`window.__fr = []; (function loop(t){ window.__fr.push(t); window.__frId = requestAnimationFrame(loop); })(performance.now()); true`);
    const dist = await evaluate("document.getElementById('ch-reassembly').getBoundingClientRect().bottom + scrollY - innerHeight");
    await send("Input.synthesizeScrollGesture", { x: Math.round(v.w / 2), y: Math.round(v.h * 0.6), yDistance: -Math.round(dist), speed: 1400, gestureSourceType: v.mobile ? "touch" : "mouse" }, 120000);
    const fr = await evaluate("cancelAnimationFrame(window.__frId); window.__fr");
    const d = fr.slice(1).map((t, i) => t - fr[i]).filter((x) => x > 0);
    const sorted = [...d].sort((a, b) => a - b), q = (p) => sorted[Math.floor(p * (sorted.length - 1))];
    // memory stays flat: only the decode window is held as bitmaps
    await sleep(1500); const s = await state();
    P[name] = { frames: d.length, medianMs: +q(0.5).toFixed(2), p95Ms: +q(0.95).toFixed(2), fpsMedian: +(1000 / q(0.5)).toFixed(1), over50ms: d.filter((x) => x > 50).length,
      decodedBitmaps: s.decoded, exactAtEnd: s.exact, heapMB: +((await evaluate("performance.memory ? performance.memory.usedJSHeapSize : 0")) / 1048576).toFixed(1) };
    await send("Emulation.setCPUThrottlingRate", { rate: 1 });
  }
  // offscreen: below the sequence, scrolling must not wake the engine
  await setViewport(VIEWPORTS[0]); await load();
  await evaluate("document.getElementById('estimate').scrollIntoView(); true"); await sleep(400);
  await evaluate("window.scrollBy(0, -120); true"); await sleep(300);
  P.offscreen = { inSeqClass: await evaluate("document.documentElement.classList.contains('in-seq')") };
  P.payload = await evaluate(`performance.getEntriesByType('resource').reduce((a, e) => { const k = e.name.split('/').pop().split('?')[0]; a[k] = (a[k] || 0) + (e.encodedBodySize || e.transferSize || 0); return a; }, {})`);
  report.perf = P; console.log(JSON.stringify(P, null, 1));
}

async function runProbe() {
  // below the sequence no chapter card may show (desktop cards are position: fixed)
  await setViewport(VIEWPORTS[0]); await load();
  const out = [];
  for (const id of ["proof", "final", "estimate"]) {
    await evaluate(`document.getElementById('${id}').scrollIntoView(); true`);
    for (const ms of [100, 400, 1200]) {
      await sleep(ms);
      out.push({ id, ms, ...(await evaluate(`({ inSeq: document.documentElement.classList.contains('in-seq'),
        visibleCards: [...document.querySelectorAll('.chapter .card')].filter(c => parseFloat(getComputedStyle(c).opacity) > 0.05).length })`)) });
    }
  }
  await evaluate("window.scrollBy(0, -120); true"); await sleep(600);
  out.push({ id: "estimate-120", ...(await evaluate(`({ inSeq: document.documentElement.classList.contains('in-seq'), visibleCards: [...document.querySelectorAll('.chapter .card')].filter(c => parseFloat(getComputedStyle(c).opacity) > 0.05).length })`)) });
  out.push(await evaluate(`(() => { const t = ScrollTrigger.getAll()[0]; const c = [...document.querySelectorAll('.chapter .card')].find(c => parseFloat(getComputedStyle(c).opacity) > 0.05);
    const r = c && c.getBoundingClientRect();
    return { scrollY, start: t.start, end: t.end, active: t.isActive, progress: t.progress, cls: document.documentElement.className, card: c && c.closest('.chapter').id, rect: r && [r.left, r.top, r.width, r.height], op: c && getComputedStyle(c).opacity, vis: c && getComputedStyle(c).visibility }; })()`));
  await shot(path.join(process.env.QA_OUT || REPORT_DIR, "probe-estimate.jpg"));
  report.probe = out; console.log(JSON.stringify(out));
}

try {
  if (MODE === "probe") await runProbe();
  else if (MODE === "shots") await runShots();
  else if (MODE === "behaviour") await runBehaviour();
  else if (MODE === "perf") await runPerf();
} catch (e) { console.error("QA error:", e.message, e.stack.split("\n")[1]); report.error = e.message; if (report.behaviour) console.log(JSON.stringify(report.behaviour, null, 1)); }
fs.writeFileSync(path.join(REPORT_DIR, `report-${MODE}.json`), JSON.stringify(report, null, 1));
ws.close(); chrome.kill(); server.close();
try { fs.rmSync(profile, { recursive: true, force: true }); } catch {}
process.exit(0);
