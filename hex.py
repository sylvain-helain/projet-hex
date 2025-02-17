import tkinter as tk
from math import cos,sin,pi,sqrt
import numpy as np

letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

N = 9
WIDTH = 900
HEIGHT = 650
PAD = 35


root = tk.Tk()
canvas = tk.Canvas(root,width=WIDTH,height=HEIGHT,bg='white')
canvas.pack()

COLOR = ('blue','red')
TURN = 0

grille = np.zeros((N,N), dtype=int)

print(grille)


def update_grille(x,y,player):
    global grille
    grille[y][x] = player
    print(grille,end='\n\n')


# def check_dist(player,x1,y1,x2,y2, grid_dist = np.full((9,9), fill_value=-1, dtype=int), first=True):
#     if first:
#         grid_dist[y1][x1] = 0
#         if grille[y2][x2] == (player+1)%2:
#             return np.inf
#         first = False
#     to_check= [[x1+i-1,y1+o-1] for i in range(3) for o in range(3) if i != o]
#     to_expand = []
#     for x,y in to_check:
#         if x < 0 or x >= N or y < 0 or x >= N:
#             continue
#         if grid_dist[y][x] != -1:
#             continue

#         if grille[y][x] == (player+1)%2:
#             grid_dist[y][x] = np.inf
#         elif grille[y][x] == player:
#             grid_dist[y][x] = grid_dist[y1][x1]
#         else:
#             grid_dist[y][x] = grid_dist[y1][x1]+1
        
#         if (x,y) == (x2,y2):
#             return grid_dist[y][x]
#         else:
#             to_expand.append([x,y])

#     for x,y in to_expand:  
#         check_dist(player,x,y,x2,y2, grid_dist, first)

# check_dist(1,4,6,2,3)

def click(event):
    global TURN
    couleur = COLOR[TURN%2]
    overlap = canvas.find_overlapping(event.x-1,event.y-1,event.x+1,event.y+1)
    if len(overlap) == 0:
        return
    tags = [canvas.gettags(overlap[i])[0] for i in range(len(overlap))]
    tags = [i for i in tags if i not in ['ignore', 'ignore2']]
    if len(tags) == 0:
        return
    tag = tags[0]
    if canvas.itemcget(tag,"fill") == 'light grey':
        canvas.itemconfig(tag, fill=couleur)
        x,y = tag.split(':')
        x,y = int(x), int(y)
        update_grille(x,y, TURN%2+1)
    else:
        return
    canvas.delete('turn')
    TURN += 1
    couleur = COLOR[TURN%2]
    canvas.create_text(PAD,PAD,text=couleur.upper(), font=('consolas',20), fill=couleur, tag='turn')

canvas.bind('<Button-1>', click)

couleur = COLOR[TURN%2]
canvas.create_text(PAD,PAD,text=couleur.upper(), font=('consolas',20), fill=couleur, tag='turn')

def draw_hexagon(x,y,r,tag):
    points = [[x+cos(pi/6+i*pi/3)*r,y+sin(pi/6+i*pi/3)*r] for i in range(6)]
    canvas.create_polygon(points,fill='light grey',outline='black',width=2,tag=tag)
    if tag.split(':')[0] == str(0):
        for ligne in (points[1:3], points[2:4]):
            canvas.create_line(ligne, fill='blue', width=5, tag='ignore2')
    if tag.split(':')[0] == str(N-1):
        for ligne in ([points[-1], points[0]],points[4:6]):
            canvas.create_line(ligne, fill='blue', width=5, tag='ignore2')
    if tag.split(':')[-1] == str(0):
        for ligne in (points[3:5], points[4:6]):
            canvas.create_line(ligne, fill='red', width=5, tag='ignore2')
    if tag.split(':')[-1] == str(N-1):
        for ligne in (points[1:3], points[0:2]):
            canvas.create_line(ligne, fill='red', width=5, tag='ignore2')
        

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
            # if (y == 0 or y == n-1) and (x == 0 or x == n-1):
            #     corners.append([x1,y1])
            if x == 0:
                canvas.create_text(x1-rad*1.75,y1,text=str(y+1),font=('consolas',20),tag='ignore')
            if x == n-1:
                canvas.create_text(x1+rad*1.75,y1,text=str(y+1),font=('consolas',20),tag='ignore')
            if y == 0:
                canvas.create_text(x1-rad,y1-rad*1.5,text=letters[x],font=('consolas',20),tag='ignore')
            if y == n-1:
                canvas.create_text(x1+rad,y1+rad*1.5,text=letters[x],font=('consolas',20),tag='ignore')
    # corners[2], corners[3] = corners[3], corners[2]
    # corners.append(corners[0])
    # colors = ('red', 'blue')
    # for i in range(4):
    #     canvas.create_line(corners[i], corners[i+1], fill=colors[i%2], capstyle='round', width=rad*1.8, tag='ignore')
    canvas.tag_lower('ignore')
    canvas.tag_raise('ignore2')

draw_board(N)

root.mainloop()

