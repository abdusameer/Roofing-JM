"""Procedural PBR materials at real-world scale (object-space metres). Dry and wet states are one
material driven by the scene property "wet" (0-1), read through a View Layer attribute so it can
be keyframed per frame. The "Night Sky" shingle blend follows the Owens Corning Duration COOL range
(dark charcoal with grey and blue-grey granules)."""
import bpy, os

def srgb(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)

class G:
    """Tiny node-graph helper."""
    def __init__(self, name):
        self.m = bpy.data.materials.new(name); self.m.use_nodes = True
        self.nt = self.m.node_tree; self.n = self.nt.nodes; self.ln = self.nt.links
        self.bsdf = self.n["Principled BSDF"]; self.out = self.n["Material Output"]
        self._coord = None
    def node(self, t, **kw):
        nd = self.n.new(t)
        for k, v in kw.items():
            if k.startswith("_"): setattr(nd, k[1:], v); continue
            sock = nd.inputs[k] if isinstance(k, str) and k in nd.inputs else None
            if sock is None: setattr(nd, k, v); continue
            self.set(sock, v)
        return nd
    def set(self, sock, v):
        if hasattr(v, "is_output") or hasattr(v, "links"): self.ln.new(v, sock)
        else: sock.default_value = v
    def link(self, a, b): self.ln.new(a, b)
    def coord(self, kind="Object"):
        if not self._coord: self._coord = self.node("ShaderNodeTexCoord")
        return self._coord.outputs[kind]
    def math(self, op, a, b=None, c=None):
        nd = self.node("ShaderNodeMath", _operation=op)
        for s, v in zip(nd.inputs, (a, b, c)):
            if v is not None: self.set(s, v)
        return nd.outputs[0]
    def mix(self, fac, a, b, blend="MIX"):
        nd = self.node("ShaderNodeMix", _data_type="RGBA", _blend_type=blend)
        self.set(nd.inputs[0], fac); self.set(nd.inputs[6], a); self.set(nd.inputs[7], b)
        return nd.outputs[2]
    def attr(self, name, kind="VIEW_LAYER"):
        return self.node("ShaderNodeAttribute", _attribute_type=kind, _attribute_name=name)
    def noise(self, scale, detail=4.0, rough=0.55, vec=None, dim="3D", w=None):
        nd = self.node("ShaderNodeTexNoise", Scale=scale, Detail=detail, Roughness=rough)
        nd.noise_dimensions = dim
        if vec is not None: self.link(vec, nd.inputs["Vector"])
        else: self.link(self.coord(), nd.inputs["Vector"])
        if w is not None: self.set(nd.inputs["W"], w)
        return nd
    def voronoi(self, scale, vec=None, feature="F1", rnd=1.0):
        nd = self.node("ShaderNodeTexVoronoi", Scale=scale, _feature=feature)
        nd.inputs["Randomness"].default_value = rnd
        self.link(vec if vec is not None else self.coord(), nd.inputs["Vector"])
        return nd
    def ramp(self, fac, stops):
        nd = self.node("ShaderNodeValToRGB"); cr = nd.color_ramp
        cr.elements[0].position, cr.elements[0].color = stops[0][0], srgb(stops[0][1])
        cr.elements[1].position, cr.elements[1].color = stops[-1][0], srgb(stops[-1][1])
        for p, c in stops[1:-1]: e = cr.elements.new(p); e.color = srgb(c)
        self.link(fac, nd.inputs[0]); return nd.outputs[0]
    def bump(self, height, strength, distance, normal=None):
        nd = self.node("ShaderNodeBump", Strength=strength, Distance=distance)
        self.link(height, nd.inputs["Height"])
        if normal is not None: self.link(normal, nd.inputs["Normal"])
        return nd.outputs["Normal"]
    def wet(self, base_col, rough, normal, darken=0.45, keep_bump=True):
        """Wet state: darker albedo, a clear water film (coat) with low roughness."""
        w = self.attr("wet").outputs["Fac"]
        col = self.mix(self.math("MULTIPLY", w, darken), base_col, (0.0, 0.0, 0.0, 1.0))
        r = self.math("SUBTRACT", rough, self.math("MULTIPLY", w, 0.45)) if not isinstance(rough, float) else self.math("SUBTRACT", rough, self.math("MULTIPLY", w, rough * 0.6))
        self.set(self.bsdf.inputs["Coat Weight"], self.math("MULTIPLY", w, 1.0))
        self.bsdf.inputs["Coat Roughness"].default_value = 0.04
        self.bsdf.inputs["Coat IOR"].default_value = 1.33
        return col, r
    def finish(self, col, rough, normal=None, metallic=0.0, spec=0.5):
        self.set(self.bsdf.inputs["Base Color"], col)
        self.set(self.bsdf.inputs["Roughness"], rough)
        self.bsdf.inputs["Metallic"].default_value = metallic
        self.bsdf.inputs["Specular IOR Level"].default_value = spec
        if normal is not None: self.link(normal, self.bsdf.inputs["Normal"])
        return self.m

