"""Traducciones al español para el explorador Sky Fragment."""
import re

FAM_ES = {"Deep Teal": "Verde azulado profundo", "Teal": "Verde azulado", "Aqua": "Agua marina", "Silver": "Plata",
          "Dark Wood": "Madera oscura", "Wood": "Madera", "Lamplight Stone": "Piedra cálida", "Sage": "Salvia",
          "White": "Blanco", "Plaster": "Yeso", "Slate": "Pizarra", "Night": "Noche"}
MAT_PART_ES = {
    "Accent lacquer blue": "Laca de acento azul", "Accessible bay paint": "Pintura de cajón accesible", "Diagrid steel": "Acero del diagrid",
    "Green lacquer": "Laca verde", "Outdoor stripe": "Tela de rayas para exterior", "Painted steel": "Acero pintado", "Velvet": "Terciopelo",
    "Accent lacquer teal": "Laca de acento verde azulado", "Facade crystal glass": "Vidrio de fragmentos de fachada", "Felt": "Fieltro",
    "Clear glass": "Vidrio claro", "Curtain wall glazing": "Vidrio de muro cortina", "EV bay paint": "Pintura de cajón para auto eléctrico",
    "Outer skin glass": "Vidrio de piel exterior", "Pool water": "Agua de alberca", "Brushed steel": "Acero cepillado", "Concrete": "Concreto",
    "Core wall, concrete 200": "Muro de núcleo, concreto 200", "Stone 600": "Piedra 600", "Burgundy textile": "Textil color vino",
    "Persian rug": "Tapete persa", "Red lacquer": "Laca roja", "Striped parasol canvas": "Lona de sombrilla a rayas",
    "Terracotta rug": "Tapete terracota", "Wool throw": "Manta de lana", "Boards 140": "Duela 140", "Oak timber": "Madera de encino",
    "Saddle leather": "Cuero café", "Teak": "Teca", "Timber slats": "Listones de madera", "Walnut": "Nogal", "Walnut panelling": "Lambrín de nogal",
    "Accent lacquer ochre": "Laca de acento ocre", "Brass": "Latón", "Flush door leaf, oak": "Hoja de puerta lisa, encino", "LED panel": "Panel LED",
    "Lampshade fabric": "Tela de pantalla de lámpara", "Light oak": "Encino claro", "Oak Herringbone 90": "Encino en espiga 90",
    "Rattan cane": "Ratán", "Stone": "Piedra", "Stone 600x300": "Piedra 600×300", "Stone path": "Sendero de piedra",
    "Warm light (lamp)": "Luz cálida (lámpara)", "Green tile": "Loseta verde", "Planting": "Vegetación", "Tile 200": "Loseta 200",
    "Upholstery": "Tapicería", "Ceramic": "Cerámica", "Concrete slab": "Losa de concreto", "Door frame, white": "Marco de puerta, blanco",
    "Line paint": "Pintura de señalización", "Marble": "Mármol", "Matt white": "Blanco mate", "Pool Stone 600x400": "Piedra de alberca 600×400",
    "Boucle": "Tela bouclé", "Cream rug": "Tapete crema", "Deck Boards 140": "Duela de exterior 140", "Linen": "Lino",
    "Paper lantern": "Lámpara de papel", "Partition, plaster": "Partición, yeso", "Plaster": "Yeso",
    "Plaza fragment paving": "Pavimento de fragmentos de la plaza", "Terrazzo 600": "Terrazo 600", "Travertine": "Travertino",
    "Aluminium fins": "Aletas de aluminio", "Carpet": "Alfombra", "Grating 100x30": "Rejilla 100×30", "Grey felt": "Fieltro gris",
    "Metal grating": "Rejilla metálica", "Mirror": "Espejo", "Parking bay": "Cajón de estacionamiento", "Pebble Strip": "Franja de grava",
    "Slate lacquer": "Laca pizarra", "Black lacquer": "Laca negra", "Blackened steel": "Acero ennegrecido", "Mullion 50 x 150": "Montante 50 × 150",
    "Spandrel panel": "Panel de antepecho",
    "Asphalt": "Asfalto", "Building, grey": "Edificio gris", "Building, light": "Edificio claro", "Building, warm": "Edificio cálido",
    "Ground": "Terreno", "Pavement": "Banqueta",
}
def mat_es(name):
    if not name: return name
    m = re.match(r"^SF (\d\d) (.+?) - (.+)$", name)
    if m:
        num, fam, part = m.groups()
        return f"{MAT_PART_ES.get(part, part)} (SF {num} {FAM_ES.get(fam, fam)})"
    m = re.match(r"^Context - (.+)$", name)
    if m:
        return f"{MAT_PART_ES.get(m.group(1), m.group(1))} (contexto)"
    return name

