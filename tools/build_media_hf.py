"""Phase 2B: build the web image sequences from the three Higgsfield clips and write the manifest.
  python3 tools/build_media_hf.py --frames <dir with a/ b/ c/ PNG frames extracted from the clips>
Website order (one scroll timeline):
  opening hold (clip A frame 0) → clip A forward → clip B forward → clip C → clip B REVERSED →
  clip A REVERSED → final hold on roof-complete-master.
The reversed segments reuse the forward files through a step→file map, so the return and the
reassembly pass through exactly the same images and cost no extra downloads."""
import json, os, glob, argparse, datetime
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "prototype/roof-sequence")
HF = os.path.join(ROOT, "higgsfield")
ap = argparse.ArgumentParser()
ap.add_argument("--frames", required=True)
ap.add_argument("--q", type=int, default=68); ap.add_argument("--q-mobile", type=int, default=64)
a = ap.parse_args()

SRC = {k: sorted(glob.glob(os.path.join(a.frames, k, "*.png"))) for k in ("a", "b", "c")}
STEP = {"a": 3, "b": 3, "c": 4}           # every 3rd frame of A and B, every 4th of C (24 fps sources) keeps the payload in budget
HOLD_OPEN, HOLD_END = 10, 10
MASTER = os.path.join(HF, "v2/masters/roof-complete-master.png")   # 4K v2 masters

# unique source images, in file order
files = []                                 # (clip, source path)
seg = {}
for k in ("a", "b", "c"):
    idx = list(range(0, len(SRC[k]), STEP[k]))
    if idx[-1] != len(SRC[k]) - 1: idx.append(len(SRC[k]) - 1)   # always keep the exact end frame
    seg[k] = list(range(len(files), len(files) + len(idx)))
    files += [(k, SRC[k][i]) for i in idx]
f_master = len(files); files.append(("master", MASTER))

# desktop timeline: step -> file index
tl, beats = [], {}
def add(name, ids):
    beats[name] = [len(tl), len(tl) + len(ids) - 1]; tl.extend(ids)
add("opening", [seg["a"][0]] * HOLD_OPEN)
add("anatomy", seg["a"])
add("panel", seg["b"])
nc = len(seg["c"])                          # clip C shots by time: calm 0-2 s, heat 2-4 s, wind 4-6 s, rain 6-10 s, clear 10-12 s
cut = lambda s: round(s / 12 * (nc - 1))
c = seg["c"]
add("calm", c[:cut(2)]); add("heat", c[cut(2):cut(4)]); add("wind", c[cut(4):cut(6)]); add("rain", c[cut(6):cut(10)]); add("clear", c[cut(10):])
add("return", list(reversed(seg["b"])))
add("reassembly", list(reversed(seg["a"])))
add("hold", [f_master] * HOLD_END)
LAST = len(tl) - 1

chapters = [
    {"id": "opening", "f0": beats["opening"][0], "f1": beats["opening"][1], "beats": ["opening"]},
    {"id": "anatomy", "f0": beats["anatomy"][0], "f1": beats["anatomy"][1], "beats": ["clip A forward"]},
    {"id": "panel", "f0": beats["panel"][0], "f1": beats["panel"][1], "beats": ["clip B forward"]},
    {"id": "heat", "f0": beats["calm"][0], "f1": beats["heat"][1], "beats": ["clip C calm", "clip C heat"]},
    {"id": "wind", "f0": beats["wind"][0], "f1": beats["wind"][1], "beats": ["clip C wind"]},
    {"id": "rain", "f0": beats["rain"][0], "f1": beats["clear"][1], "beats": ["clip C rain", "clip C clear"]},
    {"id": "return", "f0": beats["return"][0], "f1": beats["return"][1], "beats": ["clip B reversed"]},
    {"id": "reassembly", "f0": beats["reassembly"][0], "f1": beats["hold"][1], "beats": ["clip A reversed", "final hold on roof-complete-master"]},
]

