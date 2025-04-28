import numpy as np
from utils import create_mat_adjacence, dijkstra

class Player(object):
    def __init__(self, id, color, game_size):
        self.id = id
        self.color_id = 1 if color == 'red' else 2 # id de couleur utilisé dans la matrice mat_plateau de Game
        self.color = color
        self.pcc = [np.inf,[]]
        self.max_pcc = 0
        self.game_size = game_size
        self.score = 0

        if self.color == 'blue':
            self.game_borders = [(x,y) for x in [0, game_size-1] for y in range(game_size)]
        else:
            self.game_borders = [(x,y) for y in [0, game_size-1] for x in range(game_size)]

        self.mat_adjacence = create_mat_adjacence(self.game_borders, self.game_size)
        self.mat_points = np.full((game_size, game_size), fill_value=np.inf)

    def copy(self):
        player_copy = Player(self.id, self.color, self.game_size)
        player_copy.mat_adjacence = np.copy(self.mat_adjacence)
        player_copy.score = self.score
        return player_copy


    def update_mat_points_pcc(self):
        self.pcc = [np.inf, []]
        self.max_pcc = 0
        self.mat_points = np.full((self.game_size, self.game_size), fill_value=np.inf)
        border1, border2 = self.game_borders[:self.game_size], self.game_borders[self.game_size:]
        for x1, y1 in border1:
            poids, chemins = dijkstra(self.mat_adjacence, self.game_size, x1,y1)
            # print(poids,chemins)
            for x2, y2 in border2:
                p = poids[(x2, y2)]
                if p < self.pcc[0]:
                    self.pcc = [p, []]
                    new_pcc = True
                else:
                    new_pcc = False
                
                if p > self.max_pcc:
                    self.max_pcc = p

                node = (x2, y2)
                while node != None:
                    x3, y3 = node
                    if new_pcc:
                        self.pcc[1].append((x3,y3))
                    if p < self.mat_points[y3][x3]:
                        self.mat_points[y3][x3] = p
                    node = chemins[(x3, y3)]

    @staticmethod
    def update_mat_adj(player, opponent, mat_plateau:np.ndarray, game_size:int, x:int, y:int):
        for y1 in range(-1,2):
            for x1 in range(-1,2):
                y2, x2 = y+y1, x+x1
                if (y1 == x1) or (y2 >= game_size) or (y2 < 0) or (x2 >= game_size) or (x2 < 0):
                    # on skip les cases inatteignables ou inexistantes
                    continue
                yp, xp = y*game_size + x, y2*game_size + x2 #calcul des coordonnées pour la matrice de poids
                value = mat_plateau[y2][x2]
                if value == 0: # si la case adjacente est libre
                    # si seulement une des deux case est dans le but et pas l'autre, le lien entre celles-ci sera doublé
                    if ((x,y) in player.game_borders) ^ ((x2,y2) in player.game_borders): # ^ -> XOR (ou exclusif)
                        poid = 1
                    else:
                        poid = 0.5
                elif value == player.color_id: # si la case est la notre
                    poid = 0
                else: # si la case est occupée par le joueur adverse
                    poid = np.inf
                player.mat_adjacence[yp][xp], player.mat_adjacence[xp][yp] = poid, poid
                opponent.mat_adjacence[yp][xp], opponent.mat_adjacence[xp][yp] = np.inf, np.inf
    
    @staticmethod
    def switch(player1, player2):
        player1.color, player2.color = player2.color, player1.color
        player1.color_id, player2.color_id = player2.color_id, player1.color_id
        player1.game_borders, player2.game_borders = player2.game_borders, player1.game_borders
        player1.mat_adjacence, player2.mat_adjacence = player2.mat_adjacence, player1.mat_adjacence
        player1.mat_points, player2.mat_points = player2.mat_points, player1.mat_points
    

class BotPlayer(Player):
    def __init__(self, id, color, game_size, difficulty):
        super().__init__(id, color, game_size)
        self.difficulty = difficulty