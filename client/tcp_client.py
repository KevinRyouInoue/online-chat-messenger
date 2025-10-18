import json
import os
import socket
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from protocol.tcrp import TCRProtocol, OP_CREATE_ROOM, OP_JOIN_ROOM, STATE_REQUEST, STATE_COMPLIANCE, STATE_COMPLETE

class TCP_Create_Join_Client:
    def __init__(self, host='localhost', port=9090):
        self.host = host
        self.port = port
        self.client_socket = None
        self.token = None

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"TCP connection successful")
            return True
        except Exception as e:
            print(f"Cannot connect to server: {e}")
            return False

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None

    def create_room(self, room_name, username):
        return self._handle_create_or_join('1', room_name, username)

    def join_room(self, room_name, username):
        return self._handle_create_or_join('2', room_name, username)

    def _handle_create_or_join(self, choice, room_name, username):
        op = OP_CREATE_ROOM if choice == '1' else OP_JOIN_ROOM

        try:
            TCRProtocol.send_tcrp_message(
                self.client_socket, room_name, op, STATE_REQUEST, username
            )

            op_c, state_c, room_c, payload_c = TCRProtocol.receive_tcrp_message(self.client_socket)
            if state_c != STATE_COMPLIANCE:
                print("Error receiving compliance response")
                return False

            compliance_result = json.loads(payload_c)
            if not compliance_result.get("success", False):
                print("Operation failed (server response)")
                return False

            op_f, state_f, room_f, payload_f = TCRProtocol.receive_tcrp_message(self.client_socket)
            if state_f == STATE_COMPLETE:
                complete_result = json.loads(payload_f)
                self.token = complete_result.get("token")
                return True
            else:
                print("Could not receive completion response")
                return False

        except Exception as e:
            print(f"Processing error: {e}")
            return False

    def get_token(self):
        return self.token
