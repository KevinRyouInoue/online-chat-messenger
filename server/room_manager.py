from datetime import datetime
import json
import secrets
import time

class RoomManager:
    def __init__(self):
        # チャットルーム情報
        # {room_name: {"host_token": token, "members": [tokens], "created_at": timestamp}}
        self.rooms = {}
        # トークン情報
        # {token: {"username": name, "room_name": room, "is_host": bool, "address": (ip, port)}}
        self.tokens = {}
        
        print("RoomManager initialized: Cache cleared")

    def generate_token(self):
        return "token_" + secrets.token_hex(16)

    def room_exists(self, room_name):
        return room_name in self.rooms
    
    def find_user_token_in_room(self, room_name, username):
        if room_name not in self.rooms:
            return None
        
        for token in self.rooms[room_name]["members"]:
            if token in self.tokens and self.tokens[token]["username"] == username:
                return token
        return None

    def validate_token_and_address(self, token, room_name):
        if token not in self.tokens:
            return False, "Invalid token"
        
        if room_name not in self.rooms:
            return False, "Room does not exist"
        
        if token not in self.rooms[room_name]["members"]:
            return False, "Token is not a member of this room"
        
        if self.tokens[token]["room_name"] != room_name:
            return False, "Token belongs to a different room"
        
        return True, "Valid token"

    def create_room(self, room_name, username, address):
        if self.room_exists(room_name):
            return False, None

        token = self.generate_token()
        
        self.rooms[room_name] = {
            "host_token": token,
            "members": [token],
            "created_at": time.time()
        }
        
        self.tokens[token] = {
            "username": username,
            "room_name": room_name,
            "is_host": True,
            "address": address
        }

        return True, token

    def join_room(self, room_name, username, address):
        if not self.room_exists(room_name):
            return False, None

        existing_token = self.find_user_token_in_room(room_name, username)
        if existing_token:
            self.tokens[existing_token]["address"] = address
            username = username.strip('"')
            print(f"Existing user: {repr(username)} (Address updated: {address}, Token: {existing_token})")
            return True, existing_token

        token = self.generate_token()
        
        self.rooms[room_name]["members"].append(token)
        
        self.tokens[token] = {
            "username": username,
            "room_name": room_name,
            "is_host": False,
            "address": address
        }

        return True, token

    def save_to_json(self, filename="room_manager.json"):
        try:
            data = {
                'rooms': self.rooms,
                'tokens': self.tokens,
                'saved_at': datetime.now().isoformat()
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Data saved to {filename}")
            return True

        except Exception as e:
            print(f"Save error: {e}")
            return False

    def load_from_json(self, filename="room_manager.json"):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.rooms = data.get('rooms', {})
            self.tokens = data.get('tokens', {})

            print(f"Data manually loaded from {filename}")
            if 'saved_at' in data:
                print(f"Saved at: {data['saved_at']}")
            
            print(f"Load result: {len(self.rooms)} rooms, {len(self.tokens)} tokens")
            return True

        except FileNotFoundError:
            print(f"File {filename} not found")
            return False
        except Exception as e:
            print(f"Load error: {e}")
            return False
        
    def delete_room_if_host_left(self, room_name, token):
        tokens = self.tokens
        rooms = self.rooms
        token_info = tokens.get(token)

        if not token_info:
            print(f"Unknown token: {token}")
            return None
        room_name = token_info["room_name"]

        if rooms.get(room_name, {}).get("host_token") == token:
            username = token_info['username'].strip('"')
            print(f"Deleting room '{room_name}' because host {repr(username)} is leaving")
            for member_token in rooms[room_name]["members"]:
                if member_token in tokens:
                    del tokens[member_token]
            del rooms[room_name]
            print(f"All tokens for room '{room_name}' have been deleted")
            return None
        else:
            username = token_info['username'].strip('"')
            print(f"{repr(username)} is leaving room '{room_name}'")
            if token in rooms[room_name]["members"]:
                rooms[room_name]["members"].remove(token)
            if token in tokens:
                del tokens[token]
            print(f"Deleted token and member information for {repr(username)}")
            return None