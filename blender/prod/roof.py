"""Roof assembly at real scale: hip roof, Owens Corning Duration-style laminated shingles over a
synthetic underlayment, OSB deck, eave drip edge, starter course, hip/ridge caps over a ridge vent,
fascia, vented soffit, K-style gutter, rafters, and a plumbing-vent boot. Every layer is its own
named object; the Proof Panel is cut from the same objects with the same prisms that cut the opening."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from common import *

# ------------------------------------------------------------------ roof planes
def planes():
    """Each plane: eave start A (at the fascia face, deck-underside height), unit eave direction e,
    inward horizontal w, eave length Lp."""
    out = []
    for name, a, b in (("Front", (EX0, EY0), (EX1, EY0)), ("Right", (EX1, EY0), (EX1, EY1)),
                       ("Back", (EX1, EY1), (EX0, EY1)), ("Left", (EX0, EY1), (EX0, EY0))):
        A = Vector((a[0], a[1], ZE)); B = Vector((b[0], b[1], ZE))
        e = (B - A); Lp = e.length; e.normalize()
        w = Vector((-e.y, e.x, 0.0))                 # inward (left of the eave direction)
        out.append(dict(name=name, A=A, e=e, w=w, Lp=Lp,
                        up=Vector((w.x * CA, w.y * CA, SA)), n=Vector((-w.x * SA, -w.y * SA, CA))))
    return out

PLANES = planes()

def pt(pl, u, v, h):
    """Plane-local (u along eave, v up-slope from the fascia line, h along the roof normal)."""
    return pl["A"] + pl["e"] * u + pl["up"] * v + pl["n"] * h

def clip_to_plane(bm, i):
    """Keep only the part of the mesh inside roof plane i (hip bisector planes and the ridge)."""
    pl = PLANES[i]
    for j, q in enumerate(PLANES):
        if j == i: continue
        nrm = Vector((pl["w"].x - q["w"].x, pl["w"].y - q["w"].y, 0.0))
        if nrm.length < 1e-6: continue
        c = pl["A"].dot(Vector((pl["w"].x, pl["w"].y, 0))) - q["A"].dot(Vector((q["w"].x, q["w"].y, 0)))
        # plane: p . nrm = c  ->  a point on it along nrm
        co = nrm * (c / nrm.length_squared)
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=co, plane_no=nrm.normalized(), clear_outer=True)

# ------------------------------------------------------------------ layer shells (deck, underlayment)
def hip_shell(name, h0, h1, coll, mat, uv=True):
    """Closed hip-roof shell between normal offsets h0..h1 (equal pitches -> vertical translation)."""
    bm = bmesh.new()
    z0, z1 = h0 / CA, h1 / CA
    def ring(z):
        e = [bm.verts.new((EX0, EY0, ZE + z)), bm.verts.new((EX1, EY0, ZE + z)), bm.verts.new((EX1, EY1, ZE + z)), bm.verts.new((EX0, EY1, ZE + z))]
        r = [bm.verts.new((-RH, 0, ZR + z)), bm.verts.new((RH, 0, ZR + z))]
        return e, r
    (b1, b2, b3, b4), (r1, r2) = ring(z0)
    (t1, t2, t3, t4), (s1, s2) = ring(z1)
    tops = [(t1, t2, s2, s1), (t2, t3, s2), (t3, t4, s1, s2), (t4, t1, s1)]
    bots = [(b1, r1, r2, b2), (b2, r2, b3), (b3, r2, r1, b4), (b4, r1, b1)]
    for f in tops + bots: bm.faces.new(f)
    for a, b, c, d in ((b1, b2, t2, t1), (b2, b3, t3, t2), (b3, b4, t4, t3), (b4, b1, t1, t4)): bm.faces.new((a, b, c, d))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if uv:
        lay = bm.loops.layers.uv.new("UVMap")
        for f in bm.faces:
            nz = f.normal.z
            best = max(range(4), key=lambda k: f.normal.dot(PLANES[k]["n"]) if abs(nz) > 0.5 else f.normal.dot(-Vector((PLANES[k]["w"].x, PLANES[k]["w"].y, 0))))
            pl = PLANES[best]
            for lo in f.loops:
                d = lo.vert.co - pl["A"]
                lo[lay].uv = (d.dot(pl["e"]), d.dot(pl["up"]))
    return mesh_from_bm(name, bm, coll, (mat,))

# ------------------------------------------------------------------ shingles
def shingle_plane(i, mats, coll, near_box=None):
    """Laminated architectural shingles for plane i: base layer + random 'teeth', each course
    tilting over the two below, staggered offsets. Returns (main_obj, near_bm or None)."""
    pl = PLANES[i]
    bm = bmesh.new(); tone = bm.faces.layers.float.new("tone"); shadow = bm.faces.layers.float.new("shadow")
    nb = None
    if near_box:
        nb = bmesh.new(); ntone = nb.faces.layers.float.new("tone"); nshadow = nb.faces.layers.float.new("shadow")
    vmax = (EY1 - EY0) / 2 / CA + 0.05
    off_prev, k = 0.0, 0
    def h_at(v, vb, r):
        t = (v - vb) / SH_H
        return H_SHB + r * max(0.0, 1.0 - t)
    while True:
        vb = -SH_OVER + k * SH_EXP
        if vb > vmax: break
        r = T_START if k == 0 else (T_START + T_BASE + T_TAB if k == 1 else 2 * T_BASE + T_TAB)
        off = rng.uniform(0.0, SH_W)
        while abs(((off - off_prev) % SH_W)) < 0.12 or abs(((off - off_prev) % SH_W) - SH_W) < 0.12:
            off = rng.uniform(0.0, SH_W)
        off_prev = off
        u_lo = vb * CA - SH_W - 0.2; u_hi = pl["Lp"] - vb * CA + SH_W
        u0 = u_lo + ((off - u_lo) % SH_W) - SH_W
        while u0 < u_hi:
            target_near = near_box and (pl["name"] == "Front") and (u0 + SH_W > near_box[0] and u0 < near_box[1]) and vb < near_box[2]
            B, TL, SL = (nb, ntone, nshadow) if target_near else (bm, tone, shadow)
            v0, v1 = vb, vb + SH_H
            def box(ua, ub, va, vb_, hb_extra, th, tval, sval):
                cs = []
                for (uu, vv) in ((ua, va), (ub, va), (ub, vb_), (ua, vb_)):
                    cs.append(pt(pl, uu, vv, h_at(vv, vb, r) + hb_extra))
                for (uu, vv) in ((ua, va), (ub, va), (ub, vb_), (ua, vb_)):
                    cs.append(pt(pl, uu, vv, h_at(vv, vb, r) + hb_extra + th))
                add_box(B, cs, 0, None, None)
                for f in B.faces[-6:]: f[TL] = tval; f[SL] = sval
            # base layer (its exposed strips read as the darker laminate shadow band)
            box(u0, u0 + SH_W, v0, v1, 0.0, T_BASE, rng.uniform(0.0, 0.25), 1.0)
            # top-layer teeth across the exposure, running up under the next course; each shingle
            # carries its own granule-blend bias so the field reads mottled, not gridded
            bias = rng.uniform(-0.25, 0.25)
            ut = u0 + rng.uniform(0.0, 0.03)
            while ut < u0 + SH_W - 0.05:
                wdt = min(rng.choice((rng.uniform(0.08, 0.14), rng.uniform(0.14, 0.26))), u0 + SH_W - ut)
                d0 = rng.uniform(0.0, 0.012)
                box(ut, ut + wdt, v0 + d0, v0 + 0.205, T_BASE, T_TAB, min(1.0, max(0.0, rng.uniform(0.15, 1.0) + bias)), 0.0)
                ut += wdt + rng.uniform(0.018, 0.07)
            u0 += SH_W
        k += 1
    clip_to_plane(bm, i)
    if nb is not None: clip_to_plane(nb, i)
    ob = mesh_from_bm(f"Shingles_{pl['name']}", bm, coll, mats)
    return ob, nb

# ------------------------------------------------------------------ starter, drip edge, fascia, soffit, gutter
def strip_along_eaves(name, coll, mat, profile, extend=0.3, clip=True, thickness=None):
    """Extrude a (y_in, z) profile along every eave and clip each run at the hips. Closed profiles
    become solids directly; open profiles (sheet metal) get real thickness from Solidify so every
    piece is a watertight solid that booleans can cut."""
    obs = []
    closed = thickness is None
    for i, pl in enumerate(PLANES):
        bm = bmesh.new()
        rows = []
        for u in (-extend, pl["Lp"] + extend):
            base = Vector((pl["A"].x, pl["A"].y, 0.0))          # profile z values are absolute heights
            rows.append([bm.verts.new(base + pl["e"] * u + pl["w"] * y + Vector((0, 0, z))) for y, z in profile])
        n = len(profile)
        for k in range(n if closed else n - 1):
            j = (k + 1) % n
            bm.faces.new((rows[0][k], rows[0][j], rows[1][j], rows[1][k]))
        if closed: bm.faces.new(rows[0]); bm.faces.new(list(reversed(rows[1])))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        if clip: clip_to_plane(bm, i)
        ob = mesh_from_bm(f"{name}_{pl['name']}", bm, coll, (mat,))
        if not closed:
            so = ob.modifiers.new("solidify", "SOLIDIFY"); so.thickness = thickness; so.offset = 0.0; so.use_rim = True; so.use_even_offset = True
            apply_modifiers(ob)
        obs.append(ob)
    return obs

def deck_top_z():
    return ZE + T_DECK / CA

def drip_profile():
    """Open sheet profile: 2-inch flange on the deck, kick, 40 mm drip leg, hemmed edge."""
    z0 = deck_top_z() + 0.0006
    run = 0.05
    return [(run * CA, z0 + run * SA), (0.0, z0), (-0.008, z0 - 0.007), (-0.008, z0 - 0.042), (-0.004, z0 - 0.047), (-0.0015, z0 - 0.044)]

def fascia_profile():
    z0 = deck_top_z()
    return [(0.0, z0 - 0.002), (0.0, z0 - 0.195), (0.038, z0 - 0.195), (0.038, z0 - 0.002)]

def soffit_profile():
    z0 = deck_top_z()
    return [(0.038, z0 - 0.195), (O, z0 - 0.195), (O, z0 - 0.183), (0.038, z0 - 0.183)]

def vent_profile():
    z0 = deck_top_z()
    return [(0.07, z0 - 0.1975), (0.125, z0 - 0.1975), (0.125, z0 - 0.194), (0.07, z0 - 0.194)]

def gutter_profile():
    """5-inch K-style gutter (outward = negative y_in), 1.0 mm wall rendered as a closed profile."""
    z0 = deck_top_z() - 0.032
    pts = [(0.0, 0.0), (0.0, -0.104), (-0.012, -0.108), (-0.068, -0.108), (-0.088, -0.098), (-0.104, -0.078), (-0.099, -0.058),
           (-0.115, -0.040), (-0.121, -0.012), (-0.127, 0.0), (-0.122, 0.007), (-0.116, 0.004)]
    return [(y - 0.0025, z0 + z) for y, z in pts]

def gutters(coll, mat):
    obs = strip_along_eaves("Gutter", coll, mat, gutter_profile(), extend=0.14, clip=False, thickness=0.0012)
    # hangers every 600 mm across the opening
    bm = bmesh.new()
    z0 = deck_top_z() - 0.032
    for pl in PLANES:
        u = 0.3
        while u < pl["Lp"] - 0.2:
            base = Vector((pl["A"].x, pl["A"].y, 0.0)) + pl["e"] * u
            a = base + pl["w"] * 0.0 + Vector((0, 0, z0 - 0.002)); b = base + pl["w"] * -0.123 + Vector((0, 0, z0 + 0.002))
            e = pl["e"] * 0.0125; up = Vector((0, 0, 0.0015))
            add_box(bm, [a - e, a + e, b + e, b - e, a - e + up, a + e + up, b + e + up, b - e + up])
            u += 0.6
    obs.append(mesh_from_bm("Gutter_Hangers", bm, coll, (mat,)))
    # downspout at the front-left corner: outlet, two elbows, run down the corner of the wall
    bm = bmesh.new()
    x, y = EX0 + 0.26, EY0 - 0.06
    def rect(cx, cy, z0, z1, wx=0.076, wy=0.05):
        add_box(bm, [Vector((cx - wx / 2, cy - wy / 2, z0)), Vector((cx + wx / 2, cy - wy / 2, z0)), Vector((cx + wx / 2, cy + wy / 2, z0)), Vector((cx - wx / 2, cy + wy / 2, z0)),
                     Vector((cx - wx / 2, cy - wy / 2, z1)), Vector((cx + wx / 2, cy - wy / 2, z1)), Vector((cx + wx / 2, cy + wy / 2, z1)), Vector((cx - wx / 2, cy + wy / 2, z1))])
    zg = z0 - 0.11
    rect(x, y, zg - 0.18, zg)
    rect(x, -W / 2 - 0.05, 0.25, zg - 0.30, 0.076, 0.05)
    rect(x, (y + (-W / 2 - 0.05)) / 2, zg - 0.36, zg - 0.16, 0.076, 0.10)
    rect(x, -W / 2 - 0.05, 0.05, 0.25, 0.076, 0.05)
    obs.append(mesh_from_bm("Downspout", bm, coll, (mat,)))
    return obs

# ------------------------------------------------------------------ rafters (structure, revealed when the deck lifts)
def rafters(coll, mat):
    bm = bmesh.new()
    def rafter(x0, y0, x1, y1):
        d = Vector((x1 - x0, y1 - y0, 0)); d.normalize(); s = Vector((-d.y, d.x, 0)) * 0.019
        a = Vector((x0, y0, deck_z(x0, y0))); b = Vector((x1, y1, deck_z(x1, y1)))
        add_box(bm, [a - s - Vector((0, 0, 0.184)), a + s - Vector((0, 0, 0.184)), b + s - Vector((0, 0, 0.184)), b - s - Vector((0, 0, 0.184)), a - s, a + s, b + s, b - s])
    x = EX0 + 0.45
    while x < EX1 - 0.3:
        yend = min(0.0, (x - EX0) + EY0, (EX1 - x) + EY0)
        if yend - EY0 > 0.25:
            rafter(x, EY0 + 0.04, x, yend - 0.02); rafter(x, EY1 - 0.04, x, -yend + 0.02)
        x += 0.61
    y = EY0 + 0.45
    while y < EY1 - 0.3:
        xend = min(-RH, EX0 + (y - EY0), EX0 + (EY1 - y))
        if xend - EX0 > 0.25:
            rafter(EX0 + 0.04, y, xend - 0.02, y); rafter(EX1 - 0.04, y, -xend + 0.02, y)
        y += 0.61
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        rafter(sx * (EX1 - 0.06), sy * (EY1 - 0.06), sx * RH, 0.0)
    rafter(-RH, 0.0, RH, 0.0)
    return mesh_from_bm("Rafters", bm, coll, (mat,))

# ------------------------------------------------------------------ hip and ridge caps, ridge vent
def cap_height():
    return H_SHB + 2 * T_BASE + T_TAB + T_BASE + T_TAB + 0.0015

def tent(bm, p0, p1, na, nb, width, thick, lift):
    d = (p1 - p0).normalized()
    bis = (na + nb).normalized()
    F0 = p0 + bis * (lift / na.dot(bis)); F1 = p1 + bis * (lift / na.dot(bis))
    for n in (na, nb):
        wv = n.cross(d).normalized()
        if wv.z > 0: wv = -wv
        # three segments across the fold give a soft rounded bend
        prof = [(0.0, 0.0), (0.012, 0.0006), (0.04, 0.0002), (width, -0.0012)]
        ring0 = [F0 + wv * s + n * hh for s, hh in prof]; ring1 = [F1 + wv * s + n * hh for s, hh in prof]
        top0 = [p + n * thick for p in ring0]; top1 = [p + n * thick for p in ring1]
        vb0 = [bm.verts.new(p) for p in ring0]; vb1 = [bm.verts.new(p) for p in ring1]
        vt0 = [bm.verts.new(p) for p in top0]; vt1 = [bm.verts.new(p) for p in top1]
        for k in range(len(prof) - 1):
            bm.faces.new((vt0[k], vt0[k + 1], vt1[k + 1], vt1[k]))
            bm.faces.new((vb0[k], vb1[k], vb1[k + 1], vb0[k + 1]))
        for (a, b) in ((vb0, vt0), (vb1, vt1)):
            for k in range(len(prof) - 1): bm.faces.new((a[k], a[k + 1], b[k + 1], b[k]))
        bm.faces.new((vb0[-1], vb1[-1], vt1[-1], vt0[-1]))

def caps_and_vent(coll, cap_mat, vent_mat):
    h = cap_height()
    NF, NB = PLANES[0]["n"], PLANES[2]["n"]
    NR, NL = PLANES[1]["n"], PLANES[3]["n"]
    ridge_a, ridge_b = Vector((-RH, 0, ZR)), Vector((RH, 0, ZR))
    bm = bmesh.new()
    tent(bm, ridge_a + Vector((0.08, 0, 0)), ridge_b - Vector((0.08, 0, 0)), NF, NB, 0.14, 0.024, h)
    vent = mesh_from_bm("RidgeVent", bm, coll, (vent_mat,))
    hips = [(Vector((EX0, EY0, ZE)), ridge_a, NF, NL), (Vector((EX1, EY0, ZE)), ridge_b, NF, NR),
            (Vector((EX1, EY1, ZE)), ridge_b, NB, NR), (Vector((EX0, EY1, ZE)), ridge_a, NB, NL)]
    bm = bmesh.new(); tone = bm.faces.layers.float.new("tone")
    for a, b, na, nb in hips:
        a = a + (b - a).normalized() * 0.0
        ln = (b - a).length; d = (b - a).normalized(); s = 0.0; n = 0
        while s < ln - 0.08:
            nf = len(bm.faces)
            tent(bm, a + d * s, a + d * min(s + 0.305, ln), na, nb, 0.152, 0.0042, h + (n % 2) * 0.0021)
            tv = rng.uniform(0.2, 0.9)
            for f in bm.faces[nf:]: f[tone] = tv
            s += SH_EXP; n += 1
    # ridge caps over the vent, left to right; the final cap is its own object (the lock piece)
    lift = h + 0.026
    ln = (ridge_b - ridge_a).length; d = (ridge_b - ridge_a).normalized(); s = 0.0; n = 0
    while s + SH_EXP < ln - 0.305:
        nf = len(bm.faces)
        tent(bm, ridge_a + d * s, ridge_a + d * (s + 0.305), NF, NB, 0.16, 0.0042, lift + (n % 2) * 0.0021)
        tv = rng.uniform(0.2, 0.9)
        for f in bm.faces[nf:]: f[tone] = tv
        s += SH_EXP; n += 1
    caps = mesh_from_bm("HipRidgeCaps", bm, coll, (cap_mat,))
    bm = bmesh.new(); tone = bm.faces.layers.float.new("tone")
    tent(bm, ridge_a + d * (ln - 0.305), ridge_b, NF, NB, 0.16, 0.0042, lift + 0.0042)
    for f in bm.faces: f[tone] = 0.55
    final = mesh_from_bm("RidgeCap_Final", bm, coll, (cap_mat,))
    return caps, vent, final, ridge_a + d * (ln - 0.15)

# ------------------------------------------------------------------ the Proof Panel cut
def prism(v_top, name="PanelPrism"):
    """L-shaped cutter over the eave overhang and the roof above the wall plate, x in [PX0, PX1]."""
    py = EY0 + v_top * CA
    prof = [(EY0 - 0.5, ZE - 0.26), (-W / 2 - 0.001, ZE - 0.26), (-W / 2 - 0.001, H + 0.002), (py, H + 0.002), (py, 30.0), (EY0 - 0.5, 30.0)]
    bm = bmesh.new()
    a = [bm.verts.new((PX0, y, z)) for y, z in prof]; b = [bm.verts.new((PX1, y, z)) for y, z in prof]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    for k in range(len(prof)):
        j = (k + 1) % len(prof); bm.faces.new((a[k], a[j], b[j], b[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = mesh_from_bm(name, bm, bpy.context.scene.collection)
    ob.hide_render = True; ob.hide_viewport = True
    return ob

def pipe_boot(coll, rubber, pipe_mat, base_mat):
    """2-inch plumbing vent through the panel: pipe, rubber collar, flange shingled in."""
    pl = PLANES[0]
    u, v = (PX0 - EX0) + 0.61, 1.05
    base = pt(pl, u, v, H_SHB)
    obs = []
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=40, radius1=0.0302, radius2=0.0302, depth=0.62)
    p = mesh_from_bm("PipeVent", bm, coll, (pipe_mat,)); p.location = base + Vector((0, 0, 0.18)); obs.append(p)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=40, radius1=0.085, radius2=0.036, depth=0.11)
    c = mesh_from_bm("PipeBoot_Collar", bm, coll, (rubber,)); c.location = base + Vector((0, 0, 0.065)); obs.append(c)
    bm = bmesh.new()
    cs = []
    for (du, dv, hh) in ((-0.17, -0.2, 0.0165), (0.17, -0.2, 0.0165), (0.17, 0.2, 0.003), (-0.17, 0.2, 0.003)):
        cs.append(pt(pl, u + du, v + dv, H_SHB + hh))
    cs += [c_ + pl["n"] * 0.0012 for c_ in cs]
    add_box(bm, cs)
    f = mesh_from_bm("PipeBoot_Flange", bm, coll, (base_mat,)); obs.append(f)
    return obs
