# LostMiner 1.6.4 — hallazgos adicionales (24-11-2026)

Este informe complementa la auditoría estática del XAPK original.

## Parser DEX regenerado
Se corrigió el parser offline: invoke-virtual e invoke-super (opcodes 0x6e y 0x6f) se decodifican como formato 35c. Se reprocesaron los seis DEX y se regeneraron los listados y CSV.
- 6 DEX; 37.396 clases; 248.837 métodos definidos; 232.651 métodos con bytecode.
- 636 clases propias del juego y 5.928 métodos.
- 817.308 referencias directas de llamadas; 29.931 llamadas entre clases del juego; 6.583 llamadas desde el juego a jPCT.
Los listados .smali siguen siendo Dalvik/Smali-like creados por parser propio, no salida oficial Baksmali ni fuente certificada como ensamblable.

## Motor
La evidencia apunta a jPCT-AE integrado con los sistemas propios del juego. El paquete com.threed.jpct incluye World, Object3D, Camera, FrameBuffer, GLRenderer, GL20, GLSLShader, TextureManager y SimpleVector. Hay 6.583 llamadas directas desde el juego a jPCT, el manifiesto requiere OpenGL ES 2.0 y hay 56 shaders GLSL. Unity Ads es SDK de anuncios, no evidencia de que el juego use Unity como motor.

## Idiomas
Textos.init() lee el recurso 0x7f0e03f2. Si su contenido es br, el predeterminado pasa a portugués brasileño. Si Textos.enableRUaES está habilitado, también reconoce ru y es. getLocale() produce pt_BR, ru_RU, es_ES o Locale.ENGLISH como fallback. La preferencia manual se guarda bajo language. El parser no reconstruye completamente los encoded_array estáticos, así que no se infiere que las cuatro opciones estén activas en todas las configuraciones.

## Multijugador: fragmentación UDP
SplitedMsg usa 10 bytes de cabecera: ID de 32 bits, cantidad e índice de parte (un byte cada uno), longitud total de 32 bits; el payload se fragmenta con tramos cercanos a 508 bytes.
LHost$Thread2 elimina ensamblados cuyo expirou() alcanza 16.000 ms. LClient$Thread2 no realiza caducidad periódica: elimina el objeto al completar y el mapa se limpia al cerrar o terminar el hilo. Una pérdida de fragmento en una sesión cliente activa podría retener entradas hasta cerrar o completar; esto es un riesgo estático, no una fuga medida en ejecución.
El ID se crea mediante Object.hashCode() de un nuevo byte[] copiado por MyBuf.getBuf(), no mediante contador monotónico; hay posibilidad teórica de colisión, no una colisión observada.
Se retira la hipótesis de truncamiento por reutilización de DatagramPacket: la prueba UDP de control en JVM no la reprodujo.
Parámetros encontrados: puerto LAN 4773; descubrimiento 0xFF; MAXBYTES_MSG 1200; maxUDPPackagesize 508; timeout 16.000 ms; reintentos ICE/conexión 300 ms; keepalive 5.000 ms; STUN stun:stun.l.google.com:19302; REMOTE_ON=true; enable_multiplayer=true.

## Bibliotecas nativas
- libjingle_peerconnection_so.so: WebRTC JNI (PeerConnection, DataChannel, ICE, Offer/Answer).
- libbuffer_pgl.so y libfile_lock_pgl.so: SDK ByteDance/Geckox, buffers mmap y locks.
- libpglarmor.so: cargada por PglCryptUtils, asociada a protección/criptografía PGL.
- libtt_ugen_layout.so: Yoga/UGen de SDK de anuncios.
- libapminsighta.so y libapminsightb.so: APM/diagnóstico nativo.
- libdatastore_shared_counter.so: AndroidX DataStore/Firebase Sessions.
- libnms.so: se carga desde com.pgl.ssdk; símbolos no permiten precisar su función.
Se analizaron metadatos ELF, símbolos, imports, dependencias, relocations y desensamblado AArch64, pero no se ejecutó C/C++ nativo ni se reconstruyó el fuente.

## Recursos sin resolver
assets/dic mide 4.016 bytes; no tiene magic estándar evidente ni formato identificado. No se encontró referencia literal en el código propio, pero myResources.openAsset(String) construye rutas por SDManage.getFileName(), por lo que no se demuestra que el archivo esté sin uso.

## Herramientas y límites
Se localizaron releases oficiales JADX 1.5.7 y Apktool 3.0.3, pero no fue posible descargar sus binarios al contenedor. No se instalaron JADX, Apktool, Baksmali/Smali, ADB, Android Emulator, aapt2 ni apksigner. Tampoco se ejecutó el juego ni se probó LAN con dos teléfonos. No se reconstruyó ni firmó APK.
