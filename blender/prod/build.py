"""Build the production roof master scene and save blender/roof_master.blend.
  Blender -b --factory-startup -P blender/prod/build.py -- [--out blender/roof_master.blend]
"""
import bpy, bmesh, math, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, common, materials, roof, env, fx
for m in (common, materials, roof, env, fx): importlib.reload(m)
from common import *
from mathutils import Vector, Matrix, Euler

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
arg = lambda n, d=None: ARGS[ARGS.index(n) + 1] if n in ARGS else d
HERE = os.path.dirname(os.path.abspath(__file__)); BL = os.path.dirname(HERE); ROOT = os.path.dirname(BL)
OUT = os.path.join(ROOT, arg("--out", "blender/roof_master.blend"))
PLATES = [os.path.join(BL, "textures/plates", f) for f in ("clear-afternoon.png", "rain-overcast.png", "golden-hour.png")]
CFG = json.load(open(os.path.join(HERE, "cameras.json")))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
for p in ("wet", "heat", "heat_t", "plate_rain", "plate_gold"): sc[p] = 0.0

# ------------------------------------------------------------------ timeline (master = desktop frames)
TIMELINE = json.load(open(os.path.join(HERE, "timeline.json")))      # shared with tools/build_media.py
TL = TIMELINE["beats"]
LAST = TIMELINE["last"]
sc.frame_start, sc.frame_end = 0, LAST
sc.render.fps = 24

# ------------------------------------------------------------------ materials
M = {
    "shingle": materials.shingle(), "cap": materials.shingle("Cap_NightSky"),
    "underlay": materials.underlayment(), "osb": materials.osb(), "lumber": materials.wood(),
    "trim": materials.paint("Trim_DarkBronze", "#2b2724", 0.36, "#5b544b", wear_amt=0.2), "drip": materials.paint("DripEdge_DarkBronze", "#2b2724", 0.32, "#6b6258", wear_amt=0.12),
    "gutter": materials.paint("Gutter_DarkBronze", "#2a2622", 0.3, "#5e574d", wear_amt=0.15), "soffit": materials.paint("Soffit_White", "#e9e6df", 0.55, "#c9c4ba", wear_amt=0.08),
    "vent": materials.soffit_vent(), "ridgevent": materials.simple("RidgeVent_Plastic", "#1d1e20", 0.55),
    "stucco": materials.stucco(), "glass": materials.glass(), "frame": materials.simple("Frame_Black", "#141414", 0.35),
    "interior": materials.interior(), "interior_floor": materials.simple("InteriorFloor", "#6b5440", 0.45),
    "furniture": materials.simple("Furniture", "#3a3530", 0.6), "concrete": materials.concrete(), "lawn": materials.lawn(),
    "leaves": materials.leaves(), "leaves_dark": materials.leaves("FoliageDark", "#24361d", "#41562c"), "bark": materials.simple("Bark", "#5a4a3a", 0.85, bump_scale=40.0),
    "rubber": materials.simple("BootRubber", "#202224", 0.7), "pipe": materials.simple("ABS_Black", "#121314", 0.4), "boot_base": materials.paint("BootFlange", "#3b3c3d", 0.45, "#6d6f70"),
    "insul": materials.simple("Insulation", "#a29f98", 1.0, bump_scale=60.0),
    "water": materials.water(), "rain": materials.rain_streak(), "dust": materials.dust(), "heat": materials.heat_shimmer(),
    "backdrop": materials.backdrop(PLATES),
}

# ------------------------------------------------------------------ collections
C_ROOF = collection("ROOF"); C_PANEL = collection("PROOF_PANEL"); C_HOUSE = collection("HOUSE")
C_LAND = collection("LANDSCAPE"); C_ENV = collection("ENVIRONMENT"); C_FX = collection("WEATHER_FX"); C_CAM = collection("CAMERAS")
LC = {k: collection(k, C_ROOF) for k in ("L1_HipRidgeCaps", "L2_Shingles", "L3_Underlayment", "L4_DripEdge", "L5_Deck", "Eave_Fascia_Soffit_Gutter", "Structure")}

