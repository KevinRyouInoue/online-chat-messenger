import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tcp_client import TCP_Create_Join_Client
from udp_client import UDP_Chat_Client

def prompt_valid_input(prompt_text):
    while True:
        value = input(prompt_text).strip()
        if not value or value.isspace():
            print("Empty strings or spaces only are not allowed. Please enter again.")
            continue
        return value

class Client:
    def __init__(self, server_ip, tcp_port, udp_port):
        self.server_ip = server_ip
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.tcp_client = TCP_Create_Join_Client(server_ip, tcp_port)

    def run(self):
        try:
            while True:
                print("\n=== Client Operation Menu ===")
                print("1. Create Room")
                print("2. Join Room")
                print("3. Exit")

                choice = input("Please select (1-3): ").strip().translate(str.maketrans("１２３", "123"))

                if choice == '3':
                    print("Exiting.")
                    break
                elif choice in ['1', '2']:
                    if self._handle_room_operation(choice):
                        break
                else:
                    print("Please choose '1', '2', or '3'")
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            print("Client terminated")

    def _handle_room_operation(self, choice):
        room_name = prompt_valid_input("Enter room name: ")
        username = prompt_valid_input("Enter username: ")

        print(f"\n--- TCP Connection Phase ---")
        if not self.tcp_client.connect():
            print("[Error] TCP connection failed")
            return False

        success = False
        if choice == '1':
            print(f"Creating room '{room_name}'...")
            success = self.tcp_client.create_room(room_name, username)
        elif choice == '2':
            print(f"Joining room '{room_name}'...")
            success = self.tcp_client.join_room(room_name, username)

        if not success:
            print("[Error] Failed to obtain token")
            self.tcp_client.disconnect()
            return False

        token = self.tcp_client.get_token()
        print("Token obtained successfully")
        self.tcp_client.disconnect()
        print("TCP connection disconnected")

        print(f"\n--- UDP Connection Phase ---")
        print(f"Room: {room_name}")
        print(f"User: {username}")
        print(f"Status: {'Entered as room creator' if choice == '1' else 'Joined room'}")

        udp_client = UDP_Chat_Client(
            username=username,
            server_ip=self.server_ip,
            server_port=self.udp_port,
            room_name=room_name,
            token=token
        )
        udp_client.start()

        return True

def main():
    try:
        server_ip = input("Server address (default: 127.0.0.1): ").strip() or "127.0.0.1"

        tcp_port_input = input("TCP port number (default: 9090): ").strip()
        tcp_port = int(tcp_port_input) if tcp_port_input else 9090

        udp_port_input = input("UDP port number (default: 9091): ").strip()
        udp_port = int(udp_port_input) if udp_port_input else 9091

        client = Client(server_ip, tcp_port, udp_port)
        client.run()

    except ValueError:
        print("[Error] Please enter port numbers as numeric values")
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"[Error] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()