def edge_wear(g, base, worn, amount=0.6):
    """Lighter worn edges from geometry pointiness, broken up by noise."""
    geo = g.node("ShaderNodeNewGeometry")
    pt = g.math("SUBTRACT", geo.outputs["Pointiness"], 0.52)
    pt = g.math("MULTIPLY", pt, 9.0)
    nz = g.noise(60.0, 3.0).outputs["Fac"]
    f = g.math("MULTIPLY", g.math("MAXIMUM", pt, 0.0), g.math("GREATER_THAN", nz, 0.45))
    return g.mix(g.math("MINIMUM", g.math("MULTIPLY", f, amount), 1.0), base, worn)

def shingle(name="Shingle_NightSky", tone_attr="tone"):
    """Granule surface: ~1.2 mm granules (voronoi), per-tab tone from a face attribute, slight soot/
    streak variation, granule-level normal detail. The 'shadow' attribute darkens the laminate gaps."""
    g = G(name)
    tone = g.attr(tone_attr, "GEOMETRY").outputs["Fac"]
    shadow = g.attr("shadow", "GEOMETRY").outputs["Fac"]
    base = g.ramp(tone, [(0.0, "#0d0d0e"), (0.4, "#131415"), (0.75, "#19191b"), (1.0, "#212123")])
    # granule-blend mottling inside each tab (2-6 cm), so tabs read as one blend, not flat tiles
    mot = g.noise(28.0, 3.0, 0.6).outputs["Fac"]
    base = g.mix(g.math("MULTIPLY", g.math("SUBTRACT", mot, 0.35), 0.6), base, srgb("#2a2927"))
    gr = g.voronoi(820.0)                       # ~1.2 mm granules
    grn = g.voronoi(820.0, feature="F1")
    speck = g.math("GREATER_THAN", gr.outputs["Color"], 0.0)
    # granule colour variation: a few lighter grey and blue-grey granules
    rc = g.node("ShaderNodeSeparateColor"); g.link(gr.outputs["Color"], rc.inputs[0])
    light = g.math("GREATER_THAN", rc.outputs[0], 0.86)
    blue = g.math("GREATER_THAN", rc.outputs[1], 0.90)
    col = g.mix(g.math("MULTIPLY", light, 0.7), base, srgb("#4d4f52"))
    col = g.mix(g.math("MULTIPLY", blue, 0.5), col, srgb("#262c33"))
    col = g.mix(g.math("MULTIPLY", g.math("SUBTRACT", 1.0, shadow), 0.0), col, col)
    col = g.mix(g.math("MULTIPLY", shadow, 0.55), col, (0.0, 0.0, 0.0, 1.0))
    # large-scale weathering / soot variation
    big = g.noise(1.4, 3.0).outputs["Fac"]
    col = g.mix(g.math("MULTIPLY", g.math("SUBTRACT", big, 0.4), 0.35), col, srgb("#2e2c29"))
    rough = g.math("ADD", 0.84, g.math("MULTIPLY", g.noise(300.0, 2.0).outputs["Fac"], 0.12))
    h = g.math("ADD", g.math("MULTIPLY", gr.outputs["Distance"], -1.0), g.math("MULTIPLY", g.noise(1500.0, 1.0).outputs["Fac"], 0.25))
    nrm = g.bump(h, 0.55, 0.0012)
    col, rough = g.wet(col, rough, nrm, darken=0.38)
    return g.finish(col, rough, nrm, spec=0.22)

