import socket
import threading

clients = []
code_state = ""
draw_state = []
highlight_state = []

def send_large_message(client_socket, message):
    message_bytes = message.encode('utf-8')
    message_length = len(message_bytes)
    header = message_length.to_bytes(4, 'big')
    try:
        client_socket.sendall(header + message_bytes)
        print(f"Sent full message of length: {message_length}")
    except Exception as e:
        print(f"Error sending message to client: {e}")

def broadcast(message, sender_socket=None):
    disconnected_clients = []
    for client in clients:
        try:
            send_large_message(client, message)
        except Exception as e:
            print(f"Error sending to client: {e}")
            disconnected_clients.append(client)
    
    for client in disconnected_clients:
        if client in clients:
            clients.remove(client)

def handle_client(client_socket, client_addr):
    global code_state
    try:
        nickname = client_socket.recv(1024).decode('utf-8')
        print(f"{nickname} connected from {client_addr}")
        broadcast(f"CHAT_MESSAGE:{nickname}님이 채팅에 참여하였습니다.")
        
        if code_state:
            send_large_message(client_socket, f"CODE_UPDATE:{code_state}")
        for draw_cmd in draw_state:
            send_large_message(client_socket, f"DRAW_UPDATE:{draw_cmd}")
        for highlight_cmd in highlight_state:
            send_large_message(client_socket, f"HIGHLIGHT_UPDATE:{highlight_cmd}")
            
        while True:
            length_bytes = client_socket.recv(4)
            if not length_bytes:
                break
                
            message_length = int.from_bytes(length_bytes, 'big')
            data = b""
            while len(data) < message_length:
                chunk = client_socket.recv(min(message_length - len(data), 1024))
                if not chunk:
                    raise ConnectionError("Connection closed while receiving data")
                data += chunk
                
            message = data.decode('utf-8')
            
            if message.startswith("DRAW_UPDATE:"):
                draw_data = message[len("DRAW_UPDATE:"):]
                if draw_data == '"CLEAR"':
                    draw_state.clear()
                    broadcast(message)
                else:
                    draw_data_tuple = eval(draw_data)
                    draw_state.append(draw_data_tuple)
                    broadcast(message)
            elif message.startswith("CODE_UPDATE:"):
                code_state = message[len("CODE_UPDATE:"):]
                broadcast(message, sender_socket=client_socket)
            elif message.startswith("CHAT_MESSAGE:"):
                chat_message = message[len("CHAT_MESSAGE:"):]
                broadcast(message, sender_socket=client_socket)
            elif message.startswith("HIGHLIGHT_UPDATE:"):
                highlight_data = message[len("HIGHLIGHT_UPDATE:"):]
                highlight_state.append(eval(highlight_data))
                broadcast(message)
            elif message.startswith("HIGHLIGHT_ERASE:"):
                erase_data = message[len("HIGHLIGHT_ERASE:"):]
                broadcast(message)
                
    except Exception as e:
        print(f"Error with {client_addr}: {e}")
    finally:
        if client_socket in clients:
            clients.remove(client_socket)
        client_socket.close()

def start_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 8888))
        server.listen(5)
        print("Server started on port 8888")
        
        while True:
            client_socket, client_addr = server.accept()
            if code_state:
                send_large_message(client_socket, f"CODE_UPDATE:{code_state}")
            threading.Thread(target=handle_client, args=(client_socket, client_addr)).start()
            clients.append(client_socket)
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_server()