REVIT_TYPE_ES = {
    "Skyfragment - CW Housing": "Muro cortina Sky Fragment · Vivienda",
    "Skyfragment - CW Offices": "Muro cortina Sky Fragment · Oficinas",
    "Skyfragment - CW Commerce": "Muro cortina Sky Fragment · Comercio",
    "0915 x 2134mm": "Puerta 915 × 2134 mm", "0762 x 2032mm": "Puerta 762 × 2032 mm",
    "Interior - Partición 79 mm (1-hr)": "Partición interior 79 mm (resistencia al fuego 1 h)",
    "Interior - Partición 138 mm (1-hr)": "Partición interior 138 mm (resistencia al fuego 1 h)",
    "Interior - Partición 135 mm (2-hr)": "Partición interior 135 mm (resistencia al fuego 2 h)",
    "Skyfragment - Slab 100 mm": "Losa Sky Fragment 100 mm", "Skyfragment - Mezzanine 200 mm": "Losa de mezanine Sky Fragment 200 mm",
    "Genérico - 200 mm": "Genérico 200 mm",
}
def type_es(t):
    return REVIT_TYPE_ES.get(t, t) if t else ""

PART_ES = {
    "Timber slat": "Listón de madera", "Chair base": "Base de silla", "Book": "Libro", "Leg": "Pata", "Hook": "Gancho",
    "Chair back": "Respaldo de silla", "Headboard channel": "Canal de cabecera", "Door frame": "Marco de puerta", "Bench leg": "Pata de banca",
    "Wainscot panel": "Panel de lambrín", "Wainscot field": "Campo de lambrín", "Desk top": "Cubierta de escritorio",
    "Rug medallion": "Medallón de tapete", "Monitor foot": "Base de monitor", "Monitor arm": "Brazo de monitor", "Monitor": "Monitor",
    "Chair column": "Columna de silla", "Chair seat": "Asiento de silla", "Jar": "Frasco", "Saucer": "Plato de taza", "Cup": "Taza",
    "Castor": "Rodaja", "Desk leg": "Pata de escritorio", "Chair": "Silla", "Rug border": "Borde de tapete", "Rug field": "Campo de tapete",
    "Mirror": "Espejo", "Rug band": "Franja de tapete", "Curtain": "Cortina", "Bolster": "Cojín cilíndrico", "Bed runner": "Pie de cama",
    "Seat": "Asiento", "Cane seat": "Asiento de ratán", "Hoop back": "Respaldo curvo", "Fin": "Aleta", "Door leaf": "Hoja de puerta",
    "Table top": "Cubierta de mesa", "Cushion": "Cojín", "Table base": "Base de mesa", "Garment": "Prenda", "Table stem": "Pie de mesa",
    "Coffee bag": "Bolsa de café", "Nightstand": "Buró", "Nightstand plinth": "Zoclo de buró", "Knob": "Perilla",
    "Club chair arm": "Brazo de sillón club", "WC": "Inodoro", "WC cistern": "Tanque de inodoro", "Stool seat": "Asiento de banco",
    "Doormat": "Tapete de entrada", "Fire stair flight": "Tramo de escalera de emergencia", "Stair balustrade": "Barandal de escalera",
    "Wall handrail": "Pasamanos de muro", "Basin bowl": "Ovalín", "Tap": "Llave", "Striped pouf": "Puf a rayas", "Towel": "Toalla",
    "Vanity": "Lavabo con mueble", "Stone basin": "Lavabo de piedra", "Rug": "Tapete", "Base cabinets": "Gabinetes inferiores",
    "Countertop": "Cubierta", "Sink": "Tarja", "Cooktop": "Parrilla", "Wall cabinets": "Gabinetes superiores", "Range hood": "Campana",
    "Seat cushion": "Cojín de asiento", "Screen slat": "Listón de celosía", "Armchair": "Sillón", "Armchair back": "Respaldo de sillón",
    "Wardrobe": "Clóset", "Pouf foot": "Pata de puf", "Glass partition": "Cancel de vidrio", "Bed frame": "Base de cama",
    "Bed plinth": "Zoclo de cama", "Mattress": "Colchón", "Duvet": "Edredón", "Headboard cap": "Remate de cabecera",
    "Bench cushion": "Cojín de banca", "Club chair base": "Base de sillón club", "Club chair back": "Respaldo de sillón club",
    "Coffee table base": "Base de mesa de centro", "Coffee table top": "Cubierta de mesa de centro", "Desk screen": "Mampara de escritorio",
    "Mailbox door": "Puerta de buzón", "Dado rail": "Moldura de lambrín", "Skirting": "Zoclo", "Stone tub": "Tina de piedra",
    "Bar slat": "Listón de barra", "Fire stair landing": "Descanso de escalera de emergencia", "Sofa arm": "Brazo de sofá",
    "Console leg": "Pata de consola", "Fridge": "Refrigerador", "Lift door leaf": "Hoja de puerta de elevador",
    "Shower screen": "Cancel de regadera", "Turned leg": "Pata torneada", "Side table": "Mesa lateral", "Grating slat": "Barra de rejilla",
    "Floor finish": "Acabado de piso", "Bottle": "Botella", "Table leg": "Pata de mesa", "Rail post": "Poste de barandal",
    "Stool leg": "Pata de banco", "Bench slat": "Listón de banca", "Desk apron": "Faldón de escritorio", "Writing inlay": "Incrustación de escritorio",
    "Stool base": "Base de banco", "Console top": "Cubierta de consola", "Drain": "Coladera", "Floor indicator": "Indicador de piso",
    "Sofa seat": "Asiento de sofá", "Sofa back": "Respaldo de sofá", "Shower tray": "Plato de regadera", "Rolled arm": "Brazo enrollado",
    "Arm": "Brazo", "Rail": "Barandal", "Bench seat": "Asiento de banca", "Shelf": "Repisa", "Rolled towel": "Toalla enrollada",
    "Grab bar": "Barra de apoyo", "Basin": "Lavabo", "Laptop": "Computadora portátil", "Cart frame": "Estructura de carrito",
    "Loveseat base": "Base de sofá de dos plazas", "Loveseat back": "Respaldo de sofá de dos plazas", "Corner fin": "Aleta de esquina",
    "Sofa leg": "Pata de sofá", "Gate post": "Poste de reja", "Glass balustrade": "Barandal de vidrio", "Handrail": "Pasamanos",
    "Bar top": "Cubierta de barra", "Pastry": "Repostería", "Entrance canopy": "Marquesina de acceso", "Canopy fascia": "Faldón de marquesina",
    "Felt panel": "Panel de fieltro", "Bookshelf": "Librero", "Piano leg": "Pata de piano", "Back cushion": "Cojín de respaldo",
    "Foot ring": "Aro para pies", "Lounger frame": "Estructura de camastro", "Lounger cushion": "Cojín de camastro",
    "Lounger back": "Respaldo de camastro", "Headrest roll": "Reposacabezas", "Rain head": "Regadera de lluvia", "Plinth": "Pedestal",
    "Elevator car": "Cabina de elevador", "Coffee grinder": "Molino de café", "Shelf side": "Costado de repisa", "Portal post": "Poste del portal",
    "Sofa strap": "Correa de sofá", "Booth side": "Costado de cabina", "Cart shelf": "Repisa de carrito", "Easel leg": "Pata de caballete",
    "Towel shelf": "Toallero", "Shower post": "Poste de regadera", "Shower arm": "Brazo de regadera",
    "Pool enclosure curb": "Guarnición del cerco de alberca", "Pool glass screen": "Cancel de vidrio de alberca", "Screen cap": "Remate de celosía",
    "Pool gate": "Puerta de alberca", "Condenser": "Condensador", "Fan guard": "Rejilla de ventilador", "Slab Ground Floor": "Losa de planta baja",
    "Core cap": "Remate de núcleo", "Mezzanine slab": "Losa de mezanine", "Feature stair": "Escalera escultórica",
    "Stair glass balustrade": "Barandal de vidrio de escalera", "Stair handrail": "Pasamanos de escalera", "Bar counter": "Mostrador de barra",
    "Foot rail": "Reposapiés", "Back bar": "Contrabarra", "Back bar top": "Cubierta de contrabarra", "Arch niche": "Nicho en arco",
    "Espresso machine": "Cafetera de espresso", "Register": "Caja registradora", "Case base": "Base de vitrina", "Case glass": "Vidrio de vitrina",
    "Menu board": "Pizarrón de menú", "Banquette seat": "Asiento de banca corrida", "Banquette back": "Respaldo de banca corrida",
    "Shelf plinth": "Zoclo de repisa", "Portal lintel": "Dintel del portal", "Moon window wall": "Muro con ventana circular",
    "Baby change table": "Cambiador de bebé", "Bin": "Bote", "Rock reception desk": "Mostrador de recepción de piedra",
    "Directory screen": "Directorio digital", "Concierge desk": "Mostrador de conserjería", "Concierge top": "Cubierta de conserjería",
    "Curved sofa seat": "Asiento de sofá curvo", "Curved sofa back": "Respaldo de sofá curvo", "Mailboxes": "Buzones",
    "Booth floor": "Piso de cabina", "Booth roof": "Techo de cabina", "Booth back": "Respaldo de cabina", "Booth glass": "Vidrio de cabina",
    "Booth shelf": "Repisa de cabina", "Booth stool": "Banco de cabina", "Piano case": "Caja de piano", "Piano lid": "Tapa de piano",
    "Keyboard": "Teclado", "Piano bench": "Banco de piano", "Easel post": "Poste de caballete", "Crown ring": "Anillo de coronamiento",
    "Skin coping": "Remate de la piel", "Cavity vent grille": "Rejilla de ventilación de cámara", "Parapet upstand": "Pretil",
    "Canopy": "Cubierta", "Canopy edge": "Borde de cubierta", "Canopy soffit": "Plafón de cubierta", "Sofa frame": "Estructura de sofá",
    "Outdoor rug": "Tapete de exterior", "Bar body": "Cuerpo de barra", "Parasol base": "Base de sombrilla", "Parasol pole": "Mástil de sombrilla",
    "Parasol canopy": "Lona de sombrilla", "Daybed frame": "Estructura de diván", "Daybed mattress": "Colchón de diván",
    "Pool house roof": "Cubierta del pabellón de alberca", "Shower area": "Área de regadera", "Shower seat": "Asiento de regadera",
    "Shower curtain": "Cortina de regadera", "Pool coping": "Remate de alberca", "Sky mirror": "Espejo mirador", "Bar": "Barra",
}
def part_and_id(name):
    """Devuelve (parte en español, id del modelo) a partir del nombre del objeto en Rhino."""
    n = (name or "").strip()
    if re.match(r"^L\d\d-\d{4}$", n): return "", n
    m = re.match(r"^Wall (.+)$", n)
    if m: return "Muro", m.group(1)
    if n.startswith("Floor finish"): return "Acabado de piso", ""
    return PART_ES.get(n, ""), ""

def code_es(num):
    """Códigos de espacio: GF→PB, R→AZ; sufijos L (vestíbulo de elevadores)→VE y S (escalera)→ESC."""
    if not num: return num
    m = re.match(r"^(GF|MZ|R|\d\d)-(.+)$", num)
    if not m: return num
    pre, rest = m.groups()
    return f"{ {'GF': 'PB', 'R': 'AZ'}.get(pre, pre) }-{ {'L': 'VE', 'S': 'ESC'}.get(rest, rest) }"
