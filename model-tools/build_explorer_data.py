"""Genera los datos del explorador interactivo de Sky Fragment a partir del .3dm.

Salidas (en OUT/):
  shell.glb           envolvente de la torre + sitio + contexto (sin interiores)
  levels/<ID>.glb     interior de cada nivel (sin luminarias), con _FEATURE_ID por vértice
  model.json          niveles, usos, espacios, zonas (polígonos), superficies, accesos y estadísticas

Convenciones: glTF Y-up en metros. Origen = centro de la torre a nivel de planta baja.
Rhino (X, Y, Z) -> glTF (X - X0, Z - Z0, -(Y - Y0)).  Polígonos en planta: (X - X0, Y - Y0).
"""
import sys, os, json, math, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations_es import mat_es, type_es, part_and_id, code_es
LANG = os.environ.get("SF_LANG", "es")
import numpy as np
import rhino3dm as r
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.ops import unary_union

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(OUT, "levels"), exist_ok=True)
m = r.File3dm.Read(SRC)
LP = {l.Index: l.FullPath for l in m.Layers}

# ------------------------------------------------------------------ diccionarios ES
LEVEL_ES = {"Ground Floor": ("PB", "Planta baja"), "Mezzanine": ("MZ", "Mezanine"), "Roof": ("AZ", "Azotea")}
for i in range(1, 18):
    LEVEL_ES[f"Level {i:02d}"] = (f"N{i:02d}", f"Nivel {i:02d}")
DEPT = {"Commerce": "comercio", "Offices": "oficinas", "Housing": "vivienda", "Core": "nucleo"}
ROOM_ES = {
    "Café": "Café", "Accessible WC": "Sanitario accesible", "WC 1": "Sanitario 1", "WC 2": "Sanitario 2",
    "Restroom Lobby": "Vestíbulo de sanitarios", "Office Reception": "Recepción de oficinas",
    "Residential Lobby": "Vestíbulo residencial", "Lift Lobby": "Vestíbulo de elevadores", "Stair": "Escalera",
    "Coworking": "Espacio de trabajo compartido", "Art Lounge": "Sala de arte", "Sky Deck": "Terraza mirador",
    "Plant": "Cuarto de máquinas", "Pool Deck": "Terraza de alberca", "Changing Room 1": "Vestidor 1",
    "Changing Room 2": "Vestidor 2", "Accessible WC + Shower": "Sanitario accesible con regadera",
    "Commerce": "Comercio (planta tipo)", "Offices": "Oficinas (planta tipo)", "Housing": "Vivienda (planta tipo)",
}
def room_es(name):
    if name in ROOM_ES: return ROOM_ES[name]
    if name.startswith("Apartment "): return "Departamento " + name.split(" ", 1)[1]
    if name.startswith("Bath "): return "Baño " + name.split(" ", 1)[1]
    if name.startswith("Corridor "): return "Pasillo " + name.split(" ", 1)[1]
    return name
