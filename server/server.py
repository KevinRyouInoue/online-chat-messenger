import threading
import time

from room_manager import RoomManager
from tcp_server import TCP_Create_Join_Server
from udp_server import UDP_Chat_Server

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
