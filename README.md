System Overview
This is a real-time chat messenger that uses a hybrid TCP/UDP architecture to separate control operations from data transmission.

Architecture Design
TCP Connection Phase (Control Plane)

Handles room creation and joining operations
Manages authentication and token generation
Provides reliable delivery for critical operations
Connection is established, operation completed, then closed
UDP Chat Phase (Data Plane)

Handles real-time message transmission
Provides low-latency, fast communication
Suitable for high-frequency chat messages
Continuous connection maintained during chat session
System Diagrams
Overall System Architecture
Code
┌─────────────────────────────────────────────────────────────┐
│                      Server System                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │   TCP Server     │         │   UDP Server     │        │
│  │   Port: 9090     │         │   Port: 9091     │        │
│  │                  │         │                  │        │
│  │ - Create Room    │         │ - Relay Messages │        │
│  │ - Join Room      │         │ - Register Addr  │        │
│  │ - Generate Token │         │ - Handle Leave   │        │
│  └────────┬─────────┘         └────────┬─────────┘        │
│           │                            │                   │
│           └──────────┬─────────────────┘                   │
│                      │                                     │
│           ┌──────────▼──────────┐                         │
│           │   Room Manager      │                         │
│           │                     │                         │
│           │ - Rooms             │                         │
│           │ - Tokens            │                         │
│           │ - User Addresses    │                         │
│           │ - Persistence       │                         │
│           └─────────────────────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