# ------------------------------------------------------------------ roof layers
deck = roof.hip_shell("Deck_OSB", 0.0, T_DECK, LC["L5_Deck"], M["osb"])
bmv = bmesh.new()
env.box_bm(bmv, -RH + 0.3, RH - 0.3, -0.035, 0.035, ZR - 0.3, ZR + 0.3)
slot = mesh_from_bm("RidgeSlotCutter", bmv, C_ROOF)
boolean(deck, slot, "DIFFERENCE")
under = roof.hip_shell("Underlayment", H_UND, H_UND + T_UND, LC["L3_Underlayment"], M["underlay"])
boolean(under, slot, "DIFFERENCE"); bpy.data.objects.remove(slot)

drips = roof.strip_along_eaves("DripEdge", LC["L4_DripEdge"], M["drip"], roof.drip_profile(), thickness=0.0009)
# starter strip: a flat 12-inch course on the underlayment at every eave
starters = []
for i, pl in enumerate(roof.PLANES):
    bm = bmesh.new(); a, b = -0.3, pl["Lp"] + 0.3
    cs = [roof.pt(pl, a, -SH_OVER, H_SHB), roof.pt(pl, b, -SH_OVER, H_SHB), roof.pt(pl, b, 0.305, H_SHB), roof.pt(pl, a, 0.305, H_SHB)]
    cs += [c + pl["n"] * T_START for c in cs]
    add_box(bm, cs)
    tl = bm.faces.layers.float.new("tone"); sl = bm.faces.layers.float.new("shadow")
    for f in bm.faces: f[tl] = 0.35; f[sl] = 0.4
    roof.clip_to_plane(bm, i)
    starters.append(mesh_from_bm(f"StarterCourse_{pl['name']}", bm, LC["L2_Shingles"], (M["shingle"],)))

NEAR = (PX0 - EX0 - 0.06, PX1 - EX0 + 0.06, PV_SH + 0.05)
shingle_obs = []; near_bm = None
for i in range(4):
    ob, nb = roof.shingle_plane(i, (M["shingle"],), LC["L2_Shingles"], NEAR if i == 0 else None)
    shingle_obs.append(ob)
    if nb is not None: near_bm = nb
near = mesh_from_bm("Shingles_FrontNear", near_bm, LC["L2_Shingles"], (M["shingle"],))
for ob in shingle_obs + [near] + starters:
    bevel(ob, 0.0007, 1); apply_modifiers(ob)

caps, ridgevent, cap_final, LOCK = roof.caps_and_vent(LC["L1_HipRidgeCaps"], M["cap"], M["ridgevent"])
for ob in (caps, cap_final): bevel(ob, 0.0008, 1); apply_modifiers(ob)
fascias = roof.strip_along_eaves("Fascia", LC["Eave_Fascia_Soffit_Gutter"], M["trim"], roof.fascia_profile(), extend=0.04, clip=False)
soffits = roof.strip_along_eaves("Soffit", LC["Eave_Fascia_Soffit_Gutter"], M["soffit"], roof.soffit_profile(), extend=0.0, clip=False)
vents = roof.strip_along_eaves("SoffitVent", LC["Eave_Fascia_Soffit_Gutter"], M["vent"], roof.vent_profile(), extend=-0.4, clip=False)
gutter_obs = roof.gutters(LC["Eave_Fascia_Soffit_Gutter"], M["gutter"])
for ob in gutter_obs + fascias: bevel(ob, 0.0012, 2); apply_modifiers(ob)
raft = roof.rafters(LC["Structure"], M["lumber"]); bevel(raft, 0.002, 1); apply_modifiers(raft)
insul = env.box_ob("Insulation_Context", LC["Structure"], M["insul"], -L / 2 + 0.3, L / 2 - 0.3, -W / 2 + 0.3, W / 2 - 0.3, H, H + 0.22)

