"""
JM Roofing concept, Phase 1 proxy master scene.

Builds one single-story LA stucco house with a hip roof and the Phase 0 assembly
(docs/phase-0/02 §3): roof deck, eave drip edge, underlayment, laminated shingle
courses, hip/ridge caps over a ridge vent, fascia, soffit with intake vent, gutters,
rafters and ceiling insulation (context only). The Proof Panel is cut from the same
layer solids with one prism, so it can only ever be the same geometry.

Everything is proxy geometry for a pitch prototype. It is not construction guidance.

Run headless:
  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
      -P blender/build_scene.py -- --out review/roof.blend
"""
import bpy, bmesh, math, json, os, sys
from mathutils import Vector, Matrix, Euler

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else default

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_BLEND = os.path.join(ROOT, arg("--out", "review/roof.blend"))

# ---------------------------------------------------------------- dimensions (m)
L, W, H = 12.0, 8.4, 2.75            # wall footprint and plate height
O = 0.45                             # eave overhang (fascia face)
P = 5.0 / 12.0                       # 5:12 pitch
A = math.atan(P); SA, CA = math.sin(A), math.cos(A)
EX0, EX1 = -L / 2 - O, L / 2 + O     # eave outline
EY0, EY1 = -W / 2 - O, W / 2 + O
RH = (EX1 - EX0) / 2 - (EY1 - EY0) / 2   # ridge half-length (hips at 45° in plan)
ZE = H                               # deck underside at the eave line
ZR = ZE + (EY1 - EY0) / 2 * P        # deck underside at the ridge

# layer thicknesses, measured normal to the roof plane (exaggerated where noted)
T_DECK, T_UND, T_SH = 0.030, 0.006, 0.016
V = 1.0 / CA                         # vertical offset per unit of normal thickness
Z_DECK_TOP = T_DECK * V
Z_UND_TOP = Z_DECK_TOP + (0.003 + T_UND) * V   # 3 mm allowance for the drip-edge flange
Z_SH_TOP = Z_UND_TOP + T_SH * V

# shingle geometry from the Owens Corning Duration data sheet (13¼″ × 39⅜″, 5⅝″ exposure)
SH_H, SH_EXP, SH_OVERHANG = 0.3366, 0.1429, 0.0127

# Proof Panel: ~4 ft wide beside the left hip, ~6 ft up-slope from the eave
PX0, PX1 = -4.60, -4.60 + 1.22
PV = 1.83                            # up-slope length (deck)
PV_UND, PV_SH = 1.62, 1.40           # stepped cutaway: underlayment and shingles stop short so every layer shows
PY1 = EY0 + PV * CA                  # plan position of the panel's upper cut

# exploded (anatomy) lifts, vertical, metres
LIFT = {"deck": 1.10, "drip": 1.52, "underlay": 1.98, "shingles": 2.55, "caps": 2.98}

# ---------------------------------------------------------------- timeline (frames)
TL = {
    "opening": [0, 0],
    "anatomy": [0, 112],
    "panel": [112, 165],
    "heat": [165, 195],
    "wind": [195, 225],
    "rain": [225, 280],       # includes clearing 260-280
    "return": [280, 330],
    "reassembly": [330, 405],
}
FRAME_END = 405
LOCK_FRAME = 395
STILLS = {"opening": 0, "anatomy": 110, "panel": 165, "heat": 192, "wind": 222,
          "rain": 256, "return": 330, "reassembly": 405}

# ---------------------------------------------------------------- reset
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 0, FRAME_END
sc.render.fps = 30
sc.unit_settings.system = "METRIC"
sc["dim"] = 0.0
sc["wet"] = 0.0

def link(obj, coll=None):
    (coll or sc.collection).objects.link(obj)
    return obj

