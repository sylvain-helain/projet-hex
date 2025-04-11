import tkinter as tk
from math import cos,sin,pi,sqrt
import numpy as np
# import threading
# import time

letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

N = 26
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
        self.mat_poids = [np.full((size*size,size*size), fill_value=np.inf), np.full((size*size,size*size), fill_value=np.inf)]
        self.size = size
        self.turn = 0
        self.game_over = False
        self.winner = ''
        self.pcc_bleu = []
        self.pcc_rouge = []

        self.borders = [
            [(x,y) for y in [0,size-1] for x in range(size)],
            [(x,y) for y in range(size) for x in [0,size-1]]

        ]

        for y in range(size*size):
            for x in range(y,size*size):
                x1, y1 = y%size, y//size
                x2, y2 = x%size, x//size
                dx ,dy = x1-x2, y1-y2
                if y==x:
                    self.mat_poids[0][y][x] = 0
                    self.mat_poids[1][y][x] = 0
                    self.mat_poids[0][x][y] = 0
                    self.mat_poids[1][x][y] = 0
                elif (dx == -1 and dy == -1) or (dx == 1 and dy == 1):
                    continue
                elif abs(dx) <= 1 and abs(dy) <= 1:
                    if ((x1,y1) in self.borders[0]) ^ ((x2,y2) in self.borders[0]):
                        coef0 = 1.5
                    else:
                        coef0 = 1
                    if ((x1,y1) in self.borders[1]) ^ ((x2,y2) in self.borders[1]):
                        coef1 = 1.5
                    else:
                        coef1 = 1
                    self.mat_poids[0][y][x] = coef0
                    self.mat_poids[1][y][x] = coef1
                    self.mat_poids[0][x][y] = coef0
                    self.mat_poids[1][x][y] = coef1
        self.fonction_eval()

    def fonction_eval(self):
        for player in [1,2]:
            if player == 1:
                A = {(0,i) for i in range(self.size)}
                B = {(self.size-1,i) for i in range(self.size)}
            else:
                A = {(i,0) for i in range(self.size)}
                B = {(i,self.size-1) for i in range(self.size)}
            
            plus_court_chemin = np.inf
            chemin = []
            for x,y in A:
                poids, dict_chemins = self.dijkstra(x,y,player)
                res = {key : value for key, value in poids.items() if key in B}
                if (mini := min(res.values())) < plus_court_chemin:
                    plus_court_chemin = mini
                    sommet = [key for key,val in res.items() if val == plus_court_chemin][0]
                    chemin = []
                    while sommet != None:
                        chemin.append(sommet)
                        sommet = dict_chemins[sommet]
            
            if player == 1:
                self.pcc_rouge = chemin
            else:
                self.pcc_bleu = chemin
            
            if plus_court_chemin == 0:
                print(f'joueur {COLORS[(player+1)%2]} gagne')
                self.game_over = True
                self.winner = COLORS[(player+1)%2]
            elif plus_court_chemin == np.inf:
                print(f'joueur {COLORS[(player+1)%2]} perd')


    def update_mat(self, x, y, player):
        self.mat[y][x] = player
        for y1 in range(-1,2):
            for x1 in range(-1,2):
                y2, x2 = y+y1, x+x1
                if (y1 == x1) or (y2 >= self.size) or (y2 < 0) or (x2 >= self.size) or (x2 < 0):
                    continue
                yp, xp = y*self.size + x, y2*self.size + x2
                value = self.mat[y2][x2]
                if value == 0:
                    if not ((x,y) in self.borders[player%2]) and ((x2,y2) in self.borders[player%2]):
                        coef = 1
                    else:
                        coef = 0.5
                    self.mat_poids[player%2][yp][xp] = coef
                    self.mat_poids[player%2][xp][yp] = coef
                    self.mat_poids[(player+1)%2][yp][xp] = np.inf
                    self.mat_poids[(player+1)%2][xp][yp] = np.inf
                elif value == player:
                    self.mat_poids[player%2][yp][xp] = 0
                    self.mat_poids[player%2][xp][yp] = 0
                    self.mat_poids[(player+1)%2][yp][xp] = np.inf
                    self.mat_poids[(player+1)%2][xp][yp] = np.inf
                else:
                    self.mat_poids[player%2][yp][xp] = np.inf
                    self.mat_poids[player%2][xp][yp] = np.inf
                    self.mat_poids[(player+1)%2][yp][xp] = np.inf
                    self.mat_poids[(player+1)%2][xp][yp] = np.inf

        self.fonction_eval()

            



    def dijkstra(self, x, y, player):
        poids = {(i%self.size, i//self.size) : np.inf for i in range(self.size**2)}
        chemins = {(i%self.size, i//self.size) : None for i in range(self.size**2)}
        poids[(x,y)] = 0
        marqués = set([(x,y)])
        traités = set([])
        while len(marqués) != len(traités):
            x,y = min(marqués-traités,key=lambda i: poids[i])
            traités.add((x,y))
            for x1 in range(-1,2):
                for y1 in range(-1,2):
                    y2, x2 = y+y1, x+x1
                    if (y1 == x1) or (y2 >= self.size) or (y2 < 0) or (x2 >= self.size) or (x2 < 0):
                        continue
                    yp, xp = y*self.size + x, y2*self.size + x2
                    value = self.mat_poids[player%2][yp][xp]
                    if value != np.inf:
                        marqués.add((x2,y2))
                        if (longueur := value+poids[(x,y)]) < poids[(x2,y2)]:
                            poids[(x2,y2)] = longueur
                            chemins[(x2,y2)] = (x,y)
                        
        return poids,chemins
                    
                    


class App(tk.Tk):
    def __init__(self, game:Game, width=WIDTH, height=HEIGHT):
        super().__init__()
        self.game = game
        self.width = width
        self.height = height
        self.resizable(False,False)
        
        self.canvas = tk.Canvas(self, width=width, height=height, bg='white')
        self.canvas.grid(row=0, column=0)

        self.canvas.create_text(self.width-PAD,PAD,text=COLORS[self.game.turn%2].upper(), font=('consolas',20), fill=COLORS[self.game.turn%2], tag='turn_count')

        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<Motion>', self.move)

        self.draw_board(self.game.size)

    def click(self, event):
        if self.game.game_over:
            return
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
        n = self.game.size
        spacing_x = (WIDTH-PAD*2)/(n+n/2)
        rad = spacing_x/sqrt(3)
        spacing_y = rad*sqrt(2)
        pad_y = ((HEIGHT-PAD*2)-spacing_y*n)/2
        print('a', self.game.pcc_bleu)
        self.canvas.delete('chemin')
        for o in range(2):
            chemin = [self.game.pcc_rouge, self.game.pcc_bleu][o]
            for i in range(len(chemin)):
                x,y = chemin[i]
                x1 = x*spacing_x+PAD+rad+y*spacing_x/2
                y1 = pad_y + y*spacing_y+PAD+rad
                chemin[i] = (x1,y1)
            if chemin:
                self.canvas.create_line(chemin, fill='light grey', tag='chemin', width=8, smooth=True, capstyle='round')
                self.canvas.create_line(chemin, fill=COLORS[o], tag='chemin', width=4, smooth=True, capstyle='round')

        if self.game.game_over:
            self.canvas.create_text(self.width/2,self.height/2, text=f'PLAYER {self.game.winner.upper()} WINS!', font=('consolas',40), fill='white')
            self.canvas.create_text(self.width/2+2,self.height/2, text=f'PLAYER {self.game.winner.upper()} WINS!', font=('consolas',40), fill=self.game.winner)
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