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
    '''Retourne les (au plus) 6 cases adjacentes à la case (x,y)'''
    return [(x+dx, y+dy) for dx, dy in CASES_ADJ if (0 <= x+dx < n) and (0 <= y+dy < n)]

def get_cases_adj_minimax(x,y,n):
    '''Utilisé dans minimax pour trouver les prochains coups potentiels à explorer pour chaque récursion
    On inclut les cases adjacentes à (x,y) ainsi que les cases formant un pont avec (x,y).
    (pont : deux cases positionnées de telles sortes que deux cases peuvent les relier)'''
    return [(x+dx, y+dy) for dx, dy in CASES_ADJ_MINIMAX if (0 <= x+dx < n) and (0 <= y+dy < n)]

def blue(char:str):
    '''Retourne le str en entrée avec un code couleur bleu'''
    return f"\033[34m{char}\033[0m"

def red(char:str):
    '''Retourne le str en entrée avec un code couleur rouge'''
    return f"\033[31m{char}\033[0m"

def dessine_plateau(mat:np.ndarray):
    '''Fonction qui affiche dans le terminal une représentation du plateau à l'aide de carctères ascii hexagonaux
    On ajoute aussi de la couleur pour la lisibilité.'''
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