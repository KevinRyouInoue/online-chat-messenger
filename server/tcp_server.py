import os
import socket
import sys
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from protocol.tcrp import TCRProtocol, OP_CREATE_ROOM, OP_JOIN_ROOM, STATE_REQUEST

class TCP_Create_Join_Server:
    def __init__(self, host, tcp_port, room_manager):
        self.host = host
        self.tcp_port = tcp_port
        self.socket = None
        self.running = False
        self.room_manager = room_manager
        
        print(f"TCPサーバー初期化: {host}:{tcp_port}")

    def bind(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.tcp_port))
        self.socket.listen()
        self.running = True

    def start(self):
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                print(f"[TCP] 接続: {address}")
                thread = threading.Thread(target=self._handle_client, args=(client_socket, address), daemon=True)
                thread.start()
            except OSError:
                break
            except Exception as e:
                print(f"接続処理エラー: {e}")

    def _handle_client(self, client_socket, address):
        try:
            op, state, room_name, payload = TCRProtocol.receive_tcrp_message(client_socket)

            if state != STATE_REQUEST:
                print(f"無効な状態コード: {state}")
                return

            if op == OP_CREATE_ROOM:
                success, token = self.room_manager.create_room(room_name, payload, address)
                payload = payload.strip('"')
                print(f"{'作成成功' if success else '既に存在'}: ルーム'{room_name}' (ユーザー: {repr(payload)}, Address: {address})")
                if success:
                    print(f"  → 発行されたトークン: {token}")
                    self.room_manager.save_to_json()
            elif op == OP_JOIN_ROOM:
                success, token = self.room_manager.join_room(room_name, payload, address)
                payload = payload.strip('"')
                print(f"{'参加成功' if success else '参加失敗'}: ルーム'{room_name}'に{repr(payload)}入室 (Address: {address})")
                if success:
                    print(f"  → 発行されたトークン: {token}")
                    self.room_manager.save_to_json()
            else:
                print(f"その操作コードは使えません（コード: {op}）")
                return

            compliance = TCRProtocol.build_response_compliance(room_name, op, int(success))
            complete = TCRProtocol.build_response_complete(room_name, op, token if success else "")
            client_socket.sendall(compliance + complete)

        except Exception as e:
            print(f"クライアント処理エラー: {e}")
        finally:
            client_socket.close()
            print(f"[TCP] 切断: {address}")

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
            print("[停止] TCPサーバーを停止しました")
