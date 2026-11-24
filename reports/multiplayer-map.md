# Multiplayer and chat code map

This is a focused call-reference map extracted from the app's `classes2.dex`; it is not reconstructed Java source. Method signatures are shown in DEX descriptor notation.

## LAN discovery

`DiscoverDevices.<init>(I)` creates a `DatagramSocket`, enables broadcast with `setBroadcast(true)`, sets a receive timeout, and starts receiver/sender threads.

`DiscoverDevices.senderDThread.run()` obtains the discovery packet from `StaticValues.getDiscoveryMsg()`, sends it to `255.255.255.255`, then enumerates active non-loopback network interfaces and sends to each `InterfaceAddress.getBroadcast()`.

`DiscoverDevices.receiverDThread.run()` blocks on `DatagramSocket.receive()`, reads the source IP from `DatagramPacket.getAddress()`, and passes the address to `ScreenMultiJoinOld.achouend()`.

`DiscoverDevices.stop_this()` closes the datagram socket and wakes the worker threads.

## Host/client connection path

- `NearbyConnectionsAux.discoverLocalServer()` starts local server discovery; `stop_discoverLocalServer()` stops it.
- `NearbyConnectionsAux.serverConnect(...)` routes to `startServer(...)`.
- `NearbyConnectionsAux.startServer(...)` constructs an `LHost` and calls `LHost.bind(port, listener)`.
- The `LHost.bind(...)` path starts its listener threads, creates a bound `DatagramSocket`, acquires the Wi-Fi multicast lock, and calls `proceedToBind()`.
- `NearbyConnectionsAux.startClient(...)` constructs `LClient` and calls `LClient.connect(listener, address, port, ...)`.
- `LClient.connect(...)` parses/normalizes the remote address, creates a datagram socket, starts worker threads, and reports connection errors through `connectError(...)`.
- `LConnection` contains WebRTC data-channel / ICE / offer-answer callbacks, including `onDataChannel`, `onIceCandidate`, `createOffer`, `createAnswer`, `addIceCandidate`, and send/receive methods.

## Message flow

- `NearbyConnectionsAux.sendMsg(...)`, `sendMsgToHost(...)`, and `sendMsgToOthers(...)` enqueue messages through `putMessage(...)`.
- `MessageSender.run()` / `MessageSenderAux.run()` process queued sends.
- Incoming bytes are decoded by `StaticValues.extractType`, `extractTo`, `extractMsg`, and `extractReliable`, then passed to `MultiPlayer.tratamsg(...)`.
- `ScreenMultiChat.sendMessage()` validates user input and calls `MultiPlayer.sendMessage(text, ...)`.
- Incoming chat text is marshalled back to the UI using `ClassePonte.runOnUI(...)` and appended by `MessageAdapter.add(...)`.

## Lifecycle and cleanup

`NearbyConnectionsAux.stopAll(...)` closes the host/client, clears message queues and leaves the multiplayer room. `LHost.close()` calls `OtherStuff.releaseMultiCast()`; `LHost.bind(...)` calls `OtherStuff.acquireMultiCast()`.

## High-value files/classes to inspect next

1. `com.fsilva.marcelo.lostminer.multiplayer.DiscoverDevices` — UDP broadcast discovery.
2. `com.fsilva.marcelo.lostminer.multiplayer.mynet.LHost` — server port bind, receiver/sender and multicast-lock lifecycle.
3. `com.fsilva.marcelo.lostminer.multiplayer.mynet.LClient` — client socket setup and connect retries.
4. `com.fsilva.marcelo.lostminer.multiplayer.mynet.LConnection` — WebRTC peer connection, ICE and data channel.
5. `com.fsilva.marcelo.lostminer.droidstuff.OtherStuff` — acquire/release multicast lock.
6. `com.fsilva.marcelo.lostminer.multiplayer.NearbyConnectionsAux` — orchestration, queues and connect/disconnect callbacks.

## Caution

The discovery broadcast path and the peer connection path are distinct parts of the multiplayer stack. A device appearing in local discovery does not prove the WebRTC data channel will negotiate successfully. Likewise, a successful connection does not prove game-state messages or chat are flowing correctly. Test discovery, host/client handshake, WebRTC channel, game packets and chat separately.
