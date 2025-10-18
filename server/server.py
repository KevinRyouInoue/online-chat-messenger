import threading
import time

from room_manager import RoomManager
from tcp_server import TCP_Create_Join_Server
from udp_server import UDP_Chat_Server

def main():
    room_manager = RoomManager()

    host = input("ホスト名 (デフォルト: localhost): ").strip() or "localhost"

    tcp_port_str = input("TCPポート番号 (デフォルト: 9090): ").strip()
    if tcp_port_str:
        try:
            tcp_port = int(tcp_port_str)
        except ValueError:
            print("ポート番号が不正です。数値で入力してください。")
            return
    else:
        tcp_port = 9090

    udp_port_str = input("UDPポート番号 (デフォルト: 9091): ").strip()
    if udp_port_str:
        try:
            udp_port = int(udp_port_str)
        except ValueError:
            print("ポート番号が不正です。数値で入力してください。")
            return
    else:
        udp_port = 9091

    tcp_server = TCP_Create_Join_Server(host, tcp_port, room_manager)
    udp_server = UDP_Chat_Server(host, udp_port, room_manager)

    tcp_server.bind()
    udp_server.bind()

    print(f"[起動] TCPサーバーを {host}:{tcp_port} にバインドしました")
    print(f"[起動] UDPサーバーを {host}:{udp_port} にバインドしました\n")
    print("UDPチャットサーバーが起動しました。メッセージを待っています...")

    tcp_thread = threading.Thread(target=tcp_server.start, daemon=False)
    udp_thread = threading.Thread(target=udp_server.start, daemon=False)

    tcp_thread.start()
    udp_thread.start()

    print("Ctrl+Cで停止...")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCtrl+Cが検出されたので停止します")
        tcp_server.stop()
        udp_server.stop()
        tcp_thread.join()
        udp_thread.join()
        print("サーバー停止完了")

if __name__ == "__main__":
    main()