# ------------------------------------------------------------------ the Proof Panel: cut from the master objects
PC = roof.pt(roof.PLANES[0], (PX0 + PX1) / 2 - EX0, PV / 2, 0.0)
rig = bpy.data.objects.new("PanelRig", None); C_PANEL.objects.link(rig); rig.location = PC; rig.empty_display_size = 0.3
bpy.context.view_layer.update()
pz = {k: roof.prism(v, "Prism_" + k) for k, v in (("deck", PV), ("und", PV_UND), ("sh", PV_SH))}
CUTS = [("Panel_Deck", deck, "deck"), ("Panel_Underlayment", under, "und"), ("Panel_DripEdge", drips[0], "deck"),
        ("Panel_StarterCourse", starters[0], "sh"), ("Panel_Fascia", fascias[0], "deck"),
        ("Panel_Soffit", soffits[0], "deck"), ("Panel_SoffitVent", vents[0], "deck"), ("Panel_Gutter", gutter_obs[0], "deck"),
        ("Panel_GutterHangers", gutter_obs[4], "deck"), ("Panel_Rafters", raft, "deck")]
panel_parts = {}
for name, src, key in CUTS:
    piece = bpy.data.objects.new(name, src.data.copy()); C_PANEL.objects.link(piece)
    boolean(piece, pz[key], "INTERSECT"); boolean(src, pz[key], "DIFFERENCE")
    panel_parts[name] = piece
# Shingles: hundreds of overlapping laminate solids, so they are split with three exact bisect planes
# (the same faces as the prism) and every cut is capped. Panel piece + remainder = the original shingles.
def bisect_keep(bm, co, no):
    """Keep the side of the plane opposite to 'no' and cap the cut."""
    res = bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), dist=1e-7,
                                 plane_co=co, plane_no=no, clear_outer=True)
    cut_edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_boundary]
    if cut_edges: bmesh.ops.holes_fill(bm, edges=cut_edges, sides=0)
def split_copy(src, planes):
    bm = bmesh.new(); bm.from_mesh(src.data)
    for co, no in planes: bisect_keep(bm, Vector(co), Vector(no))
    return bm
py_sh = EY0 + PV_SH * CA
bm_panel = split_copy(near, [((PX0, 0, 0), (-1, 0, 0)), ((PX1, 0, 0), (1, 0, 0)), ((0, py_sh, 0), (0, 1, 0))])
parts = [split_copy(near, [((PX0, 0, 0), (1, 0, 0))]), split_copy(near, [((PX1, 0, 0), (-1, 0, 0))]),
         split_copy(near, [((PX0, 0, 0), (-1, 0, 0)), ((PX1, 0, 0), (1, 0, 0)), ((0, py_sh, 0), (0, -1, 0))])]
panel_parts["Panel_Shingles"] = mesh_from_bm("Panel_Shingles", bm_panel, C_PANEL, (M["shingle"],))
bm = bmesh.new(); bm.from_mesh(shingle_obs[0].data)
for b in parts:
    tmp = bpy.data.meshes.new("tmp"); b.to_mesh(tmp); b.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
bm.to_mesh(shingle_obs[0].data); bm.free(); bpy.data.objects.remove(near)
for p in pz.values(): bpy.data.objects.remove(p)
for ob in roof.pipe_boot(C_PANEL, M["rubber"], M["pipe"], M["boot_base"]): panel_parts[ob.name] = ob
bpy.context.view_layer.update()
for ob in panel_parts.values():
    set_origin(ob, PC)
    mw = ob.matrix_world.copy(); ob.parent = rig; ob.matrix_parent_inverse = rig.matrix_world.inverted(); ob.matrix_world = mw

# ------------------------------------------------------------------ layer pivots: one lift empty per layer, origins on the roof base
LIFT = {}
for key in ("L1_HipRidgeCaps", "L2_Shingles", "L3_Underlayment", "L4_DripEdge", "L5_Deck"):
    e = bpy.data.objects.new("Lift_" + key, None); LC[key].objects.link(e); e.location = (0, 0, ZE); LIFT[key] = e
bpy.context.view_layer.update()
for key, e in LIFT.items():
    for ob in list(LC[key].objects):
        if ob is e: continue
        set_origin(ob, Vector((0, 0, ZE)))
        mw = ob.matrix_world.copy(); ob.parent = e; ob.matrix_parent_inverse = e.matrix_world.inverted(); ob.matrix_world = mw
