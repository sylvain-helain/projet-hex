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

def get_cases_adj(x,y,n):
    return [(x+dx, y+dy) for dx, dy in CASES_ADJ if (0 <= x+dx < n) and (0 <= y+dy < n)]

def get_cases_adj_minimax(x,y,n):
    return [(x+dx, y+dy) for dx, dy in CASES_ADJ_MINIMAX if (0 <= x+dx < n) and (0 <= y+dy < n)]