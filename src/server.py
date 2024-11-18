import socket
import threading

clients = []  # 클라이언트 소켓을 저장할 리스트

def handle_client(client_socket, client_addr):
    try:
        # 클라이언트 닉네임을 수신
        nickname = client_socket.recv(1024).decode('utf-8')
        print(f"Nickname set: {nickname} ({client_addr})")

        while True:
            # 클라이언트로부터 데이터를 수신
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"Received from {nickname}: {data}")
                # 채팅 메시지 또는 코드 변경 내용을 처리
                broadcast(data, client_socket)  # 모든 클라이언트로 브로드캐스트
    except:
        print(f"Connection lost from {client_addr}")
    finally:
        clients.remove(client_socket)  # 클라이언트 연결 종료 시 리스트에서 제거
        client_socket.close()

def broadcast(message, sender_socket):
    # 모든 클라이언트에게 메시지를 전달
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                clients.remove(client)

def start_server():
    # 서버 소켓 생성
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8888))  # 모든 IP에서 8888 포트로 접속 가능
    server.listen(5)
    print("Server started on port 8888")

    while True:
        # 클라이언트 연결 대기
        client_socket, client_addr = server.accept()
        print(f"Accepted connection from {client_addr}")
        clients.append(client_socket)  # 클라이언트 소켓 리스트에 추가
        threading.Thread(target=handle_client, args=(client_socket, client_addr)).start()

if __name__ == "__main__":
    start_server()
