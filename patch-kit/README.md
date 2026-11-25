# Kit de trabajo para LostMiner 1.6.4 (build 142)

Este kit prepara el trabajo reproducible para corregir el multijugador LAN y verificar ARMv7/ARM64. **No es una APK modificada**: no se pudo compilar ni probar el juego en este entorno. No reemplaza el XAPK original.

## Incluye
- `LAN-PATCH-SPEC.md`: cambios justificados por el análisis y pruebas necesarias.
- `scripts/decompile_xapk.sh`: extrae el XAPK, descompila cada split con Apktool, genera Java con JADX y desensambla todos los DEX con Baksmali.
- `scripts/check_abis.py`: comprueba los .so presentes para ARMv7 y ARM64.

## Uso (Linux/WSL)

Instala Java, Python 3, JADX, Apktool y Baksmali. Ejecuta:

```bash
chmod +x patch-kit/scripts/decompile_xapk.sh
patch-kit/scripts/decompile_xapk.sh /ruta/LostMiner.xapk ./work
python3 patch-kit/scripts/check_abis.py /ruta/LostMiner.xapk
```

Los splits se conservan por separado. Los scripts no modifican el original ni reconstruyen una APK.

## Bloqueo ARMv7

El XAPK auditado tiene bibliotecas nativas en `arm64-v8a`, pero no en `armeabi-v7a`. Hace falta obtener o compilar versiones 32-bit compatibles de cada dependencia. Cambiar el manifiesto o renombrar bibliotecas ARM64 no añade soporte ARMv7.

## Estado

- Análisis estático LAN: realizado.
- Desensamblado Smali oficial completo y parche LAN: pendiente.
- Bibliotecas ARMv7: no disponibles en el XAPK auditado.
- APK reconstruida, firmada e instalada: no.
- Prueba LAN en dos dispositivos: no.