for ob in list(LC["Eave_Fascia_Soffit_Gutter"].objects) + [raft, insul]: set_origin(ob, Vector((0, 0, ZE)))
# anchors for the page's numbered layer markers (numbers match the anatomy list); each rides its layer's lift
# placed just right of the panel cut, where both the desktop and the portrait framing see every layer edge
ANCH = [(1, "L1_HipRidgeCaps", Vector((EX0, EY0, ZE)).lerp(Vector((-RH, 0, ZR)), 0.8) + Vector((0, 0, roof.cap_height() + 0.02))),
        (2, "L2_Shingles", roof.pt(roof.PLANES[0], 4.3, 2.0, H_SHB + 0.008)),
        (3, "L3_Underlayment", roof.pt(roof.PLANES[0], 3.4, 0.03, H_UND + T_UND)),
        (4, "L4_DripEdge", roof.pt(roof.PLANES[0], 4.8, -0.012, H_UND)),
        (5, "L5_Deck", roof.pt(roof.PLANES[0], 6.2, 0.04, T_DECK))]
for n, key, co in ANCH:
    a = bpy.data.objects.new(f"Anchor_{n}_{key}", None); LC[key].objects.link(a); a.location = co; a.empty_display_size = 0.1
    a.parent = LIFT[key]; a.matrix_parent_inverse = LIFT[key].matrix_world.inverted()

# ------------------------------------------------------------------ house, landscape, environment
env.house(C_HOUSE, M)
ground, shrubs, trees = env.landscape(C_LAND, M, **CFG.get("landscape", {}))
env.backdrop(C_ENV, M["backdrop"], **CFG.get("backdrop", {}))
SKY = env.sky_and_sun(C_ENV)

# ------------------------------------------------------------------ weather FX
bpy.context.view_layer.update()
psh = panel_parts["Panel_Shingles"]
# rain dies on light collision proxies (camera- and ray-invisible), not on the dense shingle meshes:
# the lifted roof surface follows the shingle lift, the panel top follows the Proof Panel rig
def ghost(ob):
    for k in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter", "visible_shadow"):
        setattr(ob, k, False)
    return ob
roof_col = ghost(roof.hip_shell("RainCollider_Roof", H_SHB + 0.006, H_SHB + 0.010, C_FX, M["shingle"], uv=False))
roof_col.parent = LIFT["L2_Shingles"]; roof_col.matrix_parent_inverse = LIFT["L2_Shingles"].matrix_world.inverted()
bmc = bmesh.new(); plf = roof.PLANES[0]; hc = H_SHB + 2 * T_BASE + T_TAB + 0.0005
cs = [roof.pt(plf, PX0 - EX0, -SH_OVER, hc), roof.pt(plf, PX1 - EX0, -SH_OVER, hc), roof.pt(plf, PX1 - EX0, PV_SH, hc), roof.pt(plf, PX0 - EX0, PV_SH, hc)]
add_box(bmc, [c - plf["n"] * 0.004 for c in cs] + cs)
panel_col = ghost(mesh_from_bm("RainCollider_Panel", bmc, C_FX))
panel_col.parent = rig; panel_col.matrix_parent_inverse = rig.matrix_world.inverted()
killers = [roof_col, panel_col, ground, panel_parts["Panel_Gutter"]]
drop, bead, rain_em = fx.rain(C_FX, M, psh, killers, TL["rain"][0], TL["rain"][1])
def shingle_top(v):
    return H_SHB + 2 * T_BASE + T_TAB + 0.001
runoffs, edge_em = fx.runoff(C_FX, M, rig, shingle_top)
edge_drop = fx.edge_drips(edge_em, M, C_FX, TL["rain"][0], TL["rain"][1])
# the storm is over by the end of "clear": the rain and drip systems switch off for rendering, so no stray
# drops remain (they would read as specks with the short shutter) and no hidden instances cost render time
for em_ob in (rain_em, bpy.data.objects["RainEmitterNear"], edge_em):
    for mod in em_ob.modifiers:
        if mod.type != "PARTICLE_SYSTEM": continue
        for f, v in ((0, True), (TL["clear"][1] - 1, True), (TL["clear"][1], False), (LAST, False)):
            mod.show_render = v; mod.keyframe_insert("show_render", frame=f)
