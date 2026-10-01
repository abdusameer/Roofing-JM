"""Shared constants and mesh helpers for the production roof scene (Phase 1 rework)."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

# ------------------------------------------------------------------ house and roof dimensions (metres)
L, W, H = 12.0, 8.4, 2.75            # wall footprint, plate height
O = 0.50                             # eave overhang to the fascia face
P = 5.0 / 12.0                       # 5:12 pitch
A = math.atan(P); SA, CA = math.sin(A), math.cos(A)
EX0, EX1 = -L / 2 - O, L / 2 + O
EY0, EY1 = -W / 2 - O, W / 2 + O
RH = (EX1 - EX0) / 2 - (EY1 - EY0) / 2       # ridge half-length (equal-pitch hips at 45 deg in plan)
ZE = H + 0.02                                # deck underside at the fascia line
ZR = ZE + (EY1 - EY0) / 2 * P

# real material thicknesses, measured normal to the roof plane
T_DECK = 0.0111          # 7/16" OSB
T_DRIP = 0.0008
T_UND = 0.0012           # synthetic underlayment (lap step comes from the texture)
T_START = 0.0028
T_BASE = 0.0026          # laminated shingle base layer
T_TAB = 0.0024           # laminated top layer ("teeth")
H_UND = T_DECK + 0.0009                       # underlayment sits over the drip-edge flange
H_SHB = H_UND + T_UND                         # shingle bed (underlayment top)
SH_W, SH_H, SH_EXP = 1.0, 0.3366, 0.1429      # Owens Corning Duration: 39 3/8 x 13 1/4 in, 5 5/8 in exposure
SH_OVER = 0.019                               # first course overhangs the drip edge

# Proof Panel (eave corner beside the front-left hip), stepped cutaway at the top
PX0, PX1 = -4.70, -4.70 + 1.22
PV, PV_UND, PV_SH = 1.83, 1.64, 1.44

rng = random.Random(11)

def V(*a): return Vector(a)

def link(ob, coll):
    coll.objects.link(ob); return ob

def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c

def mesh_from_bm(name, bm, coll, mats=()):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    return ob

def add_box(bm, corners, mat_index=0, attr=None, layer=None):
    """corners: 8 Vectors (bottom 4 ccw, top 4 ccw)."""
    vs = [bm.verts.new(c) for c in corners]
    idx = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    fs = []
    for f in idx:
        face = bm.faces.new([vs[i] for i in f]); face.material_index = mat_index
        if layer is not None and attr is not None: face[layer] = attr
        fs.append(face)
    return fs

def set_origin(ob, world_point):
    """Move an object's origin (pivot) to world_point without moving its geometry."""
    mw = ob.matrix_world.copy()
    local = mw.inverted() @ world_point
    ob.data.transform(Matrix.Translation(-local))
    ob.matrix_world = mw @ Matrix.Translation(local)

def bevel(ob, width=0.0012, segments=2, limit="ANGLE"):
    m = ob.modifiers.new("bevel", "BEVEL"); m.width = width; m.segments = segments
    m.limit_method = limit; m.harden_normals = False
    return m

def shade_smooth(ob, angle=35):
    for p in ob.data.polygons: p.use_smooth = True
    try:
        mod = ob.modifiers.new("smooth_by_angle", "NODES")
    except Exception:
        return
    # Blender 4.1+: auto-smooth via the "Smooth by Angle" node group if present
    ng = bpy.data.node_groups.get("Smooth by Angle")
    if ng: mod.node_group = ng; mod["Input_1"] = math.radians(angle)
    else: ob.modifiers.remove(mod)

def apply_modifiers(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    for m in list(ob.modifiers): ob.modifiers.remove(m)
    old = ob.data; ob.data = me; bpy.data.meshes.remove(old)

def boolean(target, cutter, op):
    mod = target.modifiers.new("b", "BOOLEAN"); mod.operation = op; mod.object = cutter; mod.solver = "EXACT"
    apply_modifiers(target)

def deck_z(x, y):
    return ZE + P * min(y - EY0, EY1 - y, x - EX0, EX1 - x)
