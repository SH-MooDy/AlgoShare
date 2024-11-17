import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            # 서버에서 받은 메시지 출력
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except:
            print("Disconnected from server")
            client_socket.close()
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8888))  # 서버의 IP와 포트로 연결

    # 서버에 닉네임 전송
    nickname = input("Enter your nickname: ")
    client.send(nickname.encode('utf-8'))

    # 수신 스레드 시작
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    # 메시지 입력 및 전송
    while True:
        message = input()
        client.send(message.encode('utf-8'))

if __name__ == "__main__":
    start_client()
