'''On met ici des fonctions utiles diverses'''

CASES_ADJ = [(0,-1), (1,-1), (1,0), (-1,0), (-1,1), (0,1)] # (dx,dy)
# . O O                      -->    . O O
# O X O   (vue matrice)      -->     O X O   (vue plateau hexagonal)
# O O .                      -->      O O .

CASES_ADJ_MINIMAX = CASES_ADJ + [(-1,-1), (1,1), (-2,1), (-1,2), (1,-2), (2,-1)]
# . . . O .                  -->    . . . O .
# . O O O O                  -->     . O O O O
# . O X O .  (vue matrice)   -->      . O X O .    (vue plateau hexagonal)
# O O O O .                  -->       O O O O .
# . O . . .                  -->        . O . . .
# on regarde les cases adjacentes et les ponts (cases avec lesquelles on peut les relier avec deux différents chemins possibles)

p1_border1 = lambda n: [(x, 0) for x in range(n)]
p1_border2 = lambda n: [(x, n - 1) for x in range(n)]

p2_border1 = lambda n: [(0, y) for y in range(n)]
p2_border2 = lambda n: [(n - 1, y) for y in range(n)]

p1_borders = lambda n: p1_border1(n) + p1_border2(n)
p2_borders = lambda n: p2_border1(n) + p2_border2(n)

def get_cases_adj(x,y,n):
    return [(x+dx, y+dy) for dx, dy in CASES_ADJ if (0 <= x+dx < n) and (0 <= y+dy < n)]

def get_cases_adj_minimax(x,y,n):
    return [(x+dx, y+dy) for dx, dy in CASES_ADJ_MINIMAX if (0 <= x+dx < n) and (0 <= y+dy < n)]