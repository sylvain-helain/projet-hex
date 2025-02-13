import tkinter as tk
from math import cos,sin,pi,sqrt

letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

N = 9
WIDTH = 650
HEIGHT = 650
PAD = 35


root = tk.Tk()
canvas = tk.Canvas(root,width=WIDTH,height=HEIGHT,bg='white')
canvas.pack()



def click(event):
    overlap = canvas.find_overlapping(event.x-1,event.y-1,event.x+1,event.y+1)
    if len(overlap) == 0:
        return
    tags = [canvas.gettags(overlap[i])[0] for i in range(len(overlap))]
    tags = [i for i in tags if i != 'ignore']
    if len(tags) == 0:
        return
    tag = tags[0]
    if canvas.itemcget(tag,"fill") == 'red':
        canvas.itemconfig(tag, fill="light grey")
    else:
        canvas.itemconfig(tag, fill="red")

canvas.bind('<Button-1>', click)

def draw_hexagon(x,y,r,tag):
    points = [[x+cos(pi/6+i*pi/3)*r,y+sin(pi/6+i*pi/3)*r] for i in range(6)]
    canvas.create_polygon(points,fill='light grey',outline='black',width=2,tag=tag)

def draw_board(n):
    spacing_x = (WIDTH-PAD*2)/(n+n/2)
    rad = spacing_x/sqrt(3)
    spacing_y = rad*sqrt(2)
    pad_y = ((HEIGHT-PAD*2)-spacing_y*n)/2
    corners = []
    for y in range(n):
        for x in range(n):
            x1 = x*spacing_x+PAD+rad+y*spacing_x/2
            y1 = pad_y + y*spacing_y+PAD+rad
            draw_hexagon(x1,y1,rad,tag=f"{x}:{y}")
            if (y == 0 or y == n-1) and (x == 0 or x == n-1):
                corners.append([x1,y1])
            if x == 0:
                canvas.create_text(x1-rad*1.75,y1,text=str(y+1),font=('consolas',20),tag='ignore')
            if x == n-1:
                canvas.create_text(x1+rad*1.75,y1,text=str(y+1),font=('consolas',20),tag='ignore')
            if y == 0:
                canvas.create_text(x1-rad,y1-rad*1.5,text=letters[x],font=('consolas',20),tag='ignore')
            if y == n-1:
                canvas.create_text(x1+rad,y1+rad*1.5,text=letters[x],font=('consolas',20),tag='ignore')
    corners[2], corners[3] = corners[3], corners[2]
    corners.append(corners[0])
    colors = ('red', 'blue')
    for i in range(4):
        canvas.create_line(corners[i], corners[i+1], fill=colors[i%2], capstyle='round', width=rad*1.8, tag='ignore')
    canvas.tag_lower('ignore')
# draw_hexagon(250,250,20)

draw_board(N)

root.mainloop()

