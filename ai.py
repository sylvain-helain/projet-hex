'''Cette section du code est dédiée à l'ia du jeu et le caclul des meilleurs coups
Pour chaque joueur on utilisera plusieurs matrices:
- Une matrice d'adjacence (ou poids) n²*n², un poid sera attribué à chaque arrête en fonction du coloris des cases adjacentes
- Une matrice de points n*n qui permettra d'attribuer à chaque case un score pour le joueur. 
La somme de cette matrice de points donnera le score du joueur.

Pour calculer ces points, nous utilisons une fonction d'évaluation faisant appel à un algorithme de Dijkstra.
Pour trouver le meilleur coup pour un joueur, nous utilisons un algorithme min-max avec un élagage alpha-beta pour parcourir
toutes les meilleures solutions plus rapidement en éliminant celles avec un potentiel faible.
'''

import numpy as np
# from player import Bot
from game import Game
from player import Player, BotPlayer
from utils import dijkstra

class Ai(object):
    def __init__(self, game:Game):
        self.game = game
    
    def get_next_turn(self):
        pass

    def simulate_switch(self):
        pass

    def simulate_tile_change(self):
        pass

    @staticmethod
    def evaluate_position(p1:Player|BotPlayer, p2:Player|BotPlayer):
        p1.update_mat_points_pcc()
        p2.update_mat_points_pcc()
        min_pcc = min(p1.pcc[0], p2.pcc[0])
        for player in (p1,p2):
            grid_eval = min_pcc + 5 - player.mat_points
            grid_eval[grid_eval < 0] = 0
            grid_eval = grid_eval**2
            score = np.sum(grid_eval)
            player.mat_points = grid_eval
            player.score = score
        return p1.score, p2.score

    
    def update_evaluation(self):
        p1, p2 = self.players
        
        # max_pcc = max(self.player0.max_pcc, self.player1.max_pcc)
        

    # def find_shortest_paths(self, bot:Bot):
    #     bot.pcc = [np.inf, []]
    #     bot.max_pcc = 0
    #     bot.mat_points = np.full((bot.game_size, bot.game_size), fill_value=np.inf)
    #     border1, border2 = bot.game_borders[:bot.game_size], bot.game_borders[bot.game_size:]
    #     for x1, y1 in border1:
    #         poids, chemins = bot.dijkstra(x1,y1)
    #         # print(poids,chemins)
    #         for x2, y2 in border2:
    #             p = poids[(x2, y2)]
    #             if p < bot.pcc[0]:
    #                 bot.pcc = [p, []]
    #                 new_pcc = True
    #             else:
    #                 new_pcc = False
                
    #             if p > bot.max_pcc:
    #                 bot.max_pcc = p

    #             node = (x2, y2)
    #             while node != None:
    #                 x3, y3 = node
    #                 if new_pcc:
    #                     bot.pcc[1].append((x3,y3))
    #                 if p < bot.mat_points[y3][x3]:
    #                     bot.mat_points[y3][x3] = p
    #                 node = chemins[(x3, y3)]