dust_em, dust_mote = fx.dust(C_FX, M, TL["wind"][0], TL["wind"][1])
# the wind settles before the storm: dust is gone by the time the rain starts
for f, sc_ in ((0, 1.0), (98, 1.0), (101, 0.0), (LAST, 0.0)):
    dust_mote.scale = (sc_, sc_, sc_); dust_mote.keyframe_insert("scale", frame=f)
heat = fx.heat_sheet(C_FX, M, rig, PC)
heat.parent = rig; heat.matrix_parent_inverse = rig.matrix_world.inverted()

# ------------------------------------------------------------------ animation
def key_loc(ob, f, loc):
    ob.location = loc; ob.keyframe_insert("location", frame=f)
def prop(name, pairs):
    for f, v in pairs: sc[name] = v; sc.keyframe_insert(f'["{name}"]', frame=f)

LIFTS = CFG["lifts"]          # metres, vertical (the stacking direction of a hip roof of equal pitches)
UP = {"L1_HipRidgeCaps": (12, 22), "L2_Shingles": (16, 28), "L3_Underlayment": (22, 32), "L4_DripEdge": (27, 36), "L5_Deck": (32, 42)}
DOWN = {"L5_Deck": (146, 150), "L4_DripEdge": (147, 151), "L3_Underlayment": (149, 153), "L2_Shingles": (151, 155), "L1_HipRidgeCaps": (153, 157)}
for key, e in LIFT.items():
    z0 = e.location.copy(); z1 = z0 + Vector((0, 0, LIFTS[key]))
    a, b = UP[key]; c, d = DOWN[key]
    key_loc(e, 0, z0); key_loc(e, a, z0); key_loc(e, b, z1); key_loc(e, c, z1); key_loc(e, d, z0); key_loc(e, LAST, z0)
# the final ridge cap seats last: it is the lock piece
fc = cap_final; base = fc.location.copy()
key_loc(fc, 155, base + Vector((0, 0, 0.22))); key_loc(fc, 159, base); key_loc(fc, LAST, base)
for f in (0, 154): key_loc(fc, f, base)

# Proof Panel path (translation only, orientation never changes):
#  anatomy  - every panel piece rides with its own layer, so the exploded roof has no holes;
#  isolate  - the exploded slice slides straight out of the roof (horizontal, away from the house: it only
#             ever moves away from the surrounding layers, so nothing interpenetrates), then the pieces
#             close onto the rig and the assembled panel rises into the hero position;
#  return   - the exact reverse: re-explode to the layer heights, slide back into the openings, and the
#             reassembly brings panel and roof down together to the original transforms.
p0 = rig.location.copy(); pS = p0 + Vector((0, -CFG["panel"]["slide"], 0)); p2 = pS + Vector(CFG["panel"]["hero"])
for f, loc in ((0, p0), (48, p0), (56, pS), (63, p2), (132, p2), (139, pS), (145, p0), (LAST, p0)):
    key_loc(rig, f, loc.copy())
PANEL_LAYER = {"Panel_Deck": "L5_Deck", "Panel_DripEdge": "L4_DripEdge", "Panel_Underlayment": "L3_Underlayment",
               "Panel_StarterCourse": "L2_Shingles", "Panel_Shingles": "L2_Shingles"}
for nm, ob in panel_parts.items():
    key = PANEL_LAYER.get(nm, "L2_Shingles" if nm.startswith("PipeBoot") or nm.startswith("VentPipe") or "Boot" in nm or "Pipe" in nm else None)
    if key is None: continue
    up = Vector((0, 0, LIFTS[key])); zero = Vector((0, 0, 0))
    a, b = UP[key]; c, d = DOWN[key]
    for f, v in ((0, zero), (a, zero), (b, up), (56, up), (62, zero), (132, zero), (138, up), (c, up), (d, zero), (LAST, zero)):
        ob.delta_location = v; ob.keyframe_insert("delta_location", frame=f)

