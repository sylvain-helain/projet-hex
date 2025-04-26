from player import Player, Bot
import numpy as np
import random as rd

class Game(object):
    def __init__(self, size:int, is_PvBot:bool, color_choice:int|None, difficulty:int|None=5):
        # color_choice, 0,1 ou 2 : 0 = red ; 1 = blue ; 2 = random
        if color_choice == None:
            color_choice = 0
        if color_choice == 2: #choix couleur random
            color_choice = rd.randint(0,1)
        color = ['red', 'blue']

        self.size = size
        self.mat_plateau = np.zeros((size,size),dtype=int)

        self.player0 = Player(0, color.pop(color_choice), size)
        if is_PvBot:
            self.player1 = Bot(1, color.pop(), size, difficulty)
        else:
            self.player1 = Player(1, color.pop(), size)
        self.players = (self.player0, self.player1)

        self.create_mat_adjacence()

        self.turn = 0
        self.game_over = False

    def update_evaluation(self):
        min_pcc = min(self.player0.pcc[0], self.player0.pcc[0])
        # max_pcc = max(self.player0.max_pcc, self.player1.max_pcc)
        for player in self.players:
            # print('###############""')
            player.find_shortest_paths()
            np.mask_indices
            # print('1)', player.mat_points)
            grid_eval = min_pcc + 5 - player.mat_points
            # print('2)', grid_eval)
            grid_eval[grid_eval < 0] = 0
            # print(np.sum(grid_eval > 0))
            # print('3)', grid_eval)
            grid_eval = grid_eval**2
            score = np.sum(grid_eval)
            # print('score)', score)
            player.mat_points = grid_eval
            player.score = score


    def create_mat_adjacence(self):
        '''Fonction pour créer une matrice adjacence des joueurs
        Une matrice d'adjacence pour un plateau de 11x11 est une matrice symétrique de taille 121x121
        Chaque colonne et chaque ligne représente une case et leur intersection est un lien pondéré entre elles'''
        for player in self.players:
            for y in range(self.size**2):
                for x in range(y,self.size**2):
                    # on parcours la matrice du plateau de jeu de gauche a droite et haut en bas
                    x1, y1 = y%self.size, y//self.size 
                    x2, y2 = x%self.size, x//self.size
                    dx, dy = x1-x2, y1-y2
                    if y == x:
                        player.mat_adjacence[y][x] = 0
                        player.mat_adjacence[x][y] = 0
                    elif (dx == -1 and dy == -1) or (dx == 1 and dy == 1):
                        # on évite les cases qui se trouvent sur la diagonale non adjacente
                        continue
                    elif abs(dx) <= 1 and abs(dy) <= 1:
                        # on gère les connexions entre les cases "but" et les cases "non but"
                        if ((x1,y1) in player.game_borders) ^ ((x2,y2) in player.game_borders):
                            poid = 1.5
                        else:
                            poid = 1
                        
                        player.mat_adjacence[y][x] = poid
                        player.mat_adjacence[x][y] = poid
    
    def update_mat_plateau(self, x, y, player_n):
        '''Fonction qui gère l'ajout d'un pion sur le plateau'''
        player = self.players[player_n]
        other_player = self.players[(player_n+1)%2]
        self.mat_plateau[y][x] = player_n+1
        for y1 in range(-1,2):
            for x1 in range(-1,2):
                y2, x2 = y+y1, x+x1
                if (y1 == x1) or (y2 >= self.size) or (y2 < 0) or (x2 >= self.size) or (x2 < 0):
                    # on skip les cases inatteignables ou inexistantes
                    continue
                yp, xp = y*self.size + x, y2*self.size + x2 #calcul des coordonnées pour la matrice de poids
                value = self.mat_plateau[y2][x2]
                if value == 0:
                    if not ((x,y) in player.game_borders) and ((x2,y2) in player.game_borders):
                        poid = 1
                    else:
                        poid = 0.5
                elif value == player.id+1:
                    poid = 0
                else:
                    poid = np.inf
                player.mat_adjacence[yp][xp] = poid
                player.mat_adjacence[xp][yp] = poid
                other_player.mat_adjacence[yp][xp] = np.inf
                other_player.mat_adjacence[xp][yp] = np.inf
        self.turn += 1
        self.update_evaluation()
    
    def switch(self):
        self.player0.color, self.player1.color = self.player1.color, self.player0.color
        self.player0, self.player1 = self.player1, self.player0
        self.players = self.players[::-1]


    def dijkstra(self, x:int, y:int, player:Player|Bot):
        poids = {(i%self.size, i//self.size) : np.inf for i in range(self.size**2)}
        chemins = {(i%self.size, i//self.size) : None for i in range(self.size**2)}
        poids[(x,y)] = 0
        marqués = set([(x,y)])
        traités = set([])
        while len(marqués) != len(traités):
            x,y = min(marqués-traités, key=lambda i: poids[i])
            traités.add((x,y))
            for x1 in range(-1,2):
                for y1 in range(-1,2):
                    y2, x2 = y+y1, x+x1
                    if (y1 == x1) or (y2 >= self.size) or (y2 < 0) or (x2 >= self.size) or (x2 < 0):
                        continue
                    yp, xp = y*self.size + x, y2*self.size + x2
                    value = player.mat_adjacence[yp][xp]
                    if value != np.inf:
                        marqués.add((x2,y2))
                        if (longueur := value + poids[(x,y)]) < poids[(x2,y2)]:
                            poids[(x2,y2)] = longueur
                            chemins[(x2,y2)] = (x,y)

        
        return poids, chemins