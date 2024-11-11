import socket

def start_client():
    # 서버 소켓에 연결
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 8888))  # 서버 IP와 포트로 연결
    
    # 서버로 메시지 전송
    client.send("Hello, Server!".encode('utf-8'))
    
    # 서버로부터 응답 받기
    response = client.recv(1024)
    print(f"Received from server: {response.decode('utf-8')}")
    
    # 연결 종료
    client.close()

if __name__ == "__main__":
    start_client()
