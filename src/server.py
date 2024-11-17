import socket
import threading

clients = []  # 연결된 모든 클라이언트 소켓을 저장
nicknames = {}  # 클라이언트 소켓과 닉네임 매핑

def broadcast(message):
    for client in clients:
        client.send(message)

def handle_client(client_socket):
    try:
        # 클라이언트로부터 닉네임 수신
        nickname = client_socket.recv(1024).decode('utf-8')
        nicknames[client_socket] = nickname
        clients.append(client_socket)
        
        # 다른 클라이언트에게 알림
        broadcast(f"{nickname} has joined the chat!".encode('utf-8'))
        print(f"{nickname} connected.")

        # 메시지 처리
        while True:
            message = client_socket.recv(1024)
            broadcast(f"{nickname}: {message.decode('utf-8')}".encode('utf-8'))

    except:
        # 클라이언트 연결 종료 시
        print(f"{nicknames[client_socket]} disconnected.")
        clients.remove(client_socket)
        broadcast(f"{nicknames[client_socket]} has left the chat.".encode('utf-8'))
        del nicknames[client_socket]
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8888))
    server.listen()
    print("Server started on port 8888")

    while True:
        client_socket, addr = server.accept()
        print(f"Connected to {addr}")
        
        # 클라이언트 처리 스레드 생성
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    start_server()
