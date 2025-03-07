import tkinter as tk
from math import cos,sin,pi,sqrt
import numpy as np

letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

N = 9
WIDTH = 900
HEIGHT = 650
PAD = 35


# root = tk.Tk()
# canvas = tk.Canvas(root,width=WIDTH,height=HEIGHT,bg='white')
# canvas.pack()

COLORS = ('blue','red')
# TURN = 0

# class Player(object):
#     def __init__(self, number):
#         self.number = number
#         if number == 1:
#             self.color = 'red'
#         else:
#             self.color = 'blue'


# class Bot(object):
#     def __init__(self):
#         pass


class Game(object):
    def __init__(self, size):
        self.mat = np.zeros((size, size), dtype=int)
        self.size = size
        self.turn = 0

    def update_mat(self, x, y, player):
        self.mat[y][x] = player
        print(self.mat,end='\n\n')


class App(tk.Tk):
    def __init__(self, game:Game, width=WIDTH, height=HEIGHT):
        super().__init__()
        self.game = game
        self.width = width
        self.height = height
        
        self.canvas = tk.Canvas(self, width=width, height=height, bg='white')
        self.canvas.grid(row=0, column=0)

        self.canvas.create_text(self.width-PAD,PAD,text=COLORS[self.game.turn%2].upper(), font=('consolas',20), fill=COLORS[self.game.turn%2], tag='turn_count')

        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<Motion>', self.move)

        self.draw_board(self.game.size)

    def click(self, event):
        overlap = self.canvas.find_overlapping(event.x-1,event.y-1,event.x+1,event.y+1)
        if len(overlap) == 0:
            return
        tags = [self.canvas.gettags(overlap[i])[0] for i in range(len(overlap))]
        tags = [i for i in tags if i not in ['ignore', 'ignore2']]
        if len(tags) == 0:
            return
        tag = tags[0]
        if self.canvas.itemcget(tag,"fill") == 'light grey':
            self.canvas.itemconfig(tag, fill=COLORS[self.game.turn%2])
            x,y = tag.split(':')
            x,y = int(x), int(y)
            self.game.update_mat(x,y, self.game.turn%2+1)
        else:
            return
        self.canvas.delete('turn_count')
        self.canvas.delete('cursor')
        self.game.turn += 1
        self.canvas.create_text(self.width-PAD,PAD,text=COLORS[self.game.turn%2].upper(), font=('consolas',20), fill=COLORS[self.game.turn%2], tag='turn_count')
        self.canvas.create_oval(event.x-7,event.y-7,event.x+7,event.y+7,fill=COLORS[self.game.turn%2], width=0, tag='cursor')

    def move(self, event):
        x,y = event.x, event.y
        self.canvas.delete('cursor')
        if x > self.width or x < 0 or y > self.height or y < 0:
            return
        self.canvas.create_oval(x-7,y-7,x+7,y+7,fill=COLORS[self.game.turn%2], width=0, tag='cursor')

    def draw_hexagon(self, x,y,r,tag):
        points = [[x+cos(pi/6+i*pi/3)*r,y+sin(pi/6+i*pi/3)*r] for i in range(6)]
        self.canvas.create_polygon(points,fill='light grey',outline='black',width=2,tag=tag)
        if tag.split(':')[0] == str(0):
            for ligne in (points[1:3], points[2:4]):
                self.canvas.create_line(ligne, fill='blue', width=5, tag='ignore2')
        if tag.split(':')[0] == str(N-1):
            for ligne in ([points[-1], points[0]],points[4:6]):
                self.canvas.create_line(ligne, fill='blue', width=5, tag='ignore2')
        if tag.split(':')[-1] == str(0):
            for ligne in (points[3:5], points[4:6]):
                self.canvas.create_line(ligne, fill='red', width=5, tag='ignore2')
        if tag.split(':')[-1] == str(N-1):
            for ligne in (points[1:3], points[0:2]):
                self.canvas.create_line(ligne, fill='red', width=5, tag='ignore2')

    def draw_board(self, n):
        spacing_x = (WIDTH-PAD*2)/(n+n/2)
        rad = spacing_x/sqrt(3)
        spacing_y = rad*sqrt(2)
        pad_y = ((HEIGHT-PAD*2)-spacing_y*n)/2
        corners = []
        for y in range(n):
            for x in range(n):
                x1 = x*spacing_x+PAD+rad+y*spacing_x/2
                y1 = pad_y + y*spacing_y+PAD+rad
                self.draw_hexagon(x1,y1,rad,tag=f"{x}:{y}")
                # if (y == 0 or y == n-1) and (x == 0 or x == n-1):
                #     corners.append([x1,y1])
                if x == 0:
                    self.canvas.create_text(x1-rad*1.75,y1,text=str(y+1),font=('consolas',20),tag='ignore')
                if x == n-1:
                    self.canvas.create_text(x1+rad*1.75,y1,text=str(y+1),font=('consolas',20),tag='ignore')
                if y == 0:
                    self.canvas.create_text(x1-rad,y1-rad*1.5,text=letters[x],font=('consolas',20),tag='ignore')
                if y == n-1:
                    self.canvas.create_text(x1+rad,y1+rad*1.5,text=letters[x],font=('consolas',20),tag='ignore')
        self.canvas.tag_lower('ignore')
        self.canvas.tag_raise('ignore2')



# canvas.bind('<Button-1>', click)

# couleur = COLORS[TURN%2]


def main(n=N):
    game = Game(n)
    root = App(game)
    root.mainloop()



if __name__ == '__main__':
    main()