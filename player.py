from utils import get_cases_adj
import numpy as np


class Player(object):
    def __init__(self, id, n, mat):
        self.id = id
        self.n = n
        self.mat = mat
        if id==1:
            self.border1 = [(x,0) for x in range(n)]
            self.border2 = [(x,n-1) for x in range(n)]
        elif id==2:
            self.border1 = [(0,y) for y in range(n)]
            self.border2 = [(n-1,y) for y in range(n)]
        else:
            raise Exception('id incorrect: veuillez entrer 1 ou 2')
        self.borders = self.border1 + self.border2
        self.adjacences = self.create_dict_adj(self.id, self.borders)

    def find_shortest_path_length(self, dict_adj:dict, game_size:int, border1:list, border2:list):
        min_value = np.inf
        for x, y in border1:
            poids = self.dijkstra(dict_adj, game_size, x, y)
            min_value = min(min_value, min([poids[coo] for coo in border2]))
        return min_value
    
    def dijkstra(self, dict_adj:dict, game_size:int, x:int, y:int):
        poids = {(x, y) : np.inf for x in range(game_size) for y in range(game_size)}
        poids[(x,y)] = 0
        marqués = set([(x,y)])
        traités = set()
        while len(marqués) != len(traités):
            x,y = min(marqués-traités, key=lambda i: poids[i])
            traités.add((x,y))
            for value, x1, y1 in dict_adj[(x,y)]:
                marqués.add((x1,y1))
                if (longueur := value + poids[(x,y)]) < poids[(x1,y1)]:
                    poids[(x1,y1)] = longueur
        return poids
    
    def create_dict_adj(self, id:int, borders:list):
        id_opp = 1 if id==2 else 2
        res = {(x,y):list() for x in range(self.n) for y in range(self.n)}
        for y1 in range(self.n):
            for x1 in range(self.n):
                for x2, y2 in get_cases_adj(x1,y1,self.n):
                    case1, case2 = self.mat[y1][x1], self.mat[y2][x2]
                    if case1 == id_opp or case2 == id_opp:
                        continue
                    is_c1_border, is_c2_border = (x1,y1) in borders, (x2,y2) in borders
                    if case1 == id and case2 == id:
                        value = 0.0
                    elif is_c1_border and is_c2_border:
                        value = 1.5
                    elif is_c1_border:
                        if case1 == id and case2 == 0:
                            value = 0.5
                        elif case1 == 0 and case2 == id:
                            value = 1.0
                        else:
                            value = 1.5
                    elif is_c2_border:
                        if case2 == id and case1 == 0:
                            value = 0.5
                        elif case2 == 0 and case1 == id:
                            value = 1.0
                        else:
                            value = 1.5
                    elif case1==id or case2==id:
                        value = 0.5
                    else:
                        value = 1.0
                    
                    res[(x1,y1)].append([value,x2,y2])

        return res
