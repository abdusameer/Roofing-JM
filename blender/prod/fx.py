"""Weather as physical effects in the scene (no drawn overlays):
rain = motion-blurred 3D drops that die on contact, contact splashes on the panel, water beads,
thin runoff, and drops leaving the drip edge; wind = fine dust and swaying foliage;
heat = a thin refractive shimmer sheet above the panel (restrained, no glow)."""
import bpy, bmesh, math
from mathutils import Vector
from common import *

def _hidden_obj(name, bm, coll, mat=None):
    ob = mesh_from_bm(name, bm, coll, (mat,) if mat else ())
    ob.hide_render = True; ob.hide_viewport = True
    return ob

def drop_mesh(name, coll, mat, length, radius):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * length, v.co.y * radius, v.co.z * radius))    # long along X (velocity axis)
    ob = mesh_from_bm(name, bm, coll, (mat,))
    for p in ob.data.polygons: p.use_smooth = True
    ob.location = (0, 0, -50)
    return ob

def plane_emitter(name, coll, x0, x1, y0, y1, z, flip=True):
    bm = bmesh.new()
    vs = [bm.verts.new(c) for c in ((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z))]
    f = bm.faces.new(vs if not flip else list(reversed(vs)))
    ob = mesh_from_bm(name, bm, coll)
    ob.show_instancer_for_render = False; ob.show_instancer_for_viewport = False
    return ob

def particles(ob, name, **kw):
    mod = ob.modifiers.new(name, "PARTICLE_SYSTEM")
    ps = ob.particle_systems[-1]; st = ps.settings; st.name = name
    for k, v in kw.items():
        if "." in k:
            a, b = k.split("."); setattr(getattr(st, a), b, v)
        else: setattr(st, k, v)
    return ps

def rain(coll, M, panel_shingles, killers, t0, t1):
    drop = drop_mesh("RainDrop", coll, M["rain"], 0.009, 0.0019)
    rain_kw = dict(type="EMITTER", frame_start=t0 - 14, frame_end=t1, lifetime=40, emit_from="FACE",
                   physics_type="NEWTON", normal_factor=0.0, object_align_factor=(0.9, 0.35, -9.2), factor_random=0.6,
                   render_type="OBJECT", instance_object=drop, particle_size=1.0, size_random=0.55,
                   use_rotations=True, rotation_mode="VEL", use_scale_instance=True, **{"effector_weights.gravity": 0.0})
    em = plane_emitter("RainEmitter", coll, -16.0, 4.0, -18.0, 2.0, 11.0)
    particles(em, "Rain", count=36000, **rain_kw)
    # denser rain in the hero volume between the camera and the Proof Panel, so streaks read at every depth
    near = plane_emitter("RainEmitterNear", coll, -11.8, -5.6, -11.5, -4.2, 9.0)
    particles(near, "RainNear", count=16000, **rain_kw)
    for k in killers:
        k.modifiers.new("Collision", "COLLISION"); k.collision.use_particle_kill = True
    # contact splashes off the panel's top surface
    up = panel_shingles.vertex_groups.new(name="up")
    n_up = Vector((0, -SA, CA))
    ids = [v.index for v in panel_shingles.data.vertices]
    top = set()
    for p in panel_shingles.data.polygons:
        if p.normal.dot(n_up) > 0.92: top.update(p.vertices)
    up.add(list(top), 1.0, "REPLACE")
    splash = drop_mesh("SplashDrop", coll, M["water"], 0.0018, 0.0014)
    ps = particles(panel_shingles, "Splash", type="EMITTER", count=9000, frame_start=t0 + 4, frame_end=t1 - 2, lifetime=6, lifetime_random=0.5,
                   emit_from="FACE", physics_type="NEWTON", normal_factor=0.65, factor_random=0.45, render_type="OBJECT", instance_object=splash,
                   particle_size=1.0, size_random=0.6, use_rotations=True, rotation_mode="VEL")
    ps.vertex_group_density = "up"
    # water beads that grow while the surface wets and shrink as it dries
    bead = drop_mesh("Bead", coll, M["water"], 0.0026, 0.0026)
    bead.data.transform(__import__("mathutils").Matrix.Diagonal((0.42, 1, 1, 1)))      # X follows the surface normal
    ps = particles(panel_shingles, "Beads", type="HAIR", count=2600, hair_length=0.004, use_advanced_hair=True, emit_from="FACE",
                   render_type="OBJECT", instance_object=bead, particle_size=1.0, size_random=0.7, use_rotations=True, rotation_mode="NOR")
    ps.vertex_group_density = "up"
    if hasattr(ps.settings, "use_scale_instance"): ps.settings.use_scale_instance = True
    return drop, bead, em