FINISH_ES = {
    "SF 10 Plaster - Terrazzo 600": "Terrazo 600", "SF 08 Sage - Tile 200": "Loseta 200 (salvia)",
    "SF 07 Lamplight Stone - Stone 600x300": "Piedra 600×300", "SF 04 Silver - Stone 600": "Piedra 600",
    "SF 06 Wood - Boards 140": "Duela de madera 140", "SF 11 Slate - Carpet": "Alfombra",
    "SF 07 Lamplight Stone - Oak Herringbone 90": "Encino en espiga 90",
    "SF 09 White - Pool Stone 600x400": "Piedra de alberca 600×400", "SF 10 Plaster - Deck Boards 140": "Duela de exterior 140",
    "SF 11 Slate - Pebble Strip": "Franja de grava", "SF 11 Slate - Grating 100x30": "Rejilla metálica 100×30",
    "SF 09 White - Concrete slab": "Losa de concreto", "SF 09 White - Tile 200": "Loseta 200 (blanca)",
}
CAT_ES = {
    "Floors": ("pisos", "Pisos"), "Walls": ("muros", "Muros"), "Doors": ("puertas", "Puertas"),
    "Stairs": ("escaleras", "Escaleras"), "Railings": ("barandales", "Barandales"),
    "Furniture": ("mobiliario", "Mobiliario"), "Casework": ("carpinteria", "Carpintería"),
    "Plumbing Fixtures": ("sanitarios", "Muebles sanitarios"), "Specialty Equipment": ("equipo", "Equipo especial"),
    "Generic Models": ("genericos", "Elementos genéricos"), "Lighting Fixtures": ("luminarias", "Luminarias"),
}
PIECE_ES = {
    "Desk bench": "Bancada de escritorios", "Bed": "Cama", "Timber slat screen": "Celosía de madera", "Desk pair": "Par de escritorios",
    "Bentwood chair": "Silla de madera curvada", "Persian rug": "Tapete persa", "Kitchenette": "Cocineta", "Table": "Mesa",
    "Wainscot": "Lambrín", "Bookshelf": "Librero", "Coat hooks": "Perchero", "Club chair": "Sillón club", "Chair": "Silla",
    "Coffee table": "Mesa de centro", "Vanity": "Lavabo con mueble", "Armchair": "Sillón", "WC": "Inodoro",
    "Writing desk": "Escritorio", "Mirror": "Espejo", "Curtain": "Cortina", "Clothes rail": "Barra para ropa",
    "Pavilion fins": "Aletas del pabellón", "Bar stool": "Banco alto", "Striped pouf": "Puf", "Loveseat": "Sofá de dos plazas",
    "Retail shelf": "Anaquel de tienda", "Sofa": "Sofá", "Rug": "Tapete", "Doormat": "Tapete de entrada", "Towel": "Toalla",
    "Cafe table": "Mesa de café", "Plant screen": "Jardinera divisoria", "Bench": "Banca", "Parking markings": "Señalización de estacionamiento",
    "Lamp post": "Poste de luz", "Corridor console": "Consola de pasillo", "Wardrobe": "Clóset", "Lift doors": "Puertas de elevador",
    "Sun lounger": "Camastro", "Poolside shower": "Regadera de alberca", "Meeting room": "Sala de juntas", "Rooftop bar": "Bar de azotea",
    "Mailboxes": "Buzones", "Stone tub": "Tina de piedra", "Bicycle": "Bicicleta", "Fridge": "Refrigerador", "Sheffield stand": "Soporte para bicicletas",
    "Task chair": "Silla de trabajo", "Shower": "Regadera", "Shower screen": "Cancel de baño", "Side table": "Mesa lateral",
    "Bar equipment": "Equipo de barra", "Changing bench": "Banca de vestidor", "Outdoor sofa": "Sofá de exterior", "Basin": "Lavabo",
    "Bollard": "Bolardo", "Terrace table": "Mesa de terraza", "Terrace chair": "Silla de terraza", "Bike shelter": "Biciestacionamiento",
    "Bar cart": "Carrito de bar", "Parasol": "Sombrilla", "Wayfinding totem": "Tótem de señalización", "Phone booth": "Cabina para llamadas",
    "Daybed": "Diván", "Towel shelf": "Toallero", "Litter bin": "Bote de basura", "Curved sofa": "Sofá curvo", "Piano": "Piano",
    "Back bar": "Contrabarra", "Monitor": "Monitor", "Entrance canopy": "Marquesina de acceso", "Accessible shower": "Regadera accesible",
    "Display plinth": "Pedestal de exhibición", "Pastry case": "Vitrina de repostería", "Mezzanine balustrade": "Barandal del mezanine",
    "Grab bar": "Barra de apoyo", "Laptop": "Computadora portátil", "Tableware": "Vajilla", "Condenser unit": "Unidad condensadora",
    "EV charger": "Cargador para auto eléctrico", "Feature stair": "Escalera escultórica", "Bar": "Barra", "Red portal": "Portal rojo",
    "Acoustic panel": "Panel acústico", "Easel": "Caballete", "Sky canopy": "Cubierta mirador", "Pool enclosure N": "Cerco de alberca N",
    "Pool gate N": "Puerta de alberca N", "Pool enclosure S": "Cerco de alberca S", "Pool gate S": "Puerta de alberca S",
    "Elevator car": "Cabina de elevador", "Banquette": "Banca corrida", "Reception desk": "Mostrador de recepción",
    "Concierge desk": "Mostrador de conserjería", "Glass balustrade": "Barandal de vidrio", "Travertine coffee table": "Mesa de centro de travertino",
    "Sky mirror": "Espejo mirador", "Restaurant bar": "Barra de restaurante", "Menu board": "Pizarrón de menú",
    "Moon window wall": "Muro con ventana circular", "Baby change": "Cambiador de bebé", "Bin": "Bote", "Directory screen": "Directorio digital",
    "Crown ring - diagrid compression ring": "Anillo de coronamiento del diagrid", "Double-skin coping": "Remate de doble piel",
    "Cavity vent grille": "Rejilla de ventilación de cámara", "Parapet upstand": "Pretil", "Outdoor rug": "Tapete de exterior",
    "Pool house roof": "Cubierta del pabellón de alberca", "Stone path": "Sendero de piedra",
}
def lvl_name_es(n):
    return LEVEL_ES.get(n, (n, n))[1]
def piece_es(p):
    if p in PIECE_ES: return PIECE_ES[p]
    if p.startswith("Fire stair "):
        a, b = p[len("Fire stair "):].split(" - ")
        return f"Escalera de emergencia {lvl_name_es(a)} – {lvl_name_es(b)}"
    if p.startswith("Parking stall "):
        return "Cajón de estacionamiento " + p.split()[-1]
    return p

