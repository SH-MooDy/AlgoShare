
# 프로젝트 네트워크 통신 설명

## 네트워크 관점에서의 클라이언트-서버 통신

이 프로젝트는 **TCP(Transmission Control Protocol)**를 기반으로 클라이언트와 서버가 통신하며, 아래의 순서로 데이터가 송수신됩니다.

---

## 1. **TCP 소켓 초기화 및 연결 설정**

### 클라이언트 측

```python
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8888))
```

- **소켓 생성**: `socket.AF_INET`은 IPv4를, `socket.SOCK_STREAM`은 TCP를 사용하도록 지정합니다. 이 소켓은 클라이언트가 데이터를 송수신할 수 있는 네트워크 통로입니다.
- **연결 요청**: `connect()`를 통해 서버의 IP 주소(`localhost`)와 포트 번호(`8888`)로 연결을 요청합니다.

### 서버 측

```python
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8888))
server.listen(5)
```

- **소켓 생성**: 서버에서도 TCP 소켓을 생성합니다.
- **포트 바인딩**: 서버는 지정된 IP와 포트에서 클라이언트의 연결 요청을 수락할 준비를 합니다.
- **연결 대기**: `listen()`은 서버가 최대 5개의 클라이언트 연결을 기다릴 수 있도록 설정합니다.

```python
client_socket, client_addr = server.accept()
```

- **연결 수락**: 클라이언트가 요청한 연결을 `accept()`로 수락하며, 클라이언트와 연결된 새 소켓(`client_socket`)과 해당 클라이언트의 IP 주소/포트(`client_addr`) 정보를 반환합니다.

---

## 2. **닉네임 전송**

1. 클라이언트는 사용자로부터 닉네임을 입력받아 서버로 전송합니다:

   ```python
   client_socket.sendall(nickname.encode('utf-8'))
   ```

   - 닉네임을 UTF-8로 인코딩하여 바이트 데이터로 변환한 후, `sendall()`을 통해 서버로 보냅니다.

2. 서버는 이를 수신합니다:

   ```python
   nickname = client_socket.recv(1024).decode('utf-8')
   ```

   - 서버는 `recv()`를 통해 최대 1024바이트의 데이터를 읽습니다. 이를 UTF-8로 디코딩하여 닉네임을 문자열로 변환합니다.

---

## 3. **채팅 메시지 전송**

### 클라이언트 측

```python
message = f"CHAT_MESSAGE:{chat_input.get()}"
send_large_message(message)
```

1. 채팅 입력창에서 사용자가 메시지를 입력하면 `CHAT_MESSAGE:`라는 접두사를 붙여 서버로 전송합니다.
2. 메시지는 `send_large_message()` 함수를 통해 크기를 포함한 헤더와 함께 서버로 전송됩니다:

   ```python
   header = f"{len(message_bytes):<{HEADER_SIZE}}".encode('utf-8')
   client_socket.sendall(header + message_bytes)
   ```

   - 메시지 길이를 고정 크기(`HEADER_SIZE`)의 헤더로 포함시켜 전송합니다.
   - 이를 통해 큰 데이터도 분할 없이 처리할 수 있습니다.

### 서버 측

1. 서버는 클라이언트가 보낸 메시지를 수신합니다:

   ```python
   message = client_socket.recv(HEADER_SIZE).decode('utf-8')
   data = client_socket.recv(int(message)).decode('utf-8')
   ```

   - 헤더에서 메시지의 크기를 읽은 뒤, 해당 크기만큼 데이터를 수신합니다.
2. `CHAT_MESSAGE` 유형의 메시지는 서버에서 모든 클라이언트로 브로드캐스트됩니다:

   ```python
   broadcast(message)
   ```

   - 서버는 연결된 모든 클라이언트에게 동일한 메시지를 전송합니다.

---

## 4. **코드 업데이트 전송**

### 클라이언트 측

```python
message = f"CODE_UPDATE:{code_editor.get('1.0', tk.END)}"
send_large_message(message)
```

1. 클라이언트는 코드 에디터에 입력된 내용을 가져와 `CODE_UPDATE:` 접두사와 함께 서버로 전송합니다.
2. 데이터는 헤더와 함께 서버로 전달됩니다.

### 서버 측

1. 서버는 `recv()`를 통해 데이터를 수신합니다.
2. 메시지 유형이 `CODE_UPDATE`인 경우, 서버는 새로운 코드 상태를 저장하고 모든 클라이언트로 전파합니다:

   ```python
   code_state = message[len("CODE_UPDATE:"):] 
   broadcast(message)
   ```

---

## 5. **그림 데이터 전송**

### 클라이언트 측

```python
draw_data = f"{x0},{y0},{x1},{y1},{color},{width}"
message = f"DRAW_UPDATE:{draw_data}"
send_large_message(message)
```

- 마우스 이벤트로 생성된 좌표(`x0, y0, x1, y1`)와 펜 속성(색상, 두께)을 기반으로 데이터를 구성하여 서버로 전송합니다.

### 서버 측

- 서버는 그림 데이터를 수신하여 다른 클라이언트로 브로드캐스트합니다:

   ```python
   broadcast(message)
   ```

---

## 6. **하이라이트 정보 전송**

### 클라이언트 측

```python
highlight_data = f"{start},{end},{color}"
message = f"HIGHLIGHT_UPDATE:{highlight_data}"
send_large_message(message)
```

- 하이라이트 시작 위치(`start`), 끝 위치(`end`), 색상을 기반으로 데이터를 구성하여 서버로 전송합니다.

### 서버 측

- 서버는 하이라이트 데이터를 수신하고 모든 클라이언트로 전달합니다:

   ```python
   broadcast(message)
   ```

---

## 7. **연결 종료**

### 클라이언트 측

- 클라이언트가 종료되면, 소켓을 닫고 서버와의 연결을 해제합니다:

   ```python
   client_socket.close()
   ```

### 서버 측

- 서버는 연결이 끊어진 클라이언트를 감지하고 이를 처리합니다:

   ```python
   clients.remove(client_socket)
   client_socket.close()
   ```

---

## 요약: 네트워크 흐름

1. **TCP 연결**: 클라이언트가 서버에 연결 요청 → 서버가 연결을 수락
2. **데이터 교환**: 클라이언트가 `sendall()`로 데이터를 보내고, 서버가 `recv()`로 수신
3. **브로드캐스트**: 서버가 수신한 데이터를 다른 모든 클라이언트에게 전달
4. **종료 처리**: 클라이언트가 연결을 끊으면 서버가 이를 감지하고 정리