def mesh_obj(name, bm, mat=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    if mat: ob.data.materials.append(mat)
    return link(ob)

def box(name, x0, x1, y0, y1, z0, z1, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((x0 + x1) / 2 + v.co.x * (x1 - x0), (y0 + y1) / 2 + v.co.y * (y1 - y0), (z0 + z1) / 2 + v.co.z * (z1 - z0)))
    return mesh_obj(name, bm, mat)

def join_objects(name, objs):
    """Merge objects into one mesh without bpy.ops (keeps material slots)."""
    bm = bmesh.new(); mats = []
    for ob in objs:
        me = ob.data
        ob_bm = bmesh.new(); ob_bm.from_mesh(me); ob_bm.transform(ob.matrix_world)
        remap = {}
        for i, m in enumerate(me.materials):
            if m not in mats: mats.append(m)
            remap[i] = mats.index(m)
        for f in ob_bm.faces: f.material_index = remap.get(f.material_index, 0)
        tmp = bpy.data.meshes.new("tmp"); ob_bm.to_mesh(tmp); ob_bm.free()
        bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
        bpy.data.objects.remove(ob)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    return link(bpy.data.objects.new(name, me))

# ---------------------------------------------------------------- materials
def _mix_rgb(nt, a, b, fac):
    n = nt.nodes.new("ShaderNodeMix"); n.data_type = "RGBA"; n.blend_type = "MIX"
    for s, v in ((n.inputs[0], fac), (n.inputs[6], a), (n.inputs[7], b)):
        if isinstance(v, (float, int)): s.default_value = v
        elif isinstance(v, tuple): s.default_value = v
        else: nt.links.new(v, s)
    return n.outputs[2]

def _scene_attr(nt, name):
    n = nt.nodes.new("ShaderNodeAttribute"); n.attribute_type = "VIEW_LAYER"; n.attribute_name = name
    return n.outputs["Fac"]

def _math(nt, op, a, b=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op
    for s, v in zip(n.inputs, (a, b)):
        if v is None: continue
        if isinstance(v, (float, int)): s.default_value = v
        else: nt.links.new(v, s)
    return n.outputs[0]

HAZE = (0.80, 0.785, 0.76, 1.0)

def srgb(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)

def material(name, hexcol, rough=0.85, metal=0.0, dim=True, noise=0.0, bump=0.0, color_socket=None, wet=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes["Principled BSDF"]
    col = color_socket(nt) if color_socket else None
    if col is None:
        base = srgb(hexcol)
        if noise > 0:
            tc = nt.nodes.new("ShaderNodeTexCoord")
            nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 38.0
            nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
            dark = tuple(c * (1 - noise) for c in base[:3]) + (1.0,)
            col = _mix_rgb(nt, dark, base, nz.outputs["Fac"])
        else:
            rgb = nt.nodes.new("ShaderNodeRGB"); rgb.outputs[0].default_value = base; col = rgb.outputs[0]
    rough_out = rough
    if wet:
        w = _scene_attr(nt, "wet")
        col = _mix_rgb(nt, col, (0.02, 0.02, 0.022, 1.0), _math(nt, "MULTIPLY", w, 0.42))
        rough_out = _math(nt, "SUBTRACT", rough, _math(nt, "MULTIPLY", w, rough - 0.18))
    if dim:
        col = _mix_rgb(nt, col, HAZE, _math(nt, "MULTIPLY", _scene_attr(nt, "dim"), 0.72))
    nt.links.new(col, bsdf.inputs["Base Color"])
    if isinstance(rough_out, float): bsdf.inputs["Roughness"].default_value = rough_out
    else: nt.links.new(rough_out, bsdf.inputs["Roughness"])
    bsdf.inputs["Metallic"].default_value = metal
    if bump > 0:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 220.0
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m

def shingle_color(courses):
    """Oyster Shell-like laminated blend: per-tab tone from a Voronoi cell on
    (along-eave, course index); optional butt shadow line for the textured roof layer."""
    def build(nt):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
        along = _math(nt, "ADD", sep.outputs[0], sep.outputs[1])
        z0 = ZE + Z_SH_TOP - SH_OVERHANG * SA
        u = _math(nt, "DIVIDE", _math(nt, "SUBTRACT", sep.outputs[2], z0), SH_EXP * SA)
        course = _math(nt, "FLOOR", u)
        comb = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(_math(nt, "MULTIPLY", along, 2.3), comb.inputs[0]); nt.links.new(_math(nt, "MULTIPLY", course, 1.93), comb.inputs[1])
        vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 1.0
        nt.links.new(comb.outputs[0], vor.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        cr = ramp.color_ramp; cr.elements[0].color = srgb("#8a857c"); cr.elements[1].color = srgb("#b7b0a4")
        e = cr.elements.new(0.55); e.color = srgb("#a39c90")
        nt.links.new(vor.outputs["Color"], ramp.inputs[0])
        col = ramp.outputs[0]
        # granule speckle
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 520.0; nz.inputs["Detail"].default_value = 1.0
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        col = _mix_rgb(nt, col, srgb("#5f5a52"), _math(nt, "MULTIPLY", _math(nt, "GREATER_THAN", nz.outputs["Fac"], 0.62), 0.55))
        if courses:
            frac = _math(nt, "FRACT", u)
            line = _math(nt, "LESS_THAN", frac, 0.085)
            col = _mix_rgb(nt, col, srgb("#4d4943"), _math(nt, "MULTIPLY", line, 0.8))
        return col
    return build

M = {
    "stucco": material("Stucco", "#e7e0d4", 0.95, bump=0.25, noise=0.05),
    "plinth": material("Plinth", "#bdb7ad", 0.9, noise=0.08),
    "trim": material("Trim", "#f1efea", 0.6),
    "glass": material("Glass", "#2b3036", 0.18),
    "door": material("Door", "#6d5a45", 0.6),
    "floor": material("Floor", "#e8e4dc", 1.0, dim=False),
    "shingles": material("Shingles", None, 0.86, bump=0.35, color_socket=shingle_color(True)),
    "caps": material("Caps", None, 0.86, bump=0.35, color_socket=shingle_color(False)),
    "underlay": material("Underlayment", "#373a3e", 0.55, noise=0.1),
    "deck": material("Deck", "#c9a26a", 0.8, noise=0.22, bump=0.2),
    "metal": material("PaintedMetal", "#ecebe6", 0.38, metal=0.0),
    "vent": material("SoffitVent", "#3b3b39", 0.7),
    "ridgevent": material("RidgeVent", "#4a4c4f", 0.6),
    "rafter": material("Rafter", "#b88f5e", 0.8, noise=0.15),
    "insul": material("Insulation", "#a6a39c", 1.0, bump=0.6, noise=0.12),
    "pipe": material("Pipe", "#1f1f1f", 0.4),
    "boot": material("Boot", "#5d6064", 0.5),
}
# Proof Panel variants: never dimmed; the panel shingles take the wet state
PM = {k: material(v.name + "_P", None, 0.86, dim=False, bump=0.35, color_socket=shingle_color(True), wet=True) if k == "shingles"
      else None for k, v in M.items()}
def panel_mat(key):
    if PM.get(key): return PM[key]
    src = M[key]; m = src.copy(); m.name = src.name + "_P"
    # remove the dim mix: relink the node feeding the dim mix's A input straight to the BSDF
    nt = m.node_tree; bsdf = nt.nodes["Principled BSDF"]
    link_in = bsdf.inputs["Base Color"].links[0]; mix = link_in.from_node
    if mix.bl_idname == "ShaderNodeMix" and mix.inputs[6].links:
        nt.links.new(mix.inputs[6].links[0].from_socket, bsdf.inputs["Base Color"])
    PM[key] = m
    return m

# ---------------------------------------------------------------- geometry: house
box("Plinth", -L / 2 - 0.08, L / 2 + 0.08, -W / 2 - 0.08, W / 2 + 0.08, 0.0, 0.16, M["plinth"])
walls = box("Walls", -L / 2, L / 2, -W / 2, W / 2, 0.16, H, M["stucco"])

def window(name, face, c, w, h, z0):
    """face: 'front' (y=-W/2) or 'left' (x=-L/2). Recessed dark glass with a white sill/frame."""
    d = 0.02
    if face == "front":
        box(name + "G", c - w / 2, c + w / 2, -W / 2 - d, -W / 2 + 0.01, z0, z0 + h, M["glass"])
        box(name + "T", c - w / 2 - 0.07, c + w / 2 + 0.07, -W / 2 - 0.045, -W / 2 + 0.01, z0 - 0.07, z0, M["trim"])
        box(name + "H", c - w / 2 - 0.07, c + w / 2 + 0.07, -W / 2 - 0.035, -W / 2 + 0.01, z0 + h, z0 + h + 0.06, M["trim"])
    else:
        box(name + "G", -L / 2 - d, -L / 2 + 0.01, c - w / 2, c + w / 2, z0, z0 + h, M["glass"])
        box(name + "T", -L / 2 - 0.045, -L / 2 + 0.01, c - w / 2 - 0.07, c + w / 2 + 0.07, z0 - 0.07, z0, M["trim"])
        box(name + "H", -L / 2 - 0.035, -L / 2 + 0.01, c - w / 2 - 0.07, c + w / 2 + 0.07, z0 + h, z0 + h + 0.06, M["trim"])

window("WinF1", "front", -3.2, 1.9, 1.35, 1.0)
window("WinF2", "front", 3.4, 1.9, 1.35, 1.0)
window("WinL1", "left", -1.6, 1.4, 1.2, 1.1)
window("WinL2", "left", 1.9, 1.0, 1.2, 1.1)
box("Door", -0.5, 0.5, -W / 2 - 0.03, -W / 2 + 0.01, 0.16, 2.2, M["door"])
box("DoorTrim", -0.6, 0.6, -W / 2 - 0.04, -W / 2 + 0.01, 2.2, 2.28, M["trim"])
box("Step", -0.9, 0.9, -W / 2 - 0.55, -W / 2, 0.0, 0.16, M["plinth"])

# floor: large enough that no camera ever sees a horizon
bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=260.0)
mesh_obj("Floor", bm, M["floor"])

# ---------------------------------------------------------------- geometry: roof layer solids
def hip_solid(name, zb, zt, mat):
    """Hip-roof shell between two vertical offsets of the deck-underside surface.
    Equal pitches mean a normal offset is a pure vertical translation, so every layer
    is the same shape and exploding along Z keeps them nested."""
    bm = bmesh.new()
    def ring(z):
        e = [bm.verts.new((EX0, EY0, ZE + z)), bm.verts.new((EX1, EY0, ZE + z)),
             bm.verts.new((EX1, EY1, ZE + z)), bm.verts.new((EX0, EY1, ZE + z))]
        r = [bm.verts.new((-RH, 0.0, ZR + z)), bm.verts.new((RH, 0.0, ZR + z))]
        return e, r
    (b1, b2, b3, b4), (br1, br2) = ring(zb)
    (t1, t2, t3, t4), (tr1, tr2) = ring(zt)
    for f in ((t1, t2, tr2, tr1), (t2, t3, tr2), (t3, t4, tr1, tr2), (t4, t1, tr1)):
        bm.faces.new(f)
    for f in ((b1, br1, br2, b2), (b2, br2, b3), (b3, br2, br1, b4), (b4, br1, b1)):
        bm.faces.new(f)
    for a, b, c, d in ((b1, b2, t2, t1), (b2, b3, t3, t2), (b3, b4, t4, t3), (b4, b1, t1, t4)):
        bm.faces.new((a, b, c, d))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, mat)

deck = hip_solid("DeckRoof", 0.0, Z_DECK_TOP, M["deck"])
under = hip_solid("UnderlayRoof", Z_DECK_TOP + 0.003 * V, Z_UND_TOP, M["underlay"])
shing = hip_solid("ShinglesRoof", Z_UND_TOP, Z_SH_TOP, M["shingles"])

# ridge-vent slot through deck and underlayment (exhaust opening along the ridge)
def cut(target, cutter, op="DIFFERENCE"):
    mod = target.modifiers.new("cut", "BOOLEAN"); mod.operation = op; mod.object = cutter; mod.solver = "EXACT"
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(target.evaluated_get(dg))
    target.modifiers.remove(mod)
    old = target.data; target.data = me; bpy.data.meshes.remove(old)

slot = box("RidgeSlotCutter", -RH + 0.3, RH - 0.3, -0.04, 0.04, ZR - 0.2, ZR + 0.3)
cut(deck, slot); cut(under, slot); bpy.data.objects.remove(slot)

# drip edge (eave): flange on the deck top 2″ up-slope, face down the fascia, ¼″ kick below the deck
def drip_edge():
    bm = bmesh.new()
    th = 0.004
    flange_run = 0.052
    ztop = ZE + Z_DECK_TOP
    sides = [((EX0, EY0), (EX1, EY0), (0, -1)), ((EX1, EY0), (EX1, EY1), (1, 0)),
             ((EX1, EY1), (EX0, EY1), (0, 1)), ((EX0, EY1), (EX0, EY0), (-1, 0))]
    for (x0, y0), (x1, y1), (ox, oy) in sides:
        inx, iny = -ox, -oy
        # flange: a thin slab lying on the deck plane from the eave line up-slope
        fz = flange_run * SA
        v = [bm.verts.new((x0 + ox * 0.004, y0 + oy * 0.004, ztop)), bm.verts.new((x1 + ox * 0.004, y1 + oy * 0.004, ztop)),
             bm.verts.new((x1 + inx * flange_run * CA, y1 + iny * flange_run * CA, ztop + fz)), bm.verts.new((x0 + inx * flange_run * CA, y0 + iny * flange_run * CA, ztop + fz))]
        vt = [bm.verts.new((p.co.x, p.co.y, p.co.z + th)) for p in v]
        # face leg: from the deck top down 0.045 on the outside of the fascia
        w0 = [bm.verts.new((x0 + ox * 0.004, y0 + oy * 0.004, ztop - 0.045)), bm.verts.new((x1 + ox * 0.004, y1 + oy * 0.004, ztop - 0.045))]
        w1 = [bm.verts.new((x0 + ox * 0.008, y0 + oy * 0.008, ztop - 0.045)), bm.verts.new((x1 + ox * 0.008, y1 + oy * 0.008, ztop - 0.045))]
        top_out = [bm.verts.new((x0 + ox * 0.008, y0 + oy * 0.008, ztop + th)), bm.verts.new((x1 + ox * 0.008, y1 + oy * 0.008, ztop + th))]
        for f in ((v[0], v[1], v[2], v[3]), (vt[3], vt[2], vt[1], vt[0]), (v[3], v[2], vt[2], vt[3]),
                  (w0[0], w0[1], v[1], v[0]), (top_out[0], top_out[1], w1[1], w1[0]), (w1[0], w1[1], w0[1], w0[0]),
                  (vt[0], vt[1], top_out[1], top_out[0])):
            try: bm.faces.new(f)
            except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj("DripEdgeRoof", bm, M["metal"])

drip = drip_edge()

# fascia, soffit, soffit vent strip, gutters, downspout
fasc = []
fasc.append(box("FasciaF", EX0, EX1, EY0, EY0 + 0.025, ZE - 0.20, ZE + 0.012, M["metal"]))
fasc.append(box("FasciaB", EX0, EX1, EY1 - 0.025, EY1, ZE - 0.20, ZE + 0.012, M["metal"]))
fasc.append(box("FasciaL", EX0, EX0 + 0.025, EY0, EY1, ZE - 0.20, ZE + 0.012, M["metal"]))
fasc.append(box("FasciaR", EX1 - 0.025, EX1, EY0, EY1, ZE - 0.20, ZE + 0.012, M["metal"]))
fascia = join_objects("Fascia", fasc)

sof = []
sof.append(box("SofF", EX0 + 0.025, EX1 - 0.025, EY0 + 0.025, -W / 2, ZE - 0.20, ZE - 0.185, M["metal"]))
sof.append(box("SofB", EX0 + 0.025, EX1 - 0.025, W / 2, EY1 - 0.025, ZE - 0.20, ZE - 0.185, M["metal"]))
sof.append(box("SofL", EX0 + 0.025, -L / 2, -W / 2, W / 2, ZE - 0.20, ZE - 0.185, M["metal"]))
sof.append(box("SofR", L / 2, EX1 - 0.025, -W / 2, W / 2, ZE - 0.20, ZE - 0.185, M["metal"]))
soffit = join_objects("Soffit", sof)
vs = []
vs.append(box("VentF", EX0 + 0.2, EX1 - 0.2, EY0 + 0.10, EY0 + 0.16, ZE - 0.203, ZE - 0.199, M["vent"]))
vs.append(box("VentB", EX0 + 0.2, EX1 - 0.2, EY1 - 0.16, EY1 - 0.10, ZE - 0.203, ZE - 0.199, M["vent"]))
vs.append(box("VentL", EX0 + 0.10, EX0 + 0.16, EY0 + 0.2, EY1 - 0.2, ZE - 0.203, ZE - 0.199, M["vent"]))
vs.append(box("VentR", EX1 - 0.16, EX1 - 0.10, EY0 + 0.2, EY1 - 0.2, ZE - 0.203, ZE - 0.199, M["vent"]))
svent = join_objects("SoffitVent", vs)

def gutter_run(name, a, b, out):
    """K-style proxy: U channel hung on the fascia face. a,b: (x,y) along the fascia face; out: outward unit (x,y)."""
    bm = bmesh.new()
    prof = [(0.006, 0.0), (0.006, -0.13), (0.125, -0.13), (0.14, -0.04), (0.14, 0.0), (0.132, 0.0), (0.132, -0.04), (0.118, -0.122), (0.014, -0.122), (0.014, 0.0)]
    ztop = ZE - 0.02
    d = Vector((b[0] - a[0], b[1] - a[1], 0)).normalized()
    rows = []
    for p in (a, b):
        rows.append([bm.verts.new((p[0] + out[0] * o, p[1] + out[1] * o, ztop + z)) for o, z in prof])
    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        try: bm.faces.new((rows[0][i], rows[0][j], rows[1][j], rows[1][i]))
        except ValueError: pass
    bm.faces.new(rows[0]); bm.faces.new(list(reversed(rows[1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, M["metal"])

gl = [gutter_run("GutF", (EX0 - 0.14, EY0), (EX1 + 0.14, EY0), (0, -1)),
      gutter_run("GutB", (EX0 - 0.14, EY1), (EX1 + 0.14, EY1), (0, 1)),
      gutter_run("GutL", (EX0, EY0 + 0.0), (EX0, EY1 - 0.0), (-1, 0)),
      gutter_run("GutR", (EX1, EY0 + 0.0), (EX1, EY1 - 0.0), (1, 0))]
gutter = join_objects("Gutter", gl)
box("Downspout", EX0 + 0.22, EX0 + 0.29, EY0 - 0.105, EY0 - 0.035, 0.16, ZE - 0.14, M["metal"])
box("Splash", EX0 + 0.12, EX0 + 0.39, EY0 - 0.5, EY0 - 0.02, 0.0, 0.03, M["plinth"])

# rafters (structure; shown only when the deck lifts)
def deck_z(x, y):
    return ZE + P * min(y - EY0, EY1 - y, x - EX0, EX1 - x)

def rafter(x0, y0, x1, y1):
    d = Vector((x1 - x0, y1 - y0, 0)); ln = d.length; d.normalize(); s = Vector((-d.y, d.x, 0)) * 0.022
    a = Vector((x0, y0, deck_z(x0, y0))); b = Vector((x1, y1, deck_z(x1, y1)))
    bm = bmesh.new()
    vs_ = [bm.verts.new(p) for p in (a - s, a + s, b + s, b - s)]
    vb = [bm.verts.new(p.co - Vector((0, 0, 0.19))) for p in vs_]
    for f in ((vs_[0], vs_[1], vs_[2], vs_[3]), (vb[3], vb[2], vb[1], vb[0]), (vs_[0], vb[0], vb[1], vs_[1]),
              (vs_[1], vb[1], vb[2], vs_[2]), (vs_[2], vb[2], vb[3], vs_[3]), (vs_[3], vb[3], vb[0], vs_[0])):
        bm.faces.new(f)
    return mesh_obj("R", bm, M["rafter"])

rf = []
x = EX0 + 0.5
while x < EX1 - 0.3:
    yend = min(0.0, (x - EX0) + EY0, (EX1 - x) + EY0)
    if yend - EY0 > 0.25:
        rf.append(rafter(x, EY0 + 0.03, x, yend - 0.01))
        rf.append(rafter(x, EY1 - 0.03, x, -yend + 0.01))
    x += 0.61
y = EY0 + 0.5
while y < EY1 - 0.3:
    xend = min(-RH, EX0 + (y - EY0), EX0 + (EY1 - y))
    if xend - EX0 > 0.25:
        rf.append(rafter(EX0 + 0.03, y, xend - 0.01, y))
        rf.append(rafter(EX1 - 0.03, y, -xend + 0.01, y))
    y += 0.61
for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
    rf.append(rafter(sx * (EX1 - 0.05), sy * (EY1 - 0.05), sx * RH, 0.0))
rf.append(rafter(-RH, 0.0, RH, 0.0))
rafters = join_objects("Rafters", rf)

insul = box("Insulation", -L / 2 + 0.3, L / 2 - 0.3, -W / 2 + 0.3, W / 2 - 0.3, H, H + 0.2, M["insul"])

# ridge vent (exhaust; exact product is an owner question) and hip / ridge caps
def tent(bm, p0, p1, n_a, n_b, width, thick, lift):
    d = (p1 - p0).normalized()
    faces = []
    for n in (n_a, n_b):
        w = n.cross(d).normalized()
        # point the wing down its own slope (away from the hip/ridge line)
        if w.z > 0: w = -w
        q0 = p0 + n * lift; q1 = p1 + n * lift
        a0, a1, b0, b1 = q0, q1, q1 + w * width, q0 + w * width
        vv = [bm.verts.new(p) for p in (a0, a1, b0, b1)]
        vt = [bm.verts.new(p.co + n * thick) for p in vv]
        for f in ((vv[0], vv[1], vv[2], vv[3]), (vt[3], vt[2], vt[1], vt[0]), (vv[0], vt[0], vt[1], vv[1]),
                  (vv[1], vt[1], vt[2], vv[2]), (vv[2], vt[2], vt[3], vv[3]), (vv[3], vt[3], vt[0], vv[0])):
            bm.faces.new(f)

NF, NB = Vector((0, -SA, CA)), Vector((0, SA, CA))
NL, NR = Vector((-SA, 0, CA)), Vector((SA, 0, CA))
zc = ZE + Z_SH_TOP
bm = bmesh.new()
tent(bm, Vector((-RH, 0, ZR + Z_SH_TOP)), Vector((RH, 0, ZR + Z_SH_TOP)), NF, NB, 0.15, 0.03, 0.002)
ridgevent = mesh_obj("RidgeVent", bm, M["ridgevent"])

hips = [(Vector((EX0, EY0, zc)), Vector((-RH, 0, ZR + Z_SH_TOP)), NF, NL),
        (Vector((EX1, EY0, zc)), Vector((RH, 0, ZR + Z_SH_TOP)), NF, NR),
        (Vector((EX1, EY1, zc)), Vector((RH, 0, ZR + Z_SH_TOP)), NB, NR),
        (Vector((EX0, EY1, zc)), Vector((-RH, 0, ZR + Z_SH_TOP)), NB, NL)]
bm = bmesh.new()
for a, b, na, nb in hips:
    ln = (b - a).length; d = (b - a).normalized(); n = 0; s = 0.0
    while s < ln - 0.1:
        p0 = a + d * s; p1 = a + d * min(s + 0.305, ln)
        tent(bm, p0, p1, na, nb, 0.15, 0.006, 0.003 + (n % 2) * 0.0025)
        s += SH_EXP; n += 1
# ridge caps run left to right over the vent; the last one is the final piece (the lock)
ra, rb = Vector((-RH, 0, ZR + Z_SH_TOP + 0.03)), Vector((RH, 0, ZR + Z_SH_TOP + 0.03))
ln = (rb - ra).length; d = (rb - ra).normalized(); s = 0.0; n = 0
while s + SH_EXP < ln - 0.305:
    tent(bm, ra + d * s, ra + d * (s + 0.305), NF, NB, 0.17, 0.006, 0.004 + (n % 2) * 0.0025)
    s += SH_EXP; n += 1
caps = mesh_obj("Caps", bm, M["caps"])
bm = bmesh.new()
tent(bm, ra + d * (ln - 0.305), rb, NF, NB, 0.17, 0.006, 0.009)
cap_final = mesh_obj("CapFinal", bm, M["caps"])
LOCK_POS = (ra + d * (ln - 0.15) + Vector((0, 0, 0.02)))

# ---------------------------------------------------------------- the Proof Panel cut
def prism(v_top=PV):
    """L-shaped cutter: the eave overhang (fascia, soffit, gutter, drip edge) plus the
    roof layers above the wall plate, between PX0 and PX1, up to the panel's upper cut."""
    bm = bmesh.new()
    py = EY0 + v_top * CA
    prof = [(EY0 - 0.6, ZE - 0.225), (-W / 2 - 0.001, ZE - 0.225), (-W / 2 - 0.001, H + 0.001),
            (py, H + 0.001), (py, 30.0), (EY0 - 0.6, 30.0)]
    a = [bm.verts.new((PX0, y, z)) for y, z in prof]
    b = [bm.verts.new((PX1, y, z)) for y, z in prof]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj("PanelPrism", bm)

pz = prism()
pz_und = prism(PV_UND)
pz_sh = prism(PV_SH)
panel_rig = bpy.data.objects.new("PanelRig", None); link(panel_rig)
PC = Vector(((PX0 + PX1) / 2, EY0 + PV / 2 * CA, ZE + PV / 2 * SA))   # panel centre on the deck-underside plane
panel_rig.location = PC
panel_parts = {}
for key, ob, mk in (("deck", deck, "deck"), ("underlay", under, "underlay"), ("drip", drip, "metal"),
                    ("fascia", fascia, "metal"), ("soffit", soffit, "metal"), ("svent", svent, "vent"),
                    ("gutter", gutter, "metal"), ("rafters", rafters, "rafter")):
    piece = bpy.data.objects.new("P_" + key, ob.data.copy()); link(piece)
    cutter = pz_und if key == "underlay" else pz
    cut(piece, cutter, "INTERSECT")
    cut(ob, cutter, "DIFFERENCE")
    piece.data.materials.clear(); piece.data.materials.append(panel_mat(mk))
    panel_parts[key] = piece
cut(shing, pz_sh, "DIFFERENCE")  # the textured roof layer gets the hole; the panel gets real courses
for c in (pz, pz_und, pz_sh): c.hide_render = True; c.hide_viewport = True

# panel shingle courses (real geometry, laid bottom-up so each course laps the one below)
def plane_pt(u, v, h):
    """Front roof plane frame: u along the eave from PX0, v up-slope from the eave, h normal offset above the deck underside."""
    return Vector((PX0 + u, EY0 + v * CA, ZE + v * SA)) + NF * h

bm = bmesh.new()
h0 = T_DECK + 0.003 + T_UND        # underlayment top (normal)
k = 0
starter_h = 0.004
# starter course at the eave
def slab(bm, u0, u1, v0, v1, hb0, hb1, t):
    ps = [plane_pt(u0, v0, hb0), plane_pt(u1, v0, hb0), plane_pt(u1, v1, hb1), plane_pt(u0, v1, hb1)]
    vv = [bm.verts.new(p) for p in ps]; vt = [bm.verts.new(p + NF * t) for p in ps]
    for f in ((vv[3], vv[2], vv[1], vv[0]), (vt[0], vt[1], vt[2], vt[3]), (vv[0], vv[1], vt[1], vt[0]),
              (vv[1], vv[2], vt[2], vt[1]), (vv[2], vv[3], vt[3], vt[2]), (vv[3], vv[0], vt[0], vt[3])):
        bm.faces.new(f)
slab(bm, 0.0, 1.22, -SH_OVERHANG, 0.18, h0, h0, starter_h)
starter = mesh_obj("P_starter", bm, PM["shingles"])
bm = bmesh.new()
while True:
    v0 = -SH_OVERHANG + k * SH_EXP
    if v0 >= PV_SH - 0.02: break
    v1 = min(v0 + SH_H, PV_SH)
    raise_ = 0.013 if k > 0 else starter_h + 0.001
    frac = (v1 - v0) / SH_H
    slab(bm, 0.0, 1.22, v0, v1, h0 + raise_, h0 + raise_ * (1 - frac), 0.006)
    k += 1
courses = mesh_obj("P_courses", bm, PM["shingles"])
panel_parts["starter"] = starter; panel_parts["courses"] = courses

# plumbing vent pipe and boot near the top of the panel
BOOT_U, BOOT_V = 0.61, 1.06
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.045, radius2=0.045, depth=0.62)
pipe = mesh_obj("P_pipe", bm, panel_mat("pipe"))
base = plane_pt(BOOT_U, BOOT_V, h0 + 0.02)
pipe.location = base + Vector((0, 0, 0.12))
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.11, radius2=0.052, depth=0.12)
boot = mesh_obj("P_boot", bm, panel_mat("boot"))
boot.location = base + Vector((0, 0, 0.05))
bm = bmesh.new()
slab(bm, BOOT_U - 0.2, BOOT_U + 0.2, BOOT_V - 0.2, BOOT_V + 0.22, h0 + 0.018, h0 + 0.004, 0.003)
flange = mesh_obj("P_flange", bm, panel_mat("boot"))
panel_parts.update(pipe=pipe, boot=boot, flange=flange)

bpy.context.view_layer.update()
for p in panel_parts.values():
    mw = p.matrix_world.copy(); p.parent = panel_rig; p.matrix_parent_inverse = panel_rig.matrix_world.inverted(); p.matrix_world = mw

# ---------------------------------------------------------------- anchors (empties that follow their object)
bpy.context.view_layer.update()
ANCH = {}
def anchor(name, world_pos, parent=None):
    e = bpy.data.objects.new("A_" + name, None); link(e); e.empty_display_size = 0.05
    e.location = world_pos
    if parent:
        e.parent = parent; e.matrix_parent_inverse = parent.matrix_world.inverted()
    ANCH[name] = e
    return e

def roof_pt(x, y, zoff):
    return Vector((x, y, deck_z(x, y) + zoff))

anchor("caps", Vector((EX0, EY0, zc)).lerp(Vector((-RH, 0.0, ZR + Z_SH_TOP)), 0.45) + Vector((0, 0, 0.03)), caps)
anchor("ridgevent", Vector((0.4, 0.0, ZR + Z_SH_TOP + 0.05)), ridgevent)
anchor("shingles", roof_pt(1.2, -2.6, Z_SH_TOP), shing)
anchor("underlay", roof_pt(2.8, -3.3, Z_UND_TOP), under)
anchor("drip", Vector((3.9, EY0 - 0.006, ZE + Z_DECK_TOP - 0.02)), drip)
anchor("deck", roof_pt(4.6, -3.7, Z_DECK_TOP), deck)
anchor("soffit", Vector((1.6, EY0 + 0.13, ZE - 0.205)))
anchor("attic", Vector((0.6, -2.2, H + 0.75)))
anchor("ridge_out", Vector((0.6, 0.0, ZR - 0.08)))
anchor("insulation", Vector((-1.6, -2.4, H + 0.2)))
anchor("panel", plane_pt(0.61, PV * 0.55, h0 + 0.03), panel_rig)
anchor("lock", LOCK_POS, cap_final)
# panel-local anchors (for the weather overlays; the panel is static 165-280)
hs = h0 + 0.02
anchor("p_center", plane_pt(0.61, 0.95, hs), panel_rig)
anchor("p_granule", plane_pt(0.36, 0.62, hs), panel_rig)
anchor("p_seal_a", plane_pt(0.06, -SH_OVERHANG + 5 * SH_EXP + 0.128, hs), panel_rig)
anchor("p_seal_b", plane_pt(1.16, -SH_OVERHANG + 5 * SH_EXP + 0.128, hs), panel_rig)
anchor("p_nail_a", plane_pt(0.06, -SH_OVERHANG + 3 * SH_EXP + 0.155, hs), panel_rig)
anchor("p_nail_b", plane_pt(1.16, -SH_OVERHANG + 3 * SH_EXP + 0.155, hs), panel_rig)
anchor("p_eave_a", plane_pt(0.0, -SH_OVERHANG, h0 + 0.004), panel_rig)
anchor("p_eave_b", plane_pt(1.22, -SH_OVERHANG, h0 + 0.004), panel_rig)
anchor("p_starter", plane_pt(1.0, 0.02, hs), panel_rig)
anchor("p_gutter_a", Vector((PX0 + 0.05, EY0 - 0.07, ZE - 0.05)), panel_rig)
anchor("p_gutter_b", Vector((PX1 - 0.05, EY0 - 0.07, ZE - 0.05)), panel_rig)
anchor("p_soffit", Vector((PX0 + 0.61, EY0 + 0.13, ZE - 0.205)), panel_rig)
anchor("p_up", plane_pt(0.61, PV, T_DECK * 0.5 - 0.1), panel_rig)
anchor("p_band_under", plane_pt(0.61, (PV_SH + PV_UND) / 2, T_DECK + 0.009), panel_rig)
anchor("p_band_deck", plane_pt(0.61, (PV_UND + PV) / 2, T_DECK), panel_rig)
anchor("p_rafter", Vector((PX0 + 0.35, -4.45, ZE - 0.08)), panel_rig)
anchor("p_attic", Vector((PX0 + 0.61, -4.3, ZE + 0.05)), panel_rig)
anchor("p_boot", base + Vector((0, 0, 0.36)), panel_rig)
anchor("p_underlay_edge", plane_pt(0.0, 0.42, T_DECK + 0.006), panel_rig)
anchor("p_deck_edge", plane_pt(0.0, 0.30, T_DECK * 0.5), panel_rig)
GRID_U = [0.10, 0.26, 0.44, 0.61, 0.78, 0.96, 1.12]
GRID_V = [1.34, 1.14, 0.94, 0.74, 0.54, 0.34, 0.14, -0.012]
for i, u in enumerate(GRID_U):
    for j, v in enumerate(GRID_V):
        # the flow sits on the course surface; courses raise it a little near each butt
        anchor(f"g{i}_{j}", plane_pt(u, v, hs + 0.006), panel_rig)

# ---------------------------------------------------------------- animation
def key(ob, frame, loc=None, rot=None):
    if loc is not None: ob.location = loc; ob.keyframe_insert("location", frame=frame)
    if rot is not None: ob.rotation_euler = rot; ob.keyframe_insert("rotation_euler", frame=frame)

LAYERS = [("caps", [caps, cap_final, ridgevent]), ("shingles", [shing]), ("underlay", [under]),
          ("drip", [drip]), ("deck", [deck])]
# anatomy: lift top-down; reassembly: settle bottom-up, final ridge cap last
UP = {"caps": (10, 36), "shingles": (28, 54), "underlay": (46, 72), "drip": (62, 84), "deck": (78, 104)}
DOWN = {"deck": (330, 350), "drip": (344, 360), "underlay": (354, 372), "shingles": (366, 384), "caps": (378, 390)}
for name, obs in LAYERS:
    for ob in obs:
        z0 = ob.location.copy(); z1 = z0 + Vector((0, 0, LIFT[name]))
        a, b = UP[name]; c, d = DOWN[name]
        key(ob, 0, z0); key(ob, a, z0); key(ob, b, z1); key(ob, c, z1)
        if ob is cap_final:
            key(ob, 386, z1); key(ob, LOCK_FRAME, z0)
        else:
            key(ob, d, z0)
        key(ob, FRAME_END, z0)

# the Proof Panel path; the return keys reuse the exact outbound values
p0 = panel_rig.location.copy(); r0 = Euler((0, 0, 0))
p1 = p0 + NF * 0.55
POSES = json.load(open(os.path.join(HERE, "camera_poses.json")))
ISO = POSES["panel_iso"]
p2 = p0 + Vector(ISO["offset"]); r2 = Euler(tuple(math.radians(a) for a in ISO["rot_deg"]))
for f, loc, rot in ((0, p0, r0), (112, p0, r0), (130, p1, r0), (165, p2, r2), (280, p2, r2), (315, p1, r0), (330, p0, r0), (FRAME_END, p0, r0)):
    key(panel_rig, f, loc.copy(), rot.copy())

def prop_key(name, pairs):
    for f, v in pairs:
        sc[name] = v; sc.keyframe_insert(f'["{name}"]', frame=f)
prop_key("dim", [(0, 0.0), (118, 0.0), (160, 1.0), (285, 1.0), (326, 0.0), (FRAME_END, 0.0)])
prop_key("wet", [(0, 0.0), (228, 0.0), (248, 1.0), (262, 1.0), (280, 0.0), (FRAME_END, 0.0)])

# ---------------------------------------------------------------- light: the LA calendar
sun_d = bpy.data.lights.new("Sun", "SUN"); sun_d.angle = math.radians(2.2)
sun = bpy.data.objects.new("Sun", sun_d); link(sun)
wd = bpy.data.worlds.new("World"); sc.world = wd; wd.use_nodes = True
bg = wd.node_tree.nodes["Background"]

def sun_dir(elev, azim):
    return Euler((0, math.radians(90 - elev), math.radians(azim)), "XYZ")

LIGHT = {   # elevation, azimuth, energy, colour, sky colour, sky strength
    "clear":  (52, -128, 3.3, (1.0, 0.972, 0.93), (0.66, 0.71, 0.78), 0.95),
    "heat":   (74, -112, 3.9, (1.0, 0.905, 0.78), (0.78, 0.72, 0.64), 0.85),
    "wind":   (27, -150, 3.6, (1.0, 0.93, 0.84), (0.70, 0.74, 0.80), 0.95),
    "rain":   (40, -120, 0.35, (0.85, 0.88, 0.93), (0.60, 0.64, 0.70), 1.55),
    "washed": (48, -125, 3.4, (0.985, 0.985, 1.0), (0.66, 0.72, 0.80), 1.0),
    "lock":   (48, -125, 3.75, (1.0, 0.985, 0.97), (0.68, 0.73, 0.80), 1.05),
}
def light_key(f, state):
    el, az, en, col, sky, ss = LIGHT[state]
    sun.rotation_euler = sun_dir(el, az); sun.keyframe_insert("rotation_euler", frame=f)
    sun_d.energy = en; sun_d.keyframe_insert("energy", frame=f)
    sun_d.color = col; sun_d.keyframe_insert("color", frame=f)
    bg.inputs[0].default_value = sky + (1.0,); bg.inputs[0].keyframe_insert("default_value", frame=f)
    bg.inputs[1].default_value = ss; bg.inputs[1].keyframe_insert("default_value", frame=f)

for f, s in ((0, "clear"), (120, "clear"), (165, "heat"), (192, "heat"), (212, "wind"), (222, "wind"),
             (240, "rain"), (262, "rain"), (280, "washed"), (LOCK_FRAME - 1, "washed"), (LOCK_FRAME + 4, "lock"),
             (FRAME_END, "washed")):
    light_key(f, s)

# ---------------------------------------------------------------- cameras (one choreography, two framings)
def make_cam(name, lens, sensor_fit):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_fit = sensor_fit; cd.sensor_width = 36.0; cd.sensor_height = 36.0
    cd.clip_start = 0.1; cd.clip_end = 900
    cam = bpy.data.objects.new(name, cd); link(cam)
    tgt = bpy.data.objects.new(name + "_T", None); link(tgt)
    c = cam.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    return cam, tgt

def cam_keys(cam, tgt, poses):
    for f, (loc, look, lens, shx, shy) in poses:
        cam.location = loc; cam.keyframe_insert("location", frame=f)
        tgt.location = look; tgt.keyframe_insert("location", frame=f)
        cam.data.lens = lens; cam.data.keyframe_insert("lens", frame=f)
        cam.data.shift_x = shx; cam.data.keyframe_insert("shift_x", frame=f)
        cam.data.shift_y = shy; cam.data.keyframe_insert("shift_y", frame=f)

for name, fit in (("desktop", "HORIZONTAL"), ("portrait", "VERTICAL")):
    cam, tgt = make_cam("Cam_" + name, 40, fit)
    poses = []
    for f, pose in POSES[name]:
        poses.append((f, (Vector(pose["loc"]), Vector(pose["look"]), pose["lens"], pose.get("sx", 0.0), pose.get("sy", 0.0))))
    cam_keys(cam, tgt, poses)
    # depth of field only while the camera is close to the panel
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = panel_rig
    for f, fs in ((0, 22.0), (118, 22.0), (160, POSES["dof_fstop"]), (285, POSES["dof_fstop"]), (326, 22.0), (FRAME_END, 22.0)):
        cam.data.dof.aperture_fstop = fs; cam.data.dof.keyframe_insert("aperture_fstop", frame=f)

# ease every curve: Bezier with auto-clamped handles gives ease-in/out between holds
for ob in list(bpy.data.objects) + [sc, sun_d, wd.node_tree] + [o.data for o in bpy.data.objects if o.type == "CAMERA"]:
    ad = getattr(ob, "animation_data", None)
    if not ad or not ad.action: continue
    for fc in getattr(ad.action, "fcurves", []) or []:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"; kp.handle_left_type = "AUTO_CLAMPED"; kp.handle_right_type = "AUTO_CLAMPED"

# ---------------------------------------------------------------- render settings
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "Standard"
sc.view_settings.exposure = POSES.get("exposure", -0.6)
ee = sc.eevee
for attr, val in (("taa_render_samples", 24), ("use_raytracing", True), ("use_shadows", True),
                  ("shadow_ray_count", 2), ("shadow_step_count", 8)):
    try: setattr(ee, attr, val)
    except Exception: pass
sc.render.film_transparent = False

meta = {"frames": FRAME_END + 1, "fps": 30, "timeline": TL, "lock": LOCK_FRAME, "stills": STILLS,
        "panel": {"width_m": PX1 - PX0, "upslope_m": PV}, "anchors": sorted(ANCH.keys())}
sc["meta"] = json.dumps(meta)
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
