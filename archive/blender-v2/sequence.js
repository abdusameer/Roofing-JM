/* JM Roofing concept · roof-sequence engine (Phase 1, photoreal rework)
   One canvas, one prerendered WebP image sequence. GSAP ScrollTrigger (scrub: true) maps scroll
   progress straight to a frame number: frame = round(progress × (count − 1)). Scrolling back plays
   it backwards. Nothing autoplays. Every word lives in the HTML chapters; the canvas only shows them.
   Loading: poster → first chapter → keyframes → the rest in bounded groups nearest the reader.
   Only a small window of frames around the current one stays decoded, so memory stays flat, and
   the canvas always shows the nearest frame that is ready (it is never blank). */
(() => {
  "use strict";
  const html = document.documentElement;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);

  const seq = $("#sequence"), stage = $(".stage"), frameBox = $(".stage .frame");
  const canvas = $(".stage-canvas"), poster = $(".stage-poster");
  const dotsHost = $(".stage .dots"), illus = $(".stage .note-illus"), chip = $(".stage .cond-chip");
  const ctx = canvas.getContext("2d", { alpha: false });
  const chapters = $$(".chapter").map((el) => ({ el, id: el.dataset.ch, f0: +el.dataset.f0, f1: +el.dataset.f1 }));
  const rail = $$(".rail a[href^='#ch-']");
  const MANIFEST = "media/seq/manifest.json";

  // budgets: parallel downloads, frames per group, decoded frames kept either side of the current one
  const LIMITS = { desktop: { conc: 4, group: 12, win: 10 }, portrait: { conc: 3, group: 10, win: 7 } };

  let tier = null, kind = null, M = null, S = null, active = false, failed = false, gen = 0;
  let blobs = [], bitmaps = new Map(), decoding = new Map(), queue = [], inflight = 0, errors = 0;
  let want = 0, drawn = -1, drawnExact = false, st = null, nativeScroll = false, dots = [], master = 0, fallback = -1;

  /* ---------------------------------------------------------------- tiers */
  const pick = () => (window.__roofTier ? window.__roofTier() : "static");
  function setTier(next, keepContext) {
    if (failed && (next === "desktop" || next === "mobile")) next = "static";
    if (next === tier) return;
    const anchorEl = keepContext ? currentChapterEl() : null;
    html.classList.remove("tier-" + tier);
    html.classList.add("tier-" + next);
    tier = next;
    stopMotion();
    if (next === "desktop" || next === "mobile") startMotion();
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

  /* ---------------------------------------------------------------- lifecycle */
  function startMotion() {
    active = true; gen++;
    kind = tier === "desktop" ? "desktop" : "portrait";
    const src = `media/stills/${kind}/poster.webp`;
    if (poster.getAttribute("src") !== src) poster.src = src;
    canvas.classList.remove("live");
    const my = gen;
    loadManifest().then((man) => {
      if (my !== gen) return;
      M = man; S = M.sequences[kind];
      canvas.width = S.width; canvas.height = S.height;
      blobs = new Array(S.count).fill(null);
      buildDots();
      bindScroll();
      want = frameFor(progressNow());
      planLoads();
      pump();
      render();
    }).catch(() => { if (my === gen) fail(); });
  }
  function stopMotion() {
    active = false; gen++;
    if (st) { if (st.scrollTrigger) st.scrollTrigger.kill(); st.kill(); st = null; }
    if (nativeScroll) { window.removeEventListener("scroll", onNativeScroll); window.removeEventListener("resize", onNativeScroll); nativeScroll = false; }
    window.removeEventListener("scroll", onSeqBounds); window.removeEventListener("resize", onSeqBounds);
    for (const b of bitmaps.values()) if (b.close) b.close();
    bitmaps.clear(); decoding.clear(); blobs = []; queue = []; inflight = 0; drawn = -1; drawnExact = false; S = null; fallback = -1;
    dotsHost.textContent = ""; dots = [];
    html.classList.remove("in-seq");
    chip.classList.remove("on"); chip.dataset.c = ""; curCond = ""; curRail = -1; illus.classList.remove("on");
    rail.forEach((a) => a.removeAttribute("aria-current"));
    chapters.forEach((c) => c.el.classList.remove("is-active"));
  }
  function fail() {
    // missing media: the complete static story, keeping the reader's place
    failed = true; html.classList.add("media-failed");
    setTier("static", true);
  }
  let manifestP = null;
  function loadManifest() {
    if (!manifestP) {
      manifestP = fetch(MANIFEST).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
      manifestP.catch(() => (manifestP = null));
    }
    return manifestP;
  }

  /* ---------------------------------------------------------------- scroll → frame */
  const frameFor = (p) => Math.round(clamp(p, 0, 1) * (S.count - 1));
  function progressNow() {
    const r = seq.getBoundingClientRect(), span = seq.offsetHeight - window.innerHeight;
    return span > 0 ? clamp(-r.top / span, 0, 1) : 0;
  }
  function bindScroll() {
    const g = window.gsap, ST = window.ScrollTrigger;
    if (g && ST) {
      g.registerPlugin(ST);
      const state = { f: 0 };
      st = g.to(state, {
        f: S.count - 1, ease: "none",
        scrollTrigger: { trigger: seq, start: "top top", end: "bottom bottom", scrub: true, invalidateOnRefresh: true },
        onUpdate: () => setFrame(Math.round(state.f)),
      });
    } else {
      // the CDN can be blocked: the same linear mapping on native scroll
      nativeScroll = true;
      window.addEventListener("scroll", onNativeScroll, { passive: true });
      window.addEventListener("resize", onNativeScroll);
    }
    window.addEventListener("scroll", onSeqBounds, { passive: true });
    window.addEventListener("resize", onSeqBounds);
    updateInSeq();
  }
  // "in the sequence" = the sequence covers the middle of the viewport: drives the rail, the fixed desktop cards
  // and the phone skip link. Geometric, so it holds for any jump, either engine path, and the first paint.
  function updateInSeq() {
    const r = seq.getBoundingClientRect(), mid = window.innerHeight / 2;
    html.classList.toggle("in-seq", active && r.top < mid && r.bottom > mid);
  }
  let boundsQueued = false;
  function onSeqBounds() {
    if (boundsQueued) return; boundsQueued = true;
    requestAnimationFrame(() => { boundsQueued = false; updateInSeq(); });
  }
  let nativeQueued = false;
  function onNativeScroll() {
    if (nativeQueued) return; nativeQueued = true;
    requestAnimationFrame(() => {
      nativeQueued = false; if (!active || !S) return;
      setFrame(frameFor(progressNow()));
    });
  }
  function setFrame(f) {
    if (!S) return;
    f = clamp(f, 0, S.count - 1);
    if (f === want && drawnExact) return;
    want = f;
    requestDecodeWindow();
    render();
  }

  /* ---------------------------------------------------------------- loading */
  function planLoads() {
    // first chapter, then the keyframes (so any jump has a near frame), then groups nearest the reader
    const seen = new Set(), order = [];
    const add = (i) => { if (i >= 0 && i < S.count && !seen.has(i)) { seen.add(i); order.push(i); } };
    for (let i = 0; i < S.first; i++) add(i);
    for (const k of S.keyframes) add(k);
    queue = order;
    refill();
  }
  function refill() {
    const L = LIMITS[kind], seen = new Set(queue), groups = [];
    for (let g = 0; g < S.count; g += L.group) groups.push(g);
    groups.sort((a, b) => Math.abs(a + L.group / 2 - want) - Math.abs(b + L.group / 2 - want));
    for (const g of groups) for (let i = g; i < Math.min(S.count, g + L.group); i++) if (!blobs[i] && !seen.has(i)) { seen.add(i); queue.push(i); }
  }
  function pump() {
    const L = LIMITS[kind], my = gen;
    while (active && inflight < L.conc && queue.length) {
      const i = queue.shift();
      if (blobs[i]) continue;
      inflight++;
      fetch(url(i)).then((r) => { if (!r.ok) throw new Error(r.status); return r.blob(); }).then((b) => {
        if (my !== gen) return;
        blobs[i] = b;
        if (Math.abs(i - want) <= L.win) decode(i); else if (!drawnExact) render();
      }).catch(() => {
        if (my !== gen) return;
        if (++errors > 6) fail(); else queue.push(i);
      }).finally(() => {
        if (my !== gen) return;
        inflight--;
        pump();
      });
    }
  }
  const url = (i) => S.path.replace("{i}", String(i).padStart(S.pad, "0"));
  function decode(i) {
    if (i < 0 || i >= S.count || bitmaps.has(i) || decoding.has(i) || !blobs[i]) return;
    const my = gen;
    const p = (window.createImageBitmap ? createImageBitmap(blobs[i]) : imgDecode(blobs[i])).then((bmp) => {
      decoding.delete(i);
      if (my !== gen) { if (bmp.close) bmp.close(); return; }
      bitmaps.set(i, bmp);
      evict();
      if (!drawnExact) render();
    }).catch(() => decoding.delete(i));
    decoding.set(i, p);
  }
  function imgDecode(blob) {
    const im = new Image(), u = URL.createObjectURL(blob);
    im.src = u;
    return im.decode().then(() => { URL.revokeObjectURL(u); return im; });
  }
  function requestDecodeWindow() {
    const L = LIMITS[kind];
    decode(want);
    for (let d = 1; d <= L.win; d++) { decode(want + d); decode(want - d); }
  }
  function evict() {
    const keep = LIMITS[kind].win * 2;
    for (const [i, b] of bitmaps) if (Math.abs(i - want) > keep && i !== drawn && i !== fallback) { if (b.close) b.close(); bitmaps.delete(i); }
  }

  /* ---------------------------------------------------------------- render */
  function nearestReady(f) {
    if (bitmaps.has(f)) return f;
    for (let d = 1; d < S.count; d++) {
      if (bitmaps.has(f - d)) return f - d;
      if (bitmaps.has(f + d)) return f + d;
    }
    return -1;
  }
  // nearest downloaded frame at any distance: the stand-in while the reader is ahead of the downloads
  function nearestLoaded(f) {
    for (let d = 0; d < S.count; d++) { if (blobs[f - d]) return f - d; if (blobs[f + d]) return f + d; }
    return -1;
  }
  function render() {
    if (!active || !S) return;
    const i = nearestReady(want);
    if (i !== want) {
      const j = nearestLoaded(want);
      if (j >= 0 && j !== i && (i < 0 || Math.abs(j - want) < Math.abs(i - want))) { fallback = j; decode(j); }
    }
    if (i >= 0 && i !== drawn) {
      ctx.drawImage(bitmaps.get(i), 0, 0, S.width, S.height);
      drawn = i;
      if (!canvas.classList.contains("live")) canvas.classList.add("live");   // the poster stays until a frame is drawn
    }
    drawnExact = i === want;
    if (!drawnExact && blobs[want]) decode(want);
    master = S.master[want];
    chapterState(master);
    placeDots(want);
  }
  let curRail = -1, curCond = "";
  function chapterState(m) {
    let k = 0;
    chapters.forEach((c, j) => { if (m >= c.f0) k = j; });
    if (k !== curRail) {
      curRail = k;
      rail.forEach((a, j) => (j === k ? a.setAttribute("aria-current", "step") : a.removeAttribute("aria-current")));
      chapters.forEach((c, j) => c.el.classList.toggle("is-active", j === k));
    }
    const cond = (M.conditions || []).find((c) => m >= c.f0 && m <= c.f1);
    const id = cond ? cond.id : "";
    if (id !== curCond) { curCond = id; chip.dataset.c = id; chip.classList.toggle("on", !!cond); if (cond) chip.lastChild.textContent = cond.label; }
    illus.classList.toggle("on", m >= M.illustrationNote[0] && m <= M.illustrationNote[1]);
  }

  /* ---------------------------------------------------------------- anatomy markers (numbers match the card list) */
  function buildDots() {
    dotsHost.textContent = ""; dots = [];
    const A = (M.anchors || {})[kind]; if (!A) return;
    for (const a of A.points) {
      const el = document.createElement("span");
      el.className = "dot"; el.textContent = a.n;
      dotsHost.appendChild(el);
      dots.push({ el, a, tx: "", op: "" });
    }
  }
  function placeDots(f) {
    const A = (M.anchors || {})[kind]; if (!A || !dots.length) return;
    const fb = frameBox.getBoundingClientRect(), sb = stage.getBoundingClientRect();
    // on desktop the text card sits over the stage: a marker under it is hidden, never shown half-covered
    const ac = tier === "desktop" ? $(".chapter.is-active .card") : null, cr = ac && ac.getBoundingClientRect();
    for (const d of dots) {
      const xy = d.a.xy[f];
      let op = 0;
      if (xy && f >= A.show[0] && f <= A.show[1]) op = Math.min(1, (f - A.show[0] + 1) / 3, (A.show[1] - f + 1) / 3);
      const x = xy ? xy[0] * fb.width : 0, y = xy ? xy[1] * fb.height : 0;
      // hidden rather than misplaced: a marker whose point is occluded or off the visible stage is not shown
      const sx = fb.left - sb.left + x, sy = fb.top - sb.top + y;
      if (!xy || !xy[2] || sx < 18 || sx > sb.width - 18 || sy < 18 || sy > sb.height - 18) op = 0;
      if (cr && sb.left + sx > cr.left - 16 && sb.left + sx < cr.right + 16 && sb.top + sy > cr.top - 16 && sb.top + sy < cr.bottom + 16) op = 0;
      const ops = op <= 0 ? "0" : op.toFixed(2);
      if (ops !== d.op) { d.op = ops; d.el.style.opacity = ops; }
      if (op <= 0) continue;
      const tx = `translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0)`;
      if (tx !== d.tx) { d.tx = tx; d.el.style.transform = tx; }
    }
  }
  window.addEventListener("resize", () => { if (active && S) { drawn = -1; render(); } });

  /* ---------------------------------------------------------------- inert concept form */
  const form = $("#estimate form");
  if (form) form.addEventListener("submit", (e) => {
    e.preventDefault();
    const s = $(".status", form);
    const missing = $$("[required]", form).filter((i) => !i.value.trim());
    s.textContent = missing.length
      ? "Concept preview: add your name, phone and ZIP to see the confirmation. Nothing is sent."
      : "Concept preview: nothing was sent. In the finished site this request would go to JM Roofing.";
  });

  /* ---------------------------------------------------------------- boot */
  const initial = (html.className.match(/tier-(\w+)/) || [])[1] || pick();
  html.classList.remove("tier-" + initial);
  setTier(initial, false);
  window.addEventListener("pageshow", (e) => { if (e.persisted && active && S) { drawn = -1; setFrame(frameFor(progressNow())); } });
  // test hook (QA only reads state; it never drives the experience)
  window.__roofState = () => ({
    tier, kind, want, drawn, exact: drawnExact, master, count: S ? S.count : 0,
    loaded: blobs.filter(Boolean).length, decoded: bitmaps.size, inflight, queued: queue.length,
    gsap: !!st, live: canvas.classList.contains("live"), cond: curCond,
    dots: dots.filter((d) => d.op && d.op !== "0").map((d) => d.a.n),
  });
})();
