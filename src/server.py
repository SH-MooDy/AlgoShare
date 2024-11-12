import socket
import threading

clients = []  # 연결된 모든 클라이언트를 저장

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:  # 메시지를 보낸 클라이언트에게는 다시 전송하지 않음
            client.send(message)

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            broadcast(message, client_socket)
        except:
            clients.remove(client_socket)
            client_socket.close()
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8888))
    server.listen()
    print("Server started on port 8888")

    while True:
        client_socket, addr = server.accept()
        print(f"Connected to {addr}")
        clients.append(client_socket)
        
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    start_server()
