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
        
        print(f"TCP server initialized: {host}:{tcp_port}")

    def bind(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind((self.host, self.tcp_port))
        except Exception as e:
            # Fallback for invalid/unknown hostnames
            fallback_host = '127.0.0.1' if self.host.lower() == 'localhost' or self.host.strip() == '' else '127.0.0.1'
            print(f"[Warn] Failed to bind to {self.host}:{self.tcp_port} ({e}). Falling back to {fallback_host}:{self.tcp_port}.")
            self.host = fallback_host
            self.socket.bind((self.host, self.tcp_port))
        self.socket.listen()
        self.running = True

    def start(self):
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                print(f"[TCP] Connected: {address}")
                thread = threading.Thread(target=self._handle_client, args=(client_socket, address), daemon=True)
                thread.start()
            except OSError:
                break
            except Exception as e:
                print(f"Connection processing error: {e}")

    def _handle_client(self, client_socket, address):
        try:
            op, state, room_name, payload = TCRProtocol.receive_tcrp_message(client_socket)

            if state != STATE_REQUEST:
                print(f"Invalid state code: {state}")
                return

            if op == OP_CREATE_ROOM:
                success, token = self.room_manager.create_room(room_name, payload, address)
                payload = payload.strip('"')
                print(f"{'Creation successful' if success else 'Already exists'}: Room '{room_name}' (User: {repr(payload)}, Address: {address})")
                if success:
                    print(f"  → Issued token: {token}")
                    self.room_manager.save_to_json()
            elif op == OP_JOIN_ROOM:
                success, token = self.room_manager.join_room(room_name, payload, address)
                payload = payload.strip('"')
                print(f"{'Join successful' if success else 'Join failed'}: {repr(payload)} entering room '{room_name}' (Address: {address})")
                if success:
                    print(f"  → Issued token: {token}")
                    self.room_manager.save_to_json()
            else:
                print(f"Cannot use that operation code (Code: {op})")
                return

            compliance = TCRProtocol.build_response_compliance(room_name, op, int(success))
            complete = TCRProtocol.build_response_complete(room_name, op, token if success else "")
            client_socket.sendall(compliance + complete)

        except Exception as e:
            print(f"Client processing error: {e}")
        finally:
            client_socket.close()
            print(f"[TCP] Disconnected: {address}")

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
            print("[Stopped] TCP server stopped")