def underlayment():
    """Synthetic underlayment: woven polypropylene micro-texture, printed lap guide lines."""
    g = G("Underlayment")
    co = g.coord("UV")
    sep = g.node("ShaderNodeSeparateXYZ"); g.link(co, sep.inputs[0])
    # printed white lap lines every 1.0 m along the roll width (v in metres), and a faint grid
    v = sep.outputs[1]
    line = g.math("LESS_THAN", g.math("FRACT", g.math("DIVIDE", v, 1.0)), 0.006)
    line2 = g.math("LESS_THAN", g.math("FRACT", g.math("DIVIDE", g.math("ADD", v, 0.1), 1.0)), 0.003)
    base = g.mix(g.math("MULTIPLY", g.noise(9.0, 2.0).outputs["Fac"], 0.25), srgb("#73777c"), srgb("#83878c"))
    weave = g.node("ShaderNodeTexWave", Scale=900.0, Distortion=0.0, _wave_type="BANDS")
    g.link(g.coord(), weave.inputs["Vector"])
    col = g.mix(g.math("MAXIMUM", line, line2), base, srgb("#e4e6e8"))
    nrm = g.bump(g.math("ADD", weave.outputs["Fac"], g.math("MULTIPLY", g.noise(3.0, 2.0).outputs["Fac"], 4.0)), 0.25, 0.0004)
    col, rough = g.wet(col, 0.62, nrm, darken=0.25)
    return g.finish(col, rough, nrm)

def osb():
    """Oriented strand board: stretched voronoi flakes in three tones, fine fibre bump."""
    g = G("OSB")
    co = g.coord()
    mp = g.node("ShaderNodeMapping"); g.link(co, mp.inputs["Vector"])
    mp.inputs["Scale"].default_value = (1.0, 3.2, 1.0)
    fl = g.voronoi(26.0, vec=mp.outputs["Vector"])
    fl2 = g.voronoi(55.0, vec=mp.outputs["Vector"])
    rc = g.node("ShaderNodeSeparateColor"); g.link(fl.outputs["Color"], rc.inputs[0])
    rc2 = g.node("ShaderNodeSeparateColor"); g.link(fl2.outputs["Color"], rc2.inputs[0])
    t = g.math("ADD", g.math("MULTIPLY", rc.outputs[0], 0.6), g.math("MULTIPLY", rc2.outputs[1], 0.4))
    col = g.ramp(t, [(0.0, "#8a6338"), (0.35, "#b48a55"), (0.7, "#cfa772"), (1.0, "#e2c08b")])
    edge = g.math("LESS_THAN", fl.outputs["Distance"], 0.06)
    col = g.mix(g.math("MULTIPLY", g.math("SUBTRACT", 1.0, edge), 0.0), col, col)
    nrm = g.bump(g.math("ADD", fl.outputs["Distance"], g.math("MULTIPLY", g.noise(240.0, 3.0).outputs["Fac"], 0.5)), 0.35, 0.0015)
    return g.finish(col, 0.82, nrm)

def wood():
    g = G("Lumber")
    co = g.coord()
    mp = g.node("ShaderNodeMapping"); g.link(co, mp.inputs["Vector"]); mp.inputs["Scale"].default_value = (1.0, 1.0, 9.0)
    wv = g.node("ShaderNodeTexWave", Scale=3.5, Distortion=6.0, _wave_type="RINGS"); g.link(mp.outputs["Vector"], wv.inputs["Vector"])
    col = g.ramp(wv.outputs["Fac"], [(0.0, "#a87a47"), (0.5, "#c99b62"), (1.0, "#dcb27a")])
    nrm = g.bump(wv.outputs["Fac"], 0.08, 0.002)
    return g.finish(col, 0.7, nrm)

def paint(name, hexcol, rough=0.38, wear="#6a645c", metallic=0.0, wear_amt=0.5):
    g = G(name)
    base = g.mix(g.math("MULTIPLY", g.noise(4.0, 3.0).outputs["Fac"], 0.12), srgb(hexcol), srgb(wear))
    col = edge_wear(g, base, srgb(wear), wear_amt) if wear_amt > 0 else base
    nrm = g.bump(g.noise(180.0, 3.0).outputs["Fac"], 0.06, 0.0005)
    col, rough2 = g.wet(col, rough, nrm, darken=0.15)
    return g.finish(col, rough2, nrm, metallic=metallic)

