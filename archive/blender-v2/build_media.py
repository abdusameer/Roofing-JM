"""Encode rendered PNG frames into the web image sequences and write the frame-to-scroll manifest.
  python3 tools/build_media.py --desktop <png dir> --portrait <png dir> --anchors <anchors.json>
        [--q-desktop 82] [--q-portrait 80] [--q-still 84] [--q-poster 80]
Writes prototype/roof-sequence/media/seq/{desktop,portrait}/NNNN.webp, the stills (poster, fallback
keyframes, final) in media/stills/{desktop,portrait}/, and media/seq/manifest.json.
PNG renders stay outside the repo (they are large and iCloud-synced folders stall on them)."""
import json, os, sys, glob, argparse, datetime
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "prototype/roof-sequence")
TIMELINE = json.load(open(os.path.join(ROOT, "blender/prod/timeline.json")))

ap = argparse.ArgumentParser()
ap.add_argument("--desktop"); ap.add_argument("--portrait"); ap.add_argument("--anchors")
ap.add_argument("--q-desktop", type=int, default=82); ap.add_argument("--q-portrait", type=int, default=80)
ap.add_argument("--q-still", type=int, default=84); ap.add_argument("--q-poster", type=int, default=80)
a = ap.parse_args()
A = json.load(open(a.anchors)) if a.anchors else None
LAST = TIMELINE["last"]

def encode(src, dst, q):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    Image.open(src).convert("RGB").save(dst, "WEBP", quality=q, method=6)
    return os.path.getsize(dst)

man = {
    "version": 2,
    "generated": datetime.date.today().isoformat(),
    "source": "blender/roof_master.blend (Cycles). Every frame is a 3D render of one master timeline.",
    "fps": TIMELINE["fps"], "lastMasterFrame": LAST,
    "mapping": "frame = round(progress * (count - 1)); progress = GSAP ScrollTrigger progress of #sequence "
               "(start 'top top', end 'bottom bottom', scrub: true). master = master[frame].",
    "chapters": TIMELINE["chapters"], "beats": TIMELINE["beats"],
    "conditions": TIMELINE["conditions"], "illustrationNote": TIMELINE["illustrationNote"],
    "sequences": {}, "stills": {}, "anchors": {},
}
STILLS = TIMELINE["stills"]          # name -> master frame
for kind, src, q, step in (("desktop", a.desktop, a.q_desktop, 8), ("portrait", a.portrait, a.q_portrait, 6)):
    if not src: continue
    pngs = sorted(glob.glob(os.path.join(src, "*.png")))
    n = len(pngs)
    out = os.path.join(SITE, "media/seq", kind)
    for old in glob.glob(os.path.join(out, "*.webp")): os.remove(old)
    total = 0
    sizes = []
    for i, p in enumerate(pngs):
        b = encode(p, os.path.join(out, f"{i:04d}.webp"), q); total += b; sizes.append(b)
    master = [round(i * LAST / (n - 1), 3) for i in range(n)]
    first = sum(1 for m in master if m <= TIMELINE["chapters"][0]["f1"] + 1e-6)
    W, H = Image.open(pngs[0]).size
    man["sequences"][kind] = {
        "count": n, "width": W, "height": H, "path": f"media/seq/{kind}/{{i}}.webp", "pad": 4,
        "first": first, "keyframes": list(range(0, n, step)) + ([n - 1] if (n - 1) % step else []),
        "bytes": total, "maxFrameBytes": max(sizes), "quality": q, "master": master,
    }
    # stills: nearest frame of this sequence to each named master frame
    man["stills"][kind] = {}
    for name, mf in STILLS.items():
        i = min(range(n), key=lambda k: abs(master[k] - mf))
        qq = a.q_poster if name == "poster" else a.q_still
        b = encode(pngs[i], os.path.join(SITE, "media/stills", kind, f"{name}.webp"), qq)
        man["stills"][kind][name] = {"frame": i, "master": master[i], "bytes": b}
    if A:
        cam = A["cameras"][kind]
        assert len(cam["master"]) == n, f"anchor frames {len(cam['master'])} != {n} {kind} frames"
        lo, hi = TIMELINE["markers"]
        show = [min(k for k in range(n) if master[k] >= lo), max(k for k in range(n) if master[k] <= hi)]
        man["anchors"][kind] = {"show": show, "points": cam["points"]}
    print(f"{kind}: {n} frames, {total / 1048576:.2f} MB, max frame {max(sizes) / 1024:.0f} KB")
json.dump(man, open(os.path.join(SITE, "media/seq/manifest.json"), "w"), separators=(",", ":"))
print("manifest written")
