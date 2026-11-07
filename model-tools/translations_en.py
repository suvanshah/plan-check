"""English display names for the Sky Fragment explorer (internal keys stay the same as the Spanish build)."""
import re

LEVEL_EN = {"Ground Floor": ("PB", "Ground floor"), "Mezzanine": ("MZ", "Mezzanine"), "Roof": ("AZ", "Roof")}
for _i in range(1, 18):
    LEVEL_EN[f"Level {_i:02d}"] = (f"N{_i:02d}", f"Level {_i:02d}")
CODE_EN = {"PB": "GF", "MZ": "MZ", "AZ": "RF", **{f"N{_i:02d}": f"L{_i:02d}" for _i in range(1, 18)}}

def lvl_name_en(n):
    return LEVEL_EN.get(n, (n, n))[1]

ROOM_EN = {
    "Lift Lobby": "Lift lobby", "Restroom Lobby": "Restroom lobby", "Office Reception": "Office reception",
    "Residential Lobby": "Residential lobby", "Art Lounge": "Art lounge", "Sky Deck": "Sky deck", "Pool Deck": "Pool deck",
    "Changing Room 1": "Changing room 1", "Changing Room 2": "Changing room 2", "Accessible WC + Shower": "Accessible WC with shower",
    "Plant": "Plant room",
    "Commerce": "Commerce (typical floor)", "Offices": "Offices (typical floor)", "Housing": "Housing (typical floor)",
}
def room_en(name):
    return ROOM_EN.get(name, name)

FINISH_EN = {
    "SF 10 Plaster - Terrazzo 600": "Terrazzo 600", "SF 08 Sage - Tile 200": "Tile 200 (sage)",
    "SF 07 Lamplight Stone - Stone 600x300": "Stone 600×300", "SF 04 Silver - Stone 600": "Stone 600",
    "SF 06 Wood - Boards 140": "Timber boards 140", "SF 11 Slate - Carpet": "Carpet",
    "SF 07 Lamplight Stone - Oak Herringbone 90": "Oak herringbone 90",
    "SF 09 White - Pool Stone 600x400": "Pool stone 600×400", "SF 10 Plaster - Deck Boards 140": "Deck boards 140",
    "SF 11 Slate - Pebble Strip": "Pebble strip", "SF 11 Slate - Grating 100x30": "Metal grating 100×30",
    "SF 09 White - Concrete slab": "Concrete slab", "SF 09 White - Tile 200": "Tile 200 (white)",
}
CAT_EN = {
    "Floors": ("pisos", "Floors"), "Walls": ("muros", "Walls"), "Doors": ("puertas", "Doors"),
    "Stairs": ("escaleras", "Stairs"), "Railings": ("barandales", "Railings"),
    "Furniture": ("mobiliario", "Furniture"), "Casework": ("carpinteria", "Casework"),
    "Plumbing Fixtures": ("sanitarios", "Plumbing fixtures"), "Specialty Equipment": ("equipo", "Specialty equipment"),
    "Generic Models": ("genericos", "Generic models"), "Lighting Fixtures": ("luminarias", "Lighting fixtures"),
}
def piece_en(p):
    if p.startswith("Fire stair "):
        a, b = p[len("Fire stair "):].split(" - ")
        return f"Fire stair {lvl_name_en(a)} – {lvl_name_en(b)}"
    if p == "Crown ring - diagrid compression ring": return "Diagrid crown ring"
    return p

def mat_en(name):
    return name

REVIT_TYPE_EN = {
    "Skyfragment - CW Housing": "Sky Fragment curtain wall · Housing",
    "Skyfragment - CW Offices": "Sky Fragment curtain wall · Offices",
    "Skyfragment - CW Commerce": "Sky Fragment curtain wall · Commerce",
    "0915 x 2134mm": "Door 915 × 2134 mm", "0762 x 2032mm": "Door 762 × 2032 mm",
    "Interior - Partición 79 mm (1-hr)": "Interior partition 79 mm (1-hour fire rating)",
    "Interior - Partición 138 mm (1-hr)": "Interior partition 138 mm (1-hour fire rating)",
    "Interior - Partición 135 mm (2-hr)": "Interior partition 135 mm (2-hour fire rating)",
    "Skyfragment - Slab 100 mm": "Sky Fragment slab 100 mm", "Skyfragment - Mezzanine 200 mm": "Sky Fragment mezzanine slab 200 mm",
    "Genérico - 200 mm": "Generic 200 mm",
}
def type_en(t):
    return REVIT_TYPE_EN.get(t, t) if t else ""

def part_and_id_en(name):
    n = (name or "").strip()
    if re.match(r"^L\d\d-\d{4}$", n): return "", n
    m = re.match(r"^Wall (.+)$", n)
    if m: return "Wall", m.group(1)
    if n.startswith("Floor finish"): return "Floor finish", ""
    if n in ("Object", ""): return "", ""
    return n[:1].upper() + n[1:], ""

def code_en(num):
    return num

SHELL_NAMES_EN = {"fragmentos": "Crystal fragments", "piel": "Glass skin", "diagrid": "Diagrid", "losas": "Slabs",
                  "nucleo": "Core", "cw_comercio": "Curtain wall · Commerce", "cw_oficinas": "Curtain wall · Offices",
                  "cw_vivienda": "Curtain wall · Housing", "sitio": "Site", "contexto": "Urban context"}
ENTR_EN = {"Residential": "Residential entrance", "Office / Parking": "Office and parking entrance",
           "Cafe 1": "Café entrance 1", "Cafe 2": "Café entrance 2"}
DEPT_NAMES_EN = {"comercio": "Commerce", "oficinas": "Offices", "vivienda": "Housing", "nucleo": "Core and vertical circulation"}
