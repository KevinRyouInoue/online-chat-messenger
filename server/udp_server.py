import os
import socket
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from protocol.ucrp import build_udp_message, parse_udp_payload

MAX_MESSAGE_SIZE = 4096

class UDP_Chat_Server:
    def __init__(self, host: str, udp_port: int, room_manager):
        self.host = host
        self.udp_port = udp_port
        self.room_manager = room_manager
        self.udp_sock = None
        self.running = False

    def bind(self):
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind((self.host, self.udp_port))
        self.running = True

    def start(self):
        while self.running:
            try:
                data, address = self.udp_sock.recvfrom(MAX_MESSAGE_SIZE)
                if not data:
                    continue
                print(f"[Received] UDP packet: {address} size={len(data)}")
                self.handle_packet(data, address)
            except Exception as e:
                if self.running:
                    print(f"[Receive error] {e}")

    def handle_packet(self, data: bytes, address: tuple):
        try:
            room_name, token, message = parse_udp_payload(data)
            print(f"[Processing received] Room: {room_name}, Token: {token[:8]}..., Message: {message}")
            self.process_message(room_name, token, message, address)
        except Exception as e:
            print(f"[Processing error] {e}")

    def process_message(self, room_name: str, token: str, message: str, address: tuple):
        rooms = self.room_manager.rooms
        tokens = self.room_manager.tokens

        if message == "__REGISTER__":
            if token in tokens:
                tokens[token]["address"] = address
                self.room_manager.save_to_json()
                print(f"[Registered] Address {address} registered to token {token[:8]}...\n")
            else:
                print(f"[Registration rejected] Unknown token {token[:8]}...")
            return

        if message == "__LEAVE__":
            if token in tokens and room_name in rooms:
                is_host = (rooms[room_name].get("host_token") == token)
                if is_host:
                    username = tokens[token]['username'].strip('"')
                    print(f"[Host leaving] {repr(username)} is leaving room '{room_name}'")
                    self.notify_room_closed(room_name, excluded_tokens=[token])

            self.room_manager.delete_room_if_host_left(room_name, token)
            self.room_manager.save_to_json()
            print(f"[Leave processing] {token[:8]}...")
            print()
            return

        is_valid, reason = self.room_manager.validate_token_and_address(token, room_name)
        if not is_valid:
            print(f"[Validation failed] {reason}")
            return

        if room_name not in rooms or token not in tokens:
            print("[Relay failed] Room or token does not exist")
            return

        sender = tokens[token]["username"]
        members = rooms[room_name]["members"]

        for member_token in members:
            if member_token == token:
                continue

            addr = tokens[member_token].get("address")
            if not addr:
                continue

            if isinstance(addr, list):
                addr = tuple(addr)

            try:
                payload = build_udp_message(sender, message)
                self.udp_sock.sendto(payload, addr)
                username = tokens[token]['username'].strip('"')
                print(f"[Sent] To {repr(username)}: {message}")
            except Exception as e:
                username = tokens[token]['username'].strip('"')
                print(f"[Send error] {repr(username)}: {e}")

    def notify_room_closed(self, room_name, excluded_tokens=None):
        if excluded_tokens is None:
            excluded_tokens = []

        rooms = self.room_manager.rooms
        tokens = self.room_manager.tokens

        if room_name not in rooms:
            print(f"[Notification error] Room '{room_name}' does not exist")
            return

        members = rooms[room_name]["members"]
        print(f"[Room closed notification] Sending notification to {len(members)} members of room '{room_name}'")

        notification_count = 0
        for member_token in members:
            if member_token in excluded_tokens:
                continue

            if member_token not in tokens:
                print(f"[Warning] Token {member_token[:8]}... not found")
                continue

            addr = tokens[member_token].get("address")
            if not addr:
                username = tokens[member_token]['username'].strip('"')
                print(f"[Warning] Address not registered for {repr(username)}")
                continue

            if isinstance(addr, list):
                addr = tuple(addr)

            try:
                system_message = "__ROOM_CLOSED__"
                self.udp_sock.sendto(system_message.encode('utf-8'), addr)
                notification_count += 1
                username = tokens[member_token]['username'].strip('"')
                print(f"[Notification] Sent closing notification to {repr(username)}({addr})")
            except Exception as e:
                username = tokens[member_token]['username'].strip('"')
                print(f"[Notification error] {repr(username)} ({addr}): {e}")

        print(f"[Notification complete] Sent to {notification_count} members\n")

    def stop(self):
        self.running = False
        if self.udp_sock:
            self.udp_sock.close()
            print("[Stopped] UDP server stopped")
