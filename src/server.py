import socket
import threading

def handle_client(client_socket):
    # 클라이언트로부터 데이터 수신
    request = client_socket.recv(1024)
    print(f"Received: {request.decode('utf-8')}")
    
    # 클라이언트에 응답 전송
    client_socket.send("Message received".encode('utf-8'))
    
    # 연결 종료
    client_socket.close()

def start_server():
    # 서버 소켓 생성
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 서버 주소 및 포트 설정
    server.bind(('0.0.0.0', 8888))  # 모든 네트워크 인터페이스에서 8888번 포트
    server.listen(5)  # 최대 5개의 클라이언트 대기
    
    print("Server started on port 8888")
    
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        
        # 클라이언트 처리 스레드 생성
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
