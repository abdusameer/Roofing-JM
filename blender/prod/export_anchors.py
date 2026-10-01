"""Project the layer-marker anchors through both cameras for every web frame.
  Blender -b blender/roof_master.blend -P blender/prod/export_anchors.py -- --portrait-count 112 --out <file.json>
Desktop frames are the master frames (0..LAST); portrait frames sample the same master timeline
evenly (index i -> master i * LAST / (count - 1)), exactly as render.py --count does.
Each point is [x, y, visible] with x, y in 0..1 of the frame (y down). A point is not visible when it
is behind the camera, outside the frame, or occluded (ray cast from the camera hits something first)."""
import bpy, sys, json, math
from bpy_extras.object_utils import world_to_camera_view

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
arg = lambda n, d=None: ARGS[ARGS.index(n) + 1] if n in ARGS else d
sc = bpy.context.scene
LAST = sc.frame_end
NP = int(arg("--portrait-count", "112"))
# particles do not affect anchors; skip their simulation
for ob in sc.objects:
    for m in ob.modifiers:
        if m.type == "PARTICLE_SYSTEM": m.show_viewport = False
anchors = sorted((o for o in sc.objects if o.name.startswith("Anchor_")), key=lambda o: o.name)

def times(kind):
    if kind == "desktop": return [(i, i, 0.0) for i in range(LAST + 1)]
    out = []
    for i in range(NP):
        t = i * LAST / (NP - 1); f = int(math.floor(t)); out.append((i, f, t - f))
    return out

res = {"last": LAST, "portraitCount": NP, "cameras": {}}
for kind, W, H in (("desktop", 1600, 900), ("portrait", 900, 1200)):
    cam = bpy.data.objects["Cam_" + kind]; sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
    pts = {a.name: [] for a in anchors}
    master = []
    for idx, f, sub in times(kind):
        sc.frame_set(f, subframe=sub)
        master.append(round(f + sub, 3))
        dg = bpy.context.evaluated_depsgraph_get()
        origin = cam.matrix_world.translation.copy()
        for a in anchors:
            co = a.matrix_world.translation.copy()
            p = world_to_camera_view(sc, cam, co)
            vis = 1 if (p.z > 0 and 0.0 <= p.x <= 1.0 and 0.0 <= p.y <= 1.0) else 0
            if vis:
                d = co - origin
                hit = sc.ray_cast(dg, origin, d.normalized(), distance=max(0.0, d.length - 0.04))[0]
                if hit: vis = 0
            pts[a.name].append([round(p.x, 4), round(1.0 - p.y, 4), vis])
    res["cameras"][kind] = {"master": master, "points": [
        {"n": int(a.name.split("_")[1]), "layer": "_".join(a.name.split("_")[2:]), "xy": pts[a.name]} for a in anchors]}
    print("anchors", kind, len(master), "frames")
json.dump(res, open(arg("--out"), "w"), separators=(",", ":"))
print("wrote", arg("--out"))
