# LostMiner 1.6.4 — XAPK analysis

## Input and integrity

- Package: `com.fsilva.marcelo.lostminer`
- App version: **1.6.4**, version code **142**
- XAPK size: 61,775,196 bytes
- XAPK SHA-256: `92a1209ebbbf3284b94f45912cddefdf134ea74107f451851384911939678e62`
- All three APK ZIP containers passed `unzip -t`.
- All six DEX files passed the SHA-1 and Adler-32 header integrity checks in the offline parser.

## XAPK composition

| Split | Size | Contents |
|---|---:|---|
| `com.fsilva.marcelo.lostminer.apk` | 48,015,292 bytes | Base APK, app code, assets and resources |
| `config.arm64_v8a.apk` | 13,710,373 bytes | 9 ARM64 native shared libraries |
| `config.mdpi.apk` | 46,183 bytes | MDPI density resources |

The XAPK contains **no `armeabi-v7a` split**. The base manifest declares package `com.fsilva.marcelo.lostminer`, min SDK 24, target SDK 36, and `requiredSplitTypes="base__abi,base__density"`.

## DEX and code inventory

The base APK has four primary DEX files (DEX 037). It also embeds two Audience Network DEX payloads in `assets/audience_network/` (DEX 035).

| DEX payload | Classes | Declared methods |
|---|---:|---:|
| Base `classes.dex` | 9,504 | 54,949 |
| Base `classes2.dex` | 9,731 | 56,322 |
| Base `classes3.dex` | 7,189 | 57,750 |
| Base `classes4.dex` | 7,642 | 55,346 |
| Audience Network `classes.dex` | 38 | 25 |
| Audience Network `classes2.dex` | 3,292 | 24,445 |

The package-specific game logic is present in the base DEX files. Particularly relevant classes include `NearbyConnectionsAux`, `DiscoverDevices`, `MultiPlayer`, `LClient`, `LHost`, `LConnection`, `StaticValues`, and chat classes such as `ScreenMultiChat`.

## Native code and ARM support

All 9 packaged shared libraries are ELF64/AArch64 and exist only under `lib/arm64-v8a/`. There is no 32-bit ARM library directory in the XAPK.

The largest native library is `libjingle_peerconnection_so.so` (12,534,176 bytes). The Java/Dex connection layer references WebRTC interfaces (`other/webrtc/WDataChannelInterface`) and ICE/offer-answer negotiation, so a true ARMv7 build cannot be achieved merely by changing the ABI label: the required 32-bit WebRTC native binary and any other required 32-bit dependencies must be sourced or rebuilt and then tested.

The base APK contains no `.so` files of its own.

## LAN multiplayer findings

- Local server discovery is implemented in `DiscoverDevices` using UDP `DatagramSocket`/`DatagramPacket`.
- The sender broadcasts a discovery payload to `255.255.255.255` and to the broadcast addresses of active network interfaces.
- The discovery receiver waits for datagrams and passes the discovered address to the older join screen.
- The LAN/peer layer also uses `LHost`, `LClient`, and `LConnection`; the host path acquires/releases a Wi-Fi multicast lock via `OtherStuff.acquireMultiCast()` / `releaseMultiCast()`.
- The connection layer references WebRTC data channels, ICE candidates, STUN messages, and offer/answer exchange.
- Chat entry is handled by `ScreenMultiChat.sendMessage()`, which calls `MultiPlayer.sendMessage()`; incoming messages return through `ScreenMultiChat.onMessage()`.

Relevant permissions present in the base manifest include `INTERNET`, `ACCESS_NETWORK_STATE`, `ACCESS_WIFI_STATE`, and `CHANGE_WIFI_MULTICAST_STATE`.

These findings narrow the likely LAN investigation areas to UDP broadcast/interface handling, the multicast lock lifecycle, the host/client socket setup, and WebRTC/ICE negotiation. They do **not** by themselves prove which one causes the reported failure.

## Languages

The package listing includes many localized store-name variants; that list should not be mistaken for in-game language support.

The app's `Textos` code contains locale cases for Portuguese (Brazil), Russian (Russia), and Spanish (Spain), with a resource fallback path. The base APK has no `res/values-xx` language folders in the inspected ZIP entry list. The separate `assets/dic` file is a 4,016-byte binary data file and has not yet been decoded. Therefore, the exact complete language set and the feasibility of safely removing every non-English/non-Spanish language still need verification against the dictionary and runtime resources.

## Tooling limitations / completeness

The XAPK, APK split contents, binary Android manifests, DEX structures, class/method tables, strings, method references, resource/native file inventories, and selected method invocation cross-references were extracted with offline Python/ZIP/ELF tooling.

A full Java/Kotlin source decompilation and full Android resource recompilation were **not** completed: JADX, Apktool, AAPT/AAPT2, smali/baksmali and apksigner are not installed in this environment, and package downloads could not be reached. The produced DEX inventories and cross-reference map are useful reverse-engineering artifacts, but are not equivalent to reconstructed Java source.

## Next engineering steps

1. Obtain/run JADX and Apktool in an environment with those tools; decode the complete base and split APKs.
2. Inspect `DiscoverDevices`, `LHost`, `LClient`, `LConnection`, and `OtherStuff.acquireMultiCast()` as full smali/source, then reproduce the LAN fault.
3. Establish ARMv7 native dependency compatibility, particularly the WebRTC library. Do not mark ARMv7 as supported until a complete 32-bit build launches and multiplayer is exercised.
4. Decode the dictionary/localization data and identify exactly which language tables can be removed without damaging game text.
5. Rebuild/sign a separate test APK set and validate install, startup, local discovery, host/client joins, chat and disconnection.