def runoff(coll, M, panel_rig, shingle_top, lanes=9):
    """Thin rivulets following the courses down to the drip edge and falling into the gutter."""
    from roof import PLANES, pt
    pl = PLANES[0]
    u0 = PX0 - EX0
    obs = []
    for i in range(lanes):
        u = u0 + 0.1 + i * (1.02 / (lanes - 1)) + rng.uniform(-0.03, 0.03)
        cu = bpy.data.curves.new(f"Runoff_{i}", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.0; cu.bevel_resolution = 2
        sp = cu.splines.new("POLY")
        pts = []
        v = rng.uniform(0.7, 1.35)
        while v > -SH_OVER:
            pts.append(pt(pl, u + 0.004 * math.sin(v * 37), v, shingle_top(v) + 0.0012)); v -= 0.035
        lip = pt(pl, u, -SH_OVER - 0.004, shingle_top(-SH_OVER) - 0.002)
        pts += [lip, lip + Vector((0, -0.006, -0.03)), lip + Vector((0, -0.01, -0.07))]
        sp.points.add(len(pts) - 1)
        for p, co in zip(sp.points, pts): p.co = (co.x, co.y, co.z, 1.0)
        ob = bpy.data.objects.new(f"Runoff_{i}", cu); coll.objects.link(ob); cu.materials.append(M["water"])
        mw = ob.matrix_world.copy(); ob.parent = panel_rig; ob.matrix_parent_inverse = panel_rig.matrix_world.inverted()
        obs.append(ob)
    # drops leaving the downslope edge (emitter strip along the panel's drip edge lip)
    bm = bmesh.new()
    a = pt(pl, u0 + 0.02, -SH_OVER - 0.006, H_SHB); b = pt(pl, u0 + 1.2, -SH_OVER - 0.006, H_SHB)
    vs = [bm.verts.new(c) for c in (a, b, b + Vector((0, 0, -0.004)), a + Vector((0, 0, -0.004)))]
    bm.faces.new(vs)
    em = mesh_from_bm("EdgeDripEmitter", bm, coll); em.show_instancer_for_render = False
    em.parent = panel_rig; em.matrix_parent_inverse = panel_rig.matrix_world.inverted()
    return obs, em

def edge_drips(em, M, coll, t0, t1):
    drip = drop_mesh("EdgeDrop", coll, M["water"], 0.003, 0.0019)
    particles(em, "EdgeDrips", type="EMITTER", count=1300, frame_start=t0 + 6, frame_end=t1 + 4, lifetime=14, emit_from="FACE",
              physics_type="NEWTON", normal_factor=0.0, object_align_factor=(0.0, -0.15, -0.4), factor_random=0.1,
              render_type="OBJECT", instance_object=drip, particle_size=1.0, size_random=0.5, use_rotations=True, rotation_mode="VEL",
              use_scale_instance=True)
    return drip

def dust(coll, M, t0, t1):
    # each mote is already a fine streak along its velocity (X): motion blur would dilute a 3 mm speck to nothing
    mote = drop_mesh("DustMote", coll, M["dust"], 0.03, 0.0011)
    if hasattr(mote, "cycles") and hasattr(mote.cycles, "use_motion_blur"): mote.cycles.use_motion_blur = False
    em = plane_emitter("DustEmitter", coll, -16.0, -15.6, -16.0, 2.0, 0.6, flip=False)
    em.rotation_euler = (0, math.radians(90), 0); em.location = (0, 0, 0)
    bm = bmesh.new()
    vs = [bm.verts.new(c) for c in ((-15.0, -16.0, 0.8), (-15.0, 2.0, 0.8), (-15.0, 2.0, 9.0), (-15.0, -16.0, 9.0))]
    bm.faces.new(vs); em2 = mesh_from_bm("DustSheet", bm, coll); em2.show_instancer_for_render = False
    bpy.data.objects.remove(em)
    particles(em2, "Dust", type="EMITTER", count=9000, frame_start=t0 - 18, frame_end=t1, lifetime=60, emit_from="FACE",
              physics_type="NEWTON", normal_factor=0.0, object_align_factor=(6.5, 2.2, 0.25), factor_random=1.4,
              render_type="OBJECT", instance_object=mote, particle_size=1.0, size_random=0.8, use_rotations=True, rotation_mode="VEL",
              **{"effector_weights.gravity": 0.0})
    # a denser stream crossing the Proof Panel's hero position
    bm = bmesh.new()
    vs = [bm.verts.new(c) for c in ((-12.5, -11.0, 2.6), (-12.5, -2.5, 2.6), (-12.5, -2.5, 6.8), (-12.5, -11.0, 6.8))]
    bm.faces.new(vs); em3 = mesh_from_bm("DustSheetNear", bm, coll); em3.show_instancer_for_render = False
    particles(em3, "DustNear", type="EMITTER", count=7000, frame_start=t0 - 8, frame_end=t1, lifetime=40, emit_from="FACE",
              physics_type="NEWTON", normal_factor=0.0, object_align_factor=(6.0, 1.6, 0.3), factor_random=1.0,
              render_type="OBJECT", instance_object=mote, particle_size=1.0, size_random=0.7, use_rotations=True, rotation_mode="VEL",
              **{"effector_weights.gravity": 0.0})
    for o in (em2, em3):
        st = o.particle_systems[0].settings
        if hasattr(st, "use_scale_instance"): st.use_scale_instance = True
    return em2, mote

def heat_sheet(coll, M, panel_rig, center, size=(2.0, 1.0)):
    """Vertical sheet just behind the panel's upper edge, facing the camera's side (-Y): what it bends is
    the background seen above the panel, like heat haze over a sunlit roof."""
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
    sx, sz = size
    y = 0.98                                  # behind the deck's upper edge (PV/2 run ~0.85 m upslope)
    cs = [(-sx / 2, y, 0.18), (sx / 2, y, 0.18), (sx / 2, y, 0.18 + sz), (-sx / 2, y, 0.18 + sz)]
    vs = [bm.verts.new(center + Vector(c)) for c in cs]
    f = bm.faces.new(vs)
    for lo, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lo[uv].uv = (u, v)
    ob = mesh_from_bm("HeatShimmer", bm, coll, (M["heat"],))
    ob.visible_shadow = False; ob.visible_diffuse = False; ob.visible_glossy = False
    return ob
