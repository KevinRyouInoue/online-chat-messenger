import os
import socket
import sys
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from protocol.ucrp import build_udp_payload, parse_udp_message

MAX_MESSAGE_SIZE = 4096

class UDP_Chat_Client:
    def __init__(self, username, server_ip, server_port, room_name, token):
        self.username = username
        self.server_ip = server_ip
        self.server_port = server_port
        self.room_name = room_name
        self.token = token
        self.running = True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 0))

    def register(self):
        payload = build_udp_payload(self.room_name, self.token, "__REGISTER__")
        self.sock.sendto(payload, (self.server_ip, self.server_port))
        ip, port = self.sock.getsockname()
        print()
        print(f"[Registration complete] My address: {ip}:{port}")
        print()

    def receive_messages(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(MAX_MESSAGE_SIZE)
                if not data:
                    continue

                try:
                    text = data.decode("utf-8")
                    if text == "__ROOM_CLOSED__":
                        print(f"\n[System notification] Chat ending because the host of room '{self.room_name}' has left")
                        self.running = False
                        self.sock.close()
                        os._exit(0)
                except UnicodeDecodeError:
                    pass

                sender, message = parse_udp_message(data)
                if sender != self.username:
                    print(f"{sender}: {message}")
                    print("> ", end="", flush=True)
                    
            except OSError as e:
                if not self.running:
                    break
                print(f"[Receive error] {e}")
                break

    def send_loop(self):
        try:
            while self.running:
                print("> ", end="", flush=True)
                msg = sys.stdin.readline().strip()
                if not msg:
                    continue
                if msg.lower() in ["exit", "quit", "q"]:
                    print("Ending chat")
                    break
                payload = build_udp_payload(self.room_name, self.token, msg)
                if len(payload) > MAX_MESSAGE_SIZE:
                    print("Error: Message exceeds 4096 bytes")
                    continue
                self.sock.sendto(payload, (self.server_ip, self.server_port))
        except KeyboardInterrupt:
            print("\nEnding chat")
        finally:
            self.stop()

    def start(self):
        self.register()
        threading.Thread(target=self.receive_messages, daemon=True).start()
        print("=== Chat started === (Press Ctrl+C or type exit/q to quit)")
        self.send_loop()

    def stop(self):
        if not self.running:
            return
        try:
            payload = build_udp_payload(self.room_name, self.token, "__LEAVE__")
            self.sock.sendto(payload, (self.server_ip, self.server_port))
            print("[Leave notification] Sent leave message to server")
        except Exception as e:
            print(f"[Leave notification error] {e}")
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
