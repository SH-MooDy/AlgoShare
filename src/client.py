import socket
import threading
import tkinter as tk
import time

class AlgoShare:
    
    # 객체 생성시 초기화를 위한 함수 
    def __init__(self):
        # 메인 윈도우 생성 및 설정
        self.root = tk.Tk()
        self.root.title("AlgoShare")
        self.root.geometry("1200x800")
        
        # 기본 색상 및 펜 크기 설정
        self.mycolor = "black" # 기본 색
        self.aa = 2 # 가로 굵기
        self.bb = 2 # 세로 굵기
        
        self.nickname = None  # 닉네임 초기화
        
        # 그리기 및 하이라이트 기능 활성화 여부 초기화
        self.drawing_enabled = False  
        self.highlight_enabled = False  
        self.highlight_eraser_enabled = False #
        self.setup_gui() # GUI 구성 함수
        self.setup_network() #서버와의 네트워크 연결 설정 함수

    # GUI 생성 및 배치 함수
    def setup_gui(self):
        # 닉네임 입력을 위한 프레임 설정
        self.nickname_frame = tk.Frame(self.root)
        self.nickname_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.nickname_frame, text="닉네임을 입력하세요:").pack(pady=10)
        self.nickname_entry = tk.Entry(self.nickname_frame, width=30)
        self.nickname_entry.pack(pady=10)
        tk.Button(self.nickname_frame, text="참가하기", command=self.set_nickname).pack(pady=10)

        # 메인 프레임
        self.main_frame = tk.Frame(self.root)

        # 왼쪽 프레임 (코드 + 그림판)
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 코드/그림 컨테이너
        self.container = tk.Frame(self.left_frame)
        self.container.pack(fill=tk.BOTH, expand=True)

        # 코드 에디터
        self.code_display = tk.Text(self.container, height=25, width=50)
        self.code_display.pack(fill=tk.BOTH, expand=True)
        self.code_display.bind("<KeyRelease>", self.code_update)

        # 그림판
        self.canvas = tk.Canvas(self.container, relief="solid", bd=0, highlightthickness=0, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.pack_forget() # 초기 상태에서는 그림판을 숨김

        # 그리기 도구 프레임
        self.tools_frame = tk.Frame(self.left_frame)
        self.tools_frame.pack(fill=tk.X)

        # 그림판 버튼
        self.pen_btn = tk.Button(self.tools_frame, text="✏️ 그림판", command=self.toggle_pen)
        self.pen_btn.pack(side=tk.LEFT, padx=5)

        # 형광펜 버튼
        self.highlight_btn = tk.Button(self.tools_frame, text="🖍️ 형광펜", command=self.toggle_highlight)
        self.highlight_btn.pack(side=tk.LEFT, padx=5)

        # 형광펜 지우개 버튼
        self.highlight_eraser_btn = tk.Button(self.tools_frame, text="🧽 형광펜 지우개", command=self.toggle_highlight_eraser)
        self.highlight_eraser_btn.pack(side=tk.LEFT, padx=5)

        # 색상 선택 버튼
        colors = ["black", "red", "orange", "yellow", "green", "blue", "purple"]
        for color in colors:
            btn = tk.Button(self.tools_frame, bg=color, width=3, command=lambda c=color: self.set_color(c))
            btn.pack(side=tk.LEFT, padx=2)

        # 펜 크기 설정 UI
        tk.Label(self.tools_frame, text="펜 크기:").pack(side=tk.LEFT, padx=5)
        self.pen_size = tk.Entry(self.tools_frame, width=5)
        self.pen_size.pack(side=tk.LEFT)
        self.pen_size.insert(0, "2")
        tk.Button(self.tools_frame, text="적용", command=self.set_pen_size).pack(side=tk.LEFT, padx=5)
        # 그림판 전체 지우기 버튼
        tk.Button(self.tools_frame, text="지우기", command=self.clear_canvas).pack(side=tk.LEFT, padx=5) 

        # 채팅 프레임 
        self.chat_frame = tk.Frame(self.main_frame)
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(self.chat_frame, text="채팅").pack(anchor="w")
        self.chat_output = tk.Text(self.chat_frame, height=40, width=40, state=tk.DISABLED)
        self.chat_output.pack(fill=tk.BOTH, expand=True)
        self.chat_entry = tk.Entry(self.chat_frame, width=40)
        self.chat_entry.pack(pady=10)
        self.chat_entry.bind("<Return>", self.send_chat)

    # 그림판 토글 함수
    def toggle_pen(self):
        # 그림판 기능의 활성화 상태를 토글
        self.drawing_enabled = not self.drawing_enabled
        
        if self.drawing_enabled: # 그림판 기능이 활성화 된 격우
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

    # 형광펜 토글 함수
    def toggle_highlight(self):
        # 하이라이트 기능의 활성화 상태를 토글
        self.highlight_enabled = not self.highlight_enabled
        if self.highlight_enabled: # 하이라이트 기능이 활성화된 경우
            self.highlight_btn.config(relief=tk.SUNKEN)
            self.code_display.config(cursor="pencil")
            self.code_display.bind("<B1-Motion>", self.highlight_text) # 마우스 드래그 이벤트를 하이라이트 기능에 바인딩
            # 그림판 기능 비활성화
            self.drawing_enabled = False
            self.pen_btn.config(relief=tk.RAISED)
            self.canvas.pack_forget()
            self.code_display.pack(fill=tk.BOTH, expand=True)
        else:  
            self.highlight_btn.config(relief=tk.RAISED)
            self.code_display.config(cursor="")
            self.code_display.unbind("<B1-Motion>") # 마우스 드래그 이벤트 바인딩 해제

    # 형광펜 기능 함수
    def highlight_text(self, event):
        try:
            start = self.code_display.index(f"@{event.x},{event.y} wordstart")
            end = self.code_display.index(f"@{event.x},{event.y} wordend")
        
            # 이미 하이라이트된 부분인지 확인
            if "highlight" in self.code_display.tag_names(start):
                self.code_display.tag_remove("highlight", start, end)
                self.send_large_message(f"HIGHLIGHT_ERASE:{(start, end)}") 
            else:
                self.code_display.tag_add("highlight", start, end)
                self.code_display.tag_config("highlight", background="yellow")
                self.send_large_message(f"HIGHLIGHT_UPDATE:{(start, end)}") # 서버로 하이라이트된 부분 전송
        except tk.TclError:
            pass
            
    # 형광펜 지우개 함수
    def toggle_highlight_eraser(self):
        # 하이라이트 지우개 기능의 활성화 상태를 토글
        self.highlight_eraser_enabled = not self.highlight_eraser_enabled
        if self.highlight_eraser_enabled:
            self.highlight_eraser_btn.config(relief=tk.SUNKEN)
            self.code_display.config(cursor="crosshair")
            self.code_display.bind("<B1-Motion>", self.erase_highlight)
            self.highlight_enabled = False  # 하이라이트 기능 비활성화
            self.highlight_btn.config(relief=tk.RAISED)
        else:
            self.highlight_eraser_btn.config(relief=tk.RAISED)
            self.code_display.config(cursor="")
            self.code_display.unbind("<B1-Motion>")

    # 하이라이트된 텍스트 지우는 함수
    def erase_highlight(self, event):
        try:
            start = self.code_display.index(f"@{event.x},{event.y}")
            end = self.code_display.index(f"@{event.x},{event.y}+1c")
        
            # 하이라이트된 부분만 지우기
            if "highlight" in self.code_display.tag_names(start):
                self.code_display.tag_remove("highlight", start, end)
                self.send_large_message(f"HIGHLIGHT_ERASE:{(start, end)}")
        except tk.TclError:
            pass
        
    # 클라이언트와 서버 간의 연결을 설정하는 함수
    def setup_network(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 소켓 객체 생성 (TCP 프로토콜)
        self.client.connect(('127.0.0.1', 8888)) # 서버에 연결 (포트 8888) 127.0.0.1은 내부 테스트를 위한 로컬호스트 주소
        threading.Thread(target=self.receive_data, daemon=True).start() # 데이터 수신을 위한 별도의 스레드 시작
                                                                        # 스레드는 서버로 부터 지속적으로 데이터를 수신

    # 서버로부터 데이터를 지속적으로 수신, 처리하는 함수
    def receive_data(self):
        buffer = b""  # 수신 데이터를 저장할 버퍼
        while True:
            try:
                chunk = self.client.recv(4096)  # 최대 4096바이트 데이터 수신
                if not chunk:
                    print("서버와의 연결이 끊어졌습니다.")
                    self.reconnect()  # 연결 끊김 감지 시 재연결 시도
                    continue

                buffer += chunk  # 수신된 데이터를 버퍼에 추가
                
                # 완전한 메시지 처리
                while len(buffer) >= 4:  # 헤더 크기(4바이트) 이상의 데이터가 있는 경우
                    message_length = int.from_bytes(buffer[:4], 'big')  # 메시지 길이 추출
                    if len(buffer) < 4 + message_length:  # 완전한 메시지가 도착하지 않은 경우
                        break
                        
                    message = buffer[4:4+message_length].decode('utf-8')  # 메시지 디코딩
                    buffer = buffer[4+message_length:]  # 처리된 메시지를 버퍼에서 제거
                    
                    # 닉네임이 설정되지 않은 경우 메시지 처리 건너뛰기
                    if not hasattr(self, 'nickname') or self.nickname is None:
                        continue
                        
                    self.process_message(message)  # 수신된 메시지 처리
                    
            except ConnectionError:
                print("연결 오류 발생. 재연결을 시도합니다.")
                self.reconnect()  # 연결 오류 발생 시 재연결 시도
                time.sleep(1)  # 재연결 시도 전 1초 대기
            except Exception as e:
                print(f"데이터 수신 중 오류 발생: {e}")
                time.sleep(1)  # 오류 발생 시 1초 대기
            
    # 서버로 부터 받은 메시지를 처리하는 함수
    # 메시지의 유형에 따라 동작 수행
    def process_message(self, message):
        if message.startswith("CODE_UPDATE:"):  # 코드 업데이트 처리
            updated_code = message[len("CODE_UPDATE:"):]
            self.code_display.delete("1.0", tk.END)
            self.code_display.insert(tk.END, updated_code)
        elif message.startswith("CHAT_MESSAGE:"): # 채팅 메시지 처리
            chat_message = message[len("CHAT_MESSAGE:"):]
            if not chat_message.startswith(f"{self.nickname}:"): # 자신의 메시지가 아닌 경우에만 표시
                self.chat_output.config(state=tk.NORMAL)
                self.chat_output.insert(tk.END, chat_message + "\n")
                self.chat_output.config(state=tk.DISABLED)
                self.chat_output.see(tk.END)
        elif message.startswith("DRAW_UPDATE:"): # 그림 업데이트 처리
            draw_data = message[len("DRAW_UPDATE:"):]
            if draw_data == '"CLEAR"':
                self.canvas.delete("all")
            else:
                draw_data_tuple = eval(draw_data)
                x1, y1, x2, y2, color = draw_data_tuple
                self.canvas.create_oval(x1, y1, x2, y2, outline=color, fill=color)
        elif message.startswith("HIGHLIGHT_UPDATE:"): # 형광펜 업데이트 처리
            highlight_data = eval(message[len("HIGHLIGHT_UPDATE:"):])
            start, end = highlight_data
            self.code_display.tag_add("highlight", start, end)
            self.code_display.tag_config("highlight", background="yellow")
        elif message.startswith("HIGHLIGHT_ERASE:"): # 형광펜 지우개 처리
            erase_data = eval(message[len("HIGHLIGHT_ERASE:"):])
            start, end = erase_data
            self.code_display.tag_remove("highlight", start, end)

    # 서버로 대용량 메시지 전송 함수 (코드 복사 붙여넣기 시 많은 바이트를 잡아먹기 때문에 만든 함수)
    def send_large_message(self, message):
        try:
            message_bytes = message.encode('utf-8')  # 메시지를 UTF-8로 인코딩
            message_length = len(message_bytes)      # 메시지 길이 계산
            header = message_length.to_bytes(4, 'big')  # 메시지 길이를 4바이트 빅엔디안으로 변환
            self.client.sendall(header + message_bytes)  # 헤더와 메시지를 서버로 전송
        except ConnectionError:
            print("서버와의 연결이 끊어졌습니다. 재연결을 시도합니다.")
            self.reconnect()  # 연결이 끊긴 경우 재연결 시도
        except Exception as e:
            print(f"메시지 전송 중 오류 발생: {e}")

    # 서버와의 연결이 끊어졌을 때 재연결을 시도하는 함수
    def reconnect(self):
        try:
            self.client.close()  # 기존 소켓 연결 종료
            self.setup_network()  # 새로운 네트워크 연결 설정
            if self.nickname:
                self.send_large_message(self.nickname)  # 재연결 후 서버에 닉네임 재전송
        except Exception as e:
            print(f"재연결 실패: {e}")

    # 닉네임 설정 함수
    def set_nickname(self):
        self.nickname = self.nickname_entry.get().strip()  # 닉네임을 받아와 앞뒤 공백 제거
        if self.nickname:
            self.send_large_message(self.nickname)  # 서버에 닉네임 전송
            self.nickname_frame.pack_forget()  # 닉네임 입력 프레임을 화면에서 제거
            self.main_frame.pack(fill=tk.BOTH, expand=True)  # 메인 프레임을 화면에 표시
            
    # 코드 에디터 업데이트 및 동기화 함수
    def code_update(self, event):
        updated_code = self.code_display.get("1.0", tk.END).strip()  # 코드 에디터의 전체 내용을 가져옴
        highlight_ranges = self.code_display.tag_ranges("highlight") # 현재 존재하는 모든 하이라이트 범위를 저장
        
        self.code_display.delete("1.0", tk.END) # 코드 에디터의 내용을 모두 지움
        self.code_display.insert(tk.END, updated_code)  # 업데이트된 코드를 다시 삽입
        
        # 저장해둔 하이라이트를 다시 적용
        for i in range(0, len(highlight_ranges), 2):
            self.code_display.tag_add("highlight", highlight_ranges[i], highlight_ranges[i+1])
        
        # 업데이트된 코드를 서버에 전송하여 다른 클라이언트와 동기화
        self.send_large_message(f"CODE_UPDATE:{updated_code}")

    # 채팅 메시지를 서버로 전송하는 함수
    def send_chat(self, event=None):
        message = self.chat_entry.get().strip()  # 입력 필드에서 메시지를 가져와 앞뒤 공백 제거
        if message:
            chat_message = f"{self.nickname}: {message}" # 닉네임과 메시지를 결합하여 채팅 메시지 형식 생성
            self.send_large_message(f"CHAT_MESSAGE:{chat_message}")  # 서버로 채팅 메시지 전송
            self.chat_entry.delete(0, tk.END) # 입력 필드 초기화
            
            # 자신의 메시지를 채팅창에 추가
            self.chat_output.config(state=tk.NORMAL)
            self.chat_output.insert(tk.END, chat_message + "\n")
            self.chat_output.config(state=tk.DISABLED)
            self.chat_output.see(tk.END)

    # 그림판 기능 함수
    def paint(self, event):
        if not self.drawing_enabled: # 그리기 기능이 비활성화된 경우 함수 종료
            return
        
        # 마우스 위치를 기반으로 타원의 좌표 계산
        x1, y1 = (event.x - self.aa), (event.y - self.bb)
        x2, y2 = (event.x + self.aa), (event.y + self.bb)
        
        self.canvas.create_oval(x1, y1, x2, y2, outline=self.mycolor, fill=self.mycolor) # 캔버스에 타원 그리기
        draw_data = (x1, y1, x2, y2, self.mycolor) # 그리기 데이터 생성
        self.send_large_message(f"DRAW_UPDATE:{draw_data}") # 서버에 그리기 데이터 전송

    # 펜 색상 설정 함수
    def set_color(self, color):
        self.mycolor = color

    # 펜 크기 설정 함수
    def set_pen_size(self):
        try:
            size = float(self.pen_size.get())
            self.aa = size
            self.bb = size
        except ValueError:
            pass

    # 그림판 전체 지우기 함수
    def clear_canvas(self):
        self.canvas.delete("all")
        self.send_large_message('DRAW_UPDATE:"CLEAR"') # 서버에 캔버스 지우기 명령을 전송

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AlgoShare()
    app.run()