def soffit_vent():
    g = G("SoffitVentMetal")
    co = g.coord()
    holes = g.voronoi(160.0, vec=co, rnd=0.0)
    hole = g.math("LESS_THAN", holes.outputs["Distance"], 0.28)
    col = g.mix(hole, srgb("#e8e6e1"), srgb("#0b0b0b"))
    return g.finish(col, g.mix(hole, (0.4, 0.4, 0.4, 1), (1, 1, 1, 1)), None)

def stucco():
    g = G("Stucco")
    n1 = g.noise(90.0, 6.0, 0.6).outputs["Fac"]
    n2 = g.noise(2.0, 3.0).outputs["Fac"]
    col = g.mix(g.math("MULTIPLY", n2, 0.18), srgb("#cfc9bd"), srgb("#bdb6a9"))
    # faint dirt toward the ground
    sep = g.node("ShaderNodeSeparateXYZ"); g.link(g.coord("Object"), sep.inputs[0])
    low = g.math("SUBTRACT", 1.0, g.math("MINIMUM", g.math("DIVIDE", sep.outputs[2], 0.6), 1.0))
    col = g.mix(g.math("MULTIPLY", low, 0.25), col, srgb("#b8ad9b"))
    nrm = g.bump(n1, 0.35, 0.002)
    return g.finish(col, 0.92, nrm)

def glass():
    g = G("Glass")
    g.bsdf.inputs["Transmission Weight"].default_value = 1.0
    g.bsdf.inputs["IOR"].default_value = 1.5
    return g.finish(srgb("#eef3f3"), 0.0)

def interior():
    """Warm interior seen through the windows (emission falls off with a soft gradient)."""
    g = G("Interior")
    grad = g.noise(0.6, 2.0).outputs["Fac"]
    col = g.mix(grad, srgb("#4a3a2a"), srgb("#a07a4a"))
    g.set(g.bsdf.inputs["Emission Color"], srgb("#ffbf7a"))
    g.bsdf.inputs["Emission Strength"].default_value = 4.0
    return g.finish(col, 0.8)

def simple(name, hexcol, rough=0.5, metallic=0.0, bump_scale=0.0):
    g = G(name)
    nrm = g.bump(g.noise(bump_scale or 50.0, 3.0).outputs["Fac"], 0.1 if bump_scale else 0.0, 0.001)
    col, r = g.wet(srgb(hexcol), rough, nrm, darken=0.2)
    return g.finish(col, r, nrm, metallic=metallic)

def leaves(name="Foliage", a="#2f4a26", b="#5b7a3a"):
    g = G(name)
    vor = g.voronoi(55.0)
    col = g.mix(g.noise(8.0, 3.0).outputs["Fac"], srgb(a), srgb(b))
    col = g.mix(g.math("MULTIPLY", g.math("GREATER_THAN", vor.outputs["Distance"], 0.4), 0.6), col, srgb("#1c2b17"))
    g.bsdf.inputs["Subsurface Weight"].default_value = 0.15
    nrm = g.bump(vor.outputs["Distance"], 0.9, 0.02)
    col, r = g.wet(col, 0.6, nrm, darken=0.2)
    return g.finish(col, r, nrm)

def lawn(fade=(32.0, 58.0)):
    """Lawn that dissolves into the backdrop plate toward the edge of the lot (alpha by radius)."""
    g = G("Lawn")
    n = g.noise(25.0, 6.0).outputs["Fac"]
    col = g.mix(n, srgb("#3f5326"), srgb("#68703f"))
    col = g.mix(g.math("MULTIPLY", g.noise(3.0, 3.0).outputs["Fac"], 0.5), col, srgb("#7a7450"))
    nrm = g.bump(g.noise(400.0, 2.0).outputs["Fac"], 0.6, 0.004)
    col, r = g.wet(col, 0.85, nrm, darken=0.25)
    ln = g.node("ShaderNodeVectorMath", _operation="LENGTH"); g.link(g.coord("Object"), ln.inputs[0])
    mr = g.node("ShaderNodeMapRange"); g.link(ln.outputs["Value"], mr.inputs["Value"])
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = fade
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 1.0, 0.0
    mr.interpolation_type = "SMOOTHSTEP"
    g.link(mr.outputs["Result"], g.bsdf.inputs["Alpha"])
    return g.finish(col, r, nrm)

def concrete():
    g = G("Concrete")
    n = g.noise(12.0, 6.0).outputs["Fac"]
    col = g.mix(n, srgb("#a9a49a"), srgb("#c9c4b9"))
    nrm = g.bump(g.noise(300.0, 3.0).outputs["Fac"], 0.25, 0.001)
    col, r = g.wet(col, 0.85, nrm, darken=0.35)
    return g.finish(col, r, nrm)

