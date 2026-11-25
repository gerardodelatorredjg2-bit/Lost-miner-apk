# Especificación del parche LAN — LostMiner 1.6.4 (build 142)

## Código localizado

- `com.fsilva.marcelo.lostminer.multiplayer.DiscoverDevices`: descubrimiento UDP por broadcast.
- `...multiplayer.mynet.LHost`: socket del anfitrión.
- `...multiplayer.mynet.LClient`: socket del cliente y reintentos.
- `...multiplayer.mynet.LConnection`: ICE/WebRTC y DataChannel.
- `...multiplayer.NearbyConnectionsAux`: ciclo de vida, colas y callbacks.
- `...droidstuff.OtherStuff`: multicast lock.

El descubrimiento usa el puerto UDP 4773 y byte identificador `0xFF`. Que un dispositivo aparezca en el descubrimiento no demuestra que WebRTC haya conectado.

## Corrección prioritaria

`SplitedMsg` reensambla mensajes fragmentados. `LHost$Thread2` elimina los ensamblados que alcanzan 16.000 ms. En el análisis estático, `LClient$Thread2` no mostró un ciclo periódico equivalente de caducidad: entradas incompletas podrían permanecer hasta completarse o cerrarse el hilo.

**Cambio requerido:** aplicar en el receptor cliente una limpieza periódica de ensamblados incompletos con más de 16.000 ms, utilizando reloj monotónico y sin borrar mensajes completados.

No se proporciona un parche Smali automático: los listados disponibles proceden de un parser propio y no son Smali oficial ensamblable. Antes de editar deben obtenerse los métodos y descriptores reales de `LClient$Thread2` y `SplitedMsg` con Baksmali. Inventar campos u offsets podría romper el DEX.

## No son fallos confirmados

1. El ID se deriva de `Object.hashCode()` de un `byte[]` copiado. Hay posibilidad teórica de colisión, pero no se observó.
2. Parámetros observados: timeout 16.000 ms, reintentos 300 ms y keepalive 5.000 ms. No cambiarlos sin pruebas de interoperabilidad.
3. Se retiró la hipótesis de truncamiento por reutilización de `DatagramPacket`: una prueba UDP de control en JVM no la reprodujo.

## Pruebas de aceptación

1. Ambos teléfonos se descubren en la misma Wi-Fi; repetir tras reabrir el menú.
2. Conectar con ambos roles de host y cliente; revisar ICE y apertura del DataChannel.
3. Comprobar tráfico de juego y chat en ambos sentidos.
4. Simular una interrupción breve y pérdida de fragmentos; comprobar caducidad y recepción posterior.
5. Salir y volver a entrar; verificar cierre de sockets, hilos y multicast lock.
6. Repetir con el APK original para detectar regresiones.

Una compilación no es una reparación validada hasta pasar las pruebas en dispositivos reales.
