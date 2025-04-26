import numpy as np
from player import Bot

def evaluate(board):
    pass


def dijkstra():
    pass


def find_shortest_paths(bot:Bot):
    bot.pcc = [np.inf, []]
    bot.max_pcc = 0
    bot.mat_points = np.full((bot.game_size, bot.game_size), fill_value=np.inf)
    border1, border2 = bot.game_borders[:bot.game_size], bot.game_borders[bot.game_size:]
    for x1, y1 in border1:
        poids, chemins = bot.dijkstra(x1,y1)
        # print(poids,chemins)
        for x2, y2 in border2:
            p = poids[(x2, y2)]
            if p < bot.pcc[0]:
                bot.pcc = [p, []]
                new_pcc = True
            else:
                new_pcc = False
            
            if p > bot.max_pcc:
                bot.max_pcc = p

            node = (x2, y2)
            while node != None:
                x3, y3 = node
                if new_pcc:
                    bot.pcc[1].append((x3,y3))
                if p < bot.mat_points[y3][x3]:
                    bot.mat_points[y3][x3] = p
                node = chemins[(x3, y3)]


def dijkstra(bot:Bot, x:int, y:int):
    poids = {(i%bot.game_size, i//bot.game_size) : np.inf for i in range(bot.game_size**2)}
    chemins = {(i%bot.game_size, i//bot.game_size) : None for i in range(bot.game_size**2)}
    poids[(x,y)] = 0
    marqués = set([(x,y)])
    traités = set([])
    while len(marqués) != len(traités):
        x,y = min(marqués-traités, key=lambda i: poids[i])
        traités.add((x,y))
        for x1 in range(-1,2):
            for y1 in range(-1,2):
                y2, x2 = y+y1, x+x1
                if (y1 == x1) or (y2 >= bot.game_size) or (y2 < 0) or (x2 >= bot.game_size) or (x2 < 0):
                    continue
                yp, xp = y*bot.game_size + x, y2*bot.game_size + x2
                value = bot.mat_adjacence[yp][xp]
                if value != np.inf:
                    marqués.add((x2,y2))
                    if (longueur := value + poids[(x,y)]) < poids[(x2,y2)]:
                        poids[(x2,y2)] = longueur
                        chemins[(x2,y2)] = (x,y)

    
    return poids, chemins