"""
Render frames / stills and export anchor data from the master scene.

  Blender -b review/roof.blend -P blender/render.py -- --camera desktop --frames 0-405 \
      --out review/frames/desktop --fmt PNG --scale 100 --samples 24
  Blender -b review/roof.blend -P blender/render.py -- --camera portrait --stills --out <dir> --fmt WEBP
  Blender -b review/roof.blend -P blender/render.py -- --camera desktop --anchors <file.json>
"""
import bpy, json, os, sys, time
from bpy_extras.object_utils import world_to_camera_view

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else default
flag = lambda name: name in ARGS

sc = bpy.context.scene
meta = json.loads(sc["meta"])
cam_name = arg("--camera", "desktop")
cam = bpy.data.objects["Cam_" + cam_name]
sc.camera = cam
SIZES = {"desktop": (1600, 900), "portrait": (864, 1080)}
sc.render.resolution_x, sc.render.resolution_y = SIZES[cam_name]
sc.render.resolution_percentage = int(arg("--scale", "100"))
try: sc.eevee.taa_render_samples = int(arg("--samples", "24"))
except Exception: pass

def frame_list():
    if flag("--stills"):
        return sorted(set(meta["stills"].values()))
    spec = arg("--frames", "0")
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-"); out += list(range(int(a), int(b) + 1, int(arg("--step", "1"))))
        else: out.append(int(part))
    return out

out_dir = arg("--out")
if out_dir:
    os.makedirs(out_dir, exist_ok=True)
    fmt = arg("--fmt", "PNG")
    sc.render.image_settings.file_format = fmt
    if fmt == "WEBP": sc.render.image_settings.quality = int(arg("--quality", "80"))
    if fmt == "PNG": sc.render.image_settings.color_depth = "8"; sc.render.image_settings.compression = 15
    sc.render.image_settings.color_mode = "RGB"
    ext = {"PNG": "png", "WEBP": "webp", "JPEG": "jpg"}[fmt]
    names = {v: k for k, v in meta["stills"].items()}
    t0 = time.time(); fl = frame_list()
    for i, f in enumerate(fl):
        sc.frame_set(f)
        name = f"{names[f]}.{ext}" if flag("--stills") else f"{f:04d}.{ext}"
        sc.render.filepath = os.path.join(out_dir, name)
        if flag("--skip-existing") and os.path.exists(sc.render.filepath) and os.path.getsize(sc.render.filepath) > 0:
            continue
        bpy.ops.render.render(write_still=True)
        if i % 20 == 0: print(f"[{cam_name}] frame {f} ({i + 1}/{len(fl)}) {time.time() - t0:.1f}s", flush=True)
    print(f"done {len(fl)} frames in {time.time() - t0:.1f}s")

anchor_file = arg("--anchors")
if anchor_file:
    rx, ry = SIZES[cam_name]
    anchors = {o.name[2:]: o for o in bpy.data.objects if o.name.startswith("A_")}
    # which frames each anchor needs (keeps the file small); panel-local anchors are static 165-280
    ranges = {
        "caps": (0, 405), "ridgevent": (0, 405), "shingles": (0, 405), "underlay": (0, 405), "drip": (0, 405),
        "deck": (0, 405), "soffit": (0, 405), "attic": (0, 405), "ridge_out": (0, 405), "insulation": (0, 405),
        "panel": (0, 405), "lock": (330, 405),
    }
    data = {}
    for name, ob in anchors.items():
        a, b = ranges.get(name, (200, 200))
        data[name] = {"from": a, "to": b, "xy": []}
    for f in range(0, meta["frames"]):
        sc.frame_set(f)
        for name, ob in anchors.items():
            d = data[name]
            if d["from"] <= f <= d["to"]:
                co = world_to_camera_view(sc, cam, ob.matrix_world.translation)
                d["xy"] += [round(co.x, 4), round(1 - co.y, 4)]
    # panel transform check: the return must land on the exact outbound matrix
    rig = bpy.data.objects["PanelRig"]
    mats = {}
    for f in (0, 112, 130, 165, 280, 315, 330, 405):
        sc.frame_set(f); mats[f] = [round(x, 9) for row in rig.matrix_world for x in row]
    out = {"camera": cam_name, "size": [rx, ry], "frames": meta["frames"], "timeline": meta["timeline"],
           "lock": meta["lock"], "stills": meta["stills"], "anchors": data,
           "panelCheck": {"matrices": mats,
                          "returnExact": mats[330] == mats[0] == mats[112] == mats[405],
                          "pathMirrored": mats[315] == mats[130] and mats[280] == mats[165]}}
    os.makedirs(os.path.dirname(anchor_file), exist_ok=True)
    json.dump(out, open(anchor_file, "w"), separators=(",", ":"))
    print("anchors", anchor_file, "returnExact", out["panelCheck"]["returnExact"], "pathMirrored", out["panelCheck"]["pathMirrored"])
