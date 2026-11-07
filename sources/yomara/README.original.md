# BIMPLANING · Sky Fragment Explorer

Interactive web explorer for the **Sky Fragment** tower digital twin, built from the Rhino model
`SkyFragmentfinaldigitaltwin.3dm`. It follows the idea of the Planning Portal
[Interactive House](https://interactive.planningportal.co.uk/explore-house): you explore the building,
tap points of interest and read a details panel, here focused on floor plans and on the uses inside the tower.

- English: `index.html`
- Spanish / Español: `es/index.html`

## What it shows

| View | What you can do |
| --- | --- |
| **Exterior** | Orbit the tower with its urban context. Points of interest on the crystal fragments, glass skin, diagrid, curtain wall, core, entrances, roof, plaza and parking. “Facade by use” colors the curtain wall by the use of each level. |
| **Uses** | All 20 levels stacked and colored by use (Commerce, Offices, Housing, Core). Separate the use groups and open a table by level. |
| **Floor plans** | Pick a level and the model is cut 1.30 m above the floor, like a drawn plan. 3D or plan view with a scale bar, space labels with areas, color by use, and details for any element you tap. |

## Numbers from the model

Finished floor with an assigned use, measured on the model's floor finishes:

| Use | Area | Share | Levels |
| --- | ---: | ---: | --- |
| Housing | 1,390.6 m² | 50 % | GF lobby, L09–L17, roof terraces |
| Offices | 953.4 m² | 35 % | GF reception, L03–L08 |
| Commerce | 416.6 m² | 15 % | GF café, mezzanine, L01–L02 |

Sum of slab areas across the 20 levels: 3,693.1 m². Core footprint: 40.5 m² per level.
These are measurements of the model for comparing uses, not official areas.

## View it online (GitHub Pages)

1. In this repository go to **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**, branch **main**, folder **/ (root)**, and save.
3. After a minute the explorer is at `https://andreayomaramoralesgomez-lab.github.io/BIMPLANING/`
   and the Spanish version at `.../BIMPLANING/es/`.

## Run it on your computer

The page has to be served over http (opening `index.html` with a double click blocks the models):

```bash
python -m http.server 8000
```

Then open <http://localhost:8000>.

## Files

- `data/`, `es/data/`: `shell.glb` (envelope, site and context), `levels/*.glb` (interior of each level, loaded when you pick it)
  and `model.json` (levels, uses, spaces, areas). The `.glb` files are glTF 2.0 with `KHR_mesh_quantization`,
  in meters, Y up, origin at the center of the tower at ground floor level.
- `tools/`: scripts that rebuild both data folders from the `.3dm` (`tools/build.sh path/to/model.3dm`).
  Light fixtures, text labels and grid lines are not exported.

## Español

Explorador web de la torre **Sky Fragment** con tres vistas: **Exterior**, **Usos** (niveles apilados por uso)
y **Plantas** (corte a 1.30 m sobre el piso, etiquetas de espacios y superficies). La versión en español está en `es/`.
Para verlo en línea activa GitHub Pages (Settings → Pages → rama `main`, carpeta raíz) y abre `.../BIMPLANING/es/`.
