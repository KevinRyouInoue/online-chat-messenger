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
        
        print("RoomManager初期化: キャッシュをクリアしました")

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
            return False, "無効なトークンです"
        
        if room_name not in self.rooms:
            return False, "ルームが存在しません"
        
        if token not in self.rooms[room_name]["members"]:
            return False, "トークンがこのルームのメンバーではありません"
        
        if self.tokens[token]["room_name"] != room_name:
            return False, "トークンが別のルームに属しています"
        
        return True, "有効なトークンです"

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
            print(f"既存ユーザー: {repr(username)} (アドレス更新: {address}, トークン: {existing_token})")
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
            
            print(f"データを{filename}に保存しました")
            return True

        except Exception as e:
            print(f"保存エラー: {e}")
            return False

    def load_from_json(self, filename="room_manager.json"):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.rooms = data.get('rooms', {})
            self.tokens = data.get('tokens', {})

            print(f"データを{filename}から手動で読み込みました")
            if 'saved_at' in data:
                print(f"保存日時: {data['saved_at']}")
            
            print(f"読み込み結果: {len(self.rooms)}個のルーム, {len(self.tokens)}個のトークン")
            return True

        except FileNotFoundError:
            print(f"ファイル{filename}が見つかりません")
            return False
        except Exception as e:
            print(f"読み込みエラー: {e}")
            return False
        
    def delete_room_if_host_left(self, room_name, token):
        tokens = self.tokens
        rooms = self.rooms
        token_info = tokens.get(token)

        if not token_info:
            print(f"未知のトークン: {token}")
            return None
        room_name = token_info["room_name"]

        if rooms.get(room_name, {}).get("host_token") == token:
            username = token_info['username'].strip('"')
            print(f"ホスト{repr(username)}のため、ルーム'{room_name}'を削除します")
            for member_token in rooms[room_name]["members"]:
                if member_token in tokens:
                    del tokens[member_token]
            del rooms[room_name]
            print(f"ルーム'{room_name}'全トークンを削除しました")
            return None
        else:
            username = token_info['username'].strip('"')
            print(f"{repr(username)} がルーム'{room_name}'から退出します")
            if token in rooms[room_name]["members"]:
                rooms[room_name]["members"].remove(token)
            if token in tokens:
                del tokens[token]
            print(f"{repr(username)}のトークンとメンバー情報を削除しました")
            return None