def fit(src, w, h):
    im = Image.open(src).convert("RGB")
    sw, sh = im.size; r = w / h
    if abs(sw / sh - r) > 0.002:            # centre-crop to the exact web aspect (sources differ by < 0.1 %)
        if sw / sh > r: nw = round(sh * r); im = im.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
        else: nh = round(sw / r); im = im.crop((0, (sh - nh) // 2, sw, (sh - nh) // 2 + nh))
    return im.resize((w, h), Image.LANCZOS)

def write_seq(kind, w, h, q, file_ids, steps):
    out = os.path.join(SITE, "media/hf", kind); os.makedirs(out, exist_ok=True)
    for old in glob.glob(os.path.join(out, "*.webp")): os.remove(old)
    remap = {fid: n for n, fid in enumerate(file_ids)}
    sizes = []
    for n, fid in enumerate(file_ids):
        p = os.path.join(out, f"{n:04d}.webp"); fit(files[fid][1], w, h).save(p, "WEBP", quality=q, method=6); sizes.append(os.path.getsize(p))
    smap = [remap[tl[s]] for s in steps]
    first = sum(1 for s in steps if s <= beats["opening"][1]) + 1
    kf = sorted(set(list(range(0, len(steps), 8)) + [len(steps) - 1]))
    return {"count": len(steps), "files": len(file_ids), "width": w, "height": h, "path": f"media/hf/{kind}/{{i}}.webp", "pad": 4,
            "map": smap, "master": steps, "first": first, "keyframes": kf, "bytes": sum(sizes), "maxFrameBytes": max(sizes), "quality": q}

man = {"version": 3, "generated": datetime.date.today().isoformat(),
       "source": "Higgsfield: GPT Image 2.5 master frames + Kling 3.0 start/end-frame clips (see higgsfield/provenance.json). Concept visualization, not a product test.",
       "lastMasterFrame": LAST,
       "mapping": "step = round(progress * (count - 1)); file = map[step]; master = master[step] (desktop timeline step). progress = GSAP ScrollTrigger progress of #sequence (scrub: true).",
       "order": ["clip A forward", "clip B forward", "clip C", "clip B reversed", "clip A reversed", "final hold: roof-complete-master"],
       "chapters": chapters, "beats": beats,
       "conditions": [{"id": "heat", "label": "Heat", "f0": beats["heat"][0], "f1": beats["heat"][1]},
                      {"id": "wind", "label": "Wind", "f0": beats["wind"][0], "f1": beats["wind"][1]},
                      {"id": "rain", "label": "Rain", "f0": beats["rain"][0], "f1": beats["rain"][1]}],
       "illustrationNote": [beats["panel"][0], beats["return"][1]], "sequences": {}, "stills": {}, "anchors": {}}

# desktop: every unique file, every step
all_ids = sorted(set(tl))
man["sequences"]["desktop"] = write_seq("desktop", 1600, 900, a.q, all_ids, list(range(len(tl))))
# mobile: fewer frames and a shorter scroll (every 2nd step, every boundary kept), the full 16:9 frame shown
# uncropped until a separately composed portrait set exists
msteps = sorted(set(list(range(0, len(tl), 2)) + [b for v in beats.values() for b in v]))
man["sequences"]["mobile"] = write_seq("mobile", 960, 540, a.q_mobile, sorted(set(tl[s] for s in msteps)), msteps)

STILLS = {"poster": 0, "anatomy": beats["anatomy"][1], "panel": beats["panel"][1], "heat": beats["heat"][1] - 2,
          "wind": (beats["wind"][0] + beats["wind"][1]) // 2, "rain": (beats["rain"][0] + beats["rain"][1]) // 2,
          "return": (beats["return"][0] + beats["return"][1]) // 2, "reassembly": (beats["reassembly"][0] + beats["reassembly"][1]) // 2, "final": LAST}
for kind, (w, h, q) in {"desktop": (1600, 900, 82), "mobile": (960, 540, 78)}.items():
    man["stills"][kind] = {}
    d = os.path.join(SITE, "media/hf-stills", kind); os.makedirs(d, exist_ok=True)
    for name, step in STILLS.items():
        p = os.path.join(d, f"{name}.webp")
        fit(files[tl[step]][1], w, h).save(p, "WEBP", quality=(q - 22 if name == "poster" else q), method=6)   # the poster is the LCP: lighter
        S = man["sequences"][kind]
        i = min(range(S["count"]), key=lambda k: abs(S["master"][k] - step))
        man["stills"][kind][name] = {"frame": i, "master": step, "bytes": os.path.getsize(p)}
json.dump(man, open(os.path.join(SITE, "media/hf/manifest.json"), "w"), separators=(",", ":"))
for k, s in man["sequences"].items():
    print(f"{k}: {s['count']} steps, {s['files']} files, {s['bytes'] / 1048576:.2f} MB, max {s['maxFrameBytes'] / 1024:.0f} KB")
print("chapters", [(c["id"], c["f0"], c["f1"]) for c in chapters])
