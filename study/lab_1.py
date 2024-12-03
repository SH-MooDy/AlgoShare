#import socket module
from socket import *
import sys  # 프로그램 종료를 위해 필요

# 서버 소켓 생성
serverSocket = socket(AF_INET, SOCK_STREAM)

# 서버 소켓 준비
# 서버는 특정 IP 주소와 포트에 바인딩된 상태로 클라이언트의 연결을 기다림
serverPort = 6789  # 사용할 포트 번호
serverSocket.bind(('', serverPort))  # 모든 인터페이스에서 연결 허용
serverSocket.listen(1)  # 최대 대기 클라이언트 수 지정
print(f"Server started on port {serverPort}")

while True:
    # 클라이언트 연결 수락
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()  # 클라이언트와 연결 설정

    try:
        # 클라이언트로부터 메시지 수신
        message = connectionSocket.recv(1024).decode()  # 요청 메시지 읽기
        filename = message.split()[1]  
        f = open(filename[1:]) 

        # 파일 내용을 읽어와 전송 준비
        outputdata = f.read()

        # HTTP 응답 헤더 전송
        # 클라이언트에 성공 상태 코드와 콘텐츠 타입 전송
        connectionSocket.send("HTTP/1.1 200 OK\r\n".encode())
        connectionSocket.send("Content-Type: text/html\r\n\r\n".encode())

        # 요청한 파일의 내용을 전송
        for i in range(len(outputdata)):
            connectionSocket.send(outputdata[i].encode())

        # 연결 종료
        connectionSocket.close()

    except IOError:
        # 파일이 없는 경우 "404 Not Found" 응답 전송
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n".encode())
        connectionSocket.send("Content-Type: text/html\r\n\r\n".encode())
        connectionSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())

        # 연결 종료
        connectionSocket.close()

# 서버 종료
serverSocket.close()
sys.exit()  # 프로그램 종료
