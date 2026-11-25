#!/usr/bin/env python3
"""Inspect native libraries in an APK or XAPK without modifying it."""
from __future__ import annotations
import argparse
import io
import sys
import zipfile
from pathlib import PurePosixPath

REQUIRED = {
    "libjingle_peerconnection_so.so",
    "libbuffer_pgl.so",
    "libfile_lock_pgl.so",
    "libpglarmor.so",
    "libtt_ugen_layout.so",
    "libapminsighta.so",
    "libapminsightb.so",
    "libdatastore_shared_counter.so",
    "libnms.so",
}
ABIS = ("armeabi-v7a", "arm64-v8a")


def libs_in_zip(zf: zipfile.ZipFile) -> dict[str, set[str]]:
    found = {abi: set() for abi in ABIS}
    for name in zf.namelist():
        p = PurePosixPath(name)
        parts = p.parts
        if len(parts) >= 3 and parts[0] == "lib" and parts[1] in found and p.suffix == ".so":
            found[parts[1]].add(p.name)
    return found


def merge(dst: dict[str, set[str]], src: dict[str, set[str]]) -> None:
    for abi in ABIS:
        dst[abi].update(src[abi])


def inspect(path: str) -> tuple[dict[str, set[str]], list[str]]:
    totals = {abi: set() for abi in ABIS}
    notes: list[str] = []
    with zipfile.ZipFile(path) as outer:
        nested_apks = [n for n in outer.namelist() if n.lower().endswith(".apk")]
        if nested_apks:
            for apk_name in nested_apks:
                try:
                    with zipfile.ZipFile(io.BytesIO(outer.read(apk_name))) as inner:
                        found = libs_in_zip(inner)
                    merge(totals, found)
                    notes.append(f"{apk_name}: {sum(map(len, found.values()))} bibliotecas nativas en ABIs auditadas")
                except (zipfile.BadZipFile, KeyError) as exc:
                    notes.append(f"AVISO: no se pudo inspeccionar {apk_name}: {exc}")
        else:
            merge(totals, libs_in_zip(outer))
    return totals, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", help="Archivo APK o XAPK a comprobar")
    args = parser.parse_args()
    try:
        found, notes = inspect(args.archive)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for note in notes:
        print(note)
    failed = False
    for abi in ABIS:
        present = found[abi]
        missing = sorted(REQUIRED - present)
        print(f"\n{abi}: {len(present)} .so encontrados")
        for name in sorted(present):
            print(f"  OK   {name}")
        if missing:
            failed = True
            print("  FALTAN bibliotecas requeridas:")
            for name in missing:
                print(f"  --   {name}")
        else:
            print("  OK   conjunto requerido completo")

    if failed:
        print("\nRESULTADO: NO contiene el conjunto completo requerido para ARMv7 y ARM64.")
        return 1
    print("\nRESULTADO: conjunto de bibliotecas requerido presente en ambos ABIs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