LEVEL_CODE = {}
if LANG == "en":
    import translations_en as _en
    LEVEL_ES, lvl_name_es, room_es, FINISH_ES, CAT_ES, piece_es = _en.LEVEL_EN, _en.lvl_name_en, _en.room_en, _en.FINISH_EN, _en.CAT_EN, _en.piece_en
    mat_es, type_es, part_and_id, code_es = _en.mat_en, _en.type_en, _en.part_and_id_en, _en.code_en
    LEVEL_CODE = _en.CODE_EN

# ------------------------------------------------------------------ materiales (Rhino -> PBR)
GLASS_ALPHA = {"SF 02 Teal - Facade crystal glass": 0.4, "SF 03 Aqua - Outer skin glass": 0.18,
               "SF 03 Aqua - Curtain wall glazing": 0.2, "SF 03 Aqua - Clear glass": 0.25}
def lin(c8):
    c = c8 / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def to_pbr(mat):
    name = mat.Name; d = mat.DiffuseColor; s = mat.SpecularColor; e = mat.EmissionColor
    tr = float(mat.Transparency); shine = float(mat.Shine) / 255.0
    refl = float(mat.Reflectivity); fres = bool(mat.FresnelReflections)
    out = {"name": mat_es(name), "doubleSided": True}
    if tr > 0.0:
        alpha = GLASS_ALPHA.get(name, 1.0 - tr)
        pbr = {"baseColorFactor": [lin(d[0]), lin(d[1]), lin(d[2]), alpha], "metallicFactor": 0.0, "roughnessFactor": 0.05}
        out["alphaMode"] = "BLEND"
    elif (d[0], d[1], d[2]) == (0, 0, 0) and refl >= 0.9 and not fres:
        low = name.lower(); rough = 0.3
        if "mirror" in low: rough = 0.04
        elif "brushed" in low: rough = 0.35
        elif "grating" in low: rough = 0.45
        elif "blackened" in low: rough = 0.5
        pbr = {"baseColorFactor": [lin(s[0]), lin(s[1]), lin(s[2]), 1.0], "metallicFactor": 1.0, "roughnessFactor": rough}
    else:
        pbr = {"baseColorFactor": [lin(d[0]), lin(d[1]), lin(d[2]), 1.0], "metallicFactor": 0.0,
               "roughnessFactor": round(max(0.2, min(1.0, 1.0 - 0.75 * shine)), 3)}
    if (e[0], e[1], e[2]) != (0, 0, 0):
        out["emissiveFactor"] = [round(lin(e[0]), 5), round(lin(e[1]), 5), round(lin(e[2]), 5)]
    pbr["baseColorFactor"] = [round(x, 5) for x in pbr["baseColorFactor"]]
    out["pbrMetallicRoughness"] = pbr
    return out

# ------------------------------------------------------------------ mallas
def render_meshes(g):
    t = type(g).__name__
    if t == "Mesh": return [g]
    if t == "Extrusion":
        em = g.GetMesh(r.MeshType.Any); return [em] if em is not None else []
    if t == "Brep":
        return [f for f in (g.Faces[i].GetMesh(r.MeshType.Any) for i in range(len(g.Faces))) if f is not None]
    return []
def mesh_arrays(mesh):
    nv = len(mesh.Vertices)
    if nv == 0: return None
    V = np.array([(p.X, p.Y, p.Z) for p in (mesh.Vertices[i] for i in range(nv))], dtype=np.float64)
    N = None
    if len(mesh.Normals) == nv:
        N = np.array([(n.X, n.Y, n.Z) for n in (mesh.Normals[i] for i in range(nv))], dtype=np.float64)
    tris = []
    for i in range(len(mesh.Faces)):
        a, b, c, d = mesh.Faces[i]
        tris.append((a, b, c))
        if c != d: tris.append((a, c, d))
    F = np.array(tris, dtype=np.int64).reshape(-1, 3)
    if N is None:
        N = np.zeros_like(V)
        fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
        for k in range(3): np.add.at(N, F[:, k], fn)
        ln = np.linalg.norm(N, axis=1, keepdims=True); ln[ln == 0] = 1; N = N / ln
    return V, N, F
def obj_arrays(g):
    out = []
    for ms in render_meshes(g):
        a = mesh_arrays(ms)
        if a is not None and len(a[2]): out.append(a)
    return out
def footprint(arrs, up_only=True):
    polys = []
    for V, N, F in arrs:
        P = V[F]
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        ln = np.linalg.norm(n, axis=1)
        ok = ln > 1e-12
        if up_only: ok &= np.abs(n[:, 2]) / np.where(ln == 0, 1, ln) >= 0.5
        for tri in P[ok]:
            pg = Polygon(tri[:, :2])
            if pg.area > 1e-9: polys.append(pg)
    return unary_union(polys) if polys else None

