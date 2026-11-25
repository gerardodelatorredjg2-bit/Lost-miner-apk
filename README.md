# LostMiner APK analysis workspace

Initial analysis of the user-provided LostMiner XAPK, version **1.6.4 (build 142)**.

## Contents

- `reports/initial-analysis.md` — package, split, DEX, native-library and localization findings.
- `reports/multiplayer-map.md` — code-level map of LAN discovery, connections and chat.
- `tools/README.md` — offline analysis tooling and current limitations.
- `patch-kit/` — reproducible decompilation, ABI checks and LAN patch specification (no patched APK yet).

## Important status

This repository contains **analysis notes**, not a modified application. The original XAPK has not been committed: the available GitHub connection supports text-file commits but does not expose binary/release-asset upload for the 59 MB XAPK. The downloadable analysis archive is provided separately in the ChatGPT conversation.

No APK patch, ARMv7 port, language removal, APK rebuild, or signing has been performed yet. The findings below are a starting point for those tasks.

## Reproducibility

Input file SHA-256:
`92a1209ebbbf3284b94f45912cddefdf134ea74107f451851384911939678e62`

See the reports before making changes. Keep the original APK/XAPK immutable and work on a separate copy.
