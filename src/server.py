import socket
import threading
import time

clients = [] # 연결된 모든 클라이언트 소켓을 저장하는 리스트
code_state = "" # 현재 공유 중인 코드 상태
draw_state = [] # 그림 데이터를 저장하는 리스트
highlight_state = {} # 하이라이트 데이터를 저장하는 딕셔너리
client_info = {} # 클라이언트 정보를 저장하는 딕셔너리

# 대용량 메시지를 클라이언트에게 안전하게 전송하는 함수
def send_large_message(client_socket, message):
    message_bytes = message.encode('utf-8') # 메시지를 UTF-8로 인코딩
    message_length = len(message_bytes) # 메시지 길이 계산
    header = message_length.to_bytes(4, 'big') # 메시지 길이를 4바이트 빅엔디안으로 변환
    try:
        client_socket.sendall(header + message_bytes) # 헤더와 메시지 전송
    except Exception as e:
        print(f"클라이언트로 메시지 전송 중 에러: {e}")

# 모든 클라이언트에게 메시지를 브로드캐스트하는 함수
def broadcast(message, sender_socket=None):
    disconnected_clients = []
    for client in clients:
        if client != sender_socket: # 발신자를 제외한 모든 클라이언트에게 전송
            try:
                send_large_message(client, message)
            except Exception as e:
                print(f"클라이언트로 전송 중 에러: {e}")
                disconnected_clients.append(client)
    
    # 연결이 끊긴 클라이언트 정리
    for client in disconnected_clients:
        cleanup_client(client)

# 클라이언트 연결 종료 시 정리 작업을 수행하는 함수
def cleanup_client(client_socket):
    if client_socket in clients:
        clients.remove(client_socket)  # 클라이언트 목록에서 제거
    if client_socket in client_info:
        nickname = client_info[client_socket]['nickname']  # 종료된 클라이언트의 닉네임 저장
        print(f"{nickname} disconnected from {client_info[client_socket]['address']}")  # 서버 콘솔에 연결 종료 메시지 출력
        # 다른 클라이언트들에게 접속 종료 메시지 전송
        broadcast(f"CHAT_MESSAGE:{nickname}님이 접속을 종료하였습니다.")
        del client_info[client_socket]  # 클라이언트 정보 딕셔너리에서 제거
    try:
        client_socket.close()  # 소켓 연결 종료
    except:
        pass  # 소켓 종료 중 오류 발생 시 무시

# 개별 클라이언트 연결을 처리하는 함수
def handle_client(client_socket, client_addr):
    global code_state
    
    # 소켓 타임아웃 설정
    client_socket.settimeout(60)
    
    try:
        # 클라이언트의 닉네임 수신
        nickname = client_socket.recv(1024).decode('utf-8')
        
        # 클라이언트 정보 저장
        client_info[client_socket] = {
            'socket': client_socket,
            'address': client_addr,
            'nickname': nickname,
            'last_active': time.time()
        }
        
        print(f"{nickname} connected from {client_addr}")
        broadcast(f"CHAT_MESSAGE:{nickname}님이 참여하였습니다.")

        # 현재 상태 전송 (코드, 그림, 하이라이트)
        if code_state:
            send_large_message(client_socket, f"CODE_UPDATE:{code_state}")
        for draw_cmd in draw_state:
            send_large_message(client_socket, f"DRAW_UPDATE:{draw_cmd}")
        for highlight_cmd in highlight_state:
            send_large_message(client_socket, f"HIGHLIGHT_UPDATE:{highlight_cmd}")

        while True:
            # 메시지 길이 수신
            length_bytes = client_socket.recv(4)
            if not length_bytes:
                break

            message_length = int.from_bytes(length_bytes, 'big')
            
            # 메시지 본문 수신
            data = b""
            while len(data) < message_length:
                chunk = client_socket.recv(min(message_length - len(data), 1024))
                if not chunk:
                    raise ConnectionError("데이터를 수신하는 중 연결이 끊김")
                data += chunk

            # 클라이언트 활성 시간 업데이트
            client_info[client_socket]['last_active'] = time.time()
            
            message = data.decode('utf-8')

            # 메시지 유형에 따른 처리
            if message.startswith("DRAW_UPDATE:"):
                draw_data = message[len("DRAW_UPDATE:"):]
                if draw_data == '"CLEAR"':
                    draw_state.clear() # 그림 초기화
                else:
                    draw_data_tuple = eval(draw_data)
                    draw_state.append(draw_data_tuple) # 그림 데이터 저장
                broadcast(message)
            elif message.startswith("CODE_UPDATE:"):
                code_state = message[len("CODE_UPDATE:"):] # 코드 상태 업데이트
                broadcast(message, sender_socket=client_socket)
            elif message.startswith("CHAT_MESSAGE:"):
                broadcast(message, sender_socket=client_socket) # 채팅 메시지 전파
            elif message.startswith("HIGHLIGHT_UPDATE:"):
                highlight_data = eval(message[len("HIGHLIGHT_UPDATE:"):])
                start, end = highlight_data
                highlight_state[start] = end # 하이라이트 정보 저장
                broadcast(message)
            elif message.startswith("HIGHLIGHT_ERASE:"):
                erase_data = eval(message[len("HIGHLIGHT_ERASE:"):])
                start, end = erase_data
                if start in highlight_state:
                    del highlight_state[start] # 하이라이트 정보 삭제
                broadcast(message)

    except Exception as e:
        print(f"에러 {client_addr}: {e}")
    finally:
        cleanup_client(client_socket)

def check_inactive_clients():
    while True:
        current_time = time.time()
        inactive_clients = []
        
        for client_socket in client_info:
            if current_time - client_info[client_socket]['last_active'] > 300:  # 5분 이상 비활성
                inactive_clients.append(client_socket)
        
        for client_socket in inactive_clients:
            cleanup_client(client_socket)
        
        time.sleep(60)  # 1분마다 체크

def shutdown_server():
    print("\n서버를 종료합니다...")
    for client in clients[:]:  # 리스트 복사본으로 순회
        cleanup_client(client)
    try:
        server.close()
    except:
        pass

# 서버 시작 및 클라이언트 연결 수락
def start_server():
    global server
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 8888))
        server.listen(5)
        print("Server started on port 8888")
        
        # 비활성 클라이언트 체크 스레드 시작
        threading.Thread(target=check_inactive_clients, daemon=True).start()
        
        while True:
            try:
                client_socket, client_addr = server.accept()
                if code_state:
                    send_large_message(client_socket, f"CODE_UPDATE:{code_state}")
                # 새 클라이언트 연결을 위한 스레드 시작
                threading.Thread(target=handle_client, args=(client_socket, client_addr)).start()
                clients.append(client_socket)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error accepting client connection: {e}")
    except Exception as e:
        print(f"서버 시작 중 에러: {e}")
    finally:
        shutdown_server()

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        shutdown_server()