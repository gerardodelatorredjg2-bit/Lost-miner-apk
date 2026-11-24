# Offline analysis tools

The downloadable analysis bundle contains:

- `analyze_xapk.py`: standard-library-only XAPK/APK extraction, binary AndroidManifest decoding, DEX inventory, string/class/method/field reference export, ELF inventory and checksums.
- `inspect_game_logic.py`: targeted DEX call-reference extraction for multiplayer and chat code.

Example:
```bash
python tools/analyze_xapk.py LostMiner.xapk --out decoded
python tools/inspect_game_logic.py decoded/com.fsilva.marcelo.lostminer.apk --out decoded/game_multiplayer_calls.json
```

These are offline inspection utilities, not replacements for JADX/Apktool. The current environment did not have JADX, Apktool, AAPT/AAPT2, smali/baksmali or apksigner installed, so full source-level decompilation/rebuild was not performed.
