"""
Continuity proof for the Proof Panel: render the frame before the panel leaves (112) and the
frame after it returns (330) with the light animation frozen. Camera, layers and panel are
evaluated normally, so identical images mean identical geometry and transforms.

  Blender -b review/roof.blend -P blender/continuity_check.py -- --out <dir> [--camera desktop]
"""
import bpy, sys, os
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
arg = lambda n, d=None: ARGS[ARGS.index(n) + 1] if n in ARGS else d
out = arg("--out"); cam = arg("--camera", "desktop")
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
sc.camera = bpy.data.objects["Cam_" + cam]
sc.render.resolution_x, sc.render.resolution_y = (1600, 900) if cam == "desktop" else (864, 1080)
sc.render.resolution_percentage = 50
sc.render.image_settings.file_format = "PNG"
# freeze lighting at the frame-112 state
sc.frame_set(112)
sun = bpy.data.objects["Sun"]; rot = sun.rotation_euler.copy(); en = sun.data.energy; col = sun.data.color.copy()
bg = sc.world.node_tree.nodes["Background"]; bc = tuple(bg.inputs[0].default_value); bs = bg.inputs[1].default_value
for idb in (sun, sun.data, sc.world.node_tree):
    if idb.animation_data: idb.animation_data_clear()
sun.rotation_euler = rot; sun.data.energy = en; sun.data.color = col
bg.inputs[0].default_value = bc; bg.inputs[1].default_value = bs
for f in (112, 330):
    sc.frame_set(f)
    sc.render.filepath = os.path.join(out, f"{cam}-{f}.png")
    bpy.ops.render.render(write_still=True)
print("continuity frames written to", out)
