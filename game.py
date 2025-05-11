import numpy as np
import random as rd
import time
from player import Player
from utils import get_cases_adj_minimax, blue, red, dessine_plateau
from constants import LETTERS


class Game(object):
    def __init__(self, n:int):
        self.mat = np.zeros((n,n), dtype=int)
        self.n = n
        self.p1 = Player(1, n, self.mat)
        self.p2 = Player(2, n, self.mat)
        self.turn = self.p1
        self.game_over = False

    def switch(self):
        if np.sum(self.mat != 0) == 1:
            y,x = np.argwhere(self.mat)[0]
            value = 1 if self.mat[y][x] == 2 else 2
            self.mat[y][x], self.mat[x][y] = 0, value
            self.next_turn()
        return x,y,value
    
    def next_turn(self):
        if self.turn == self.p1:
            self.turn = self.p2
        else:
            self.turn = self.p1
        
    
    def is_board_terminal(self):
        for player in (self.p1, self.p2):
            for x,y in player.border1:
                if self.mat[y][x] == player.id:
                    marqués = []
                    if self.parcours_prodondeur(x, y, player.border2, self.n, color_id=player.id, marqués=marqués):
                        return True
        return False
    
    def parcours_prodondeur(self, x:int, y:int, goal:tuple, size:int, color_id:int, marqués:list):
        if (x,y) in goal:
            return True
        
        marqués.append((x,y))

        for y1 in range(-1,2):
            for x1 in range(-1,2):
                x2, y2 = x+x1, y+y1
                if y1 == x1 or x2 >= size or x2 < 0 or y2 >= size or y2 < 0:
                    continue
                if self.mat[y2][x2] == color_id and (x2,y2) not in marqués:
                    if self.parcours_prodondeur(x2, y2, goal, size, color_id, marqués):
                        return True
        return False

    def minimax(self, max_id:int, min_id:int, 
                            depth:int, alpha:float, beta:float, is_max_turn:bool, root=False) -> tuple:
        if self.is_board_terminal() or depth <= 0: # si la position est terminale ou si on a atteint la profondeur de recherche maximale        
            return self.fonction_evaluation(max_id, depth), None
        
        best_move = None

        if is_max_turn: #max
            max_eval = -np.inf
            moves = self.potential_moves()
            for i,coords in enumerate(moves):
                if root:
                    pourcentage = (i+1)*100//len(moves) 
                    if max_id == 1:
                        print(red(f"\r{pourcentage*'#'+(100-pourcentage)*'-'} | {pourcentage}%"), end='', flush=True)
                    else:
                        print(blue(f"\r{pourcentage*'#'+(100-pourcentage)*'-'} | {pourcentage}%"), end='', flush=True)

                x,y = coords
                self.mat[y][x] = max_id
                eval, _ = self.minimax(max_id, min_id, depth-1, alpha, beta, False)
                self.mat[y][x] = 0

                if eval > max_eval:
                    max_eval = eval
                    best_move = (x,y)

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            if root : print("\r" + " " * 150 + "\r", end='', flush=True)
            return max_eval, best_move
        else: #min
            min_eval = np.inf
            for x,y in self.potential_moves():
                self.mat[y][x] = min_id
                eval, _ = self.minimax(max_id, min_id, depth-1, alpha, beta, True)
                self.mat[y][x] = 0
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = (x,y)

                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move
    
    def fonction_evaluation(self, max_id:int, depth=0):
        p1_pcc_len = self.p1.find_shortest_path_length()
        p2_pcc_len = self.p2.find_shortest_path_length()
        if p1_pcc_len == 0:
            return 1000*(depth+1) if max_id == 1 else -1000*(depth+1)
        elif p2_pcc_len == 0:
            return 1000*(depth+1) if max_id == 2 else -1000*(depth+1)
        else:
            score_p1 = p2_pcc_len - p1_pcc_len
            return score_p1 if max_id == 1 else -score_p1
    
    def get_best_move(self, player:Player, depth=2):
        n = self.mat.shape[0]
        if np.all(self.mat <= 1): # si c'est le premier tour du bot
            while True:
                if n > 3:
                    x,y = rd.randint(1,n-2), rd.randint(1,n-2) # retourne un coup au hasard dans le centre du plateau
                else: # si la taille du plateau est <= 3
                    x,y = rd.randint(0,n-1), rd.randint(0,n-1)
                
                if self.mat[y][x] == 0:
                    return x,y
        
        _,move = self.minimax(
            max_id=player.id, 
            min_id=player.opp_id, 
            depth=depth-1, 
            alpha=-np.inf, beta=np.inf, 
            is_max_turn=True,
            root=True
            )
        return move # retourne le coup sous forme de coordonnées x,y
    
    def potential_moves(self):
        return {(x2,y2) for y1,x1 in np.argwhere(self.mat!=0) 
                for x2,y2 in get_cases_adj_minimax(x1,y1,self.n) 
                if self.mat[y2][x2] == 0}
    
    



def jeu_affichage_terminal():

    def prompt(mat:np.ndarray):
        while True:
            try:
                move = input("Case? : ").strip()
                x,y = LETTERS.index(move[0].upper()), int(move[1:])-1
                if mat[y][x] == 0:
                    return x,y
            except (ValueError, IndexError):
                continue


    game_size = int(input("Taille du plateau de jeu ? : "))
    p1_bot = True if input("Player1 Joueur ou Bot ? [J/B] : ").lower() == "b" else False
    if p1_bot:
        p1_difficutly = int(input("Difficulté ? recommandé 1-5 : "))
    p2_bot = True if input("Player2 Joueur ou Bot ? [J/B] : ").lower() == "b" else False
    if p2_bot:
        p2_difficulty = int(input("Difficulté ? recommandé 1-5 : "))
    game = Game(game_size)
    dessine_plateau(game.mat)
    # t = 0
    # start = time.time()
    count = 0
    while not game.game_over:
        count += 1
        if count == 2:
            if p2_bot:
                if rd.randint(0,1) == 1:
                    game.switch()
                    dessine_plateau(game.mat)
                    print(blue("switch"))
                    
            else:
                value = True if str(input("switch ? [y/n] : ")).lower() == 'y' else False
                if value:
                    game.switch()
                    dessine_plateau(game.mat)
                    print(blue("switch"))

        # t+= 1 
        # print(f"Tour de", "Player1" if game.turn == game.p1 else "Player2")
        if game.turn == game.p1 and p1_bot:
            x,y = game.get_best_move(game.p1, p1_difficutly)
        elif game.turn == game.p1 and not p1_bot:
            x,y = prompt(game.mat)
        elif game.turn == game.p2 and p2_bot:
            x,y = game.get_best_move(game.p2, p2_difficulty)
        else:
            x,y = prompt(game.mat)
        game.mat[y][x] = game.turn.id
        dessine_plateau(game.mat)
        if game.turn == game.p1:
            print(red(f"{LETTERS[x]}{y+1}"))
        else:
            print(blue(f"{LETTERS[x]}{y+1}"))
        # game.evaluate()
        game.next_turn()
        if game.is_board_terminal():
            game.game_over = True
            print('GAME OVER')


if __name__ == '__main__':
    jeu_affichage_terminal()

        
    