prop("heat", [(0, 0), (60, 0), (68, 1), (79, 1), (85, 0), (LAST, 0)])
prop("heat_t", [(0, 0), (LAST, 40)])
prop("wet", [(0, 0), (102, 0), (114, 1), (124, 1), (131, 0.45), (146, 0.0), (LAST, 0)])
prop("plate_rain", [(0, 0), (96, 0), (104, 1), (124, 1), (131, 0), (LAST, 0)])
prop("plate_gold", [(0, 0), (158, 0), (166, 1), (LAST, 1)])
bead.scale = (0, 0, 0); bead.keyframe_insert("scale", frame=104)
bead.scale = (1, 1, 1); bead.keyframe_insert("scale", frame=116); bead.keyframe_insert("scale", frame=126)
bead.scale = (0.4, 0.4, 0.4); bead.keyframe_insert("scale", frame=134)
bead.scale = (0, 0, 0); bead.keyframe_insert("scale", frame=142)
for i, r in enumerate(runoffs):
    cu = r.data
    for f, d in ((0, 0.0), (106 + i % 4, 0.0), (114 + i % 3, 0.0011 + 0.0004 * (i % 3)), (124, 0.0012), (130, 0.0), (LAST, 0.0)):
        cu.bevel_depth = d; cu.keyframe_insert("bevel_depth", frame=f)
# foliage sways only in the Santa Ana chapter
for ob in shrubs + trees:
    ob.rotation_euler = (0, 0, 0)
    for f, ang in ((0, 0), (80, 0), (84, 2.2), (88, -1.4), (92, 2.6), (96, -1.0), (100, 1.4), (104, 0), (LAST, 0)):
        ob.rotation_euler = (math.radians(ang * 0.5), math.radians(ang), 0); ob.keyframe_insert("rotation_euler", frame=f)

# light follows the LA calendar: clear afternoon, midsummer heat, Santa Ana, winter storm, washed clear, golden hour
LIGHT = CFG["light"]
sun = SKY["sun"]
def light_key(f, s):
    L_ = LIGHT[s]
    sun.rotation_euler = Euler((0, math.radians(90 - L_["el"]), math.radians(L_["az"])), "XYZ"); sun.keyframe_insert("rotation_euler", frame=f)
    sun.data.energy = L_["sun"]; sun.data.keyframe_insert("energy", frame=f)
    sun.data.color = L_["color"]; sun.data.keyframe_insert("color", frame=f)
    SKY["bg"].inputs[1].default_value = L_["sky"]; SKY["bg"].inputs[1].keyframe_insert("default_value", frame=f)
    SKY["mix"].inputs[0].default_value = L_["overcast"]; SKY["mix"].inputs[0].keyframe_insert("default_value", frame=f)
    try:
        SKY["sky"].sun_elevation = math.radians(L_["el"]); SKY["sky"].keyframe_insert("sun_elevation", frame=f)
        SKY["sky"].sun_rotation = math.radians(L_["az"] + 90); SKY["sky"].keyframe_insert("sun_rotation", frame=f)
    except Exception: pass
for f, s in ((0, "clear"), (50, "clear"), (66, "heat"), (79, "heat"), (86, "wind"), (97, "wind"), (104, "rain"), (124, "rain"),
             (132, "washed"), (156, "washed"), (165, "golden"), (LAST, "golden")):
    light_key(f, s)

# cameras: one camera language, two framings
def make_cam(name, fit):
    cd = bpy.data.cameras.new(name); cd.sensor_fit = fit; cd.sensor_width = 36.0; cd.sensor_height = 36.0; cd.clip_start = 0.05; cd.clip_end = 2000
    cam = bpy.data.objects.new(name, cd); C_CAM.objects.link(cam)
    tg = bpy.data.objects.new(name + "_Target", None); C_CAM.objects.link(tg)
    c = cam.constraints.new("TRACK_TO"); c.target = tg; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    cd.dof.use_dof = True; cd.dof.focus_object = tg
    return cam, tg