# ------------------------------------------------------------------ escaneo
objs = []  # (obj, path, userstrings, arrays-lazy)
levels_src = {}
room_dots = collections.defaultdict(list)
for o in m.Objects:
    path = LP[o.Attributes.LayerIndex]
    us = dict(o.Attributes.GetUserStrings())
    g = o.Geometry
    if type(g).__name__ == "TextDot":
        if path.endswith("Annotation::Levels"):
            levels_src[o.Attributes.Name] = float(us["elevation_m"])
        elif path.endswith("::Rooms"):
            room_dots[us["level"]].append((o.Attributes.Name, us, g.Point.X, g.Point.Y, g.Point.Z))
        continue
    if type(g).__name__ == "LineCurve":
        continue
    objs.append((o, path, us))

level_order = sorted(levels_src, key=lambda n: levels_src[n])
Z0 = levels_src["Ground Floor"]
# centro de la torre (envolvente)
tb = [math.inf, math.inf, -math.inf, -math.inf]
for o, path, us in objs:
    if "::Tower::" in path or path.endswith("Curtain Wall"):
        bb = o.Geometry.GetBoundingBox()
        tb = [min(tb[0], bb.Min.X), min(tb[1], bb.Min.Y), max(tb[2], bb.Max.X), max(tb[3], bb.Max.Y)]
X0, Y0 = (tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2
print(f"Origen Rhino: X0={X0:.4f} Y0={Y0:.4f} Z0={Z0:.4f}")
def to_gl(V):
    return np.stack([V[:, 0] - X0, V[:, 2] - Z0, -(V[:, 1] - Y0)], axis=1)
def nrm_gl(N):
    NN = np.stack([N[:, 0], N[:, 2], -N[:, 1]], axis=1)
    ln = np.linalg.norm(NN, axis=1, keepdims=True); ln[ln == 0] = 1
    return NN / ln
def pt_gl(x, y, z):
    return [round(x - X0, 3), round(z - Z0, 3), round(-(y - Y0), 3)]
def poly_json(pg, tol=0.01):
    pg = pg.simplify(tol, preserve_topology=True)
    geoms = pg.geoms if hasattr(pg, "geoms") else [pg]
    out = []
    for g in geoms:
        if g.area < 0.05: continue
        out.append({"o": [[round(x - X0, 3), round(y - Y0, 3)] for x, y in list(g.exterior.coords)[:-1]],
                    "h": [[[round(x - X0, 3), round(y - Y0, 3)] for x, y in list(h.coords)[:-1]] for h in g.interiors]})
    return out

# ------------------------------------------------------------------ escritor GLB
class GLB:
    def __init__(self):
        self.bin = []; self.off = 0; self.views = []; self.acc = []
        self.materials = []; self.mat_idx = {}; self.meshes = []; self.nodes = []
    def view(self, data, target):
        pad = (-self.off) % 4
        if pad: self.bin.append(b"\x00" * pad); self.off += pad
        self.views.append({"buffer": 0, "byteOffset": self.off, "byteLength": len(data), "target": target})
        self.bin.append(data); self.off += len(data)
        return len(self.views) - 1
    def material(self, mat):
        key = mat.Name if mat is not None else "Default"
        if key not in self.mat_idx:
            self.mat_idx[key] = len(self.materials)
            self.materials.append(to_pbr(mat) if mat is not None else {"name": "Default", "doubleSided": True})
        return self.mat_idx[key]
    def primitive(self, P, N, F, mat_i, fid=None):
        P = P.astype(np.float32); N = N.astype(np.float32)
        idx = F.astype(np.uint32 if len(P) > 65535 else np.uint16).ravel()
        a = {}
        self.acc.append({"bufferView": self.view(P.tobytes(), 34962), "componentType": 5126, "count": len(P), "type": "VEC3",
                         "min": P.min(0).tolist(), "max": P.max(0).tolist()}); a["POSITION"] = len(self.acc) - 1
        self.acc.append({"bufferView": self.view(N.tobytes(), 34962), "componentType": 5126, "count": len(N), "type": "VEC3"})
        a["NORMAL"] = len(self.acc) - 1
        if fid is not None:
            fa = fid.astype(np.uint16)
            self.acc.append({"bufferView": self.view(fa.tobytes() + b"\x00" * ((-fa.nbytes) % 4), 34962), "componentType": 5123, "count": len(fa), "type": "SCALAR"})
            a["_FEATURE_ID"] = len(self.acc) - 1
        self.acc.append({"bufferView": self.view(idx.tobytes(), 34963), "componentType": 5125 if idx.dtype == np.uint32 else 5123,
                         "count": int(idx.size), "type": "SCALAR"})
        return {"attributes": a, "indices": len(self.acc) - 1, "material": mat_i, "mode": 4}
    def node(self, name, prims, extras=None):
        if not prims: return
        self.meshes.append({"name": name, "primitives": prims})
        nd = {"name": name, "mesh": len(self.meshes) - 1}
        if extras: nd["extras"] = extras
        self.nodes.append(nd)
    def write(self, path, scene_name, root_extras=None):
        nodes = [{"name": scene_name, "children": list(range(1, len(self.nodes) + 1))}] + self.nodes
        if root_extras: nodes[0]["extras"] = root_extras
        binary = b"".join(self.bin); binary += b"\x00" * ((-len(binary)) % 4)
        gltf = {"asset": {"version": "2.0", "generator": "Sky Fragment explorer (rhino3dm 8)"}, "scene": 0,
                "scenes": [{"name": scene_name, "nodes": [0]}], "nodes": nodes, "meshes": self.meshes,
                "materials": self.materials, "accessors": self.acc, "bufferViews": self.views,
                "buffers": [{"byteLength": len(binary)}]}
        js = json.dumps(gltf, separators=(",", ":"), ensure_ascii=False).encode("utf-8"); js += b" " * ((-len(js)) % 4)
        with open(path, "wb") as f:
            f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(binary)))
            f.write(struct.pack("<II", len(js), 0x4E4F534A)); f.write(js)
            f.write(struct.pack("<II", len(binary), 0x004E4942)); f.write(binary)
        return os.path.getsize(path)

