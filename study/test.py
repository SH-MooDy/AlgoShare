from socket import *
import sys

# 명령줄 인자가 올바르게 제공되지 않았을 경우 에러 메시지 출력 및 종료
if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[sever_ip : It is the IP Address Of Proxy Server]')
    sys.exit(2)
    
# 서버 소켓 생성, 포트에 바인딩 및 클라이언트 연결 대기
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((sys.argv[1], 8888)) # 프록시 서버가 8888포트를 통해 요청 대기
tcpSerSock.listen(5) # 최대 5개의 클라이언트 연결을 대기

while 1:
    # 클라이언트로부터 데이터 수신 준비
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    
    # 클라이언트로부터 메시지 수신
    message = tcpCliSock.recv(4096).decode() # 데이터 수신 및 디코딩
    print(message)  
    
<<<<<<< HEAD
    # CONNECT 요청 처리
    if message.startswith('CONNECT'):
        # CONNECT 요청을 처리
        host = message.split()[1]
        print("CONNECT request for: ", host)

        # 200 OK 응답 보내기
        tcpCliSock.send("HTTP/1.1 200 Connection Established\r\n".encode())
        tcpCliSock.send("\r\n".encode())  # 빈 줄을 보내 연결이 확립되었음을 알림
        
        # 이후 클라이언트와 서버 간 데이터를 중계해야 함 (소켓을 사용하여 데이터 전달)
        try:
            # 원격 서버와의 연결
            c = socket(AF_INET, SOCK_STREAM)
            c.connect((host, 443))  # HTTPS 포트 443으로 연결

            # 클라이언트와 서버 간 데이터를 중계
            while True:
                data_from_client = tcpCliSock.recv(4096)
                if not data_from_client:
                    break
                c.send(data_from_client)
                
                data_from_server = c.recv(4096)
                if not data_from_server:
                    break
                tcpCliSock.send(data_from_server)

        except Exception as e:
            print("Error during CONNECT request: ", e)
            tcpCliSock.send("HTTP/1.1 500 Internal Server Error\r\n".encode())
            tcpCliSock.send("\r\n".encode())

    else:
        # GET 요청 처리
        # 요청 메시지에서 파일 이름 추출
        print(message.split()[1]) # 요청 메시지에서 URI 출력
        filename = message.split()[1].partition("/")[2] # URI에서 파일 이름 추출
        print(filename)
        fileExist = "false" # 파일 존재 여부
        filetouse = "/" + filename # 요청된 파일 경로 설정
        print(filetouse)

        try:
            # 파일이 캐시에 존재하는지 확인
            f = open(filetouse[1:], "r") # 캐시에서 파일 열기
            outputdata = f.readlines()
            fileExist = "true"
            
            # 캐시 히트를 찾고 응답 메시지를 생성 
            tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode()) # HTTP 200 응답
            tcpCliSock.send("Content-Type:text/html\r\n".encode()) # 응답 헤더 전송
            
            for line in outputdata: # 캐시된 파일 내용 전송
                tcpCliSock.send(line.encode())
                
            print('Read from cache')

        # 캐시에서 파일이 발견되지 않았을 경우 예외처리
        except IOError:
            if fileExist == "false":
                # 프록시 서버에 소켓 생성
                c = socket(AF_INET, SOCK_STREAM) # 원격 서버와 통신할 소켓 생성
                
                hostn = filename.replace("www.", "", 1) # www. 을 제거하여 호스트 이름 생성
                print(hostn)
                try:
                    # 포트 80을 통해 소켓과 연결
                    c.connect((hostn, 80))
                    # 이 소켓에 임시 파일을 만들고 포트 80에 클라이언트가 요청한 파일을 요청
                    fileobj = c.makefile('r', 0) # 원격 서버와의 파일 스트림 생성
                    fileobj.write("GET " + "http://" + filename + " HTTP/1.0\n\n") # HTTP GET 요청 전송
                    
                    # 버퍼에 있는 응답 읽기
                    buffer = c.recv(4096) # 원격 서버 응답 수신
                    
                    # 요청한 파일의 캐시에 새 파일을 만들고 버퍼의 응답을 클라이언트 소켓과 캐시의 해당 파일로 보냄
                    tmpFile = open("./" + filename, "wb") # 요청 파일을 캐시에 저장
                    tmpFile.write(buffer) # 응답 내용을 캐시에 기록
                    tcpCliSock.send(buffer) # 클라이언트로 응답 전송
                except:
                    print("Illegal request")
            else:
                # 파일을 찾지 못했을 경우 HTTP 응답 메시지
                tcpCliSock.send("HTTP/1.0 404 Not Found\r\n".encode()) # HTTP 404 메시지 전송
                tcpCliSock.send("Content-Type: text/html\r\n\r\n".encode())
                tcpCliSock.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())

