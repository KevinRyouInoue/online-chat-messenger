# Technical Deep Dive: Online Chat Messenger

This document explains the core Computer Science and Networking concepts embodied in this project, including protocols, API design, threading, serialization, and runtime behavior. It is intended for developers who want to understand how the system works.

## Contents
- Networking Architecture (TCP vs UDP)
- Custom Protocols (TCRP and UCRP)
- State Machines and Handshakes
- Serialization and Message Framing
- API Surfaces and Contracts
- Concurrency and Threading Model
- Data Structures and Persistence
- Error Handling and Validation
- Performance Considerations
- Security Considerations
- Extensibility Roadmap

---

## Networking Architecture (TCP vs UDP)

The system uses a hybrid architecture:

- TCP for control-plane operations (room creation/join) because it provides:
  - Reliable, ordered delivery
  - Backpressure (flow control)
  - Connection semantics (supports request/response handshakes)

- UDP for data-plane (chat messages) because it offers:
  - Low latency, no connection setup
  - Smaller per-message overhead
  - Simpler multiplexing by tokens/room name

Trade-off: UDP may drop packets or change order. For chat, occasional loss is tolerable, and the simplicity/latency wins over TCP's guarantees.

## Custom Protocols (TCRP and UCRP)

Two in-house protocols define interoperable contracts between client and server.

### TCRP (TCP Room Protocol)
Used over TCP during the handshake phase.

Fields:
- room_name (length-prefixed)
- op (1=create, 2=join)
- state (0=request, 1=compliance, 2=complete)
- payload (e.g., username or token JSON)

Server flow:
1. Receive REQUEST (room_name, op, username)
2. Emit COMPLIANCE acknowledging success/failure
3. Emit COMPLETE with token if success

### UCRP (UDP Chat Room Protocol)
Used over UDP for messaging.

Fields (length-prefixed segments):
- room_name
- token
- message

Special messages:
- "__REGISTER__" to bind sender's UDP (ip,port) to token for fan-out
- "__LEAVE__" to request removal (and host-triggered room teardown)
- "__ROOM_CLOSED__" server-initiated notice when host exits

## State Machines and Handshakes

### TCP Handshake State Machine
- REQUEST -> COMPLIANCE -> COMPLETE
- Failure at any step aborts the operation

### Room Lifecycle
- Created by host (token designated as host_token)
- Members join (tokens appended)
- Host leaves -> server closes room, notifies members, deletes state

## Serialization and Message Framing

Binary framing avoids ambiguity and supports efficient parsing:
- Length-prefixing prevents delimiter collision
- Encoding: UTF-8 for text payloads
- JSON used when nested structures are convenient (e.g., compliance results)

## API Surfaces and Contracts

Python modules expose minimal, clear APIs:

- client/tcp_client.py
  - connect() -> bool
  - create_room(room_name, username) -> bool
  - join_room(room_name, username) -> bool
  - get_token() -> str | None

- client/udp_client.py
  - start() -> None (spawns receiver thread, enters send loop)
  - stop() -> None (sends __LEAVE__ and closes socket)

- server/tcp_server.py
  - start() -> accept-loop; spawns per-connection thread

- server/udp_server.py
  - start() -> recvfrom loop; processes REGISTER/LEAVE/messages
  - notify_room_closed(room_name) -> fan-out closure notice

- server/room_manager.py
  - create_room(room_name, username, address) -> (bool, token)
  - join_room(room_name, username, address) -> (bool, token)
  - validate_token_and_address(token, room_name) -> (bool, reason)
  - delete_room_if_host_left(room_name, token) -> None
  - save_to_json()/load_from_json() -> persistence

Contract principles:
- Idempotency for REGISTER (re-register updates address)
- Deterministic side effects (create vs join)
- Explicit success/failure signaling (booleans, reason strings)

## Concurrency and Threading Model

- TCP server: per-connection threads via `threading.Thread`
- UDP server: single-threaded recvfrom loop; minimal critical sections
- Client: background receiver thread + foreground stdin loop

Rationale: Python threads are sufficient (I/O bound). The GIL is not a bottleneck for network waits.

## Data Structures and Persistence

- rooms: dict[str, {host_token: str, members: list[str], created_at: float}]
- tokens: dict[str, {username: str, room_name: str, is_host: bool, address: (ip,port)}]

Persistence:
- Saved to `room_manager.json` with `json.dump(..., ensure_ascii=False)`
- Loaded on demand or after mutations to maintain crash tolerance

## Error Handling and Validation

- Validate token membership and room existence before relaying
- Clear error messages for client and server logs
- Defensive coding around I/O and JSON parsing
- Use of try/except around network operations and file operations

## Performance Considerations

- UDP fan-out avoids per-recipient TCP connections
- Minimal allocations during hot paths (reuse sockets)
- Batching is possible but not required for chat scale
- Max UDP payload bounded (`MAX_MESSAGE_SIZE=4096`)

## Security Considerations

- Tokens generated with `secrets.token_hex` (cryptographically strong)
- No encryption; suitable only for trusted networks or behind TLS tunnels/VPN
- Spoofing risk on UDP mitigated by token and room validation
- Rate limiting and auth could be added for production

## Extensibility Roadmap

- WebSocket gateway for browser clients
- Authentication (JWT) and user profiles
- Message history (persisted), pagination
- Presence and typing indicators
- NAT traversal/STUN for P2P modes
- Monitoring/metrics (Prometheus, OpenTelemetry)
- Structured logging and log levels
