import json
import struct

OP_CREATE_ROOM = 1
OP_JOIN_ROOM = 2

STATE_REQUEST = 0
STATE_COMPLIANCE = 1
STATE_COMPLETE = 2

class TCRProtocol:
    HEADER_SIZE = 32

    @staticmethod
    def encode_tcrp_header(room_name_size, operation, state, payload_size):
        payload_size_bytes = payload_size.to_bytes(28, byteorder='big')
        return struct.pack('!BBB', room_name_size, operation, state) + b'\x00' + payload_size_bytes

    @staticmethod
    def decode_tcrp_header(header):
        if len(header) != TCRProtocol.HEADER_SIZE:
            raise ValueError("ヘッダーサイズが不正です")
        room_name_size, op, state = struct.unpack('!BBB', header[:3])
        payload_size = int.from_bytes(header[4:], byteorder='big')
        return room_name_size, op, state, payload_size

    @staticmethod
    def send_tcrp_message(sock, room_name, operation, state, payload_obj):
        room_name_bytes = room_name.encode('utf-8')
        payload_bytes = json.dumps(payload_obj).encode('utf-8')
        header = TCRProtocol.encode_tcrp_header(len(room_name_bytes), operation, state, len(payload_bytes))
        sock.sendall(header + room_name_bytes + payload_bytes)

    @staticmethod
    def receive_tcrp_message(sock):
        header = TCRProtocol._recv_exactly(sock, TCRProtocol.HEADER_SIZE)
        if not header:
            raise ConnectionError("ヘッダー受信中に切断されました")
        room_name_size, op, state, payload_size = TCRProtocol.decode_tcrp_header(header)

        room_name_bytes = TCRProtocol._recv_exactly(sock, room_name_size)
        payload_bytes = TCRProtocol._recv_exactly(sock, payload_size)

        room_name = room_name_bytes.decode('utf-8')
        payload_str = payload_bytes.decode('utf-8')
        return op, state, room_name, payload_str

    @staticmethod
    def build_response_compliance(room_name, operation, success):
        payload = json.dumps({"success": success}).encode('utf-8')
        room_name_bytes = room_name.encode('utf-8')
        header = TCRProtocol.encode_tcrp_header(len(room_name_bytes), operation, STATE_COMPLIANCE, len(payload))
        return header + room_name_bytes + payload

    @staticmethod
    def build_response_complete(room_name, operation, token):
        payload = json.dumps({"token": token}).encode('utf-8')
        room_name_bytes = room_name.encode('utf-8')
        header = TCRProtocol.encode_tcrp_header(len(room_name_bytes), operation, STATE_COMPLETE, len(payload))
        return header + room_name_bytes + payload

    @staticmethod
    def _recv_exactly(sock, size):
        buf = b''
        while len(buf) < size:
            part = sock.recv(size - len(buf))
            if not part:
                raise ConnectionError("Connection lost (during reception)")
            buf += part
        return buf