from socket import *
import sys
from urllib.parse import urlparse

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server]')
    sys.exit(2)

# 서버 소켓 생성 및 설정
tcpSerSock = socket(AF_INET, SOCK_STREAM)  # IPv4(AF_INET), TCP(SOCK_STREAM) 소켓 생성
tcpSerSock.bind(('0.0.0.0', 8888))  # 모든 네트워크 인터페이스에서 8888 포트 바인딩
tcpSerSock.listen(5)  # 최대 5개의 클라이언트 요청 대기

print(f"Proxy server is running on IP: {gethostbyname(gethostname())}, Port: 8888")

while True:
    # 클라이언트 연결 요청 수신
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)

    try:
        # 클라이언트로부터 HTTP 요청 메시지 수신
        message = tcpCliSock.recv(4096).decode()
        print("Client request message:\n", message)

        # 요청 메시지에서 파일 이름 및 호스트 추출
        first_line = message.split('\n')[0]  # HTTP 요청 첫 줄
        url = first_line.split(' ')[1]  # 요청 URL
        parsed_url = urlparse(url)  # URL 파싱
        hostn = parsed_url.netloc  # 호스트 이름 추출
        path = parsed_url.path if parsed_url.path else '/'  # 요청 경로 (없으면 '/'로 설정)

        print(f"Connecting to host: {hostn}, Path: {path}")
        filetouse = hostn + path  # 파일 경로 조합
        fileExist = "false"

        try:
            # 캐시에서 파일 열기 시도
            f = open(filetouse, "rb")
            outputdata = f.readlines()
            fileExist = "true"

            # 캐시된 파일의 데이터를 클라이언트로 전송
            tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
            tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
            for line in outputdata:
                tcpCliSock.send(line)
            print('Read from cache')

        except IOError:
            # 캐시에 파일이 없는 경우 처리
            if fileExist == "false":
                c = socket(AF_INET, SOCK_STREAM)  # 본 서버와 통신하기 위한 소켓 생성

                try:
                    # 본 서버에 연결
                    c.connect((hostn, 80))
                    print(f"Connected to {hostn} on port 80")

                    # 본 서버에 HTTP GET 요청 전송
                    request = f"GET {path} HTTP/1.0\r\nHost: {hostn}\r\n\r\n"
                    c.send(request.encode())
                    print(f"Sent request to server:\n{request}")

                    # 본 서버로부터 응답 데이터 수신
                    buffer = b""
                    while True:
                        data = c.recv(4096)
                        if not data:
                            break
                        buffer += data

                    # 응답 데이터를 캐시에 저장
                    with open(filetouse, "wb") as tmpFile:
                        tmpFile.write(buffer)

                    # 응답 데이터를 클라이언트로 전송
                    tcpCliSock.send(buffer)

                except Exception as e:
                    # 본 서버와의 연결 실패 시 처리
                    print("Error while connecting to the server:", e)
                    tcpCliSock.send("HTTP/1.0 404 Not Found\r\n".encode())
                    tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
                    tcpCliSock.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())

                finally:
                    c.close()

            else:
                # 캐시 파일이 없을 때 처리
                tcpCliSock.send("HTTP/1.0 404 Not Found\r\n".encode())
                tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
                tcpCliSock.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())

    except Exception as e:
        print("Error:", e)

    # 클라이언트 소켓 닫기
    tcpCliSock.close()
