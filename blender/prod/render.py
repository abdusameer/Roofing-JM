"""Render production frames from blender/roof_master.blend.
  Blender -b blender/roof_master.blend -P blender/prod/render.py -- --camera desktop --frames 0-167 --out <dir>
  Blender -b ... -- --camera portrait --count 112 --out <dir>        (portrait samples the same master timeline)
  Options: --scale 100 --samples 64 --fmt PNG|WEBP --quality 80 --skip-existing
Particles are simulated by stepping the timeline in order, so every frame (and subframe) is deterministic."""
import bpy, sys, os, time, json, math

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
arg = lambda n, d=None: ARGS[ARGS.index(n) + 1] if n in ARGS else d
flag = lambda n: n in ARGS
sc = bpy.context.scene
cam = arg("--camera", "desktop")
sc.camera = bpy.data.objects["Cam_" + cam]
W, H = (1600, 900) if cam == "desktop" else (900, 1200)
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.resolution_percentage = int(arg("--scale", "100"))
if arg("--samples"): sc.cycles.samples = int(arg("--samples"))
if arg("--noise"): sc.cycles.adaptive_threshold = float(arg("--noise"))
fmt = arg("--fmt", "PNG")
sc.render.image_settings.file_format = fmt
sc.render.image_settings.color_mode = "RGB"
if fmt == "WEBP": sc.render.image_settings.quality = int(arg("--quality", "80"))
if fmt == "PNG": sc.render.image_settings.color_depth = "8"; sc.render.image_settings.compression = 20
out = arg("--out"); os.makedirs(out, exist_ok=True)
ext = {"PNG": "png", "WEBP": "webp", "JPEG": "jpg"}[fmt]

last = sc.frame_end
# shutter per master frame (timeline.json): long only where motion blur is the effect (rain streaks)
TLJ = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "timeline.json")))
def shutter_at(t):
    for a, b, v in TLJ["shutter"]["ranges"]:
        if a <= t <= b: return v
    return TLJ["shutter"]["default"]
times = []          # list of (index, frame, subframe)
if arg("--count"):
    n = int(arg("--count"))
    for i in range(n):
        t = i * last / (n - 1); f = int(math.floor(t)); times.append((i, f, t - f))
else:
    for part in arg("--frames", "0").split(","):
        if "-" in part:
            a, b = map(int, part.split("-")); times += [(f, f, 0.0) for f in range(a, b + 1)]
        else: times.append((int(part), int(part), 0.0))

# step the simulation from the start so particles are correct at every requested time
cur = sc.frame_start
sc.frame_set(cur)
t0 = time.time()
for k, (idx, f, sub) in enumerate(times):
    while cur < f:
        cur += 1; sc.frame_set(cur)
    sc.frame_set(f, subframe=sub)
    path = os.path.join(out, f"{idx:04d}.{ext}")
    if flag("--skip-existing") and os.path.exists(path) and os.path.getsize(path) > 0:
        continue
    sc.render.filepath = path
    sc.render.motion_blur_shutter = shutter_at(f + sub)
    ts = time.time(); bpy.ops.render.render(write_still=True)
    print(f"[{cam}] {idx:04d} (frame {f}+{sub:.2f}) {time.time() - ts:.1f}s  total {time.time() - t0:.0f}s", flush=True)
print("done", len(times), "in", round(time.time() - t0), "s")
