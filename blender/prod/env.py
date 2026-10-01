"""House body, landscaping, backdrop plates, sky and sun."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from common import *

def box_bm(bm, x0, x1, y0, y1, z0, z1):
    return add_box(bm, [Vector((x0, y0, z0)), Vector((x1, y0, z0)), Vector((x1, y1, z0)), Vector((x0, y1, z0)),
                        Vector((x0, y0, z1)), Vector((x1, y0, z1)), Vector((x1, y1, z1)), Vector((x0, y1, z1))])

def box_ob(name, coll, mat, x0, x1, y0, y1, z0, z1):
    bm = bmesh.new(); box_bm(bm, x0, x1, y0, y1, z0, z1)
    return mesh_from_bm(name, bm, coll, (mat,))

FRONT_WINDOWS = [(-3.75, 2.7, 0.45, 2.45), (0.55, 1.1, 0.16, 2.45), (3.55, 2.7, 0.45, 2.45)]   # (centre x, width, z0, z1)
LEFT_WINDOWS = [(-1.4, 2.2, 0.75, 2.45), (2.2, 1.3, 1.05, 2.45)]                               # (centre y, width, z0, z1)

def house(coll, M):
    t = 0.25
    walls = box_ob("Walls", coll, M["stucco"], -L / 2, L / 2, -W / 2, W / 2, 0.16, H)
    inner = box_ob("WallsInner", coll, M["stucco"], -L / 2 + t, L / 2 - t, -W / 2 + t, W / 2 - t, 0.0, H + 0.5)
    boolean(walls, inner, "DIFFERENCE"); bpy.data.objects.remove(inner)
    cutters = []
    for cx, w, z0, z1 in FRONT_WINDOWS:
        cutters.append(box_ob("cut", coll, None, cx - w / 2, cx + w / 2, -W / 2 - 0.1, -W / 2 + t + 0.1, z0, z1))
    for cy, w, z0, z1 in LEFT_WINDOWS:
        cutters.append(box_ob("cut", coll, None, -L / 2 - 0.1, -L / 2 + t + 0.1, cy - w / 2, cy + w / 2, z0, z1))
    for c in cutters: boolean(walls, c, "DIFFERENCE"); bpy.data.objects.remove(c)
    walls.data.materials.clear(); walls.data.materials.append(M["stucco"])
    bevel(walls, 0.006, 2); apply_modifiers(walls)
    # black aluminium frames with mullions, glass, and a warm lived-in interior behind
    bm = bmesh.new()
    gl = bmesh.new()
    fw = 0.055
    def frame_front(cx, w, z0, z1):
        y0, y1 = -W / 2 - 0.02, -W / 2 + 0.05
        box_bm(bm, cx - w / 2, cx + w / 2, y0, y1, z0, z0 + fw); box_bm(bm, cx - w / 2, cx + w / 2, y0, y1, z1 - fw, z1)
        box_bm(bm, cx - w / 2, cx - w / 2 + fw, y0, y1, z0, z1); box_bm(bm, cx + w / 2 - fw, cx + w / 2, y0, y1, z0, z1)
        n = max(1, round(w / 1.0))
        for k in range(1, n):
            xm = cx - w / 2 + k * w / n; box_bm(bm, xm - fw / 2, xm + fw / 2, y0, y1, z0, z1)
        box_bm(gl, cx - w / 2 + 0.01, cx + w / 2 - 0.01, -W / 2 + 0.012, -W / 2 + 0.02, z0 + 0.01, z1 - 0.01)
    def frame_left(cy, w, z0, z1):
        x0, x1 = -L / 2 - 0.02, -L / 2 + 0.05
        box_bm(bm, x0, x1, cy - w / 2, cy + w / 2, z0, z0 + fw); box_bm(bm, x0, x1, cy - w / 2, cy + w / 2, z1 - fw, z1)
        box_bm(bm, x0, x1, cy - w / 2, cy - w / 2 + fw, z0, z1); box_bm(bm, x0, x1, cy + w / 2 - fw, cy + w / 2, z0, z1)
        n = max(1, round(w / 1.0))
        for k in range(1, n):
            ym = cy - w / 2 + k * w / n; box_bm(bm, x0, x1, ym - fw / 2, ym + fw / 2, z0, z1)
        box_bm(gl, -L / 2 + 0.012, -L / 2 + 0.02, cy - w / 2 + 0.01, cy + w / 2 - 0.01, z0 + 0.01, z1 - 0.01)
    for wdef in FRONT_WINDOWS: frame_front(*wdef)
    for wdef in LEFT_WINDOWS: frame_left(*wdef)
    fr = mesh_from_bm("WindowFrames", bm, coll, (M["frame"],)); bevel(fr, 0.003, 2)
    mesh_from_bm("Glazing", gl, coll, (M["glass"],))
    # interior: floor, ceiling with warm downlights, a few silhouettes of furniture
    box_ob("InteriorFloor", coll, M["interior_floor"], -L / 2 + t, L / 2 - t, -W / 2 + t, W / 2 - t, 0.12, 0.16)
    box_ob("InteriorCeiling", coll, M["interior"], -L / 2 + t, L / 2 - t, -W / 2 + t, W / 2 - t, H - 0.02, H)
    for (x0, x1, y0, y1, z1) in ((-5.2, -2.6, -2.6, -1.6, 0.6), (2.6, 4.9, -2.9, -1.9, 0.62), (-1.0, 0.2, 1.0, 2.6, 0.95), (-5.0, -4.2, 1.5, 3.3, 1.9)):
        box_ob("Furniture", coll, M["furniture"], x0, x1, y0, y1, 0.16, z1)
    for x in (-4.0, -1.2, 1.6, 4.2):
        lt = bpy.data.lights.new("Downlight", "AREA"); lt.size = 0.6; lt.energy = 260; lt.color = (1.0, 0.78, 0.55)
        lo = bpy.data.objects.new("Downlight", lt); coll.objects.link(lo); lo.location = (x, -1.6, H - 0.05); lo.rotation_euler = (math.pi, 0, 0)
    box_ob("Plinth", coll, M["concrete"], -L / 2 - 0.06, L / 2 + 0.06, -W / 2 - 0.06, W / 2 + 0.06, 0.0, 0.16)
    return walls

def shrub(name, coll, mat, loc, size):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    for v in bm.verts:
        n = v.co.normalized()
        v.co = v.co * (1.0 + 0.18 * math.sin(v.co.x * 7.1 + 1.3) * math.cos(v.co.y * 6.3) + 0.12 * math.sin(v.co.z * 9.7))
    ob = mesh_from_bm(name, bm, coll, (mat,))
    ob.scale = (size[0], size[1], size[2]); ob.location = loc
    for p in ob.data.polygons: p.use_smooth = True
    m = ob.modifiers.new("disp", "DISPLACE")
    tex = bpy.data.textures.new(name + "_t", "CLOUDS"); tex.noise_scale = 0.18; m.texture = tex; m.strength = 0.22
    sub = ob.modifiers.new("sub", "SUBSURF"); sub.levels = 1; sub.render_levels = 2
    ob.modifiers.move(1, 0)
    return ob

def tree(name, coll, leaf_mat, bark_mat, loc, h, r):
    trunk = bpy.data.meshes.new(name + "_trunk"); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.16 * h / 8, radius2=0.1 * h / 8, depth=h * 0.6)
    bm.to_mesh(trunk); bm.free()
    t = bpy.data.objects.new(name + "_trunk", trunk); coll.objects.link(t); t.location = Vector(loc) + Vector((0, 0, h * 0.3)); t.data.materials.append(bark_mat)
    c = shrub(name + "_crown", coll, leaf_mat, Vector(loc) + Vector((0, 0, h * 0.68)), (r, r * 0.95, r * 0.8))
    return c

def landscape(coll, M, ground_radius=24.0, shrubs_on=True, trees_on=False):
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=96, radius=ground_radius)
    ground = mesh_from_bm("Ground", bm, coll, (M["lawn"],))
    box_ob("Walkway", coll, M["concrete"], -0.2, 1.3, -W / 2 - 6.5, -W / 2 - 0.06, 0.0, 0.03)
    box_ob("SidePath", coll, M["concrete"], -L / 2 - 1.4, -L / 2 - 0.06, -W / 2 - 1.2, W / 2 + 1.0, 0.0, 0.025)
    shrubs = []
    if not shrubs_on: return ground, [], []
    for i, (x, y, s) in enumerate(((-5.5, -4.75, 0.55), (-4.6, -4.75, 0.45), (-2.2, -4.75, 0.5), (2.2, -4.8, 0.55), (5.3, -4.75, 0.6),
                                   (-6.65, -3.2, 0.5), (-6.65, 0.4, 0.55), (-6.7, 3.4, 0.6))):
        shrubs.append(shrub(f"Shrub_{i}", coll, M["leaves"], (x, y, s * 0.75), (s * 1.3, s, s)))
    trees = []
    if not trees_on: return ground, shrubs, trees
    for i, (x, y, h, r) in enumerate(((-17, 6, 9, 3.2), (-11, 15, 11, 3.8), (4, 18, 10, 3.5), (16, 12, 9, 3.0), (-22, -6, 8, 2.8),
                                      (24, 2, 10, 3.3), (-28, 14, 12, 4.0), (10, 26, 11, 3.6), (-4, 24, 9, 3.2))):
        trees.append(tree(f"Tree_{i}", coll, M["leaves_dark"], M["bark"], (x, y, 0), h, r))
    # neighbour hedge line that bridges the lot into the backdrop's tree line
    for i in range(14):
        a = math.radians(-20 + i * 12)
        x, y = -7 + 34 * math.cos(math.radians(42) + a - math.radians(40)), -8 + 34 * math.sin(math.radians(42) + a - math.radians(40))
        shrubs.append(shrub(f"Hedge_{i}", coll, M["leaves_dark"], (x, y, 1.4), (3.2, 2.6, 2.0)))
    return ground, shrubs, trees

def backdrop(coll, mat, center=(-7.0, -8.0), radius=300.0, az_center=42.0, az_span=120.0, eye=5.0, horizon=0.78, img_aspect=3840 / 1648):
    """Cylindrical camera-only backdrop. Uniform angular mapping so plate pixels stay undistorted;
    the plate's horizon row sits at the camera's eye height (at infinity)."""
    v_span = az_span / img_aspect
    th_top, th_bot = horizon * v_span, -(1 - horizon) * v_span
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    nu, nv = 72, 24
    grid = []
    for j in range(nv + 1):
        th = math.radians(th_bot + (th_top - th_bot) * j / nv)
        row = []
        for i in range(nu + 1):
            az = math.radians(az_center + az_span / 2 - az_span * i / nu)
            row.append(bm.verts.new((center[0] + radius * math.cos(az), center[1] + radius * math.sin(az), eye + radius * math.tan(th))))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            f = bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
            for lo, (ii, jj) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                lo[uvl].uv = (ii / nu, jj / nv)
    ob = mesh_from_bm("Backdrop", bm, coll, (mat,))
    ob.visible_diffuse = False; ob.visible_shadow = False; ob.visible_transmission = True; ob.visible_volume_scatter = False   # seen through glass, rain and heat haze
    ob.visible_glossy = True
    return ob

def sky_and_sun(coll):
    sc = bpy.context.scene
    wd = bpy.data.worlds.new("Sky"); sc.world = wd; wd.use_nodes = True
    nt = wd.node_tree; bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky"); sky.sky_type = "MULTIPLE_SCATTERING"
    for attr, val in (("sun_disc", False), ("air_density", 1.0), ("aerosol_density", 1.4), ("dust_density", 1.4), ("ozone_density", 1.0)):
        if hasattr(sky, attr):
            try: setattr(sky, attr, val)
            except Exception: pass
    over = nt.nodes.new("ShaderNodeRGB"); over.outputs[0].default_value = (0.64, 0.65, 0.665, 1.0)
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    nt.links.new(sky.outputs[0], mix.inputs[6]); nt.links.new(over.outputs[0], mix.inputs[7])
    nt.links.new(mix.outputs[2], bg.inputs[0])
    sun_d = bpy.data.lights.new("Sun", "SUN"); sun_d.angle = math.radians(0.55)
    sun = bpy.data.objects.new("Sun", sun_d); coll.objects.link(sun)
    return dict(world=wd, sky=sky, mix=mix, bg=bg, sun=sun)
