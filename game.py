import numpy as np
import random as rd
# import time
from player import Player
from utils import get_cases_adj_minimax, blue, red, dessine_plateau, get_cases_adj
from constants import LETTERS


class Game(object):
    '''Classe contenant une instance du jeu Hex, on y trouve plusieurs fonctions utiles à la prise de décision de l'ia
    On prend en entrée la taille du plateau n.'''
    def __init__(self, n:int):
        self.mat = np.zeros((n,n), dtype=int) # plateau, matrice n*n
        self.n = n
        self.p1 = Player(1, n, self.mat) # joueur rouge
        self.p2 = Player(2, n, self.mat) # joueur bleu
        self.turn = self.p1 # le tour de quel joueur
        self.game_over = False

    def switch(self):
        '''Fonction appelée lors d'un switch du joueur bleu'''
        if np.sum(self.mat != 0) == 1: # si on a bien qu'un pion sur le plateau
            y,x = np.argwhere(self.mat)[0] # on trouve l'emplacement du pion rouge
            # on intervertit les cases avec les valeurs correspondantes
            value = 1 if self.mat[y][x] == 2 else 2
            self.mat[y][x], self.mat[x][y] = 0, value
            self.next_turn()
            return x,y,value
        else:
            raise Exception("Le plateau de jeu ne permet pas le switch")
    
    def next_turn(self):
        '''Fonction pour passer d'un tour d'un joueur à l'autre.'''
        if self.turn == self.p1:
            self.turn = self.p2
        else:
            self.turn = self.p1
        
    
    def is_board_terminal(self) -> bool:
        '''Retourne Vrai si le jeu est terminé (càd un joueur a relié ses deux côtés avec une chaîne de ses pions).
        Nous sert de condition de victoire simple et rapide dans l'algorithme Minimax (au lieu d'appeler Dijkstra à chaque fois).'''
        for player in (self.p1, self.p2):
            for x,y in player.border1:
                if self.mat[y][x] == player.id:
                    marqués = []
                    if self.parcours_prodondeur(x, y, player.border2, self.n, color_id=player.id, marqués=marqués):
                        return True
        return False
    
    def parcours_prodondeur(self, x:int, y:int, goal:tuple, size:int, color_id:int, marqués:list):
        '''Parcours en profondeur d'une matrice de jeu, on part d'une case d'un côté en suivant des cases colorées par un même joueur.
        On retourne Vrai si cette case est reliée au côté opposé de la matrice, Faux sinon.'''
        if (x,y) in goal:
            return True

        marqués.append((x,y))
        for x1,y1 in get_cases_adj(x,y,size):
            if self.mat[y1][x1] == color_id and (x1,y1) not in marqués:
                if self.parcours_prodondeur(x1, y1, goal, size, color_id, marqués):
                    return True
        return False

    def minimax(self, max_id:int, min_id:int, depth:int, alpha:float, beta:float, is_max_turn:bool, root=False) -> tuple:
        '''Algorithme minimax avec élagage alpha-beta.

        max_id: ID (1 ou 2) du joueur voulant maximiser son score (l'IA), min_id: ID de son adversaire (joueur)
        depth : profondeur maximale de coups à explorer
        alpha : meilleur score que max peut garantir
        beta : pire score que min peut garantir
        is_max_turn : passe de True à False a chaque récursion pour déterminer le tour des joueurs
        root : False par défaut, True lors de l'appel initial pour pouvoir afficher la barre de progression dans la racine

        Retourne le meilleur coup de max trouvé sous la forme : score_max, (x,y)
        Grâce à une fonction d'évaluation basée sur Dijkstra, on évalue les positions non terminales atteintes par minimax.
        Grâce à l'élagage alpha-beta, on n'explore pas certains coups intutiles, accélérant ainsi considérablement la recherche de coup.
        Affichage dans le terminal de la progression avec une barre de progression.
        '''
        if self.is_board_terminal() or depth <= 0: # si la position est terminale ou si on a atteint la profondeur de recherche maximale        
            return self.fonction_evaluation(max_id, depth), None
        
        best_move = None

        if is_max_turn: # tour de max
            max_eval = -np.inf
            # moves : tous les coups ayant du potentiel (ceux adjacents aux cases déjà posées et ceux formant des ponts)
            moves = self.potential_moves()
            for i,coords in enumerate(moves):
                if root: #pour l'affichage de la barre de progression
                    pourcentage = (i+1)*100//len(moves) 
                    if max_id == 1:
                        print(red(f"\r{pourcentage*'#'+(100-pourcentage)*'-'} | {pourcentage}%"), end='', flush=True)
                    else:
                        print(blue(f"\r{pourcentage*'#'+(100-pourcentage)*'-'} | {pourcentage}%"), end='', flush=True)

                x,y = coords
                self.mat[y][x] = max_id # on joue le coup directement dans la matrice de jeu, pour éviter des copies inutiles
                eval, _ = self.minimax(max_id, min_id, depth-1, alpha, beta, False) # appel récursif
                self.mat[y][x] = 0 # on annule le coup

                if eval > max_eval:
                    max_eval = eval
                    best_move = (x,y)

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            if root : print("\r" + " " * 150 + "\r", end='', flush=True) # efface la barre de progression
            return max_eval, best_move
        else: #tour de min
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
        '''Fonction qui retourne l'évaluation du joueur maximisant selon la matrice de jeu mat.
        On base cette évaluation sur les pcc (plus courts chemins) de chaque joueurs.
        score_max = pcc_min - pcc_max
        car on veut que pcc_min soit + grand et que pcc_max soit + petit
        
        Si le jeu est terminal:
         - max gagne si son pcc_max == 0 et pcc_min == inf
         - min gagne si son pcc_min == 0 et pcc_max == inf
        Dans ces cas, le score d'un joueur gagnant est égal à 1000*(depth+1), car on veut favoriser des victoires rapides, lorsqu'un
        coup gagnant peut être joué, on le joue tout de suite. (si depth == 0, on est au maximum de la profondeur de recherche)'''
        # calcul des plus courts chemins pour les deux joueurs
        p1_pcc_len = self.p1.find_shortest_path_length()
        p2_pcc_len = self.p2.find_shortest_path_length()
        
        if p1_pcc_len == 0: #p1 gagne
            return 1000*(depth+1) if max_id == 1 else -1000*(depth+1)
        elif p2_pcc_len == 0: #p2 gagne
            return 1000*(depth+1) if max_id == 2 else -1000*(depth+1)
        else: # si le jeu n'est pas terminal
            score_p1 = p2_pcc_len - p1_pcc_len
            return score_p1 if max_id == 1 else -score_p1
    
    def get_best_move(self, player:Player, depth=2):
        '''Retourne le meilleur coup calculé par l'algo Minimax pour un joueur en entrée.
        Caclul du coup selon une profondeur en entrée, par défaut : 2.'''
        n = self.mat.shape[0]
        if np.all(self.mat <= 1): # si c'est le premier coup du bot, on le fait jouer un coup au hasard
            while True: # boucle tant que le coup joué n'est pas sur une case déjà occupée
                if n > 3:
                    x,y = rd.randint(1,n-2), rd.randint(1,n-2) # retourne un coup au hasard dans le centre du plateau
                else: # si la taille du plateau est <= 3
                    x,y = rd.randint(0,n-1), rd.randint(0,n-1)
                
                if self.mat[y][x] == 0:
                    return x,y
        # start = time.time()
        _,move = self.minimax(
            max_id=player.id, 
            min_id=player.opp_id, 
            depth=depth, 
            alpha=-np.inf, beta=np.inf, 
            is_max_turn=True,
            root=True
            )
        # end = time.time()
        # print(f"{end-start:.4f}s")
        return move # retourne le coup sous forme de coordonnées x,y
    
    def potential_moves(self):
        '''Retourne tous les coups potentiellements intéressants à joueur dans le plateau.
        Regarde chaque cases vides adjacentes à des cases occupées. On regarde aussi les cases formant des ponts avec
        celles occupées (pont : deux cases qu'on peut relier de deux manières différentes).'''
        # argwhere : trouve les cases occupées
        # get_cases_adj_minimax : trouve les cases remplissants les critères cités en description de fonction
        # self.mat[y2][x2] == 0 : on vérifie que la case trouvée et libre
        return {(x2,y2) for y1,x1 in np.argwhere(self.mat!=0) 
                for x2,y2 in get_cases_adj_minimax(x1,y1,self.n) 
                if self.mat[y2][x2] == 0}
    
    



