from tkinter import Button, Canvas, Entry, Label, Tk

mycolockcolock = "brown"
coli = ["red", "orange", "yellow", "green", "blue", "darkblue", "purple"]
aa = 10
bb = 10
def paint(event):
    x1, y1 = (event.x - aa / 2), (event.y + bb / 2)
    x2, y2 = (event.x + aa / 2), (event.y - bb / 2)
    canvas.create_oval(x1, y1, x2, y2, outline = mycolockcolock, fill = mycolockcolock)
def acolor(a):
    global mycolockcolock
    mycolockcolock = a
def wj():
    global aa
    global bb
    aa = float(wi.get())
    bb = float(do.get())
def qqq():
    canvas.delete("all")
w = Tk()
canvas = Canvas(w,relief="solid", bd=1, width=600, height=500)
canvas.grid(row = 0, column=0, columnspan=10, rowspan=4)
canvas.bind("<B1-Motion>", paint)
i = 0
for f in coli:
    b = Button(w, bg = f, command = lambda t = f: acolor(t), width=10)
    b.grid(row=5, column=i)
    i += 1
l = Label(w, text="가로 펜 굵기").grid(row = 6, column=1)
l2 = Label(w, text="세로 펜 굵기").grid(row = 6, column=3)
do = Entry(w, width = 10)
wi = Entry(w, width = 10)
do.grid(row = 6, column = 4)
wi.grid(row = 6, column = 2)

qwertyuiop = Button(w, text = "적용", font = ("Bold", 10), command=wj).grid(row=6, column= 5)
asdfghjkl = Button(w, text = "초기화", command = qqq).grid(row = 6, column=0)
w.mainloop()