import socket
import threading
import tkinter as tk

# 서버에서 받은 메시지를 출력하는 함수
def receive_data():
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            if data:
                if data.startswith("CODE:"):  # 코드가 변경되면
                    # 코드 갱신
                    code_display.config(state=tk.NORMAL)
                    code_display.delete(1.0, tk.END)  # 기존 코드 삭제
                    code_display.insert(tk.END, data[5:])  # 새로운 코드 삽입
                    code_display.config(state=tk.DISABLED)
                else:
                    display_message(data)  # 채팅 메시지 출력
        except:
            break

# 서버로 데이터를 보내는 함수 (채팅 메시지 또는 코드)
def send_data(event=None):
    # 채팅 메시지 가져오기
    chat_message = chat_entry.get().strip()
    if chat_message:
        display_message(f"You: {chat_message}")
        client.send(f"{nickname}: {chat_message}".encode('utf-8'))  # 서버로 채팅 메시지 전송
        chat_entry.delete(0, tk.END)  # 입력창 비우기

    # 코드 수정 가져오기
    code_message = code_entry.get("1.0", tk.END).strip()
    if code_message:
        client.send(f"CODE:{code_message}".encode('utf-8'))  # 코드 전송
        code_entry.delete("1.0", tk.END)  # 입력창 비우기

# 메시지를 채팅 영역에 표시
def display_message(message):
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, message + "\n")
    text_area.config(state=tk.DISABLED)

# 닉네임 설정 후 서버에 연결
def set_nickname_and_connect():
    global nickname
    nickname = nickname_entry.get()  # 닉네임 입력창에서 값 가져오기
    if nickname:
        # 서버로 닉네임 전송
        client.send(nickname.encode('utf-8'))
        nickname_entry.config(state=tk.DISABLED)  # 닉네임 입력창 비활성화
        nickname_button.config(state=tk.DISABLED)  # 닉네임 버튼 비활성화
        # GUI 업데이트: 채팅 창으로 이동
        nickname_label.config(text=f"Nickname: {nickname}")
        nickname_frame.pack_forget()
        frame.pack()  # 채팅 및 코드 입력 영역 활성화

# GUI 설정
root = tk.Tk()
root.title("Real-Time Code Share & Chat")

# 닉네임 입력 창
nickname_frame = tk.Frame(root)
nickname_frame.pack()

nickname_label = tk.Label(nickname_frame, text="Enter your nickname:")
nickname_label.pack()

nickname_entry = tk.Entry(nickname_frame)
nickname_entry.pack()

nickname_button = tk.Button(nickname_frame, text="Set Nickname", command=set_nickname_and_connect)
nickname_button.pack()

# 채팅 및 코드 입력 영역
frame = tk.Frame(root)

# 채팅 메시지를 표시하는 텍스트 영역
text_area = tk.Text(frame, height=15, width=60, state=tk.DISABLED)
text_area.pack()

# 채팅 입력창
chat_entry = tk.Entry(frame, width=60)
chat_entry.pack()

# 코드 수정 입력창
code_entry = tk.Text(frame, height=8, width=60)
code_entry.pack()

# 코드 수정 사항을 표시하는 코드 출력창
code_display = tk.Text(frame, height=8, width=60, state=tk.DISABLED)
code_display.pack()

# 전송 버튼
send_button = tk.Button(frame, text="Send", command=send_data)
send_button.pack()

# 서버와 연결
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8888))  # 서버 IP와 포트로 연결

# 서버로부터 데이터 수신을 위한 스레드 시작
threading.Thread(target=receive_data, daemon=True).start()

root.bind("<Return>", send_data)  # Enter 키로 전송
root.mainloop()
