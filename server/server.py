import threading
import time

from room_manager import RoomManager
from tcp_server import TCP_Create_Join_Server
from udp_server import UDP_Chat_Server
import socket

def main():
    room_manager = RoomManager()

    host = input("Host name (default: localhost): ").strip() or "localhost"

    tcp_port_str = input("TCP port number (default: 9090): ").strip()
    if tcp_port_str:
        try:
            tcp_port = int(tcp_port_str)
        except ValueError:
            print("Invalid port number. Please enter a numeric value.")
            return
    else:
        tcp_port = 9090

    udp_port_str = input("UDP port number (default: 9091): ").strip()
    if udp_port_str:
        try:
            udp_port = int(udp_port_str)
        except ValueError:
            print("Invalid port number. Please enter a numeric value.")
            return
    else:
        udp_port = 9091

    # Validate/normalize host
    try:
        socket.getaddrinfo(host, None)
    except Exception:
        print(f"[Info] Host '{host}' could not be resolved. Using 127.0.0.1 instead.")
        host = "127.0.0.1"

    # Validate ports range (avoid extremely low/reserved ports or out-of-range)
    def normalize_port(p: int, default_p: int) -> int:
        if 1024 <= p <= 65535:
            return p
        print(f"[Info] Port {p} is out of recommended range (1024-65535). Using default {default_p}.")
        return default_p

    tcp_port = normalize_port(tcp_port, 9090)
    udp_port = normalize_port(udp_port, 9091)

    tcp_server = TCP_Create_Join_Server(host, tcp_port, room_manager)
    udp_server = UDP_Chat_Server(host, udp_port, room_manager)

    tcp_server.bind()
    udp_server.bind()

    print(f"[Started] TCP server bound to {host}:{tcp_port}")
    print(f"[Started] UDP server bound to {host}:{udp_port}\n")
    print("UDP chat server started. Waiting for messages...")

    tcp_thread = threading.Thread(target=tcp_server.start, daemon=False)
    udp_thread = threading.Thread(target=udp_server.start, daemon=False)

    tcp_thread.start()
    udp_thread.start()

    print("Press Ctrl+C to stop...")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCtrl+C detected, stopping")
        tcp_server.stop()
        udp_server.stop()
        tcp_thread.join()
        udp_thread.join()
        print("Server stopped successfully")

if __name__ == "__main__":
    main()