for name, fit in (("desktop", "HORIZONTAL"), ("portrait", "VERTICAL")):
    cam, tg = make_cam("Cam_" + name, fit)
    for f, k in CFG["cams"][name]:
        cam.location = k["loc"]; cam.keyframe_insert("location", frame=f)
        tg.location = k["look"]; tg.keyframe_insert("location", frame=f)
        cam.data.lens = k["lens"]; cam.data.keyframe_insert("lens", frame=f)
        cam.data.shift_x = k.get("sx", 0.0); cam.data.keyframe_insert("shift_x", frame=f)
        cam.data.shift_y = k.get("sy", 0.0); cam.data.keyframe_insert("shift_y", frame=f)
        cam.data.dof.aperture_fstop = k.get("f", 5.6); cam.data.dof.keyframe_insert("aperture_fstop", frame=f)
sc.camera = bpy.data.objects["Cam_desktop"]

# ------------------------------------------------------------------ render settings
sc.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
try:
    prefs.compute_device_type = "METAL"; prefs.get_devices()
    for d in prefs.devices: d.use = (d.type != "CPU")
    sc.cycles.device = "GPU"
except Exception: pass
cy = sc.cycles
cy.samples = CFG["render"]["samples"]; cy.use_adaptive_sampling = True; cy.adaptive_threshold = CFG["render"]["noise"]
cy.use_denoising = True; cy.denoiser = "OPENIMAGEDENOISE"
cy.max_bounces = 8; cy.diffuse_bounces = 3; cy.glossy_bounces = 4; cy.transmission_bounces = 8; cy.transparent_max_bounces = 16
cy.caustics_reflective = False; cy.caustics_refractive = False; cy.sample_clamp_indirect = 8.0
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.45
sc.render.use_persistent_data = True
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = CFG["render"].get("look", "AgX - Medium High Contrast")
except Exception: pass
sc.view_settings.exposure = CFG["render"]["exposure"]
sc.render.film_transparent = False

# ------------------------------------------------------------------ verify the Proof Panel contract on every frame
# (particles are switched off for the check so stepping the timeline stays cheap)
pmods = [m for o in sc.objects for m in o.modifiers if m.type == "PARTICLE_SYSTEM"]
for m in pmods: m.show_viewport = False
sc.frame_set(0); bpy.context.view_layer.update()
ref = {nm: ob.matrix_world.copy() for nm, ob in panel_parts.items()}
rot_err, home_err, home_frames = 0.0, 0.0, list(range(0, 12)) + list(range(157, LAST + 1))
for f in range(LAST + 1):
    sc.frame_set(f)
    for nm, ob in panel_parts.items():
        m, r = ob.matrix_world, ref[nm]
        rot_err = max(rot_err, max(abs(m[i][j] - r[i][j]) for i in range(3) for j in range(3)))
        if f in home_frames: home_err = max(home_err, (m.translation - r.translation).length)
sc.frame_set(0)
for m in pmods: m.show_viewport = True
PANEL_CHECK = {"pieces": sorted(panel_parts), "translation_only": rot_err < 1e-6, "max_rotation_delta": rot_err,
               "exact_home": home_err < 1e-6, "max_home_offset_m": home_err, "home_frames": [home_frames[0], 11, 157, LAST]}
print("panel check", json.dumps(PANEL_CHECK))

manifest = {"fps": TIMELINE["fps"], "frames": LAST + 1, "timeline": TL, "lock_frame": 159, "panel_check": PANEL_CHECK,
            "panel_frames": {"home": [0, 48], "slide_out": [48, 56], "assemble_and_hero": [56, 63], "hero": [63, 132],
                             "re_explode": [132, 139], "slide_in": [139, 145], "reassembly": [146, 157]}}
sc["manifest"] = json.dumps(manifest)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
try:
    bpy.ops.file.make_paths_relative()          # plates resolve from the .blend's own folder
    bpy.ops.wm.save_mainfile(compress=True)
except Exception as e: print("relative paths:", e)
print("saved", OUT)
