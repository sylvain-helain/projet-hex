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
from constants import COLORS
import copy
from utils import is_board_terminal

class Ai(object):
    def __init__(self, game:Game, difficulty:int|None):
        self.game = game
        if difficulty == None:
            self.depth_max = 5
        else:
            self.depth_max = difficulty






            
        
    def minimax_alpha_beta(self, board:np.ndarray, player_cid:int, opp_cid:int, 
                           depth:int, alpha:float, beta:float, players_turn:bool, moves:list) -> float:
        if is_board_terminal(board) or depth <= 0: # si la position est terminale ou si on a atteint la profondeur de recherche maximale
            return self.evalutate_board_moves(moves, board)
        
        if players_turn: #max
            max_eval = -np.inf
            for y,x in np.argwhere(board == 0):
                copy_board = np.copy(board)
                copy_board[y][x] = player_cid
                new_moves = moves + [(x,y,player_cid)]
                eval = self.minimax_alpha_beta(copy_board, player_cid, opp_cid, depth-1, alpha, beta, False, new_moves)
                max_eval = max(max_eval, eval)

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else: #min
            min_eval = np.inf
            for y,x in np.argwhere(board == 0):
                copy_board = np.copy(board)
                copy_board[y][x] = opp_cid
                new_moves = moves + [(x,y,opp_cid)]
                eval = self.minimax_alpha_beta(copy_board, player_cid, opp_cid, depth-1, alpha, beta, True, new_moves)
                min_eval = min(min_eval, eval)

                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval


    def get_best_move(self, depth) -> tuple:
        mat_plateau = np.copy(self.game.mat_plateau)
        player = next(p for p in self.game.players if p.color == COLORS[self.game.turn%2])
        opponent = next(p for p in self.game.players if p.color == COLORS[(self.game.turn+1)%2])
        res = {}
        for y,x in np.argwhere(mat_plateau == 0): # argwhere retourne un array de coordonnées où la valeur de mat_plateau est égale à 0
            print('hey')
            moves = [(x,y,player.color_id)]
            copy_board = np.copy(mat_plateau)
            copy_board[y][x] = player.color_id
            res[(x,y)] = self.minimax_alpha_beta(board=copy_board, 
                                                 player_cid=player.color_id, 
                                                 opp_cid=opponent.color_id, 
                                                 depth=depth, 
                                                 alpha=-np.inf, beta=np.inf, 
                                                 players_turn=True,
                                                 moves = moves)
        return max(res, key=res.get) # retourne le coup sous forme de coordonnées x,y



    def simulate_switch(self):
        pass

    def evalutate_board_moves(self, moves, board):
        copy_player = next(p for p in self.game.players if p.color_id == moves[0][-1]).copy()
        copy_opp = next(p for p in self.game.players if p.color_id == moves[1][-1]).copy()
        for x,y,color_id in moves:
            if color_id == copy_player.color_id:
                Player.update_mat_adj(copy_player, copy_opp, board, self.game.size, x, y)
            else:
                Player.update_mat_adj(copy_opp, copy_player, board, self.game.size, x, y)
        Ai.evaluate_position(copy_player, copy_opp)
        return copy_player.score

    @staticmethod
    def simulate_move(board:np.ndarray, player:Player|BotPlayer, opponent:Player|BotPlayer, x:int, y:int, game_size:int) -> tuple:
        copy_board = np.copy(board)
        copy_player = copy.deepcopy(player)
        copy_opponent = copy.deepcopy(opponent)
        # copy_player = player.copy()
        # copy_opponent = opponent.copy()
        copy_board[y][x] = copy_player.color_id
        Player.update_mat_adj(copy_player, copy_opponent, copy_board, game_size, x, y)
        Ai.evaluate_position(copy_player, copy_opponent)
        return copy_board, copy_player, copy_opponent
    
    def handle_board_tile_change(self, player_id, x, y):
        p1 = next(p for p in self.game.players if p.id == player_id)
        p2 = next(p for p in self.game.players if p.id == (player_id+1)%2)
        Player.update_mat_adj(p1, p2, self.game.mat_plateau, self.game.size, x, y)
        Ai.evaluate_position(p1, p2)

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

        total = p1.score + p2.score
        # le score ira de -1 à 1 -> 1=gagnant, -1=perdant, 0=neutre
        p1.score = p1.score*2/total - 1
        p2.score = p2.score*2/total - 1


    def update_evaluation(self):
        p1, p2 = self.players
        
        # max_pcc = max(self.player0.max_pcc, self.player1.max_pcc)
        