def jeu_affichage_terminal():
    '''Fonction pour lancer un jeu dans le terminal, tous les paramètres de partie seront demandés à la suite par des inputs.'''
    def prompt(mat:np.ndarray):
        '''Fonction pour demander une case à placer, vérifie la bonne écriture. Boucle tant que l'utilisateur rentre une mauvaise valeur
        Retourne les coordonnées x et y de la case entrée par l'utilisateur.
        L'entrée utilisateur doit commencer par une lettre puis un nombre de 1 à n (n : taille du plateau) pour représenter la case.'''
        while True: # tant que l'entrée utilisateur est incorrecte
            try:
                move = input("Case? : ").strip() # on demande une case ex: A1, D7, B11...
                x,y = LETTERS.index(move[0].upper()), int(move[1:])-1
                if mat[y][x] == 0: # si la case est libre
                    return x,y
            except (ValueError, IndexError): # si la valeur en entrée est incorrecte
                continue # on boucle

    # paramètres du jeu
    game_size = int(input("Taille du plateau de jeu ? : "))
    p1_bot = True if input("Player1 Joueur ou Bot ? [J/B] : ").lower() == "b" else False
    if p1_bot:
        p1_difficutly = int(input("Difficulté ? recommandé 1-5 : "))
    p2_bot = True if input("Player2 Joueur ou Bot ? [J/B] : ").lower() == "b" else False
    if p2_bot:
        p2_difficulty = int(input("Difficulté ? recommandé 1-5 : "))

    game = Game(game_size)
    dessine_plateau(game.mat)

    count = 0
    while not game.game_over:
        count += 1
        if count == 2: # si on est au 1er tour du joueur bleu, il a le choix de switch
            if p2_bot: # si c'est au bot de choisir, il le fera avec une chance de 1/2
                if rd.randint(0,1) == 1:
                    game.switch()
                    dessine_plateau(game.mat)
                    print(blue("switch"))
            else: # si c'est un humain, on lui demande
                value = True if str(input("switch ? [y/n] : ")).lower() == 'y' else False
                if value:
                    game.switch()
                    dessine_plateau(game.mat)
                    print(blue("switch"))

        if game.turn == game.p1 and p1_bot: # tour de p1, bot
            x,y = game.get_best_move(game.p1, p1_difficutly)
        elif game.turn == game.p1 and not p1_bot: # tour de p1, humain
            x,y = prompt(game.mat)
        elif game.turn == game.p2 and p2_bot: # tour de p2, bot
            x,y = game.get_best_move(game.p2, p2_difficulty)
        else: # tour de p2, humain
            x,y = prompt(game.mat)

        game.mat[y][x] = game.turn.id # place le coup
        dessine_plateau(game.mat) # affiche le plateau
        if game.turn == game.p1: # affiche le coup
            print(red(f"{LETTERS[x]}{y+1}"))
        else:
            print(blue(f"{LETTERS[x]}{y+1}"))

        game.next_turn()
        if game.is_board_terminal(): # si un joueur a gagné
            game.game_over = True
            print('GAME OVER')


if __name__ == '__main__':
    jeu_affichage_terminal()

        
    