class Bucket:
    def __init__(self): self.V = []; self.N = []; self.F = []; self.fid = []; self.off = 0
    def add(self, arrs, fid=None):
        for V, N, F in arrs:
            self.V.append(V); self.N.append(N); self.F.append(F + self.off); self.off += len(V)
            if fid is not None: self.fid.append(np.full(len(V), fid, dtype=np.float32))
    def arrays(self):
        V = np.concatenate(self.V); N = np.concatenate(self.N); F = np.concatenate(self.F)
        return to_gl(V), nrm_gl(N), F, (np.concatenate(self.fid) if self.fid else None)

def mat_of(o):
    mi = o.Attributes.MaterialIndex
    return m.Materials[mi] if mi >= 0 else None

# ------------------------------------------------------------------ clasificación
SHELL_GROUPS = collections.OrderedDict()   # key -> (nombre, extras)
def shell_key(path, us):
    p = path.split("::")
    if p[1] == "Tower":
        return {"Facade panels (crystal fragments)": "fragmentos", "Glass skin": "piel", "Diagrid structure": "diagrid",
                "Slabs": "losas"}.get(p[-1])
    if p[1] == "Site": return "sitio"
    if p[1] == "Context": return "contexto"
    if p[1] == "Levels":
        if p[-1] == "Curtain Wall": return "cw_" + DEPT.get(us.get("use", ""), "otros")
        if p[-1] == "Walls" and "Core wall" in us.get("material", ""): return "nucleo"
    return None
SHELL_NAMES_ES = {"fragmentos": "Fragmentos de cristal", "piel": "Piel de vidrio", "diagrid": "Diagrid", "losas": "Losas",
               "nucleo": "Núcleo", "cw_comercio": "Muro cortina · Comercio", "cw_oficinas": "Muro cortina · Oficinas",
               "cw_vivienda": "Muro cortina · Vivienda", "sitio": "Sitio", "contexto": "Contexto urbano"}
SHELL_NAMES = _en.SHELL_NAMES_EN if LANG == "en" else SHELL_NAMES_ES

shell = collections.OrderedDict(); shell_glb = GLB()
lvl_buckets = collections.defaultdict(lambda: collections.OrderedDict())
lvl_glbs = collections.defaultdict(GLB)
lvl_features = collections.defaultdict(list)
lvl_counts = collections.defaultdict(collections.Counter)
lvl_pieces = collections.defaultdict(collections.Counter)
floors = collections.defaultdict(list)
slabs = {}; core_arrs = []
entr = collections.defaultdict(list)
feature_stats = collections.defaultdict(lambda: {"objetos": 0, "materiales": collections.Counter()})
cw_stats = collections.Counter()
interior_cats = {"Floors", "Walls", "Doors", "Stairs", "Railings", "Furniture", "Casework", "Plumbing Fixtures",
                 "Specialty Equipment", "Generic Models"}
site_objs = []

