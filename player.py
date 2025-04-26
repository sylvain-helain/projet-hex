import numpy as np

class Player(object):
    def __init__(self, id, color, game_size):
        self.id = id
        self.color = color
        self.pcc = [np.inf,[]]
        self.max_pcc = 0
        self.game_size = game_size
        self.score = 0

        self.mat_adjacence = np.full((game_size**2, game_size**2), fill_value=np.inf)
        self.mat_points = np.full((game_size, game_size), fill_value=np.inf)

        if id == 1:
            self.game_borders = [(x,y) for x in [0, game_size-1] for y in range(game_size)]
        else:
            self.game_borders = [(x,y) for y in [0, game_size-1] for x in range(game_size)]

    def find_shortest_paths(self):
        self.pcc = [np.inf, []]
        self.max_pcc = 0
        self.mat_points = np.full((self.game_size, self.game_size), fill_value=np.inf)
        border1, border2 = self.game_borders[:self.game_size], self.game_borders[self.game_size:]
        for x1, y1 in border1:
            poids, chemins = self.dijkstra(x1,y1)
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

    def dijkstra(self, x:int, y:int):
        poids = {(i%self.game_size, i//self.game_size) : np.inf for i in range(self.game_size**2)}
        chemins = {(i%self.game_size, i//self.game_size) : None for i in range(self.game_size**2)}
        poids[(x,y)] = 0
        marqués = set([(x,y)])
        traités = set([])
        while len(marqués) != len(traités):
            x,y = min(marqués-traités, key=lambda i: poids[i])
            traités.add((x,y))
            for x1 in range(-1,2):
                for y1 in range(-1,2):
                    y2, x2 = y+y1, x+x1
                    if (y1 == x1) or (y2 >= self.game_size) or (y2 < 0) or (x2 >= self.game_size) or (x2 < 0):
                        continue
                    yp, xp = y*self.game_size + x, y2*self.game_size + x2
                    value = self.mat_adjacence[yp][xp]
                    if value != np.inf:
                        marqués.add((x2,y2))
                        if (longueur := value + poids[(x,y)]) < poids[(x2,y2)]:
                            poids[(x2,y2)] = longueur
                            chemins[(x2,y2)] = (x,y)

        
        return poids, chemins
    

class Bot(Player):
    def __init__(self, id, color, game_size, difficulty):
        super().__init__(id, color, game_size)
        self.difficulty = difficulty