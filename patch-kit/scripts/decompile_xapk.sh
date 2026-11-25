#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Uso: $0 archivo.xapk directorio_salida" >&2
  exit 2
fi
XAPK=$(realpath "$1")
OUT=$(mkdir -p "$2" && realpath "$2")

for tool in unzip jadx apktool baksmali; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Falta herramienta requerida: $tool" >&2; exit 127; }
done
[[ -f "$XAPK" ]] || { echo "No existe el archivo: $XAPK" >&2; exit 2; }

mkdir -p "$OUT/splits" "$OUT/apktool" "$OUT/jadx" "$OUT/dex" "$OUT/smali"
unzip -oq "$XAPK" -d "$OUT/splits"
mapfile -t APKS < <(find "$OUT/splits" -type f -name '*.apk' | sort)
(("${#APKS[@]}" > 0)) || { echo "No se encontraron APK dentro del XAPK" >&2; exit 1; }

for apk in "${APKS[@]}"; do
  name=$(basename "$apk" .apk)
  echo "[Apktool] $name"
  apktool d -f "$apk" -o "$OUT/apktool/$name"
  echo "[JADX] $name"
  jadx --show-bad-code -d "$OUT/jadx/$name" "$apk"

  dexdir="$OUT/dex/$name"
  mkdir -p "$dexdir"
  unzip -oq "$apk" 'classes*.dex' -d "$dexdir"
  while IFS= read -r dex; do
    [[ -n "$dex" ]] || continue
    dexname=$(basename "$dex" .dex)
    echo "[Baksmali] $name/$dexname"
    baksmali disassemble "$dex" -o "$OUT/smali/${name}_${dexname}"
  done < <(find "$dexdir" -maxdepth 1 -type f -name 'classes*.dex' | sort -V)
done

echo "Terminado. Resultados en: $OUT"
echo "Los splits se conservaron separados; este paso no parchea ni reconstruye la aplicación."
