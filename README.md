# Online Chat Messenger

A real-time chat application using hybrid TCP/UDP architecture for efficient network communication.

## System Architecture

The system separates control plane and data plane operations using different transport protocols.

### Network Design

```
Client A                     Server                      Client B
   |                           |                            |
   |--TCP: Create Room-------->|                            |
   |<------Token (ABC)---------|                            |
   |                           |<--TCP: Join Room-----------|
   |                           |--------Token (XYZ)-------->|
   |                           |                            |
   |--UDP: REGISTER + Token--->|<--UDP: REGISTER + Token----|
   |                           |                            |
   |--UDP: "Hello"------------>|                            |
   |                           |---UDP: "Hello"------------>|
   |                           |<--UDP: "Hi"----------------|
   |<--UDP: "Hi"---------------|                            |
```

### Protocol Layers

**TCP Layer (Port 9090)** - Connection-oriented control plane
- Three-way handshake ensures reliable delivery
- Stateful request-response model
- Operations: CREATE_ROOM, JOIN_ROOM
- Returns authentication token for UDP phase

**UDP Layer (Port 9091)** - Connectionless data plane
- No connection setup overhead
- Low latency message delivery
- Message broadcast to room participants
- Trade-off: Packet loss possible but acceptable for chat

### Custom Protocols

**TCRP (TCP Chat Room Protocol)**
- Binary framing with length-prefixed fields
- Header: room_name_size(1B) + operation(1B) + state(1B) + payload_size(28B)
- State machine: REQUEST -> COMPLIANCE -> COMPLETE
- JSON payload for structured data

**UCRP (UDP Chat Room Protocol)**
- Compact binary format for efficiency
- Structure: room_len(1B) + token_len(1B) + room_name + token + message
- Special commands: `__REGISTER__`, `__LEAVE__`, `__ROOM_CLOSED__`

## How to Use

### Start Server

```bash
cd server
python server.py
```

Default configuration:
- TCP port: 9090
- UDP port: 9091
- Host: localhost

### Start Client

```bash
cd client
python client.py
```

Enter server address and ports when prompted.

### Create/Join Room

1. Select option 1 to create a room or option 2 to join
2. Enter room name and username
3. TCP handshake completes and issues token
4. UDP chat session begins automatically

### Chat Commands

- Type message and press Enter to send
- Type `exit`, `quit`, or `q` to leave room
- Press Ctrl+C to force quit

## Architecture Components

**Server Components**
- `tcp_server.py`: Handles room creation/join requests
- `udp_server.py`: Relays chat messages between participants
- `room_manager.py`: Maintains room state and token validation
- Thread pool for concurrent client handling

**Client Components**
- `tcp_client.py`: Performs initial handshake
- `udp_client.py`: Manages chat session with send/receive threads
- Separate threads prevent blocking I/O

**Protocol Components**
- `tcrp.py`: TCP protocol serialization/deserialization
- `ucrp.py`: UDP payload encoding/decoding

## Network Characteristics

**TCP Advantages Used**
- Ordered delivery for handshake sequence
- Flow control prevents buffer overflow
- Error detection via checksums

**UDP Advantages Used**
- Minimal latency for real-time chat
- No connection state overhead
- Efficient multicast to room members

**Design Trade-offs**
- Chat messages may arrive out of order or be lost (UDP)
- Control messages are guaranteed delivered (TCP)
- Hybrid approach balances reliability and performance
