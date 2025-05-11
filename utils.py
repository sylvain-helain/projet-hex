'''On met ici des fonctions utiles diverses'''

import numpy as np
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

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

def blue(char:str):
    return f"\033[34m{char}\033[0m"

def red(char:str):
    return f"\033[31m{char}\033[0m"

def dessine_plateau(mat:np.ndarray):
    n = mat.shape[0]
    print('', red(' '.join([i for i in LETTERS[:n]])))
    pad = 2
    for y in range(n):
        print(blue(f"{y+1} ".rjust(pad, " ")), end='')
        pad += 1
        for x in range(n):
            value = mat[y][x]
            if value == 0:
                print("⬡", end=" ")
            elif value == 1:
                print(red("⬢"), end=" ")
            elif value == 2:
                print(blue("⬢"), end=" ")
            else:
                raise Exception("erreur couleur plateau")
        print(blue(' '+str(y+1)))
    print(red(' '*pad + ' '.join([i for i in LETTERS[:n]])))