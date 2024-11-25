import socket
import threading
import tkinter as tk


# 서버에서 받은 메시지를 처리하는 함수
def receive_data():
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            if data.startswith("CODE_UPDATE:"):  # 코드 업데이트
                updated_code = data[len("CODE_UPDATE:"):]
                code_display.delete("1.0", tk.END)
                code_display.insert(tk.END, updated_code)
            else:  # 채팅 메시지
                chat_output.config(state=tk.NORMAL)
                chat_output.insert(tk.END, data + "\n")
                chat_output.config(state=tk.DISABLED)
                chat_output.see(tk.END)  # 최신 메시지로 스크롤
        except Exception as e:
            print(f"Error: {e}")
            break


# 코드 입력 내용 서버로 전송
def code_update(event):
    updated_code = code_display.get("1.0", tk.END).strip()
    client.send(f"CODE_UPDATE:{updated_code}".encode('utf-8'))


# 채팅 메시지 서버로 전송
def send_chat(event=None):
    message = chat_entry.get().strip()
    if message:
        client.send(f"{nickname}: {message}".encode('utf-8'))
        chat_entry.delete(0, tk.END)
        chat_output.config(state=tk.NORMAL)
        chat_output.insert(tk.END, f"{nickname}: {message}" + "\n")
        chat_output.config(state=tk.DISABLED)
        chat_output.see(tk.END)
        


# 닉네임 설정 후 서버 연결
def set_nickname():
    global nickname
    nickname = nickname_entry.get().strip()
    if nickname:
        client.send(nickname.encode('utf-8'))
        nickname_frame.pack_forget()
        main_frame.pack(fill=tk.BOTH, expand=True)


# GUI 설정
root = tk.Tk()
root.title("AlgoShare")
root.geometry("800x600")

# 닉네임 입력 창
nickname_frame = tk.Frame(root)
nickname_frame.pack(fill=tk.BOTH, expand=True)

tk.Label(nickname_frame, text="닉네임을 입력하세요:").pack(pady=10)
nickname_entry = tk.Entry(nickname_frame, width=30)
nickname_entry.pack(pady=10)
tk.Button(nickname_frame, text="참가하기", command=set_nickname).pack(pady=10)

# 메인 프레임 (코드창, 채팅창)
main_frame = tk.Frame(root)

# 코드창
code_frame = tk.Frame(main_frame)
code_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tk.Label(code_frame, text="Code Editor").pack(anchor="w")
code_display = tk.Text(code_frame, height=25, width=50)
code_display.pack(fill=tk.BOTH, expand=True)
code_display.bind("<KeyRelease>", code_update)

# 채팅창
chat_frame = tk.Frame(main_frame)
chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

tk.Label(chat_frame, text="Chat").pack(anchor="w")
chat_output = tk.Text(chat_frame, height=20, width=30, state=tk.DISABLED)
chat_output.pack(fill=tk.BOTH, expand=True)

# 채팅 입력창
chat_entry = tk.Entry(root, width=100)
chat_entry.pack(side=tk.BOTTOM, fill=tk.X)
chat_entry.bind("<Return>", send_chat)

# 소켓 연결
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8888))  # 서버 주소와 포트, 서버 역할을 할 컴퓨터의 IP주소 입력하기
                                    # 내부 테스트 시 127.0.0.1 사용하기!!!

# 서버 메시지 수신 스레드 시작
threading.Thread(target=receive_data, daemon=True).start()

root.mainloop()