for o, path, us in objs:
    p = path.split("::")
    cat = p[-1]
    sk = shell_key(path, us)
    mat = mat_of(o)
    if "entrance" in us:
        bb = o.Geometry.GetBoundingBox(); entr[us["entrance"]].append(bb)
    if sk is not None:
        arrs = obj_arrays(o.Geometry)
        if not arrs: continue
        b = shell.setdefault(sk, collections.OrderedDict()).setdefault(mat.Name if mat else "Default", [Bucket(), mat])
        b[0].add(arrs)
        feature_stats[sk]["objetos"] += 1; feature_stats[sk]["materiales"][mat.Name if mat else "-"] += 1
        if sk == "losas": slabs[us["level"]] = arrs
        if sk == "nucleo": core_arrs.extend(arrs)
        if sk.startswith("cw_"): cw_stats[sk[3:]] += 1
        if sk == "sitio": site_objs.append((o, us, arrs))
        continue
    if p[1] == "Levels" and "level" in us:
        lv = us["level"]
        lvl_counts[lv][cat] += 1
        if "piece" in us and cat != "Lighting Fixtures": lvl_pieces[lv][us["piece"]] += 1
        if cat not in interior_cats: continue
        arrs = obj_arrays(o.Geometry)
        if not arrs: continue
        if cat == "Floors": floors[lv].append((o, us, arrs))
        fid = len(lvl_features[lv])
        ck, cname = CAT_ES[cat]
        parte, oid = part_and_id(o.Attributes.Name)
        lvl_features[lv].append([ck, piece_es(us["piece"]) if "piece" in us else (FINISH_ES.get(us.get("material", ""), "") if cat == "Floors" else ""),
                                 parte, oid, type_es(us.get("revit_type", ""))])
        b = lvl_buckets[lv].setdefault(ck, collections.OrderedDict()).setdefault(mat.Name if mat else "Default", [Bucket(), mat])
        b[0].add(arrs, fid)

# ------------------------------------------------------------------ escribir shell.glb
for sk, mats in shell.items():
    prims = []
    for mname, (bk, mat) in mats.items():
        P, N, F, _ = bk.arrays()
        prims.append(shell_glb.primitive(P, N, F, shell_glb.material(mat)))
    shell_glb.node(SHELL_NAMES[sk], prims, {"key": sk, "tower": sk not in ("sitio", "contexto")})
sz = shell_glb.write(os.path.join(OUT, "shell.glb"), "Sky Fragment", {"units": "m", "origin_rhino": [round(X0, 4), round(Y0, 4), round(Z0, 4)]})
print(f"shell.glb {sz/1e6:.2f} MB")

# ------------------------------------------------------------------ geometría de planta
core_fp = footprint(core_arrs, up_only=False)
core_poly = unary_union([Polygon(g.exterior) for g in (core_fp.geoms if hasattr(core_fp, "geoms") else [core_fp])])
print(f"Núcleo: {core_poly.area:.1f} m²")

