import socket
import threading
import tkinter as tk

class AlgoShare:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AlgoShare")
        self.root.geometry("1200x800")
        self.mycolor = "black"
        self.aa = 2
        self.bb = 2
        self.drawing_enabled = False
        self.highlight_enabled = False
        self.highlight_eraser_enabled = False
        self.setup_gui()
        self.setup_network()

    def setup_gui(self):
        # 닉네임 프레임
        self.nickname_frame = tk.Frame(self.root)
        self.nickname_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.nickname_frame, text="닉네임을 입력하세요:").pack(pady=10)
        self.nickname_entry = tk.Entry(self.nickname_frame, width=30)
        self.nickname_entry.pack(pady=10)
        tk.Button(self.nickname_frame, text="참가하기", command=self.set_nickname).pack(pady=10)

        # 메인 프레임
        self.main_frame = tk.Frame(self.root)

        # 왼쪽 프레임 (코드 + 그림)
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 코드/그림 컨테이너
        self.container = tk.Frame(self.left_frame)
        self.container.pack(fill=tk.BOTH, expand=True)

        # 코드 에디터
        self.code_display = tk.Text(self.container, height=25, width=50)
        self.code_display.pack(fill=tk.BOTH, expand=True)
        self.code_display.bind("<KeyRelease>", self.code_update)

        # 캔버스
        self.canvas = tk.Canvas(self.container, relief="solid", bd=0,
                              highlightthickness=0, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<B1-Motion>", self.paint)
        
        # 초기 상태에서는 캔버스를 숨김
        self.canvas.pack_forget()

        # 그리기 도구 프레임
        self.tools_frame = tk.Frame(self.left_frame)
        self.tools_frame.pack(fill=tk.X)

        # 펜 버튼
        self.pen_btn = tk.Button(self.tools_frame, text="✏️ 그림판", command=self.toggle_pen)
        self.pen_btn.pack(side=tk.LEFT, padx=5)

        # 형광펜 버튼
        self.highlight_btn = tk.Button(self.tools_frame, text="🖍️ 형광펜", command=self.toggle_highlight)
        self.highlight_btn.pack(side=tk.LEFT, padx=5)

        # 형광펜 지우개 버튼
        self.highlight_eraser_btn = tk.Button(self.tools_frame, text="🧽 형광펜 지우개", command=self.toggle_highlight_eraser)
        self.highlight_eraser_btn.pack(side=tk.LEFT, padx=5)

        # 색상 버튼들
        colors = ["black", "red", "orange", "yellow", "green", "blue", "purple"]
        for color in colors:
            btn = tk.Button(self.tools_frame, bg=color, width=3,
                          command=lambda c=color: self.set_color(c))
            btn.pack(side=tk.LEFT, padx=2)

        # 펜 크기 설정
        tk.Label(self.tools_frame, text="펜 크기:").pack(side=tk.LEFT, padx=5)
        self.pen_size = tk.Entry(self.tools_frame, width=5)
        self.pen_size.pack(side=tk.LEFT)
        self.pen_size.insert(0, "2")
        tk.Button(self.tools_frame, text="적용",
                 command=self.set_pen_size).pack(side=tk.LEFT, padx=5)
        tk.Button(self.tools_frame, text="지우기",
                 command=self.clear_canvas).pack(side=tk.LEFT, padx=5)

        # 채팅 프레임 (오른쪽)
        self.chat_frame = tk.Frame(self.main_frame)
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(self.chat_frame, text="채팅").pack(anchor="w")
        self.chat_output = tk.Text(self.chat_frame, height=40, width=40, state=tk.DISABLED)
        self.chat_output.pack(fill=tk.BOTH, expand=True)
        self.chat_entry = tk.Entry(self.chat_frame, width=40)
        self.chat_entry.pack(pady=10)
        self.chat_entry.bind("<Return>", self.send_chat)

    def toggle_pen(self):
        self.drawing_enabled = not self.drawing_enabled
        if self.drawing_enabled:
            self.pen_btn.config(relief=tk.SUNKEN)
            self.code_display.pack_forget()
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.canvas.config(cursor="pencil")
            self.highlight_enabled = False
            self.highlight_btn.config(relief=tk.RAISED)
        else:
            self.pen_btn.config(relief=tk.RAISED)
            self.canvas.pack_forget()
            self.code_display.pack(fill=tk.BOTH, expand=True)
            self.canvas.config(cursor="")

    def toggle_highlight(self):
        self.highlight_enabled = not self.highlight_enabled
        if self.highlight_enabled:
            self.highlight_btn.config(relief=tk.SUNKEN)
            self.code_display.config(cursor="pencil")
            self.code_display.bind("<B1-Motion>", self.highlight_text)
            self.drawing_enabled = False
            self.pen_btn.config(relief=tk.RAISED)
            self.canvas.pack_forget()
            self.code_display.pack(fill=tk.BOTH, expand=True)
        else:
            self.highlight_btn.config(relief=tk.RAISED)
            self.code_display.config(cursor="")
            self.code_display.unbind("<B1-Motion>")

    def highlight_text(self, event):
        try:
            start = self.code_display.index(f"@{event.x},{event.y} wordstart")
            end = self.code_display.index(f"@{event.x},{event.y} wordend")
            self.code_display.tag_add("highlight", start, end)
            self.code_display.tag_config("highlight", background="yellow")
            
            highlight_data = (start, end)
            self.send_large_message(f"HIGHLIGHT_UPDATE:{highlight_data}")
        except tk.TclError:
            pass

    def toggle_highlight_eraser(self):
        self.highlight_eraser_enabled = not self.highlight_eraser_enabled
        if self.highlight_eraser_enabled:
            self.highlight_eraser_btn.config(relief=tk.SUNKEN)
            self.code_display.config(cursor="crosshair")
            self.code_display.bind("<B1-Motion>", self.erase_highlight)
            self.highlight_enabled = False
            self.highlight_btn.config(relief=tk.RAISED)
        else:
            self.highlight_eraser_btn.config(relief=tk.RAISED)
            self.code_display.config(cursor="")
            self.code_display.unbind("<B1-Motion>")

    def erase_highlight(self, event):
        try:
            start = self.code_display.index(f"@{event.x},{event.y}")
            end = self.code_display.index(f"@{event.x},{event.y}+1c")
            self.code_display.tag_remove("highlight", start, end)
            
            # 서버에 지우기 정보 전송
            erase_data = (start, end)
            self.send_large_message(f"HIGHLIGHT_ERASE:{erase_data}")
        except tk.TclError:
            pass

    def setup_network(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('localhost', 8888))
        threading.Thread(target=self.receive_data, daemon=True).start()

    def receive_data(self):
        buffer = b""
        while True:
            try:
                chunk = self.client.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                while len(buffer) >= 4:
                    message_length = int.from_bytes(buffer[:4], 'big')
                    if len(buffer) < 4 + message_length:
                        break
                    message = buffer[4:4+message_length].decode('utf-8')
                    buffer = buffer[4+message_length:]
                    self.process_message(message)
            except Exception as e:
                print(f"Error in receive_data: {e}")
                break

    def process_message(self, message):
        if message.startswith("CODE_UPDATE:"):
            updated_code = message[len("CODE_UPDATE:"):]
            self.code_display.delete("1.0", tk.END)
            self.code_display.insert(tk.END, updated_code)
        elif message.startswith("CHAT_MESSAGE:"):
            chat_message = message[len("CHAT_MESSAGE:"):]
            self.chat_output.config(state=tk.NORMAL)
            self.chat_output.insert(tk.END, chat_message + "\n")
            self.chat_output.config(state=tk.DISABLED)
            self.chat_output.see(tk.END)
        elif message.startswith("DRAW_UPDATE:"):
            draw_data = message[len("DRAW_UPDATE:"):]
            if draw_data == '"CLEAR"':
                self.canvas.delete("all")
            else:
                draw_data_tuple = eval(draw_data)
                x1, y1, x2, y2, color = draw_data_tuple
                self.canvas.create_oval(x1, y1, x2, y2, outline=color, fill=color)
        elif message.startswith("HIGHLIGHT_UPDATE:"):
            highlight_data = eval(message[len("HIGHLIGHT_UPDATE:"):])
            start, end = highlight_data
            self.code_display.tag_add("highlight", start, end)
            self.code_display.tag_config("highlight", background="yellow")
        elif message.startswith("HIGHLIGHT_ERASE:"):
            erase_data = eval(message[len("HIGHLIGHT_ERASE:"):])
            start, end = erase_data
            self.code_display.tag_remove("highlight", start, end)

    def send_large_message(self, message):
        message_bytes = message.encode('utf-8')
        message_length = len(message_bytes)
        header = message_length.to_bytes(4, 'big')
        self.client.sendall(header + message_bytes)

    def set_nickname(self):
        self.nickname = self.nickname_entry.get().strip()
        if self.nickname:
            self.send_large_message(self.nickname)
            self.nickname_frame.pack_forget()
            self.main_frame.pack(fill=tk.BOTH, expand=True)

    def code_update(self, event):
        updated_code = self.code_display.get("1.0", tk.END).strip()
        highlight_ranges = self.code_display.tag_ranges("highlight")
        
        self.code_display.delete("1.0", tk.END)
        self.code_display.insert(tk.END, updated_code)
        
        for i in range(0, len(highlight_ranges), 2):
            self.code_display.tag_add("highlight", highlight_ranges[i], highlight_ranges[i+1])
        
        self.send_large_message(f"CODE_UPDATE:{updated_code}")

    def send_chat(self, event=None):
        message = self.chat_entry.get().strip()
        if message:
            chat_message = f"{self.nickname}: {message}"
            self.send_large_message(f"CHAT_MESSAGE:{chat_message}")
            self.chat_entry.delete(0, tk.END)

    def paint(self, event):
        if not self.drawing_enabled:
            return
        x1, y1 = (event.x - self.aa), (event.y - self.bb)
        x2, y2 = (event.x + self.aa), (event.y + self.bb)
        self.canvas.create_oval(x1, y1, x2, y2, outline=self.mycolor, fill=self.mycolor)
        draw_data = (x1, y1, x2, y2, self.mycolor)
        self.send_large_message(f"DRAW_UPDATE:{draw_data}")

    def set_color(self, color):
        self.mycolor = color

    def set_pen_size(self):
        try:
            size = float(self.pen_size.get())
            self.aa = size
            self.bb = size
        except ValueError:
            pass

    def clear_canvas(self):
        self.canvas.delete("all")
        self.send_large_message('DRAW_UPDATE:"CLEAR"')

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AlgoShare()
    app.run()