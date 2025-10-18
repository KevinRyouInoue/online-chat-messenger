def parse_custom_payload(data: bytes) -> tuple[str, str, str, str]:
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    parts = data.split('|')
    if len(parts) != 4:
        raise ValueError("Invalid custom protocol format")
    return tuple(parts)

def build_udp_payload(room_name: str, token: str, message: str) -> bytes:
    room_bytes = room_name.encode('utf-8')
    token_bytes = token.encode('utf-8')
    message_bytes = message.encode('utf-8')
    return bytes([len(room_bytes), len(token_bytes)]) + room_bytes + token_bytes + message_bytes

def parse_udp_payload(data: bytes) -> tuple[str, str, str]:
    room_len = data[0]
    token_len = data[1]
    room_start = 2
    token_start = room_start + room_len
    msg_start = token_start + token_len
    
    room_name = data[room_start:token_start].decode('utf-8')
    token = data[token_start:msg_start].decode('utf-8')
    message = data[msg_start:].decode('utf-8')
    return room_name, token, message

def build_udp_message(sender: str, message: str) -> bytes:
    sender_bytes = sender.encode('utf-8')
    message_bytes = message.encode('utf-8')
    return bytes([len(sender_bytes)]) + sender_bytes + message_bytes

def parse_udp_message(data: bytes) -> tuple[str, str]:
    if not data:
        return "", ""
    username_len = data[0]
    sender = data[1:1 + username_len].decode("utf-8")
    message = data[1 + username_len:].decode("utf-8")
    return sender, message

def parse_packet_auto(data: bytes) -> dict:
    try:
        decoded = data.decode('utf-8')
        if '|' in decoded:
            parts = decoded.split('|')
            if len(parts) == 4:
                return {'format': 'string_custom', 'room_name': parts[0], 'token': parts[1], 'username': parts[2], 'operation': parts[3]}
            elif len(parts) == 3:
                return {'format': 'string_standard', 'room_name': parts[0], 'token': parts[1], 'message': parts[2]}
            elif len(parts) == 2:
                return {'format': 'string_message', 'sender': parts[0], 'message': parts[1]}
    except:
        pass
    
    try:
        room_name, token, message = parse_udp_payload(data)
        return {'format': 'binary_payload', 'room_name': room_name, 'token': token, 'message': message}
    except:
        try:
            sender, message = parse_udp_message(data)
            return {'format': 'binary_message', 'sender': sender, 'message': message}
        except:
            return {'format': 'error'}