levels_out = []
zones_all = []
for i, lv in enumerate(level_order):
    lid, lname = LEVEL_ES[lv]
    elev = levels_src[lv] - Z0
    nxt = (levels_src[level_order[i + 1]] - Z0) if i + 1 < len(level_order) else elev + 4.2
    dots = room_dots.get(lv, [])
    # departamento principal: etiqueta de nivel (planta tipo) o mayoría por área
    lvl_label = [d for d in dots if d[0] in ("Commerce", "Offices", "Housing")]
    # pisos con su polígono
    fl = []
    for o, us, arrs in floors.get(lv, []):
        zmax = o.Geometry.GetBoundingBox().Max.Z - Z0
        fp = footprint(arrs)
        if fp is None or fp.is_empty: continue
        fl.append({"o": o, "us": us, "fp": fp, "zmax": zmax, "mat": us.get("material", "")})
    canopy = [f for f in fl if f["zmax"] > elev + 1.0]
    fl = [f for f in fl if f["zmax"] <= elev + 1.0]
    # losa base (contiene varias etiquetas) vs pisos de espacio
    rooms = []
    zones = []
    def labels_in(pg):
        return [d for d in dots if pg.buffer(0.05).contains(Point(d[2], d[3]))]
    base = [f for f in fl if len(labels_in(f["fp"])) > 1 and "Concrete slab" in f["mat"]]
    room_floors = [f for f in fl if f not in base]
    main_dept = DEPT[lvl_label[0][1]["department"]] if lvl_label else None
    for f in room_floors:
        ins = labels_in(f["fp"])
        if ins:
            d = ins[0]; dept = DEPT.get(d[1]["department"], "otros"); label = d[0]
        else:
            dept = main_dept or "vivienda"; label = None
        if dept == "nucleo":
            continue  # el núcleo se representa con su polígono continuo
        pg = f["fp"].difference(core_poly) if label is None or label in ("Commerce", "Offices", "Housing") else f["fp"]
        zones.append({"dept": dept, "area": round(pg.area, 1), "poly": poly_json(pg), "label": room_es(label) if label else None,
                      "finish": FINISH_ES.get(f["mat"], f["mat"])})
    # espacios (etiquetas)
    for name, us, x, y, z in dots:
        area = float(us["area_m2"]) if "area_m2" in us else None
        finish = None
        for f in fl:
            if f["fp"].buffer(0.05).contains(Point(x, y)) and f not in base:
                finish = FINISH_ES.get(f["mat"], f["mat"])
                if area is None and name not in ("Commerce", "Offices", "Housing", "Lift Lobby", "Stair"):
                    area = round(f["fp"].area, 1)
                break
        rooms.append({"num": code_es(us.get("number", "")), "numModelo": us.get("number", ""), "name": room_es(name), "dept": DEPT.get(us["department"], "otros"),
                      "area": area, "finish": finish, "pos": pt_gl(x, y, levels_src[lv] + 0.05), "tipo": name in ("Commerce", "Offices", "Housing")})
    # placa
    if lv in slabs:
        plate = footprint(slabs[lv])
    elif base:
        plate = base[0]["fp"]
    else:
        plate = unary_union([f["fp"] for f in fl]) if fl else None
    plate_area = round(plate.area, 1) if plate is not None else None
    core_here = core_poly.intersection(plate.buffer(0.5)) if plate is not None else core_poly
    depts_area = collections.Counter()
    for z in zones: depts_area[z["dept"]] += z["area"]
    if not main_dept and depts_area:
        main_dept = depts_area.most_common(1)[0][0]
    depts_present = sorted({z["dept"] for z in zones} | {r_["dept"] for r_ in rooms if r_["dept"] != "nucleo"})
    counts = {CAT_ES[k][0]: v for k, v in lvl_counts[lv].items() if k in CAT_ES}
    pieces = [[piece_es(k), v] for k, v in lvl_pieces[lv].most_common(8)]
    levels_out.append({
        "id": lid, "code": LEVEL_CODE.get(lid, lid), "name": lname, "elev": round(elev, 3), "h": round(nxt - elev, 3),
        "dept": main_dept, "mixed": len(depts_present) > 1, "depts": depts_present,
        "plate": {"area": plate_area, "poly": poly_json(plate) if plate is not None else []},
        "core": {"area": round(core_here.area, 1), "poly": poly_json(core_here)},
        "zones": zones, "rooms": rooms, "counts": counts, "pieces": pieces,
        "canopy": [{"area": round(c["fp"].area, 1), "finish": FINISH_ES.get(c["mat"], c["mat"])} for c in canopy],
        "areaByDept": {k: round(v, 1) for k, v in depts_area.items()},
        "file": f"levels/{lid}.glb",
    })

# ------------------------------------------------------------------ escribir niveles
for lv, cats in lvl_buckets.items():
    lid = LEVEL_ES[lv][0]
    g = GLB()
    for ck, mats in cats.items():
        prims = []
        for mname, (bk, mat) in mats.items():
            P, N, F, fid = bk.arrays()
            prims.append(g.primitive(P, N, F, g.material(mat), fid))
        g.node([v[1] for k, v in CAT_ES.items() if v[0] == ck][0], prims, {"key": ck})
    sz = g.write(os.path.join(OUT, "levels", f"{lid}.glb"), lvl_name_es(lv), {"features": lvl_features[lv]})
    print(f"levels/{lid}.glb {sz/1e6:.2f} MB  objetos={len(lvl_features[lv])}")

# ------------------------------------------------------------------ accesos y elementos exteriores
ENTR_ES = {"Residential": "Acceso residencial", "Office / Parking": "Acceso oficinas y estacionamiento",
           "Cafe 1": "Acceso café 1", "Cafe 2": "Acceso café 2"}
entrances = []
for k, bbs in entr.items():
    x = (min(b.Min.X for b in bbs) + max(b.Max.X for b in bbs)) / 2
    y = (min(b.Min.Y for b in bbs) + max(b.Max.Y for b in bbs)) / 2
    z = min(b.Min.Z for b in bbs) + 1.4
    entrances.append({"key": k, "name": (_en.ENTR_EN if LANG == "en" else ENTR_ES).get(k, k), "pos": pt_gl(x, y, z), "paneles": len(bbs)})

def bbox_gl(arrs_list):
    V = np.concatenate([to_gl(a[0]) for a in arrs_list])
    return V.min(0).round(3).tolist(), V.max(0).round(3).tolist()
site_parts = collections.defaultdict(list)
for o, us, arrs in site_objs:
    site_parts[LP[o.Attributes.LayerIndex].split("::")[-1]].extend(arrs)
site_info = {}
for k, arrs in site_parts.items():
    mn, mx = bbox_gl(arrs)
    site_info[k] = {"min": mn, "max": mx}


# ------------------------------------------------------------------ anclas de puntos de interés (exterior)
def all_V(sk):
    return np.concatenate([np.concatenate(bk.V) for bk, mat in shell[sk].values()])
