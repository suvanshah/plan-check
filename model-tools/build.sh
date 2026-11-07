#!/usr/bin/env bash
# Rebuilds data/ (English) and es/data/ (Spanish) from the Rhino model.
# Usage: tools/build.sh path/to/SkyFragmentfinaldigitaltwin.3dm
# Needs: Python 3 with rhino3dm, numpy and shapely; Node.js (npx downloads @gltf-transform/cli).
set -euo pipefail
SRC="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/build"
for LANG_CODE in en es; do
  RAW="$ROOT/build/raw_$LANG_CODE"
  if [ "$LANG_CODE" = "en" ]; then OUT="$ROOT/data"; else OUT="$ROOT/es/data"; fi
  rm -rf "$RAW"
  SF_LANG="$LANG_CODE" python3 "$ROOT/tools/build_explorer_data.py" "$SRC" "$RAW"
  rm -rf "$OUT"; mkdir -p "$OUT/levels"
  for f in "$RAW/shell.glb" "$RAW"/levels/*.glb; do
    rel="${f#$RAW/}"
    npx -y @gltf-transform/cli@4 weld "$f" "$ROOT/build/tmp.glb"
    npx -y @gltf-transform/cli@4 quantize "$ROOT/build/tmp.glb" "$OUT/$rel" --pattern "{position,normal}"
  done
  cp "$RAW/model.json" "$OUT/model.json"
done
echo "Done: data/ and es/data/ rebuilt."