def water(name="Water"):
    g = G(name)
    g.bsdf.inputs["Transmission Weight"].default_value = 1.0
    g.bsdf.inputs["IOR"].default_value = 1.333
    return g.finish(srgb("#ffffff"), 0.0)

def rain_streak():
    """Rain streak: water with slight milky scatter so motion-blurred drops read against dark backgrounds."""
    g = G("RainDrop")
    g.bsdf.inputs["Transmission Weight"].default_value = 0.55
    g.bsdf.inputs["IOR"].default_value = 1.333
    g.set(g.bsdf.inputs["Emission Color"], srgb("#d6dee6"))
    g.bsdf.inputs["Emission Strength"].default_value = 0.35
    return g.finish(srgb("#dfe6ec"), 0.05)

def dust():
    """Fine desert dust: pale, matte, half transparent, so motion blur turns each mote into a soft streak."""
    g = G("Dust")
    g.bsdf.inputs["Alpha"].default_value = 0.38
    return g.finish(srgb("#b9a27a"), 0.95)

def heat_shimmer():
    """Hot air rising off the panel: a camera-facing sheet that refracts the background very slightly
    (IOR 1.012) through slow 4D noise, fading to nothing at its edges. Restrained: no glow, no colour."""
    g = G("HeatShimmer")
    w = g.attr("heat_t").outputs["Fac"]
    co = g.coord("UV")
    sep = g.node("ShaderNodeSeparateXYZ"); g.link(co, sep.inputs[0])
    # soft mask: 0 at every edge, 1 in the middle (rising air is strongest just above the surface)
    def bell(x, p):
        d = g.math("ABSOLUTE", g.math("SUBTRACT", g.math("MULTIPLY", x, 2.0), 1.0))
        return g.math("SUBTRACT", 1.0, g.math("POWER", d, p))
    mask = g.math("MULTIPLY", bell(sep.outputs[0], 3.0), bell(sep.outputs[1], 2.0))
    n = g.noise(5.5, 3.0, 0.55, vec=g.coord("Object"), dim="4D", w=w).outputs["Fac"]
    nrm = g.bump(n, 0.12, 0.03)
    ref = g.n.new("ShaderNodeBsdfRefraction"); ref.inputs["IOR"].default_value = 1.012; ref.inputs["Roughness"].default_value = 0.0
    ref.inputs["Color"].default_value = (1, 1, 1, 1)
    g.link(nrm, ref.inputs["Normal"])
    tr = g.n.new("ShaderNodeBsdfTransparent")
    amt = g.math("MULTIPLY", g.math("MULTIPLY", g.attr("heat").outputs["Fac"], mask), 0.85)
    mx = g.n.new("ShaderNodeMixShader"); g.link(amt, mx.inputs[0]); g.link(tr.outputs[0], mx.inputs[1]); g.link(ref.outputs[0], mx.inputs[2])
    g.link(mx.outputs[0], g.out.inputs["Surface"])
    return g.m

def backdrop(plates):
    """Camera-only backdrop: three aligned photographic plates (clear, rain, golden) crossfaded by scene
    properties; a small warm grade for the heat state."""
    g = G("Backdrop")
    uv = g.coord("UV")
    tex = []
    for p in plates:
        im = bpy.data.images.load(p, check_existing=True)
        t = g.node("ShaderNodeTexImage"); t.image = im; t.extension = "EXTEND"; t.interpolation = "Cubic"
        g.link(uv, t.inputs["Vector"]); tex.append(t.outputs["Color"])
    rain = g.attr("plate_rain").outputs["Fac"]; gold = g.attr("plate_gold").outputs["Fac"]; heat = g.attr("heat").outputs["Fac"]
    col = g.mix(rain, tex[0], tex[1]); col = g.mix(gold, col, tex[2])
    warm = g.mix(0.5, col, srgb("#ffd9a8"), blend="MULTIPLY")
    col = g.mix(g.math("MULTIPLY", heat, 0.35), col, warm)
    em = g.n.new("ShaderNodeEmission"); g.link(col, em.inputs["Color"])
    em.inputs["Strength"].default_value = 0.45
    g.link(em.outputs[0], g.out.inputs["Surface"])
    return g.m
