# Online Chat Messenger

A real-time chat application built with Python using TCP for connection management and UDP for message transmission.

## 📋 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Protocol Overview](#protocol-overview)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
 - [Deep Dive: Technical Concepts](#deep-dive-technical-concepts)

## ✨ Features

- **Room-based Chat**: Create or join chat rooms
- **Real-time Messaging**: UDP-based fast message delivery
- **Multi-user Support**: Multiple users can join the same room
- **Host Management**: Room creator has special privileges
- **Automatic Cleanup**: Rooms are deleted when the host leaves
- **Secure Token System**: Token-based authentication for chat sessions

## 🏗️ Architecture

The application uses a **hybrid TCP/UDP architecture**:

- **TCP Connection Phase**: 
  - Used for room creation and joining
  - Handles authentication and token generation
  - Reliable connection for critical operations

- **UDP Chat Phase**:
  - Used for real-time message transmission
  - Fast, low-latency communication
  - Suitable for chat messages

## 📦 Requirements

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/KevinRyouInoue/online-chat-messenger.git
cd online-chat-messenger
```

2. Verify the project structure:
```
online-chat-messenger/
├── client/
│   ├── client.py          # Main client application
│   ├── tcp_client.py      # TCP connection handler
│   └── udp_client.py      # UDP chat handler
├── server/
│   ├── server.py          # Main server application
│   ├── tcp_server.py      # TCP server for room management
│   ├── udp_server.py      # UDP server for chat relay
│   └── room_manager.py    # Room and token management
└── protocol/
    ├── tcrp.py            # TCP Room Protocol
    └── ucrp.py            # UDP Chat Room Protocol
```

## 💻 Usage

### Step 1: Start the Server

Open a terminal and navigate to the server directory:

```bash
cd server
python server.py
```

You'll be prompted for:
- **Host name** (default: localhost)
- **TCP port** (default: 9090)
- **UDP port** (default: 9091)

Example:
```
Host name (default: localhost): [Press Enter]
TCP port number (default: 9090): [Press Enter]
UDP port number (default: 9091): [Press Enter]
[Started] TCP server bound to localhost:9090
[Started] UDP server bound to localhost:9091

UDP chat server started. Waiting for messages...
Press Ctrl+C to stop...
```

### Step 2: Start the First Client (Create a Room)

Open a **new terminal** and navigate to the client directory:

```bash
cd client
python client.py
```

Configure the connection:
```
Server address (default: 127.0.0.1): [Press Enter]
TCP port number (default: 9090): [Press Enter]
UDP port number (default: 9091): [Press Enter]
```

Select option 1 to create a room:
```
=== Client Operation Menu ===
1. Create Room
2. Join Room
3. Exit
Please select (1-3): 1

Enter room name: MyRoom
Enter username: Alice

--- TCP Connection Phase ---
TCP connection successful
Creating room 'MyRoom'...
Token obtained successfully
TCP connection disconnected

--- UDP Connection Phase ---
Room: MyRoom
User: Alice
Status: Entered as room creator

[Registration complete] My address: 127.0.0.1:xxxxx

=== Chat started === (Press Ctrl+C or type exit/q to quit)
> 
```

### Step 3: Start Additional Clients (Join the Room)

Open **another new terminal** and start a second client:

```bash
cd client
python client.py
```

Select option 2 to join the existing room:
```
=== Client Operation Menu ===
1. Create Room
2. Join Room
3. Exit
Please select (1-3): 2

Enter room name: MyRoom
Enter username: Bob

--- TCP Connection Phase ---
TCP connection successful
Joining room 'MyRoom'...
Token obtained successfully
TCP connection disconnected

--- UDP Connection Phase ---
Room: MyRoom
User: Bob
Status: Joined room

[Registration complete] My address: 127.0.0.1:xxxxx

=== Chat started === (Press Ctrl+C or type exit/q to quit)
> 
```

### Step 4: Start Chatting!

Now you can send messages between clients:

**In Alice's terminal:**
```
> Hello Bob!
```

**In Bob's terminal:**
```
Alice: Hello Bob!
> Hi Alice! How are you?
```

**In Alice's terminal:**
```
Bob: Hi Alice! How are you?
> I'm doing great!
```

### Step 5: Exit the Chat

To exit, you can:
- Type `exit`, `quit`, or `q`
- Press `Ctrl+C`

**Important**: If the room creator (host) leaves, all other users will be automatically disconnected and notified:
```
[System notification] Chat ending because the host of room 'MyRoom' has left
```

## 📡 Protocol Overview

### TCP Room Protocol (TCRP)

Used for room management operations:

**Message Format:**
```
[1 byte: Room Name Length] [N bytes: Room Name] 
[1 byte: Operation] [1 byte: State] [Payload]
```

**Operations:**
- `1` - Create Room
- `2` - Join Room

**States:**
- `0` - Request
- `1` - Compliance (acknowledgment)
- `2` - Complete

### UDP Chat Room Protocol (UCRP)

Used for chat messages:

**Message Format:**
```
[4 bytes: Room Name Length] [N bytes: Room Name]
[4 bytes: Token Length] [N bytes: Token]
[4 bytes: Message Length] [N bytes: Message]
```

**Special Messages:**
- `__REGISTER__` - Register client address with server
- `__LEAVE__` - Notify server of client departure
- `__ROOM_CLOSED__` - Server notification that room host has left

## 📁 Project Structure

### Client Components

- **`client.py`**: Main entry point, handles user interaction and menu
- **`tcp_client.py`**: Manages TCP connection for room operations
- **`udp_client.py`**: Handles UDP communication for chat messages

### Server Components

- **`server.py`**: Main server entry point, initializes TCP and UDP servers
- **`tcp_server.py`**: Handles room creation and joining requests
- **`udp_server.py`**: Relays chat messages between clients
- **`room_manager.py`**: Manages rooms, tokens, and user data
- **`room_manager.json`**: Persistent storage for room data (auto-generated)

### Protocol Components

- **`tcrp.py`**: TCP Room Protocol implementation
- **`ucrp.py`**: UDP Chat Room Protocol implementation

## 🔧 Troubleshooting

### Connection Refused Error

**Problem**: `Cannot connect to server: [Errno 10061] No connection could be made`

**Solution**: Make sure the server is running before starting clients.

### Port Already in Use

**Problem**: `[Errno 10048] Only one usage of each socket address is allowed`

**Solution**: 
- Close any application using the port
- Or use different port numbers

### Messages Not Appearing

**Problem**: You can send messages but don't see replies

**Solution**: 
- Ensure all clients are in the same room (case-sensitive)
- Check that the server is relaying messages (check server logs)

### Room Already Exists

**Problem**: Cannot create a room with the same name

**Solution**: 
- Use a different room name
- Or join the existing room instead

## 📝 Notes

- Room names are **case-sensitive**
- Usernames can be duplicated (not recommended)
- Maximum message size: **4096 bytes**
- The server keeps room data in `room_manager.json` for persistence
- Only the **room creator (host)** can effectively close a room by leaving

## 🛡️ Security Considerations

- This is a **demonstration project** and should not be used in production without additional security measures
- Tokens are generated using Python's `secrets` module for cryptographic security
- No encryption is implemented for message transmission
- No authentication system beyond token-based room access

## 📄 License

This project is open source and available for educational purposes.

## 👤 Author

**Kevin Ryou Inoue**
- GitHub: [@KevinRyouInoue](https://github.com/KevinRyouInoue)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

**Enjoy chatting! 💬**

## Deep Dive: Technical Concepts

For an in-depth explanation of the Computer Science fundamentals behind this project (networking architecture, custom protocols, API contracts, threading model, data structures, security, and performance), see:

- docs/TECHNICAL_README.md

Highlights include:
- Why TCP for control-plane and UDP for data-plane
- TCRP/UCRP protocol formats and state machines
- How tokens, rooms, and addresses are managed
- Concurrency patterns on client and server
- Error handling, validation, and persistence strategy
