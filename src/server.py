import socket
import threading

clients = []  # 연결된 클라이언트 소켓 저장
code_state = ""  # 현재 코드 상태를 저장


# 클라이언트 메시지 처리
def handle_client(client_socket, client_addr):
    global code_state
    try:
        # 닉네임 수신
        nickname = client_socket.recv(1024).decode('utf-8')
        print(f"{nickname} connected from {client_addr}")
        broadcast(f"{nickname} 님이 채팅에 참여하였습니다.")

        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if data.startswith("CODE_UPDATE:"):  # 코드 업데이트
                code_state = data[len("CODE_UPDATE:"):]  # 코드 상태 저장
                broadcast(f"CODE_UPDATE:{code_state}", sender_socket=client_socket)
            else:  # 일반 채팅 메시지
                broadcast(data, sender_socket=client_socket)

    except Exception as e:
        print(f"Error with {client_addr}: {e}")
    finally:
        clients.remove(client_socket)
        client_socket.close()


# 모든 클라이언트에 메시지 전달
def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                clients.remove(client)


# 서버 시작
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8888))
    server.listen(5)
    print("Server started on port 8888")

    while True:
        client_socket, client_addr = server.accept()
        clients.append(client_socket)
        client_socket.send(f"CODE_UPDATE:{code_state}".encode('utf-8'))  # 현재 코드 상태 전송
        threading.Thread(target=handle_client, args=(client_socket, client_addr)).start()


if __name__ == "__main__":
    start_server()
