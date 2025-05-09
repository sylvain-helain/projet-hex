import numpy as np
import random as rd
import time
from player import Player
from utils import p1_border1, p1_border2, p2_border1, p2_border2, p1_borders, p2_borders, get_cases_adj_minimax


class GameHex(object):
    def __init__(self, n:int):
        self.mat = np.zeros((n,n), dtype=int)
        self.n = n
        self.p1 = Player(1, n, self.mat)
        self.p2 = Player(2, n, self.mat)
        self.turn = self.p1
        self.game_over = False

    
    def next_turn(self):
        if self.turn == self.p1:
            self.turn = self.p2
        else:
            self.turn = self.p1
    
    def is_board_terminal(self):
        goals = (
            [(x,y) for y in (0,self.n-1) for x in range(0,self.n)],
            [(x,y) for x in (0,self.n-1) for y in range(0,self.n)]
        )
        for i in range(2):
            side1, side2 = goals[i][:self.n], goals[i][self.n:]
            for x,y in side1:
                if self.mat[y][x] == i+1:
                    marqués = []
                    if self.parcours_prodondeur(x, y, side2, self.n, color_id=i+1, marqués=marqués):
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
                            depth:int, alpha:float, beta:float, is_max_turn:bool) -> float:
        # print(mat, is_board_terminal(mat))
        if self.is_board_terminal() or depth <= 0: # si la position est terminale ou si on a atteint la profondeur de recherche maximale        
            return self.fonction_evaluation(max_id, depth)
        
        if is_max_turn: #max
            max_eval = -np.inf
            for x,y in self.potential_moves():
                self.mat[y][x] = max_id
                eval = self.minimax(max_id, min_id, depth-1, alpha, beta, False)
                self.mat[y][x] = 0
                max_eval = max(max_eval, eval)

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else: #min
            min_eval = np.inf
            for x,y in self.potential_moves():
                self.mat[y][x] = min_id
                eval = self.minimax(max_id, min_id, depth-1, alpha, beta, True)
                self.mat[y][x] = 0
                min_eval = min(min_eval, eval)

                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    def fonction_evaluation(self, max_id:int, depth):
        n = self.mat.shape[0]
        p1_pcc_len = self.p1.find_shortest_path_length(self.p1.create_dict_adj(1, p1_borders(n)), n, p1_border1(n), p1_border2(n))
        p2_pcc_len = self.p2.find_shortest_path_length(self.p2.create_dict_adj(2, p2_borders(n)), n, p2_border1(n), p2_border2(n))
        # print(mat)
        # print(is_board_terminal(mat))
        if p1_pcc_len == 0:
            # print('win')
            return 1000*(depth+1) if max_id == 1 else -1000*(depth+1)
        elif p2_pcc_len == 0:
            # print('lose')
            return 1000*(depth+1) if max_id == 2 else -1000*(depth+1)
        else:
            # print(mat)
            score_p1 = p2_pcc_len - p1_pcc_len
            # print(score_p1)
            # score_p1 = score_p1/(p2_pcc_len+p1_pcc_len)
            # print(score_p1)
            # print(mat, score_p1)
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
        max_id = player.id
        min_id = 1 if max_id == 2 else 2
        res = {}
        moves = self.potential_moves()
        # print(len(moves))
        for index, coo in enumerate(moves):
            pourcentage = (index+1)*100//len(moves) 
            print(f"\r{pourcentage*'#'+(100-pourcentage)*'-'} | {pourcentage}%", end='', flush=True)
            # print('hey')
            x,y = coo
            self.mat[y][x] = max_id
            res[(x,y)] = self.minimax(
                max_id=max_id, 
                min_id=min_id, 
                depth=depth-1, 
                alpha=-np.inf, beta=np.inf, 
                is_max_turn=False
                )
            self.mat[y][x] = 0
        print("\r" + " " * 150 + "\r", end='', flush=True)
        return max(res, key=res.get) # retourne le coup sous forme de coordonnées x,y
    
    def potential_moves(self):
        return {(x2,y2) for y1,x1 in np.argwhere(self.mat!=0) 
                for x2,y2 in get_cases_adj_minimax(x1,y1,self.n) 
                if self.mat[y2][x2] == 0}
    
    



def affichage_terminal():
    ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    def blue(char:str):
        return f"\033[34m{char}\033[0m"

    def red(char:str):
        return f"\033[31m{char}\033[0m"

    def prompt(mat:np.ndarray):
        while True:
            try:
                move = input("Case? : ").strip()
                x,y = ALPHABET.index(move[0].upper()), int(move[1:])-1
                if mat[y][x] == 0:
                    return x,y
            except (ValueError, IndexError):
                continue
        
    def dessine_plateau(mat:np.ndarray):
        n = mat.shape[0]
        print('', red(' '.join([i for i in ALPHABET[:n]])))
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
        print(red(' '*pad + ' '.join([i for i in ALPHABET[:n]])))


    game_size = int(input("Taille du plateau de jeu ? : "))
    p1_bot = True if input("Player1 Joueur ou Bot ? [J/B] : ").lower() == "b" else False
    if p1_bot:
        p1_difficutly = int(input("Difficulté ? recommandé 1-5 : "))
    p2_bot = True if input("Player2 Joueur ou Bot ? [J/B] : ").lower() == "b" else False
    if p2_bot:
        p2_difficulty = int(input("Difficulté ? recommandé 1-5 : "))
    game = GameHex(game_size)
    dessine_plateau(game.mat)
    # t = 0
    # start = time.time()
    while not game.game_over:
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
            print(red(f"{ALPHABET[x]}{y+1}"))
        else:
            print(blue(f"{ALPHABET[x]}{y+1}"))
        # game.evaluate()
        game.next_turn()
        if game.is_board_terminal():
            game.game_over = True
            print('GAME OVER')


if __name__ == '__main__':
    affichage_terminal()

        
    
