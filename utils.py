'''On met ici des fonctions utiles diverses'''

import numpy as np

def are_sides_linked(board:np.ndarray, x:int, y:int, goal:tuple, size:int, color_id:int, marqués:list):
    if (x,y) in goal:
        return True
    
    marqués.append((x,y))

    for y1 in range(-1,2):
        for x1 in range(-1,2):
            x2, y2 = x+x1, y+y1
            if y1 == x1 or x2 >= size or x2 < 0 or y2 >= size or y2 < 0:
                continue
            if board[y2][x2] == color_id and (x2,y2) not in marqués:
                if are_sides_linked(board, x2, y2, goal, size, color_id, marqués):
                    return True
    return False


def is_board_terminal(board:np.ndarray):
    size = board.shape[0]
    goals = (
        [(x,y) for y in (0,size-1) for x in range(0,size)],
        [(x,y) for x in (0,size-1) for y in range(0,size)]
    )
    for i in range(2):
        side1, side2 = goals[i][:size], goals[i][size:]
        for x,y in side1:
            if board[y][x] == i+1:
                marqués = []
                if are_sides_linked(board, x, y, side2, size, color_id=i+1, marqués=marqués):
                    return True
    return False


def create_mat_adjacence(game_borders:list, game_size:int):
    '''Fonction pour créer une matrice adjacence des joueurs
    Une matrice d'adjacence pour un plateau de 11x11 est une matrice symétrique de taille 121x121
    Chaque colonne et chaque ligne représente une case et leur intersection est un lien pondéré entre elles'''
    res = np.full((game_size**2, game_size**2), fill_value=np.inf, dtype=float)
    for y in range(game_size**2):
        for x in range(y,game_size**2):
            # on parcours la matrice du plateau de jeu de gauche a droite et haut en bas
            x1, y1 = y%game_size, y//game_size 
            x2, y2 = x%game_size, x//game_size
            dx, dy = x1-x2, y1-y2
            if y == x:
                res[y][x], res[x][y] = 0, 0
            elif (dx == -1 and dy == -1) or (dx == 1 and dy == 1):
                # on évite les cases qui se trouvent sur la diagonale non adjacente
                continue
            elif abs(dx) <= 1 and abs(dy) <= 1:
                # on gère les connexions entre les cases "but" et les cases "non but"
                if ((x1,y1) in game_borders) ^ ((x2,y2) in game_borders):
                    poid = 1.5
                else:
                    poid = 1
                
                res[y][x], res[x][y] = poid, poid
    return res


def dijkstra(mat_adjacence:np.ndarray, game_size:int, x:int, y:int):
    poids = {(i%game_size, i//game_size) : np.inf for i in range(game_size**2)}
    chemins = {(i%game_size, i//game_size) : None for i in range(game_size**2)}
    poids[(x,y)] = 0
    marqués = set([(x,y)])
    traités = set([])
    while len(marqués) != len(traités):
        x,y = min(marqués-traités, key=lambda i: poids[i])
        traités.add((x,y))
        for x1 in range(-1,2):
            for y1 in range(-1,2):
                y2, x2 = y+y1, x+x1
                if (y1 == x1) or (y2 >= game_size) or (y2 < 0) or (x2 >= game_size) or (x2 < 0):
                    continue
                yp, xp = y*game_size + x, y2*game_size + x2
                value = mat_adjacence[yp][xp]
                if value != np.inf:
                    marqués.add((x2,y2))
                    if (longueur := value + poids[(x,y)]) < poids[(x2,y2)]:
                        poids[(x2,y2)] = longueur
                        chemins[(x2,y2)] = (x,y)

    
    return poids, chemins