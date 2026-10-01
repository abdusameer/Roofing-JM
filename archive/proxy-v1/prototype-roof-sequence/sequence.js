/* JM Roofing concept · roof-sequence engine (Phase 1 vertical slice)
   Native scroll drives one prerendered clip. Nothing autoplays; when scrolling stops, the
   picture stops. All words live in the HTML chapters; the stage only illustrates them. */
(() => {
  "use strict";
  const html = document.documentElement;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const FPS = 30;
  const META = JSON.parse(($("#roof-meta") || {}).textContent || "{}");
  const STILLS = META.stills || {};
  const BG = META.bg || {};

  const seq = $("#sequence"), stage = $(".stage"), frameBox = $(".stage .frame");
  const still = $(".stage-still"), video = $(".stage-video");
  const ovHost = $(".stage .ovs"), labHost = $(".stage .labels"), illus = $(".stage .note-illus"), chip = $(".stage .cond-chip");
  const CONDS = [["heat", 165, 196, "Heat"], ["wind", 196, 226, "Wind"], ["rain", 226, 280, "Rain"]];
  const chapters = $$(".chapter").map((el) => ({ el, id: el.dataset.ch, f0: +el.dataset.f0, f1: +el.dataset.f1, top: 0, h: 0, hold: 0 }));
  const rail = $$(".rail a[href^='#ch-']");

  // Labels: one short HTML label per layer or job, tied to the frames where its object is on screen.
  // m: 1 = also shown on phones (fewer simultaneous labels there).
  const LABELS = [
    { a: "caps", t: "Hip & ridge caps", from: 26, to: 72, m: 1 },
    { a: "shingles", t: "Laminated shingles", from: 44, to: 88, m: 1 },
    { a: "underlay", t: "Underlayment", from: 62, to: 100, m: 1 },
    { a: "drip", t: "Drip edge", from: 78, to: 112, m: 1 },
    { a: "deck", t: "Roof deck", from: 94, to: 124, m: 1 },
    { a: "attic", t: "Attic air: soffit in, ridge out", from: 100, to: 126, m: 0 },
    { a: "insulation", t: "Ceiling insulation (context)", from: 104, to: 126, m: 0 },
    { a: "panel", t: "The proof panel: every layer", from: 126, to: 162, m: 1 },
    { a: "p_granule", t: "Reflective granules", from: 168, to: 196, m: 1 },
    { a: "p_seal_b", t: "Sealant bonds in the sun", from: 174, to: 197, m: 1 },
    { a: "p_up", t: "Attic air carries heat out", from: 180, to: 197, m: 0, side: "l" },
    { a: "p_seal_b", t: "Sealed courses stay flat", from: 198, to: 226, m: 1 },
    { a: "p_nail_b", t: "Nails, under the next course", from: 203, to: 226, m: 1 },
    { a: "p_starter", t: "Starter course seals the eave", from: 208, to: 226, m: 0 },
    { a: "p_center", t: "Each course laps the one below", from: 228, to: 262, m: 1, side: "l" },
    { a: "p_boot", t: "Boot sheds water past the pipe", from: 234, to: 266, m: 0 },
    { a: "p_band_under", t: "Underlayment: the second layer", from: 242, to: 270, m: 0, side: "l" },
    { a: "p_gutter_b", t: "Drip edge into the gutter", from: 248, to: 278, m: 1 },
    { a: "panel", t: "Back to the exact spot", from: 318, to: 342, m: 1 },
    { a: "lock", t: "Final ridge cap locks", from: 389, to: 407, m: 1, cls: "lock" },
  ];
  // overlay windows: [draw from, draw to, fade-out end]
  const OVERLAYS = { anatomy: [98, 112, 124], heat: [165, 195, 197], wind: [195, 225, 227], rain: [225, 262, 280] };

  let tier = null, orient = null, anchors = null, anchorCache = {}, active = false;
  let target = 0, shown = 0, raf = null, lastT = 0, visible = true, mediaFailed = false;
  let videoReady = false, seeking = false, pendingT = null, lastFrame = -1, stallTimer = 0;
  let labels = [], overlays = [], curStill = "", curBg = "", curRail = -1, box = { w: 1, h: 1, vx0: 0, vx1: 1, vy0: 0, vy1: 1 };
  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);

  /* ---------------------------------------------------------------- tiers */
  const pick = () => (window.__roofTier ? window.__roofTier() : "static");
  function setTier(next, keepContext) {
    if (mediaFailed && (next === "desktop" || next === "mobile")) next = "static";
    if (next === tier) return;
    const anchorEl = keepContext ? currentChapterEl() : null;
    html.classList.remove("tier-" + tier);
    html.classList.add("tier-" + next);
    tier = next;
    if (next === "desktop" || next === "mobile") startMotion(); else stopMotion();
    if (anchorEl) anchorEl.scrollIntoView({ block: "start" });
  }
  function currentChapterEl() {
    const y = window.scrollY + window.innerHeight * 0.4;
    let el = null;
    for (const c of chapters) if (c.el.getBoundingClientRect().top + window.scrollY <= y) el = c.el;
    return el && window.scrollY > 0 ? el : null;
  }
  ["(prefers-reduced-motion: reduce)", "(min-width: 1024px)", "(min-height: 600px)", "(pointer: coarse)",
   "(orientation: landscape) and (pointer: coarse) and (max-height: 540px)"].forEach((q) => {
    const m = window.matchMedia(q);
    (m.addEventListener ? m.addEventListener("change", onGate) : m.addListener(onGate));
  });
  function onGate() { setTier(pick(), true); }

  /* ---------------------------------------------------------------- motion lifecycle */
  function startMotion() {
    active = true;
    orient = tier === "desktop" ? "desktop" : "portrait";
    const pic = still.parentElement;
    if (pic && pic.tagName === "PICTURE") $$("source", pic).forEach((s) => s.remove());
    curStill = ""; curBg = ""; lastFrame = -1; videoReady = false; seeking = false; pendingT = null;
    stage.classList.remove("video-live");
    buildOverlays();
    measure();
    target = shown = computeTarget().frame;
    render(true);
    loadAnchors(orient).then((A) => { if (orient === A.camera) { anchors = A; buildLabels(); render(true); } }).catch(() => {});
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize);
    io.observe(seq);
    scheduleVideo();
  }
  function stopMotion() {
    active = false;
    window.removeEventListener("scroll", onScroll);
    window.removeEventListener("resize", onResize);
    io.disconnect();
    if (raf) cancelAnimationFrame(raf); raf = null;
    clearTimeout(stallTimer);
    unloadVideo();
    ovHost.textContent = ""; labHost.textContent = ""; labels = []; overlays = [];
    html.classList.remove("in-seq");
    chip.classList.remove("on"); chip.dataset.c = ""; illus.classList.remove("on");
    rail.forEach((a) => a.removeAttribute("aria-current"));
  }

  const ioLoop = new IntersectionObserver((entries) => {
    for (const e of entries) { visible = e.isIntersecting; if (visible) kick(); else if (raf) { cancelAnimationFrame(raf); raf = null; } }
  });
  const ioMid = new IntersectionObserver((entries) => {
    for (const e of entries) html.classList.toggle("in-seq", e.isIntersecting);
  }, { rootMargin: "-45% 0px -45% 0px" });
  const io = { observe: (el) => { ioLoop.observe(el); ioMid.observe(el); }, disconnect: () => { ioLoop.disconnect(); ioMid.disconnect(); } };

  /* ---------------------------------------------------------------- geometry */
  function measure() {
    const vh = window.innerHeight;
    for (const c of chapters) {
      const r = c.el.getBoundingClientRect();
      c.top = r.top + window.scrollY; c.h = c.el.offsetHeight;
      const hold = parseFloat(getComputedStyle(c.el).getPropertyValue("--hold")) || 0;
      c.hold = tier === "desktop" ? (hold * vh) / 100 : 0;
    }
    const fb = frameBox.getBoundingClientRect(), sb = stage.getBoundingClientRect();
    // usable label area, in stage coordinates (independent of scroll): the pinned stage minus the
    // sticky header (desktop overlaps it), the text column and the chapter rail
    const ox = fb.left - sb.left, oy = fb.top - sb.top;
    let xl = 0, xr = sb.width, yt = 0;
    if (tier === "desktop") {
      yt = $(".site-header").offsetHeight + 6;
      xr = sb.width - 80;
      for (const c of chapters) { const cr = c.el.querySelector(".card"); if (cr) xl = Math.max(xl, cr.getBoundingClientRect().right - sb.left + 10); }
    }
    box = { w: fb.width, h: fb.height, vx0: xl - ox, vx1: xr - ox, vy0: yt - oy, vy1: sb.height - oy };
    for (const L of labels) L.wid = L.span.offsetWidth;
  }
  function trigger() { return window.innerHeight * (tier === "desktop" ? 0.5 : 0.74); }
  function computeTarget() {
    const y = window.scrollY + trigger();
    let i = 0;
    for (let k = 0; k < chapters.length; k++) if (y >= chapters[k].top) i = k;
    const c = chapters[i];
    const span = Math.max(1, c.h - c.hold);
    const p = clamp((y - c.top) / span, 0, 1);
    return { i, p, frame: c.f0 + (c.f1 - c.f0) * p };
  }

  /* ---------------------------------------------------------------- loop (runs only while converging) */
  function onScroll() { const t = computeTarget(); target = t.frame; setRail(t.i); kick(); }
  let resizeQueued = false;
  function onResize() {
    if (resizeQueued) return; resizeQueued = true;
    requestAnimationFrame(() => { resizeQueued = false; if (!active) return; measure(); target = computeTarget().frame; render(true); });
  }
  function kick() { if (raf == null && active && visible) raf = requestAnimationFrame(tick); }
  function tick(now) {
    raf = null;
    const dt = Math.min(100, now - (lastT || now)); lastT = now;
    const k = 1 - Math.pow(1 - 0.22, dt / 16.667);
    shown += (target - shown) * k;
    if (Math.abs(target - shown) < 0.04) shown = target;
    render(false);
    if (shown !== target) kick(); else lastT = 0;
  }

  /* ---------------------------------------------------------------- render */
  function render(force) {
    const f = clamp(shown, 0, 405);
    const fr = Math.round(f);
    // picture: the clip when it is live, otherwise the nearest rendered still (stepped fallback)
    if (videoReady && (fr !== lastFrame || force)) {
      lastFrame = fr;
      const t = (fr + 0.25) / FPS;
      // never show a stale frame: until this part of the clip has downloaded, the matching still shows
      const ok = buffered(t);
      if (!ok && stage.classList.contains("video-live")) stage.classList.remove("video-live");
      if (ok) seek(t);
    }
    const name = nearestStill(f);
    if (name !== curStill) { curStill = name; still.src = `media/stills-${orient}/${name}.webp`; }
    const bg = (BG[orient] || {})[name];
    if (bg && bg !== curBg) { curBg = bg; stage.style.setProperty("--stage-bg", bg); }
    illus.classList.toggle("on", f >= 120 && f <= 326);
    const cond = CONDS.find((c) => f >= c[1] && f < c[2]);
    const cid = cond ? cond[0] : "";
    if (cid !== chip.dataset.c) { chip.dataset.c = cid; chip.classList.toggle("on", !!cond); if (cond) chip.lastChild.textContent = cond[3]; }
    for (const o of overlays) {
      const [a, b, c] = OVERLAYS[o.id];
      const on = f >= a - 0.5 && f <= c;
      if (on !== o.on) { o.on = on; o.el.classList.toggle("on", on); }
      if (!on) continue;
      const p = clamp((f - a) / (b - a), 0, 1);
      const op = f <= b ? 1 : clamp(1 - (f - b) / Math.max(1, c - b), 0, 1);
      const ps = p.toFixed(3), os = op.toFixed(2);
      if (ps !== o.p) { o.p = ps; o.el.style.setProperty("--p", ps); }
      if (os !== o.op) { o.op = os; o.el.style.opacity = os; }
    }
    if (anchors) { for (const L of labels) placeLabel(L, f); declutter(); }
  }
  // labels never stack on top of each other: phones show only the newest, desktop nudges text boxes apart
  function declutter() {
    const vis = labels.filter((L) => L.op && L.op !== "0" && (tier !== "mobile" || L.m));
    if (tier === "mobile") {
      const newest = vis.reduce((a, L) => (!a || L.from > a.from ? L : a), null);
      for (const L of vis) if (L !== newest) { L.op = "0"; L.el.style.opacity = "0"; }
      return;
    }
    const boxes = vis.map((L) => {
      const x0 = L.side === "r" ? L.x + 34 : L.side === "l" ? L.x - 34 - L.wid : L.x - L.wid / 2;
      return { L, x0, x1: x0 + L.wid, y: L.y };
    }).sort((a, b) => a.y - b.y);
    const placed = [];
    for (const b of boxes) {
      let dy = 0;
      for (const p of placed) if (b.x0 < p.x1 + 6 && b.x1 > p.x0 - 6 && Math.abs(b.y + dy - (p.y + p.dy)) < 30) dy = p.y + p.dy + 30 - b.y;
      b.dy = dy; placed.push(b);
      const v = dy + "px";
      if (v !== b.L.dyv) { b.L.dyv = v; b.L.el.style.setProperty("--dy", v); }
    }
  }
  function nearestStill(f) {
    const s = STILLS[orient] || {};
    let best = "opening", d = 1e9;
    for (const k in s) { const dd = Math.abs(s[k] - f); if (dd < d) { d = dd; best = k; } }
    return best;
  }
  function setRail(i) {
    if (i === curRail) return; curRail = i;
    rail.forEach((a, k) => (k === i ? a.setAttribute("aria-current", "step") : a.removeAttribute("aria-current")));
  }

  /* ---------------------------------------------------------------- labels */
  function anchorAt(name, f) {
    const d = anchors.anchors[name]; if (!d) return null;
    if (d.from === d.to) return [d.xy[0], d.xy[1]];
    const x = clamp(f, d.from, d.to) - d.from, i = Math.floor(x), t = x - i, n = d.xy.length / 2 - 1;
    const i0 = Math.min(i, n), i1 = Math.min(i + 1, n);
    return [d.xy[i0 * 2] + (d.xy[i1 * 2] - d.xy[i0 * 2]) * t, d.xy[i0 * 2 + 1] + (d.xy[i1 * 2 + 1] - d.xy[i0 * 2 + 1]) * t];
  }
  function buildLabels() {
    labHost.textContent = ""; labels = [];
    for (const cfg of LABELS) {
      if (!anchors.anchors[cfg.a]) continue;
      const el = document.createElement("div");
      el.className = "lab " + (cfg.side || "r") + (cfg.cls ? " " + cfg.cls : "");
      el.dataset.m = String(cfg.m);
      el.innerHTML = "<i></i><span></span>";
      el.lastChild.textContent = cfg.t;
      labHost.appendChild(el);
      labels.push({ ...cfg, el, span: el.lastChild, wid: 0, side0: cfg.side || "r", tx: "", op: "" });
    }
    for (const L of labels) L.wid = L.span.offsetWidth;
  }
  function placeLabel(L, f) {
    if (tier === "mobile" && !L.m) return;
    const fade = 4;
    let op = 0;
    if (f >= L.from && f <= L.to) op = Math.min(1, (f - L.from) / fade, (L.to - f) / fade);
    const p = op > 0 ? anchorAt(L.a, f) : null;
    const x = p ? p[0] * box.w : 0, y = p ? p[1] * box.h : 0;
    const pad = tier === "desktop" ? 12 : 8;
    // the dot always sits on its true anchor; if that point is hidden (under the text column,
    // header or off-stage) the label is not shown rather than pointing at the wrong thing
    if (!p || x < box.vx0 + pad || x > box.vx1 - pad || y < box.vy0 + 16 || y > box.vy1 - 16) op = 0;
    const ops = op <= 0 ? "0" : op.toFixed(2);
    if (ops !== L.op) { L.op = ops; L.el.style.opacity = ops; }
    if (op <= 0) return;
    // keep text inside the visible stage: preferred side, else the other side, else centred under the dot
    const reach = (tier === "desktop" ? 34 : 22) + L.wid + pad;
    const fitsR = x + reach <= box.vx1, fitsL = x - reach >= box.vx0;
    let side = L.side0 === "l" ? (fitsL ? "l" : fitsR ? "r" : "b") : (fitsR ? "r" : fitsL ? "l" : "b");
    if (side !== L.side) { L.side = side; for (const k of ["r", "l", "b"]) L.el.classList.toggle(k, side === k); }
    if (side === "b") {
      const half = L.wid / 2, dx = Math.round(clamp(x, box.vx0 + pad + half, box.vx1 - pad - half) - x);
      if (dx !== L.dx) { L.dx = dx; L.el.style.setProperty("--dx", dx + "px"); }
    }
    L.x = x; L.y = y;
    const tx = `translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0)`;
    if (tx !== L.tx) { L.tx = tx; L.el.style.transform = tx; }
  }

  /* ---------------------------------------------------------------- overlays (cloned from the static figures) */
  function buildOverlays() {
    ovHost.textContent = ""; overlays = [];
    const key = orient === "desktop" ? ".f-desk" : ".f-port";
    for (const svg of $$(`.chapter ${key} svg.ov`)) {
      const c = svg.cloneNode(true);
      c.classList.remove("on"); c.style.setProperty("--p", "0");
      ovHost.appendChild(c);
      overlays.push({ id: c.dataset.ov, el: c, on: false, p: "", op: "" });
    }
  }

  /* ---------------------------------------------------------------- data + media */
  function loadAnchors(cam) {
    if (anchorCache[cam]) return Promise.resolve(anchorCache[cam]);
    return fetch(`media/anchors-${cam}.json`).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then((A) => (anchorCache[cam] = A));
  }
  function scheduleVideo() {
    const go = () => { if (active) loadVideo(); };
    const idle = () => ("requestIdleCallback" in window ? requestIdleCallback(go, { timeout: 1500 }) : setTimeout(go, 600));
    if (document.readyState === "complete") idle(); else window.addEventListener("load", idle, { once: true });
  }
  function loadVideo() {
    video.addEventListener("loadeddata", onVideoReady);
    video.addEventListener("seeked", onSeeked);
    video.addEventListener("error", onVideoError);
    video.preload = "auto";
    video.src = `media/sequence-${orient}.mp4`;
    video.load();
    // a slow network keeps the stepped stills; the clip takes over whenever it arrives
    clearTimeout(stallTimer);
    stallTimer = setTimeout(() => { if (!videoReady) html.classList.add("video-slow"); }, 8000);
  }
  function unloadVideo() {
    video.removeEventListener("loadeddata", onVideoReady);
    video.removeEventListener("seeked", onSeeked);
    video.removeEventListener("error", onVideoError);
    if (video.getAttribute("src")) { video.removeAttribute("src"); video.load(); }
    videoReady = false; stage.classList.remove("video-live");
  }
  function onVideoReady() { videoReady = true; html.classList.remove("video-slow"); lastFrame = -1; render(true); }
  function onSeeked() {
    seeking = false;
    if (videoReady && !stage.classList.contains("video-live")) stage.classList.add("video-live");
    if (pendingT != null) { const t = pendingT; pendingT = null; seek(t); }
  }
  function buffered(t) {
    const b = video.buffered;
    for (let i = 0; i < b.length; i++) if (t >= b.start(i) && t <= b.end(i)) return true;
    return false;
  }
  video.addEventListener("progress", () => { if (videoReady && !stage.classList.contains("video-live")) { lastFrame = -1; render(true); } });
  function seek(t) {
    if (seeking) { pendingT = t; return; }
    if (Math.abs(video.currentTime - t) < 0.5 / FPS && stage.classList.contains("video-live")) return;
    seeking = true;
    try { video.currentTime = t; } catch (e) { seeking = false; }
  }
  function onVideoError() {
    // failed media: fall back to the complete static story, keeping the reader's place
    mediaFailed = true;
    html.classList.add("media-failed");
    setTier("static", true);
  }

  /* ---------------------------------------------------------------- inert concept form */
  const form = $("#estimate form");
  if (form) form.addEventListener("submit", (e) => {
    e.preventDefault();
    const st = $(".status", form);
    const missing = $$("[required]", form).filter((i) => !i.value.trim());
    st.textContent = missing.length
      ? "Concept preview: add your name, phone and ZIP to see the confirmation. Nothing is sent."
      : "Concept preview: nothing was sent. In the finished site this request would go to JM Roofing.";
  });

  /* ---------------------------------------------------------------- boot */
  const initial = (html.className.match(/tier-(\w+)/) || [])[1] || pick();
  html.classList.remove("tier-" + initial);
  setTier(initial, false);
  window.addEventListener("pageshow", () => { if (active) { measure(); target = shown = computeTarget().frame; render(true); } });
  window.addEventListener("load", () => { if (active) { measure(); target = computeTarget().frame; kick(); } });
  // test hook (QA only reads state; it never drives the experience)
  window.__roofState = () => ({ tier, orient, shown, target, videoReady, seeking, live: stage.classList.contains("video-live"), still: curStill, raf: raf != null, labels: labels.filter((l) => l.op && l.op !== "0").map((l) => l.t), overlays: overlays.filter((o) => o.on).map((o) => o.id) });
})();