def nearest(sk, az_deg, y_rel, radius=14.0):
    V = all_V(sk)
    tx = X0 + radius * math.sin(math.radians(az_deg)); ty = Y0 - radius * math.cos(math.radians(az_deg)); tz = Z0 + y_rel
    d = (V[:, 0] - tx) ** 2 + (V[:, 1] - ty) ** 2 + (V[:, 2] - tz) ** 2
    v = V[int(np.argmin(d))]
    return pt_gl(v[0], v[1], v[2])
core_c = core_poly.centroid
core_top = float(np.max(all_V("nucleo")[:, 2]))
anchors = {
    "fragmentos": nearest("fragmentos", 35, 40),
    "piel": nearest("piel", 10, 50),
    "diagrid": nearest("diagrid", 60, 20),
    "muro_cortina": nearest("cw_oficinas", 15, 21),
    "nucleo": pt_gl(core_c.x, core_c.y, core_top + 0.2),
}
plaza_fp = footprint(site_parts["Plaza"]) if "Plaza" in site_parts else None
if plaza_fp is not None:
    tower_fp = footprint(slabs[max(slabs, key=lambda k: footprint(slabs[k]).area)]).buffer(4)
    rp = plaza_fp.difference(tower_fp)
    # punto de la plaza hacia la cámara inicial (azimut ~35°)
    best = None
    for g in (rp.geoms if hasattr(rp, "geoms") else [rp]):
        c = g.representative_point()
        score = (c.x - X0) * math.sin(math.radians(35)) - (c.y - Y0) * math.cos(math.radians(35))
        if best is None or score > best[0]: best = (score, c)
    anchors["plaza"] = pt_gl(best[1].x, best[1].y, Z0 + 0.15)
if "Parking" in site_parts:
    mn, mx = bbox_gl(site_parts["Parking"]); anchors["estacionamiento"] = [round((mn[0] + mx[0]) / 2, 3), round(mx[1] + 0.1, 3), round((mn[2] + mx[2]) / 2, 3)]
site_pieces = collections.Counter(); stalls = set()
for o, us, arrs in site_objs:
    if "piece" not in us: continue
    if us["piece"].startswith("Parking stall"): stalls.add(us["piece"].split()[-1]); continue
    site_pieces[piece_es(us["piece"])] += 1
roof_cap = float(np.max(all_V("diagrid")[:, 2])) - Z0

features = {}
for sk, st in feature_stats.items():
    features[sk] = {"name": SHELL_NAMES[sk], "objetos": st["objetos"], "materiales": [[mat_es(n), c] for n, c in st["materiales"].most_common(6)]}
# suma de superficies
tot = collections.Counter(); core_tot = 0.0; gfa = 0.0
for L_ in levels_out:
    for k, v in L_["areaByDept"].items(): tot[k] += v
    core_tot += L_["core"]["area"]; gfa += L_["plate"]["area"] or 0
model = {
    "name": "Sky Fragment",
    "lang": LANG,
    "source": os.path.basename(SRC),
    "originRhino": [round(X0, 4), round(Y0, 4), round(Z0, 4)],
    "depts": {
        "comercio": {"name": _en.DEPT_NAMES_EN["comercio"] if LANG == "en" else "Comercio"},
        "oficinas": {"name": _en.DEPT_NAMES_EN["oficinas"] if LANG == "en" else "Oficinas"},
        "vivienda": {"name": _en.DEPT_NAMES_EN["vivienda"] if LANG == "en" else "Vivienda"},
        "nucleo": {"name": _en.DEPT_NAMES_EN["nucleo"] if LANG == "en" else "Núcleo y circulación vertical"},
    },
    "levels": levels_out,
    "entrances": entrances,
    "features": features,
    "curtainWall": dict(cw_stats),
    "site": site_info,
    "anchors": anchors,
    "sitePieces": site_pieces.most_common(14),
    "parkingStalls": sorted(stalls),
    "height": round(max(roof_cap, core_top - Z0), 2),
    "diagridTop": round(roof_cap, 2),
    "totals": {"areaByDept": {k: round(v, 1) for k, v in tot.items()}, "core": round(core_tot, 1), "gfa": round(gfa, 1)},
}
with open(os.path.join(OUT, "model.json"), "w", encoding="utf-8") as f:
    json.dump(model, f, ensure_ascii=False, separators=(",", ":"))
print("model.json", os.path.getsize(os.path.join(OUT, "model.json")) / 1e3, "KB")
print("Totales:", model["totals"])
for L_ in levels_out:
    print(f"  {L_['id']:3s} {L_['name']:12s} elev={L_['elev']:6.2f} h={L_['h']:.2f} dept={L_['dept']} mixed={L_['mixed']} placa={L_['plate']['area']} zonas={[(z['dept'], z['area'], z['label']) for z in L_['zones']][:6]} rooms={len(L_['rooms'])}")
