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
                print(f"[受信] UDPパケット: {address} サイズ={len(data)}")
                self.handle_packet(data, address)
            except Exception as e:
                if self.running:
                    print(f"[受信エラー] {e}")

    def handle_packet(self, data: bytes, address: tuple):
        try:
            room_name, token, message = parse_udp_payload(data)
            print(f"[受信処理] ルーム: {room_name}, トークン: {token[:8]}..., メッセージ: {message}")
            self.process_message(room_name, token, message, address)
        except Exception as e:
            print(f"[処理エラー] {e}")

    def process_message(self, room_name: str, token: str, message: str, address: tuple):
        rooms = self.room_manager.rooms
        tokens = self.room_manager.tokens

        if message == "__REGISTER__":
            if token in tokens:
                tokens[token]["address"] = address
                self.room_manager.save_to_json()
                print(f"[登録] トークン{token[:8]}...にアドレス{address}を登録しました\n")
            else:
                print(f"[登録拒否] 未知のトークン {token[:8]}...")
            return

        if message == "__LEAVE__":
            if token in tokens and room_name in rooms:
                is_host = (rooms[room_name].get("host_token") == token)
                if is_host:
                    username = tokens[token]['username'].strip('"')
                    print(f"[ホスト退出] {repr(username)} がルーム'{room_name}'から退出します")
                    self.notify_room_closed(room_name, excluded_tokens=[token])

            self.room_manager.delete_room_if_host_left(room_name, token)
            self.room_manager.save_to_json()
            print(f"[退出処理] {token[:8]}...")
            print()
            return

        is_valid, reason = self.room_manager.validate_token_and_address(token, room_name)
        if not is_valid:
            print(f"[バリデーション失敗] {reason}")
            return

        if room_name not in rooms or token not in tokens:
            print("[中継失敗] ルームまたはトークンが存在しません")
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
                print(f"[送信] {repr(username)} へ: {message}")
            except Exception as e:
                username = tokens[token]['username'].strip('"')
                print(f"[送信エラー] {repr(username)}: {e}")

    def notify_room_closed(self, room_name, excluded_tokens=None):
        if excluded_tokens is None:
            excluded_tokens = []

        rooms = self.room_manager.rooms
        tokens = self.room_manager.tokens

        if room_name not in rooms:
            print(f"[通知エラー] ルーム'{room_name}'が存在しません")
            return

        members = rooms[room_name]["members"]
        print(f"[ルーム終了通知] ルーム'{room_name}'の{len(members)}人のメンバーに通知を送信します")

        notification_count = 0
        for member_token in members:
            if member_token in excluded_tokens:
                continue

            if member_token not in tokens:
                print(f"[警告] トークン{member_token[:8]}... が見つかりません")
                continue

            addr = tokens[member_token].get("address")
            if not addr:
                username = tokens[member_token]['username'].strip('"')
                print(f"[警告] {repr(username)} のアドレスが未登録")
                continue

            if isinstance(addr, list):
                addr = tuple(addr)

            try:
                system_message = "__ROOM_CLOSED__"
                self.udp_sock.sendto(system_message.encode('utf-8'), addr)
                notification_count += 1
                username = tokens[member_token]['username'].strip('"')
                print(f"[通知] {repr(username)}({addr}) に終了通知を送信")
            except Exception as e:
                username = tokens[member_token]['username'].strip('"')
                print(f"[通知エラー] {repr(username)} ({addr}): {e}")

        print(f"[通知完了] {notification_count}人に送信しました\n")

    def stop(self):
        self.running = False
        if self.udp_sock:
            self.udp_sock.close()
            print("[停止] UDPサーバーを停止しました")