=======
    # 요청 메시지에서 파일 이름 추출
    print(message.split()[1]) # 요청 메시지에서 URI 출력
    filename = message .split()[1].partition("/")[2] # URI에서 파일 이름 추출
    print(filename)
    fileExist = "false" # 파일 존재 여부
    filetouse = "/" + filename # 요청된 파일 경로 설정
    print(filetouse)
    try:
        # 파일이 캐시에 존재하는지 확인
        f = open(filetouse[1:], "r") # 캐시에서 파일 열기
        outputdata = f.readlines()
        fileExist = "true"
        
        # 캐시 히트를 찾고 응답 메시지를 생성 
        tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode()) # HTTP 200 응답
        tcpCliSock.send("Content-Type:text/html\r\n".encode()) # 응답 헤더 전송
        
        for line in outputdata: # 캐시된 파일 내용 전송
            tcpCliSock.send(line.encode())
            
        print('Read from cache')
    
    # 캐시에서 파일이 발견되지 않았을 경우 예외처리
    except IOError:
        if fileExist == "false":
            # 프록시 서버에 소켓 생성
            c = socket(AF_INET, SOCK_STREAM) # 원격 서버와 통신할 소켓 생성
            
            hostn = filename.replace("www.", "", 1) # www. 을 제거하여 호스트 이름 생성
            print(hostn)
            try:
                # 포트 80을 통해 소켓과 연결
                c.connect((hostn, 80))
                # 이 소켓에 임시 파일을 만들고 포트 80에 클라이언트가 요청한 파일을 요청
                fileobj = c.makefile('r',0) # 원격 서버와의 파일 스트림 생성
                c.send(("GET " + "http://" + filename + " HTTP/1.0\r\n\r\n").encode())

                
                # 버퍼에 있는 응답 읽기
                buffer = c.recv(4096) # 원격 서버 응답 수신
                
                # 요청한 파일의 캐시에 새 파일을 만들고 버퍼의 응답을 클라이언트 소켓과 캐시의 해당 파일로 보냄
                tmpFile = open("./" + filename, "wb") # 요청 파일을 캐시에 저장
                tmpFile.write(buffer) # 응답 내용을 캐시에 기록
                tcpCliSock.send(buffer) # 클라이언트로 응답 전송
            except:
                print("Illegal request")
        else:
            # 파일을 찾지 못했을 경우 HTTP 응답 메시지
            tcpCliSock.send("HTTP/1.0 404 Not Found\r\n".encode()) # HTTP 404 메시지 전송
            tcpCliSock.send("Content-Type: text/html\r\n\r\n".encode())
            tcpCliSock.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())
            
>>>>>>> 6dcbfc5b956b308df8d2a74f3f2825ed97c31bb3
    # 클라이언트와 서버 소켓을 닫기
    tcpCliSock.close()
    
tcpSerSock.close() # 서버 소켓 닫기
<<<<<<< HEAD
=======
        
        
>>>>>>> 6dcbfc5b956b308df8d2a74f3f2825ed97c31bb3
