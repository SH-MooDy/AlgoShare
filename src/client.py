import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)  # 수신된 메시지 출력
        except:
            print("Disconnected from server")
            client_socket.close()
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8888))  # 서버의 IP와 포트로 연결

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    while True:
        message = input("Enter message: ")
        client.send(message.encode('utf-8'))

if __name__ == "__main__":
    start_client()
